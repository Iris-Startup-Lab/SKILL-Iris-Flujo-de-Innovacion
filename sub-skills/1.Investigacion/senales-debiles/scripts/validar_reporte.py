"""
Validador determinista del reporte ejecutivo de señales débiles.
Verifica contra las reglas de SPEC.md (estructura, badges, numeración,
tono, heatmap, footer) y contra el invariante de clasificación de
AGENTE.md sobre los JSON de entrada (Fases 1-3): toda señal con
clasificación "confirmacion"/"tension" debe tener escala_a_fase4: false.
Además, si se proporciona fase4_output.json, verifica que mapeo_html
sea completo y coherente con los items que escalan de Fases 1-3, y que
ningún cruce transpoblacional escale solo.
Complementa —no reemplaza— la revisión manual del checklist completo de
SPEC.md seccion 10.

Uso: python validar_reporte.py reporte_ejecutivo.html fase1_output.json fase2_output.json fase3_output.json [fase4_output.json]

(fase0_output.json se ignora si se incluye por error; fase4_output.json se detecta por nombre)
"""
import sys
import re
import json
from pathlib import Path
from bs4 import BeautifulSoup
from invariante_clasificacion import (verificar_invariante,
                                      items_de_fase as invar_items_de_fase)


class ValidationError:
    def __init__(self, level, msg):
        self.level = level  # "ERROR" o "WARN"
        self.msg = msg

    def __str__(self):
        return f"[{self.level}] {self.msg}"


