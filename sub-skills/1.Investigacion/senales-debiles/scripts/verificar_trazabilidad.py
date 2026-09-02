"""
Verificador determinista de trazabilidad entre fases y del reporte.

Implementa los invariantes de SPEC.md seccion 0:
  0.1 pregunta_investigacion identica byte a byte en todos los JSON y en el
      header del HTML.
  0.3 IDs referenciados (fase3, advertencias, redundancia) existen en las
      fases que los emiten; el HTML no tiene senales duplicadas ni fuera de
      rango; los timestamps estan en orden cronologico.

Uso:
    python verificar_trazabilidad.py <fase0_output.json> ... <fase4_output.json> <reporte_ejecutivo.html>
"""
import math
import sys
import re
import json
import unicodedata

RE_ID = re.compile(r"\b(SD-CUANT-\d+|SD-CUAL-\d+|CRUCE-\d+)\b")


class Hallazgo:
    def __init__(self, nivel, msg):
        self.nivel = nivel  # "ERROR" | "WARN" | "OK"
        self.msg = msg

    def __str__(self):
        return f"[{self.nivel}] {self.msg}"


def normalizar(texto):
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", texto.lower()).strip()


def extraer_items(data):
    items = []
    for bloque in data.get("datos", {}).get("bloques", []):
        for key in ("senales", "cruces"):
            items.extend(bloque.get(key, []))
    return items


def orden_fase(nombre):
    return {"fase-0-viabilidad": 0, "fase-1-eda-cuantitativo": 1,
            "fase-2-eda-cualitativo": 2, "fase-3-cruce": 3,
            "fase-4-entrega": 4}.get(nombre, 99)


