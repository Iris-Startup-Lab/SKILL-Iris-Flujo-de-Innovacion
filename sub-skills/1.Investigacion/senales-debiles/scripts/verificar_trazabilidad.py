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
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, ValueError) as e:
            hallazgos.append(Hallazgo("ERROR", f"No se pudo leer {path}: {e}"))
            continue
        docs.append((path, data))

    # Cargar HTML una sola vez
    try:
        with open(html_path, encoding="utf-8") as f:
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
        # 0.1 vs HTML
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
    if not (3 <= n_html <= 5):
        hallazgos.append(Hallazgo("ERROR", f"HTML con {n_html} senales (rango 3-5)"))
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

    # Conteo esperado: items con escala_a_fase4=true en fases 1-3
    escalan = []
    for path, data in docs:
        if data.get("fase", "") == "fase-4-entrega":
            continue
        for item in extraer_items(data):
            if item.get("escala_a_fase4") is True:
                escalan.append(item.get("id"))
    if escalan and n_html and len(escalan) != n_html:
        hallazgos.append(Hallazgo(
            "ERROR",
            f"HTML declara {n_html} senales pero fases 1-3 marcan {len(escalan)} "
            f"items con escala_a_fase4=true ({escalan})"
        ))

    # --- 0.5 Timestamps en orden cronologico ---
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


def main():
    args = sys.argv[1:]
    if not args or "-h" in args or "--help" in args:
        print(__doc__)
        sys.exit(1)
    html_path = None
    json_paths = []
    for a in args:
        if a.lower().endswith(".html"):
            html_path = a
        else:
            json_paths.append(a)
    if html_path is None:
        print("Se requiere el reporte HTML.", file=sys.stderr)
        sys.exit(1)

    hallazgos = verificar(json_paths, html_path)
    for h in hallazgos:
        print(h)
    n_err = sum(1 for h in hallazgos if h.nivel == "ERROR")
    n_warn = sum(1 for h in hallazgos if h.nivel == "WARN")
    print(f"\nResumen: {n_err} error(es), {n_warn} advertencia(s).")
    sys.exit(1 if n_err else 0)


if __name__ == "__main__":
    main()