def validar(html_path):
    errores = []
    with open(html_path, encoding="utf-8-sig") as f:
        html = f.read()
    soup = BeautifulSoup(html, "html.parser")

    # --- 1. Estructura básica ---
    if not soup.find("html"):
        errores.append(ValidationError("ERROR", "Falta tag <html>"))
    if not soup.find("head"):
        errores.append(ValidationError("ERROR", "Falta tag <head>"))
    if not soup.find("body"):
        errores.append(ValidationError("ERROR", "Falta tag <body>"))

    # --- 2. Design system: fuentes y variables CSS ---
    style_tags = soup.find_all("style")
    css_text = " ".join(s.get_text() for s in style_tags)
    if "Sora" not in html and "Sora" not in css_text:
        errores.append(ValidationError("WARN", "No se detectó la fuente 'Sora' (títulos)"))
    if "Inter" not in html and "Inter" not in css_text:
        errores.append(ValidationError("WARN", "No se detectó la fuente 'Inter' (cuerpo)"))
    if "--" not in css_text:
        errores.append(ValidationError("WARN", "No se detectaron variables CSS (custom properties)"))

    # --- 3. Ausencia de badges de severidad ---
    badge_patterns = [r"badge", r"\betiqueta\b", r"\bpill\b", r"tag-label"]
    for pat in badge_patterns:
        hits = soup.find_all(class_=re.compile(pat, re.I))
        if hits:
            errores.append(ValidationError(
                "ERROR",
                f"Se encontraron {len(hits)} elemento(s) con clase que sugiere badge ('{pat}')"
            ))
    if re.search(r"\b(Crítica|Alta|Media|Baja)\b\s*(severidad)?", soup.get_text()) and \
       soup.find(class_=re.compile(r"badge|pill", re.I)):
        errores.append(ValidationError("WARN", "Posible etiqueta de severidad visible en el texto"))

    # --- 4. Conteo de secciones (deben ser exactamente 2) ---
    secciones = soup.find_all("section")
    if not secciones:
        secciones = soup.find_all("h2")
    if len(secciones) != 2:
        errores.append(ValidationError(
            "ERROR", f"Se esperaban 2 secciones, se encontraron {len(secciones)}"
        ))

    # --- 5. Tarjetas de señal: 5 campos esperados ---
    # Se usa word boundary para no confundir 'cards' (contenedor) con 'card'.
    tarjetas = soup.find_all(class_=re.compile(r"\b(card|tarjeta)\b", re.I))
    campos_esperados = ["dato", "expectativa", "pregunta", "hipótesis", "hipotesis"]
    # Solo tarjetas de nivel superior: si una tarjeta anida otra, no se cuenta dos veces.
    señal_cards = [
        c for c in tarjetas
        if re.search(r"señal débil \d+", c.get_text(), re.I)
        and not any(c in padre for padre in tarjetas if padre is not c)
    ]
    if señal_cards:
        for i, card in enumerate(señal_cards, start=1):
            texto = card.get_text(" ", strip=True).lower()
            campos_detectados = sum(1 for c in campos_esperados if c in texto)
            if campos_detectados < 3:
                errores.append(ValidationError(
                    "WARN",
                    f"Tarjeta de señal #{i}: solo se detectaron {campos_detectados} campos "
                    f"reconocibles (se esperan 5: dato, expectativa, pregunta, hipótesis)"
                ))
    else:
        errores.append(ValidationError("ERROR", "No se encontraron tarjetas de 'Señal Débil N'"))

    n_senales = len(señal_cards)
    if not (1 <= n_senales <= 5):
        errores.append(ValidationError(
            "ERROR", f"Número de señales fuera de rango (1-5): se encontraron {n_senales}"
        ))
    elif n_senales < 3:
        errores.append(ValidationError(
            "WARN", f"Solo {n_senales} señal(es) publicadas (3-5 es el objetivo; "
                    "con 1-2 la escasez debe declararse en las advertencias)"
        ))

    # --- 6. Numeración secuencial de títulos ("Señal Débil N:") ---
    titulos_senal = re.findall(r"Señal Débil (\d+):", soup.get_text())
    numeros = [int(n) for n in titulos_senal]
    if numeros and numeros != list(range(1, len(numeros) + 1)):
        errores.append(ValidationError(
            "ERROR", f"Numeración de señales no es secuencial: {numeros}"
        ))

    # --- 7. Sin IDs técnicos visibles en el HTML ---
    if re.search(r"\b(SD-CUANT-\d+|SD-CUAL-\d+|CRUCE-\d+)\b", soup.get_text()):
        errores.append(ValidationError(
            "ERROR", "Se encontraron IDs técnicos (SD-CUANT-*/SD-CUAL-*/CRUCE-*) visibles en el HTML"
        ))

    # --- 8. Tono: lenguaje de certeza/temporalidad prohibido ---
    prohibidos = [
        r"\bconcluimos\b", r"\bes evidente que\b", r"\bdebemos\b",
        r"\bpróxima semana\b", r"\bmañana\b", r"\bel mes que viene\b",
        r"\bimplementar\b", r"\bhacer\b\s+(esto|eso|lo siguiente)"
    ]
    texto_body = soup.get_text()
    for pat in prohibidos:
        if re.search(pat, texto_body, re.I):
            errores.append(ValidationError(
                "WARN", f"Lenguaje de certeza/temporalidad detectado: patrón '{pat}'"
            ))

    # --- 9. Heatmap SVG inline (no chartjs-chart-matrix) ---
    if "chartjs-chart-matrix" in html or "chart-matrix" in html:
        errores.append(ValidationError(
            "ERROR", "Se detectó referencia a chartjs-chart-matrix (prohibido, debe ser SVG inline)"
        ))
    svgs = soup.find_all("svg")
    if not svgs:
        errores.append(ValidationError(
            "WARN", "No se encontró ningún <svg> inline (verificar si el reporte requiere heatmap)"
        ))

    # SVG y scripts no aportan a las comprobaciones de texto; los removemos para acelerar get_text()
    for tag in soup.find_all(["svg", "script"]):
        tag.decompose()

    # --- 10. Decisiones estratégicas: proporcionales a señales publicadas ---
    decisiones_texto = soup.get_text()
    n_decisiones = len(re.findall(r"Basado en:\s*Señal Débil", decisiones_texto))
    max_decisiones = 3
    min_decisiones = 1 if n_senales <= 1 else 2
    if n_decisiones and not (min_decisiones <= n_decisiones <= max_decisiones):
        errores.append(ValidationError(
            "ERROR", f"Número de decisiones fuera de rango ({min_decisiones}-{max_decisiones}) "
                     f"para {n_senales} señal(es): se encontraron {n_decisiones}"
        ))

    # --- 11. Footer sin sección de trazabilidad ---
    footer = soup.find("footer")
    if footer:
        if re.search(r"traza|mapeo de ids|SD-CUANT|SD-CUAL|CRUCE-", footer.get_text(), re.I):
            errores.append(ValidationError(
                "ERROR", "El footer contiene referencias de trazabilidad o IDs técnicos (prohibido)"
            ))
    else:
        errores.append(ValidationError("WARN", "No se encontró tag <footer>"))

    return errores