def verificar(json_paths, html_path):
    hallazgos = []
    docs = []
    for path in json_paths:
        try:
            with open(path, encoding="utf-8-sig") as f:
                data = json.load(f)
        except (OSError, ValueError) as e:
            hallazgos.append(Hallazgo("ERROR", f"No se pudo leer {path}: {e}"))
            continue
        docs.append((path, data))

    # Cargar HTML una sola vez (opcional; sin reporte el archivo no existe)
    html_full = ""
    if html_path:
        try:
            with open(html_path, encoding="utf-8-sig") as f:
                html_full = f.read()
        except OSError as e:
            hallazgos.append(Hallazgo("ERROR", f"No se pudo leer {html_path}: {e}"))
            html_full = ""

    # --- 0.1 Pregunta congelada (entre JSON) ---
    preguntas = [(path, data.get("pregunta_investigacion")) for path, data in docs
                 if data.get("pregunta_investigacion")]
    if preguntas:
        ref_path, ref = preguntas[0]
        for path, q in preguntas[1:]:
            if q != ref:
                hallazgos.append(Hallazgo(
                    "ERROR", f"pregunta_investigacion distinta en {path} vs {ref_path}"
                ))
        # 0.1 vs HTML (solo si hay reporte; sin HTML no hay header que verificar)
        if html_path:
            html_norm = normalizar(re.sub(r"<[^>]+>", " ", html_full))
            ref_norm = normalizar(ref)
            if ref_norm and ref_norm not in html_norm:
                hallazgos.append(Hallazgo(
                    "ERROR", "La pregunta_investigacion de los JSON no aparece en el HTML (header)"
                ))
    else:
        hallazgos.append(Hallazgo("WARN", "Ningun JSON declara pregunta_investigacion"))

    # --- 0.3 IDs emitidos por fase ---
    emitidos = {}
    for path, data in docs:
        fase = data.get("fase", "")
        for item in extraer_items(data):
            iid = item.get("id")
            if iid:
                emitidos.setdefault(fase, set()).add(iid)
    ids_totales = set()
    for s in emitidos.values():
        ids_totales |= s

    for path, data in docs:
        fase = data.get("fase", "")
        for bloque in data.get("datos", {}).get("bloques", []):
            for item in bloque.get("cruces", []):
                for clave in ("senal_cuanti", "senal_cuali"):
                    ref = item.get(clave)
                    if isinstance(ref, dict) and ref.get("id"):
                        rid = ref["id"]
                        if rid not in ids_totales:
                            hallazgos.append(Hallazgo(
                                "ERROR", f"{path} {item.get('id')}: referencia a {rid} "
                                         f"que no existe en ninguna fase"
                            ))
            for item in bloque.get("senales", []) + bloque.get("cruces", []):
                texto = json.dumps(item, ensure_ascii=False)
                for rid in set(RE_ID.findall(texto)):
                    if rid == item.get("id"):
                        continue
                    if rid not in ids_totales:
                        hallazgos.append(Hallazgo(
                            "ERROR", f"{path} {item.get('id')}: menciona ID fantasma {rid}"
                        ))
        red = data.get("redundancia", {})
        reds = red if isinstance(red, list) else [red]
        for r in reds:
            if not isinstance(r, dict):
                continue
            absorbida = r.get("absorbida_por")
            if absorbida and absorbida not in ids_totales:
                hallazgos.append(Hallazgo(
                    "ERROR", f"{path}: redundancia.absorbida_por={absorbida} no existe"
                ))
        for adv in data.get("advertencias", []):
            if isinstance(adv, str):
                for rid in set(RE_ID.findall(adv)):
                    if rid not in ids_totales:
                        hallazgos.append(Hallazgo(
                            "ERROR", f"{path}: advertencia menciona ID fantasma {rid}"
                        ))

    # Conteo de señales en el HTML (usado también para el mapeo)
    titulos_html = re.findall(r"Señal Débil (\d+):", html_full)
    numeros_html = [int(x) for x in titulos_html]
    n_html = len(numeros_html)

    # Items con escala_a_fase4=true en fases 1-3 (coherencia con el reporte)
    escalan = []
    for path, data in docs:
        if data.get("fase", "") == "fase-4-entrega":
            continue
        for item in extraer_items(data):
            if item.get("escala_a_fase4") is True:
                escalan.append(item.get("id"))

    if not html_path:
        # Sin reporte: deben coincidir "ninguna señal escala" y el mapeo vacío
        if escalan:
            hallazgos.append(Hallazgo(
                "ERROR",
                f"No se generó reporte HTML pero fases 1-3 marcan {len(escalan)} item(s) "
                f"con escala_a_fase4=true ({escalan}); todo item que escala debe reportarse"
            ))
        fase4 = next((d for _, d in docs if d.get("fase") == "fase-4-entrega"), None)
        if fase4 and isinstance(fase4.get("mapeo_html"), dict) and fase4["mapeo_html"]:
            hallazgos.append(Hallazgo(
                "ERROR", "Sin reporte HTML pero fase4 declara mapeo_html no vacío"))
    else:
        # 0.3 HTML: mapeo "Señal Débil N" <-> ID (declarado en fase4_output.json)
        mapeo = None
        for path, data in docs:
            if data.get("fase") == "fase-4-entrega" and isinstance(data.get("mapeo_html"), dict):
                mapeo = data.get("mapeo_html")
        if mapeo is None:
            hallazgos.append(Hallazgo(
                "WARN", "fase4 no declara mapeo_html (mapeo 'Señal Débil N' <-> ID tecnico)"))
        else:
            if n_html and len(mapeo) != n_html:
                hallazgos.append(Hallazgo(
                    "ERROR", f"mapeo_html declara {len(mapeo)} senales pero el HTML tiene {n_html}"))
            if not mapeo and n_html:
                hallazgos.append(Hallazgo(
                    "ERROR", f"mapeo_html vacío pero el HTML declara {n_html} señal(es)"))
            ids_mapeados = list(mapeo.values())
            duplicados = sorted({i for i in ids_mapeados if ids_mapeados.count(i) > 1})
            if duplicados:
                hallazgos.append(Hallazgo(
                    "ERROR", f"mapeo_html asigna el mismo ID a mas de una senal: {duplicados}"))
            for k, v in mapeo.items():
                if v not in ids_totales:
                    hallazgos.append(Hallazgo(
                        "ERROR", f"mapeo_html: {k} -> {v} (ID inexistente en fases 1-3)"))
            numeros_mapeo = sorted(int(n) for n in re.findall(r"Señal Débil (\d+)", " ".join(mapeo.keys())))
            if numeros_mapeo and numeros_mapeo != list(range(1, len(numeros_mapeo) + 1)):
                hallazgos.append(Hallazgo(
                    "ERROR", f"mapeo_html keys no secuenciales: {numeros_mapeo}"))

        # 0.3 HTML: rango, numeracion, duplicados por contenido
        titulos = titulos_html
        numeros = numeros_html
        if not (1 <= n_html <= 5):
            hallazgos.append(Hallazgo("ERROR", f"HTML con {n_html} senales (rango 1-5)"))
        elif n_html < 3:
            hallazgos.append(Hallazgo(
                "WARN", f"HTML con {n_html} senales (3-5 es el objetivo; "
                        "con 1-2 la escasez debe declararse en las advertencias)"))
        if numeros and numeros != list(range(1, len(numeros) + 1)):
            hallazgos.append(Hallazgo("ERROR", f"Numeracion de senales no secuencial: {numeros}"))

        textos_por_senal = re.split(r"Señal Débil \d+:", html_full)[1:]
        vistos = {}
        for i, t in enumerate(textos_por_senal, start=1):
            clave = normalizar(t)[:120]
            if clave in vistos:
                hallazgos.append(Hallazgo(
                    "ERROR", f"HTML: 'Señal Débil {vistos[clave]}' y 'Señal Débil {i}' "
                             f"parecen duplicadas (mismo inicio de contenido)"
                ))
            else:
                vistos[clave] = i

        # Coherencia: items que escalan deben estar todos en el HTML.
        # El tope de 5 del reporte (SPEC.md sección 5) permite, si fase4 declara
        # el corte por score compuesto en sus advertencias, publicar solo los 5
        # mejores y dejar el resto fuera; sin ese corte, la diferencia es ERROR.
        if escalan and len(escalan) != n_html:
            corte = tope5_declarado(docs) if n_html == 5 else False
            if corte:
                hallazgos.append(Hallazgo(
                    "WARN",
                    f"HTML publica {n_html} señales pero fases 1-3 marcan "
                    f"{len(escalan)} con escala_a_fase4=true; se aplicó el corte de "
                    f"tope 5 declarado en las advertencias de fase4 "
                    f"(fuera: {sorted(set(escalan) - set(ids_mapeados)) if mapeo else escalan})"
                ))
            else:
                hallazgos.append(Hallazgo(
                    "ERROR",
                    f"HTML declara {n_html} senales pero fases 1-3 marcan {len(escalan)} "
                    f"items con escala_a_fase4=true ({escalan}). Con mas de 5 candidatos "
                    f"debe declararse el corte de tope 5 por score compuesto en las "
                    f"advertencias de fase4 (SPEC.md seccion 5)"
                ))

    verificar_blindaje_transpoblacional(docs, hallazgos)

    # --- 0.5 Timestamps en orden cronológico ---
    timestamps = []
    for path, data in docs:
        ts = data.get("timestamp")
        fase = data.get("fase", "")
        if ts:
            timestamps.append((orden_fase(fase), path, ts))
    timestamps.sort()
    for i in range(len(timestamps) - 1):
        if timestamps[i][2] > timestamps[i + 1][2]:
            hallazgos.append(Hallazgo(
                "ERROR",
                f"Timestamps desordenados: {timestamps[i][1]} ({timestamps[i][2]}) "
                f"posterior a {timestamps[i + 1][1]} ({timestamps[i + 1][2]})"
            ))

    return hallazgos


