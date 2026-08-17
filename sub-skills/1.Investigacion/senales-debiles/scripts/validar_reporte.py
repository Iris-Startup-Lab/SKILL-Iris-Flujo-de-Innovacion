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


class ValidationError:
    def __init__(self, level, msg):
        self.level = level  # "ERROR" o "WARN"
        self.msg = msg

    def __str__(self):
        return f"[{self.level}] {self.msg}"


def validar(html_path):
    errores = []
    with open(html_path, encoding="utf-8") as f:
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
    tarjetas = soup.find_all(class_=re.compile(r"card|tarjeta", re.I))
    campos_esperados = ["dato", "expectativa", "pregunta", "hipótesis", "hipotesis"]
    señal_cards = [c for c in tarjetas if re.search(r"señal débil \d+", c.get_text(), re.I)]
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
    if not (3 <= n_senales <= 5):
        errores.append(ValidationError(
            "ERROR", f"Número de señales fuera de rango (3-5): se encontraron {n_senales}"
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

    # --- 10. Decisiones estratégicas: 2 o 3, referencian señales ---
    decisiones_texto = soup.get_text()
    n_decisiones = len(re.findall(r"Basado en:\s*Señal Débil", decisiones_texto))
    if n_decisiones and not (2 <= n_decisiones <= 3):
        errores.append(ValidationError(
            "ERROR", f"Número de decisiones fuera de rango (2-3): se encontraron {n_decisiones}"
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
    - Ningún cruce transpoblacional tiene escala_a_fase4 = true."""
    errores = []
    esquemas = {
        "fase-1-eda-cuantitativo": "senales",
        "fase-2-eda-cualitativo": "senales",
        "fase-3-cruce": "cruces",
    }
    clasificaciones_validas = {"confirmacion", "señal débil", "tension"}
    for path in json_paths:
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, ValueError) as e:
            errores.append(ValidationError("ERROR", f"No se pudo leer {path}: {e}"))
            continue
        items_key = esquemas.get(data.get("fase", ""))
        if not items_key:
            continue
        bloques = data.get("datos", {}).get("bloques", [])
        for bloque in bloques:
            for item in bloque.get(items_key, []):
                clasif = item.get("clasificacion_hipotesis_previa")
                escala = item.get("escala_a_fase4")
                item_id = item.get("id", "?")
                if clasif in ("confirmacion", "tension") and escala is True:
                    errores.append(ValidationError(
                        "ERROR",
                        f"{path}: {item_id} tiene clasificacion '{clasif}' pero escala_a_fase4=true "
                        f"(Filtro 2 de AGENTE.md: no escala como señal débil)"
                    ))
                elif clasif not in clasificaciones_validas and clasif is not None:
                    errores.append(ValidationError(
                        "WARN",
                        f"{path}: {item_id} tiene clasificación inválida '{clasif}'"
                    ))
                if item.get("tipo_cruce") == "transpoblacional" and escala is True:
                    errores.append(ValidationError(
                        "ERROR",
                        f"{path}: {item_id} es transpoblacional y tiene escala_a_fase4=true "
                        f"(blindaje de cruces transpoblacionales)"
                    ))
    return errores


def validar_mapeo_completo(json_paths, fase4_path):
    """Verifica que mapeo_html de fase4 incluya exactamente los items con
    escala_a_fase4=true de fases 1-3 y nada más."""
    errores = []
    try:
        with open(fase4_path, encoding="utf-8") as f:
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
            with open(path, encoding="utf-8") as f:
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
    for iid, path in escala_ids.items():
        if iid not in ids_mapeados:
            errores.append(ValidationError(
                "ERROR",
                f"{iid} (escala_a_fase4=true en {path}) no aparece en mapeo_html"
            ))
    for k, v in mapeo.items():
        if v not in escala_ids:
            errores.append(ValidationError(
                "ERROR",
                f"{k} -> {v} está en mapeo_html pero no tiene escala_a_fase4=true en fases 1-3"
            ))
    return errores


def main():
    if len(sys.argv) < 5:
        print("Uso: python validar_reporte.py reporte_ejecutivo.html "
              "fase1_output.json fase2_output.json fase3_output.json [fase4_output.json]")
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