def validar_invariante_json(json_paths):
    """Invariantes de AGENTE.md sobre los JSON de Fases 1-3:
    - clasificacion_hipotesis_previa != "señal débil" => escala_a_fase4 = false.
    - Ningún cruce transpoblacional tiene escala_a_fase4 = true.

    Usa la implementación única en invariante_clasificacion.py, la misma que
    validar_esquema.py aplica como gate intermedio al cierre de Fases 1-3."""
    errores = []
    for path in json_paths:
        try:
            with open(path, encoding="utf-8-sig") as f:
                data = json.load(f)
        except (OSError, ValueError) as e:
            errores.append(ValidationError("ERROR", f"No se pudo leer {path}: {e}"))
            continue
        if not invar_items_de_fase(data):
            continue
        for nivel, msg in verificar_invariante(data, path):
            errores.append(ValidationError(nivel, msg))
    return errores


def validar_mapeo_completo(json_paths, fase4_path):
    """Verifica que mapeo_html de fase4 incluya exactamente los items con
    escala_a_fase4=true de fases 1-3 y nada más."""
    errores = []
    try:
        with open(fase4_path, encoding="utf-8-sig") as f:
            fase4 = json.load(f)
    except (OSError, ValueError) as e:
        errores.append(ValidationError("ERROR", f"No se pudo leer {fase4_path}: {e}"))
        return errores

    mapeo = fase4.get("mapeo_html") or {}
    if not isinstance(mapeo, dict):
        errores.append(ValidationError("ERROR", f"{fase4_path}: mapeo_html no es un dict"))
        return errores

    escala_ids = {}
    for path in json_paths:
        try:
            with open(path, encoding="utf-8-sig") as f:
                data = json.load(f)
        except (OSError, ValueError) as e:
            errores.append(ValidationError("ERROR", f"No se pudo leer {path}: {e}"))
            continue
        for bloque in data.get("datos", {}).get("bloques", []):
            for key in ("senales", "cruces"):
                for item in bloque.get(key, []):
                    iid = item.get("id")
                    if item.get("escala_a_fase4") is True:
                        escala_ids[iid] = path

    ids_mapeados = set(mapeo.values())

    # Corte estructurado (fase-4-entrega.md): bloque datos.corte con score compuesto.
    datos_f4 = fase4.get("datos") if isinstance(fase4.get("datos"), dict) else {}
    corte = datos_f4.get("corte") if isinstance(datos_f4.get("corte"), dict) else None
    corte_valido = bool(
        corte and corte.get("aplicado") is True
        and isinstance(corte.get("score"), dict) and corte["score"])
    # Fallback (legado): prosa en advertencias.
    tope5 = (len(ids_mapeados) <= 5 and (corte_valido or any(
        isinstance(adv, str) and re.search(
            r"corte\s+de\s+tope\s*5|tope\s+de\s*5\s+se[ñn]ales|score\s+compuesto", adv, re.I)
        for adv in fase4.get("advertencias", []))))

    if corte_valido:
        # Verificar coherencia del score compuesto (SPEC seccion 5) y top-5.
        try:
            ranked = sorted(
                ((iid, float(sc.get("score", 0)))
                 for iid, sc in corte["score"].items() if isinstance(sc, dict)),
                key=lambda t: t[1], reverse=True)
            top5 = [iid for iid, _ in ranked[:5]]
        except (TypeError, ValueError):
            top5 = []
        excluidas = set(corte.get("excluidas") or [])
        if top5:
            no_top = [iid for iid in ids_mapeados if iid not in top5 and iid not in excluidas]
            if no_top:
                errores.append(ValidationError(
                    "ERROR",
                    f"mapeo_html incluye {sorted(no_top)} que no estan en el top-5 por "
                    f"score compuesto de datos.corte (SPEC seccion 5)"))
        fuera_declaradas = [iid for iid in escala_ids
                            if iid not in ids_mapeados and iid not in excluidas]
        if fuera_declaradas:
            errores.append(ValidationError(
                "ERROR",
                f"{sorted(fuera_declaradas)} tienen escala_a_fase4=true, no estan en mapeo_html "
                f"y no se declaran en datos.corte.excluidas"))

    fuera_por_tope = []
    for iid, path in escala_ids.items():
        if iid not in ids_mapeados:
            if tope5:
                fuera_por_tope.append(iid)
            else:
                errores.append(ValidationError(
                    "ERROR",
                    f"{iid} (escala_a_fase4=true en {path}) no aparece en mapeo_html. "
                    f"Con mas de 5 candidatos debe declararse el corte de tope 5 por "
                    f"score compuesto (datos.corte o advertencias de fase4, SPEC seccion 5)"
                ))
    if fuera_por_tope and not corte_valido:
        errores.append(ValidationError(
            "WARN",
            f"{len(escala_ids)} items escalan y mapeo_html publica {len(ids_mapeados)}; "
            f"corte de tope 5 declarado en fase4. Fuera del reporte: {sorted(fuera_por_tope)}"
        ))
    for k, v in mapeo.items():
        if v not in escala_ids:
            errores.append(ValidationError(
                "ERROR",
                f"{k} -> {v} está en mapeo_html pero no tiene escala_a_fase4=true en fases 1-3"
            ))
    return errores