PISO_N_ABS = 30
PISO_N_PCT = 0.10
PISO_ENTREVISTAS = 2
NOTA_EXTRAPOLACION = ("Cruce entre poblaciones distintas (encuesta ≠ entrevistas); la "
                      "síntesis es una hipótesis de validación, no un hallazgo "
                      "transferible entre poblaciones.")
NATURALEZAS = ("extrapolacion", "convergencia")

RE_N_DIRECTO = re.compile(r"(?:N\s*[=:]\s*)(\d+)", re.I)
RE_DE_ENTREVISTAS = re.compile(r"(\d+)\s+de\s+(\d+)\s*(?:entrevista)", re.I)
RE_CORTE_TOPE_5 = re.compile(r"corte\s+de\s+tope\s*5|tope\s+de\s*5\s+se[ñn]ales|score\s+compuesto", re.I)


def tope5_declarado(docs):
    """True si fase4 declara en sus advertencias el corte de tope 5 por score
    compuesto (SPEC.md sección 5), lo que permite que con mas de 5 candidatos
    el reporte publique solo los 5 mejores."""
    for _, data in docs:
        if data.get("fase") == "fase-4-entrega":
            for adv in data.get("advertencias", []):
                if isinstance(adv, str) and RE_CORTE_TOPE_5.search(adv):
                    return True
    return False