def extraer_graficas_html(html):
    """Extrae el dict window.REPORT_GRAFICAS del HTML generado."""
    m = re.search(r"window\.REPORT_GRAFICAS\s*=\s*(\{.*?\});", html, re.DOTALL)
    if not m:
        return {}
    try:
        graficas = json.loads(m.group(1))
        return graficas if isinstance(graficas, dict) else {}
    except (ValueError, TypeError):
        return {}


def validar_n_etiquetas(html):
    """Verifica coherencia de N en etiquetas de gráficas (SPEC seccion 7):
    si el título de la gráfica declara N=<total> y TODAS las etiquetas llevan
    (n=<valor>), la suma de los n debe coincidir con N. Scope acotado a este
    caso para evitar falsos positivos (consenso: no parsear texto narrativo)."""
    errores = []
    for cid, cfg in extraer_graficas_html(html).items():
        title = (cfg.get("options", {}).get("plugins", {}).get("title", {}).get("text") or "")
        labels = (cfg.get("data", {}) or {}).get("labels") or []
        m_n = re.search(r"N\s*=\s*(\d+)", str(title))
        if not m_n:
            continue
        n_total = int(m_n.group(1))
        ns = []
        for lbl in labels:
            if isinstance(lbl, list):
                lbl = " ".join(lbl)
            if isinstance(lbl, str):
                m = re.search(r"\(?\s*n\s*=\s*(\d+)\s*\)?", lbl)
                if m:
                    ns.append(int(m.group(1)))
        if ns and len(ns) == len(labels) and sum(ns) != n_total:
            errores.append(ValidationError(
                "WARN",
                f"{cid}: la suma de n en etiquetas ({sum(ns)}) no coincide con "
                f"N={n_total} declarado en el título de la gráfica"))
    return errores


def main():
    if "-h" in sys.argv[1:] or "--help" in sys.argv[1:]:
        print(__doc__)
        sys.exit(0)          # la ayuda pedida no es un error
    if len(sys.argv) < 5:
        print("Uso: python validar_reporte.py reporte_ejecutivo.html "
              "fase1_output.json fase2_output.json fase3_output.json [fase4_output.json]",
              file=sys.stderr)
        sys.exit(1)

    html_path = sys.argv[1]
    raw_paths = sys.argv[2:]

    # Robustez: ignorar fase0 si alguien la incluye; separar fase4 por nombre.
    fase4_candidates = [p for p in raw_paths if "fase4" in Path(p).name]
    fase4_path = fase4_candidates[0] if fase4_candidates else None
    json_paths = [p for p in raw_paths
                  if "fase0" not in Path(p).name and p != fase4_path]

    # Si no se detectó fase4 por nombre y hay 4 JSON, asumir convención antigua.
    if fase4_path is None and len(json_paths) == 4:
        fase4_path = json_paths[-1]
        json_paths = json_paths[:3]

    errores = validar(html_path)
    if json_paths:
        errores.extend(validar_invariante_json(json_paths))
    if fase4_path:
        errores.extend(validar_mapeo_completo(json_paths, fase4_path))
    with open(html_path, encoding="utf-8-sig") as f:
        errores.extend(validar_n_etiquetas(f.read()))

    if not errores:
        print("Reporte valido. No se encontraron problemas.")
        sys.exit(0)

    n_err = sum(1 for e in errores if e.level == "ERROR")
    n_warn = sum(1 for e in errores if e.level == "WARN")
    for e in errores:
        print(e)
    print(f"\nResumen: {n_err} error(es), {n_warn} advertencia(s).")
    sys.exit(1 if n_err else 0)


if __name__ == "__main__":
    main()