def normalizar_min(texto):
    normalizado = unicodedata.normalize("NFKD", texto)
    normalizado = "".join(c for c in normalizado if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", normalizado.lower()).strip()


def piso_n_poblacion(n_poblacion):
    """Piso de N adaptativo por población (SPEC.md sección 5): max(30, 10% del
    N de la población declarado en Fase 0). Sin N disponible -> piso fijo 30."""
    if not n_poblacion:
        return PISO_N_ABS
    return max(PISO_N_ABS, int(math.ceil(n_poblacion * PISO_N_PCT)))


def parse_poblacion_fase0(valor):
    """Fase 0 declara poblaciones como {universo: {nombre, n}} (nuevo) o
    {universo: 'nombre'} (legacy, sin N por población)."""
    if isinstance(valor, dict):
        n = valor.get("n")
        if not isinstance(n, int) or n <= 0:
            n = None
        return valor.get("nombre", ""), n
    if isinstance(valor, str):
        return valor, None
    return "", None


def _n_minimo_de_senal(dato, contexto):
    """Regreso legacy para señales sin 'n' estructurado: extrae el N
    (denominador de fracción o 'N=') más alto declarado en el dato/contexto
    de una señal. Devuelve 0 si no hay ninguno explícito."""
    texto = f"{dato or ''} {contexto or ''}"
    n_max = 0
    for m in re.finditer(r"(\d+)\s*/\s*(\d+)", texto):
        n_max = max(n_max, int(m.group(2)))
    for m in RE_N_DIRECTO.finditer(texto):
        n_max = max(n_max, int(m.group(1)))
    return n_max


def _entrevistas_de_senal(dato, contexto, robustez):
    """Para señales cualitativas legacy: número de entrevistas que sostienen el
    patrón a partir de frases como '4 de 5 entrevistas' (toma el N, no la cota)."""
    texto = f"{dato or ''} {contexto or ''} {robustez or ''}"
    m = RE_DE_ENTREVISTAS.search(texto)
    return int(m.group(1)) if m else None


def verificar_blindaje_transpoblacional(docs, hallazgos):
    """P2: blindaje de cruces transpoblacionales (references/fase-3-cruce.md).

    - extrapolacion -> escala_a_fase4=false + nota exacta en exclusiones.
    - convergencia  -> senales intra-poblacion referenciadas con N >= piso
                       adaptativo por poblacion; matching de nombre de
                       poblacion por substring (nunca igualdad exacta).
    - ningun cruce transpoblacional con severidad Critica.
    """
    fase0 = next((d for _, d in docs if d.get("fase") == "fase-0-viabilidad"), None)
    poblaciones_fase0 = []
    n_por_universo = {}
    if fase0:
        pobl = fase0.get("datos", {}).get("poblaciones", {})
        if isinstance(pobl, dict):
            for universo, valor in pobl.items():
                nombre, n = parse_poblacion_fase0(valor)
                n_por_universo[universo] = n
                poblaciones_fase0.append(normalizar_min(nombre))
        elif isinstance(pobl, list):
            for valor in pobl:
                nombre, n = parse_poblacion_fase0(valor)
                n_por_universo[len(n_por_universo)] = n
                poblaciones_fase0.append(normalizar_min(nombre))

    referenciadas = {}
    for path, data in docs:
        fase = data.get("fase", "")
        if fase in ("fase-1-eda-cuantitativo", "fase-2-eda-cualitativo"):
            for item in extraer_items(data):
                if item.get("id"):
                    referenciadas[item["id"]] = (fase, item)

    for path, data in docs:
        if data.get("fase") != "fase-3-cruce":
            continue
        for cruce in extraer_items(data):
            naturaleza = cruce.get("naturaleza_cruce")
            es_trans = cruce.get("tipo_cruce") == "transpoblacional" or naturaleza is not None
            if not es_trans:
                continue

            cid = cruce.get("id", "?")
            if naturaleza not in NATURALEZAS:
                hallazgos.append(Hallazgo(
                    "ERROR", f"{path} {cid}: tipo_cruce=transpoblacional con "
                             f"naturaleza_cruce invalida: {naturaleza!r}"))
                continue

            # Cap de severidad: nunca Critica.
            if cruce.get("severidad") == "Crítica":
                hallazgos.append(Hallazgo(
                    "ERROR", f"{path} {cid}: cruce transpoblacional con severidad "
                             f"Crítica (cap: Alta, references/fase-3-cruce.md)"))

            if naturaleza == "extrapolacion":
                if cruce.get("escala_a_fase4") is not False:
                    hallazgos.append(Hallazgo(
                        "ERROR", f"{path} {cid}: extrapolacion con escala_a_fase4 "
                                 f"!= false (nunca escala solo)"))
                texto_json = normalizar_min(json.dumps(cruce.get("exclusiones", []),
                                                       ensure_ascii=False))
                if normalizar_min(NOTA_EXTRAPOLACION) not in texto_json:
                    hallazgos.append(Hallazgo(
                        "ERROR", f"{path} {cid}: extrapolacion sin la nota obligatoria "
                                 f"en exclusiones (references/fase-3-cruce.md)"))

            elif naturaleza == "convergencia":
                poblaciones = cruce.get("poblaciones") or {}
                refs = []
                for clave in ("senal_cuanti", "senal_cuali"):
                    ref = cruce.get(clave)
                    if isinstance(ref, dict) and ref.get("id"):
                        refs.append(ref["id"])
                if not refs:
                    hallazgos.append(Hallazgo(
                        "ERROR", f"{path} {cid}: convergencia sin senales "
                                 f"intra-poblacion referenciadas"))
                    continue

                # Matching por substring de poblaciones (nunca igualdad exacta).
                if poblaciones_fase0:
                    for nombre in (poblaciones.values() if isinstance(poblaciones, dict)
                                   else poblaciones):
                        if not isinstance(nombre, str):
                            continue
                        nombre_norm = normalizar_min(nombre)
                        if not any(nombre_norm in p0 or p0 in nombre_norm
                                   for p0 in poblaciones_fase0):
                            hallazgos.append(Hallazgo(
                                "WARN", f"{path} {cid}: poblacion '{nombre}' no coincide "
                                        f"por substring con las declaradas en fase0 "
                                        f"({poblaciones_fase0})"))
                else:
                    hallazgos.append(Hallazgo(
                        "WARN", f"{path} {cid}: fase0 no declara datos.poblaciones; "
                                f"no se pudo verificar la identidad de poblaciones"))

                # Cada señal referenciada debe existir con N propio >= piso
                # (cuanti: adaptativo por población; cuali: N de entrevistas).
                for rid in refs:
                    par = referenciadas.get(rid)
                    if par is None:
                        hallazgos.append(Hallazgo(
                            "ERROR", f"{path} {cid}: convergencia referencia {rid} "
                                     f"(no existe en fases 1-2)"))
                        continue
                    fase_senal, senal = par
                    poblacion = senal.get("poblacion")
                    n_estruc = senal.get("n")
                    if isinstance(n_estruc, int) and n_estruc > 0:
                        n_senal = n_estruc
                    elif fase_senal == "fase-2-eda-cualitativo":
                        n_cuali = _entrevistas_de_senal(senal.get("dato"),
                                                        senal.get("contexto"),
                                                        senal.get("robustez"))
                        n_senal = n_cuali if n_cuali is not None else _n_minimo_de_senal(
                            senal.get("dato"), senal.get("contexto"))
                    else:
                        n_senal = _n_minimo_de_senal(senal.get("dato"), senal.get("contexto"))

                    if fase_senal == "fase-2-eda-cualitativo":
                        piso = PISO_ENTREVISTAS
                        base = (f"cuali: N de entrevistas que sostienen el patrón "
                                f"(>= {PISO_ENTREVISTAS})")
                    else:
                        n_pob = n_por_universo.get(poblacion) if poblacion else None
                        piso = piso_n_poblacion(n_pob)
                        if n_pob is None:
                            hallazgos.append(Hallazgo(
                                "WARN", f"{path} {cid}: señal {rid} sin N de población "
                                        f"en fase0 ('{poblacion}'); el piso por "
                                        f"población cayó al fijo {PISO_N_ABS}"))
                        base = (f"cuanti: max(30, 10% del N de '{poblacion}') = {piso}")

                    if n_senal < piso:
                        hallazgos.append(Hallazgo(
                            "ERROR", f"{path} {cid}: señal intra-población {rid} no "
                                     f"alcanza el piso {base} (n={n_senal}); la "
                                     f"convergencia exige N propio por población"))


def main():
    args = sys.argv[1:]
    if "-h" in args or "--help" in args:
        print(__doc__)
        sys.exit(0)          # la ayuda pedida no es un error
    if not args:
        print(__doc__, file=sys.stderr)
        sys.exit(1)
    html_path = None
    json_paths = []
    for a in args:
        if a.lower().endswith(".html"):
            html_path = a
        else:
            json_paths.append(a)
    if html_path is None:
        print("Sin reporte HTML: se validan solo las invariantes entre JSON "
              "(pregunta congelada, IDs, timestamps).", file=sys.stderr)

    hallazgos = verificar(json_paths, html_path)
    for h in hallazgos:
        print(h)
    n_err = sum(1 for h in hallazgos if h.nivel == "ERROR")
    n_warn = sum(1 for h in hallazgos if h.nivel == "WARN")
    print(f"\nResumen: {n_err} error(es), {n_warn} advertencia(s).")
    sys.exit(1 if n_err else 0)


if __name__ == "__main__":
    main()
