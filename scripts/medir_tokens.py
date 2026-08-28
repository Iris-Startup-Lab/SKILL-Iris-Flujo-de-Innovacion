#!/usr/bin/env python3
"""Nivel 1 de medición de tokens del flujo IRIS (estático y reproducible).

Mide el coste en tokens de entrada de recorrer el flujo, por paso y por ruta,
a partir de los archivos del propio repo. Es determinista: el mismo repo da el
mismo número siempre. No mide lo que el modelo gasta de más al razonar.

Componentes (PLAN_MEDICION_TOKENS.md §1):
    E1  arranque fijo     — los archivos que se cargan una vez por sesión
    E2  briefing          — salida de `estado_flujo.py mostrar` por paso
    E3  sub-skills        — AGENTE.md + references/ de cada sub-skill invocada
    E4  herencia          — reporte.json de los predecesores (tres estrategias)
    S1  salida generada   — reporte.json que el paso escribe

Uso:
    python scripts/medir_tokens.py                          # E1 + E3, ambas rutas
    python scripts/medir_tokens.py --proyecto output/<proyecto>   # + E2/E4/S1 reales
    python scripts/medir_tokens.py --decisiones decisiones.json    # skills elegidas
    python scripts/medir_tokens.py --csv medicion.csv       # salida CSV
    python scripts/medir_tokens.py --modelo "Claude Sonnet" # + costo estimado por paso
    python scripts/medir_tokens.py --grafica                # + gráfica de barras (Plotly)
    python scripts/medir_tokens.py --precios                # catálogo de precios
    python scripts/medir_tokens.py --precios --actualizar   # comprobar fuentes online
"""

import argparse
import csv
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

E1_FILES = [
    "SKILL.md",
    "pasos.json",
    "AGENTS.md",
    "_plantilla_html/README.md",
    "sub-skills/CONTRATO_JSON.md",
]

PRECIOS_JSON = REPO_ROOT / "scripts" / "precios_modelos.json"

### Comenzando el modelo de encoding (adecuado para Claude)
ENCODING_DEFAULT = "cl100k_base"


def tokenizar(texto, enc):
    try:
        import tiktoken
        return len(tiktoken.get_encoding(enc).encode(texto))
    except Exception:
        return len(texto) // 4


def tokens_archivo(ruta, enc):
    texto = Path(ruta).read_text(encoding="utf-8")
    return len(texto), tokenizar(texto, enc)


def cargar_pasos():
    ruta = REPO_ROOT / "pasos.json"
    if not ruta.is_file():
        raise FileNotFoundError(f"No encuentro {ruta}")
    return json.loads(ruta.read_text(encoding="utf-8"))


def cargar_precios():
    """Lee el catálogo de precios (scripts/precios_modelos.json).

    Es el fichero curado a mano: cada modelo lleva su precio por 1M tokens de
    entrada y salida, la fuente oficial y la fecha. Devuelve el dict completo o
    un dict vacío si aún no existe.
    """
    if not PRECIOS_JSON.is_file():
        return {}
    try:
        return json.loads(PRECIOS_JSON.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def buscar_modelo(precios, nombre):
    """Busca un modelo en el catálogo por nombre o modelo_api, sin distinguir
    mayúsculas ni acentos. Devuelve el dict del modelo o None si no está."""
    nombre = nombre or ""
    if not nombre:
        return None
    clave = nombre.strip().lower()
    for m in precios.get("modelos", []):
        candidatos = [m.get("nombre", ""), m.get("modelo_api", "") or ""]
        if any(clave in c.lower() for c in candidatos if c):
            return m
    return None


def fetch_url(url, timeout=15):
    """Descarga una URL con urllib (stdlib). Devuelve (estado, descripción).

    Solo se usa para *visualizar* si la fuente sigue viva, no para parsear el
    precio: el HTML de estas páginas cambia y parsearlo es frágil. El precio de
    verdad vive en precios_modelos.json, curado a mano contra la fuente.
    """
    req = urllib.request.Request(
        url, headers={"User-Agent": "Mozilla/5.0 (compatible; IRIS-cost-check)"}
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, "accesible"
    except urllib.error.HTTPError as exc:
        return exc.code, f"error HTTP {exc.code}"
    except urllib.error.URLError as exc:
        return None, f"no accesible ({exc.reason})"
    except Exception as exc:  # pragma: no cover - red o SSL raros
        return None, f"no accesible ({exc})"


def medir_e1(enc):
    filas = []
    for rel in E1_FILES:
        ruta = REPO_ROOT / rel
        if ruta.is_file():
            chars, tok = tokens_archivo(ruta, enc)
            filas.append((rel, chars, tok))
    return filas


def skills_de_paso(paso, decisiones):
    posibles = paso.get("skills_posibles", [])
    if paso["id"] in decisiones:
        return list(decisiones[paso["id"]])
    if len(posibles) == 1:
        return list(posibles)
    if posibles:
        return [posibles[0]]
    return []


def medir_subskill(ruta_skill, enc):
    base = REPO_ROOT / "sub-skills" / ruta_skill
    chars, tok = 0, 0
    agente = base / "AGENTE.md"
    if agente.is_file():
        c, t = tokens_archivo(agente, enc)
        chars += c
        tok += t
    refs = base / "references"
    if refs.is_dir():
        for f in sorted(refs.glob("**/*.md")):
            c, t = tokens_archivo(f, enc)
            chars += c
            tok += t
    return chars, tok


def medir_e3(pasos, decisiones, enc):
    filas = []
    for paso in pasos["pasos"]:
        skills = skills_de_paso(paso, decisiones)
        chars, tok = 0, 0
        detalle = []
        for s in skills:
            c, t = medir_subskill(s, enc)
            chars += c
            tok += t
            detalle.append((s, c, t))
        filas.append((paso["id"], paso["titulo"], skills, chars, tok, detalle))
    return filas


def medir_mostrar(paso_id, proyecto, enc):
    estado = Path(proyecto) / "flujo_estado.json"
    if not estado.is_file():
        return None
    cmd = [
        sys.executable, str(REPO_ROOT / "scripts" / "estado_flujo.py"),
        "mostrar", "--paso", paso_id, "--estado", str(estado),
    ]
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    salida = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", env=env)
    if salida.returncode != 0:
        return None
    return len(salida.stdout), tokenizar(salida.stdout, enc)


def reporte_de_paso(estado_pasos, paso_id):
    for p in estado_pasos:
        if p["id"] == paso_id and p.get("datos"):
            return Path(p["datos"])
    return None


def medir_proyecto(pasos, proyecto, enc):
    estado = json.loads(
        (Path(proyecto) / "flujo_estado.json").read_text(encoding="utf-8")
    )
    estado_pasos = estado["pasos"]
    completados = [p for p in estado_pasos if p["estado"] == "completado"]
    por_id = {p["id"]: p for p in estado_pasos}
    orden = {p["id"]: p["orden"] for p in pasos["pasos"]}

    filas = []
    for paso in pasos["pasos"]:
        pid = paso["id"]
        predecs = paso.get("predecesores", [])

        def tokens_reporte(otros):
            tot = 0
            for o in otros:
                r = reporte_de_paso(estado_pasos, o)
                if r and (Path(proyecto) / r).is_file():
                    _, t = tokens_archivo(Path(proyecto) / r, enc)
                    tot += t
            return tot

        comp_previos = [p["id"] for p in completados if orden[p["id"]] < orden[pid]]
        directo = max(
            (p for p in comp_previos if p in predecs), key=lambda x: orden[x], default=None
        )
        directo = [directo] if directo else []

        e2 = medir_mostrar(pid, proyecto, enc)
        propio = reporte_de_paso(estado_pasos, pid)
        s1 = 0
        if propio and (Path(proyecto) / propio).is_file():
            _, s1 = tokens_archivo(Path(proyecto) / propio, enc)

        e4_directo = tokens_reporte(directo)
        e4_declarados = tokens_reporte([p for p in predecs if p in por_id])
        e4_cadena = tokens_reporte(comp_previos)

        filas.append({
            "id": pid,
            "titulo": paso["titulo"],
            "orden": orden[pid],
            "estado": por_id[pid]["estado"],
            "E2": e2[1] if e2 else None,
            "E4_directo": e4_directo,
            "E4_declarados": e4_declarados,
            "E4_cadena": e4_cadena,
            "S1": s1,
        })
    return filas


def rutas(pasos, nombre):
    if nombre == "minima":
        ids = set(pasos["ruta_minima"])
        return [p for p in pasos["pasos"] if p["id"] in ids]
    return list(pasos["pasos"])


def dias_desde_actualizacion(precios):
    """Días transcurridos desde `actualizado` (YYYY-MM-DD) hasta hoy.

    Devuelve None si la fecha falta o no se puede interpretar: en ese caso no se
    emite aviso de caducidad (no se puede afirmar que esté viejo).
    """
    raw = (precios or {}).get("actualizado")
    if not raw:
        return None
    try:
        actualizado = date.fromisoformat(str(raw))
    except ValueError:
        return None
    return (date.today() - actualizado).days


def umbral_dias(precios):
    return (precios or {}).get("validez_dias", 90)


def advertencia_caducidad(precios):
    """Texto de aviso si los precios superan el umbral de caducidad; None si están
    al día (o si no se puede calcular la antigüedad)."""
    dias = dias_desde_actualizacion(precios)
    if dias is None:
        return None
    umbral = umbral_dias(precios)
    if dias <= umbral:
        return None
    return (f"AVISO: los precios tienen {dias} días (umbral {umbral}). "
            f"Verifícalos en la fuente oficial antes de usarlos para presupuesto.")


def comprobar_fuentes(precios):
    """Chequea online si las fuentes del catálogo siguen accesibles.

    Devuelve la lista de (proveedor, descripción, url) lista para imprimir.
    """
    filas = []
    urls = {}
    for m in (precios or {}).get("modelos", []):
        url = m.get("url")
        if url:
            urls.setdefault(url, m.get("proveedor", "?"))
    for url, prov in urls.items():
        _, desc = fetch_url(url)
        filas.append((prov, desc, url))
    return filas


def imprimir_precios(precios, actualizar=False):
    """Muestra el catálogo de precios y comprueba online si las fuentes siguen
    accesibles. El chequeo corre con --actualizar o, automáticamente, cuando los
    precios superan el umbral de caducidad (aviso + fetch de accesibilidad)."""
    modelos = precios.get("modelos", []) if precios else []
    if not modelos:
        print("No hay catálogo de precios todavía (scripts/precios_modelos.json).")
        print("Se irán añadiendo modelos conforme avance la skill.")
        return
    aviso = advertencia_caducidad(precios)
    print(f"## Precios de modelos (USD por 1M tokens) — actualizado {precios.get('actualizado', '?')}")
    if precios.get("nota"):
        print(f"  {precios['nota']}")
    if aviso:
        print(f"  {aviso}")
    print()
    for m in modelos:
        entrada, salida = m.get("entrada"), m.get("salida")
        if entrada is None or salida is None:
            precio = "sin precio oficial verificado"
        else:
            precio = f"${entrada:.2f} / ${salida:.2f}"
        api = f"  [{m['modelo_api']}]" if m.get("modelo_api") else ""
        nota = f"  ({m['nota']})" if m.get("nota") else ""
        print(f"  {m['nombre']:<16} {m['proveedor']:<9} entrada/salida: {precio}{api}{nota}")
        print(f"      fuente: {m.get('url', '')}")
    print()
    if actualizar or aviso:
        print("## Comprobación de fuentes (online)")
        for prov, desc, url in comprobar_fuentes(precios):
            print(f"  [{prov}] {desc} · {url}")
    else:
        print("(pasa --actualizar junto a --precios para comprobar online si las fuentes siguen accesibles)")


def costo_por_paso(pid, por_id, filas_proyecto, precio_entrada, precio_salida):
    """Tokens de entrada (E2+E3+E4) y salida (S1) de un paso, y su costo en USD."""
    e3 = por_id[pid][4]
    e2 = e4 = s1 = 0
    if filas_proyecto:
        pf = next((f for f in filas_proyecto if f["id"] == pid), None)
        if pf:
            e2 = pf.get("E2") or 0
            e4 = pf.get("E4_declarados") or 0
            s1 = pf.get("S1") or 0
    entrada = e2 + e3 + e4
    salida = s1
    costo = (entrada / 1e6) * precio_entrada + (salida / 1e6) * precio_salida
    return entrada, salida, costo


def imprimir_costo(modelo, pasos, por_id, filas_proyecto, total_e1, nombres_ruta, aviso=None):
    pe, ps = modelo["entrada"], modelo["salida"]
    print(f"## Costo estimado — {modelo['nombre']} ({modelo['proveedor']})")
    print(f"  ${pe:.2f} / 1M entrada · ${ps:.2f} / 1M salida   (fuente: {modelo.get('url', '')})")
    print("  Estimación de lista, sin descuentos enterprise ni impuestos.")
    if aviso:
        print(f"  {aviso}")
        url = modelo.get("url", "")
        if url:
            _, desc = fetch_url(url)
            print(f"  Fuente: {desc} · {url}")
    print()
    for ruta in nombres_ruta:
        pasos_ruta = rutas(pasos, ruta)
        print(f"### Ruta {ruta}")
        total_ruta = 0.0
        for p in pasos_ruta:
            pid = p["id"]
            entrada, salida, costo = costo_por_paso(pid, por_id, filas_proyecto, pe, ps)
            total_ruta += costo
            if filas_proyecto:
                det = f"entrada {entrada:,} tok · salida {salida:,} tok"
            else:
                det = f"entrada {entrada:,} tok (sin --proyecto no se mide salida)"
            print(f"  {pid} {p['titulo']:<38} ${costo:>8.4f}   {det}")
        e1_costo = (total_e1 / 1e6) * pe
        print(f"  {'TOTAL ' + ruta:<38} ${total_ruta:>8.4f}")
        print(f"  {'+ arranque fijo (E1)':<38} ${e1_costo:>8.4f}")
        print(f"  {'= TOTAL con arranque':<38} ${total_ruta + e1_costo:>8.4f}\n")


def filas_grafica(pasos, por_id, filas_proyecto, ids):
    """Totales por paso para la gráfica de barras: tokens de entrada y de salida.

    `ids` es el conjunto de pasos que entran (según `--ruta`). Sin `--proyecto` solo
    hay E3 (las sub-skills); la salida (S1) y el resto de entrada (E2/E4) requieren
    el proyecto real. Devuelve la lista con {id, titulo, orden, entrada, salida}.
    """
    filas = []
    for p in pasos["pasos"]:
        if p["id"] not in ids:
            continue
        e3 = por_id[p["id"]][4]
        e2 = e4 = s1 = 0
        if filas_proyecto:
            pf = next((f for f in filas_proyecto if f["id"] == p["id"]), None)
            if pf:
                e2 = pf.get("E2") or 0
                e4 = pf.get("E4_declarados") or 0
                s1 = pf.get("S1") or 0
        filas.append({
            "id": p["id"],
            "titulo": p["titulo"],
            "orden": p["orden"],
            "entrada": e2 + e3 + e4,
            "salida": s1,
        })
    return filas


def generar_grafica(filas, salida, titulo=None):
    """Gráfica de barras horizontal (Plotly) de tokens por paso, ordenada de mayor a
    menor: el paso que más tokens consume es la primera barra (arriba). La escribe
    como HTML autocontenido (Plotly desde CDN) y devuelve la ruta, o None si falta
    `plotly` en el entorno."""
    try:
        import plotly.graph_objects as go
    except ImportError:
        print("AVISO: no se pudo generar la gráfica: falta `plotly`.")
        print("  Instálalo con: pip install plotly")
        return None

    filas = sorted(filas, key=lambda f: f["entrada"] + f["salida"], reverse=True)
    labels = [f"Paso {f['orden']} — {f['titulo']}" for f in filas]
    totales = [f["entrada"] + f["salida"] for f in filas]
    maximo = max(totales) if totales else 0
    # La barra que más consume se destaca en dorado; el resto, en morado IRIS.
    colores = ["#D4A73E" if t == maximo else "#5A3A8C" for t in totales]
    hover = [
        (f"entrada {f['entrada']:,} tok · salida {f['salida']:,} tok")
        if f["salida"] else f"entrada {f['entrada']:,} tok (sin proyecto no se mide la salida)"
        for f in filas
    ]

    fig = go.Figure(go.Bar(
        y=labels,
        x=totales,
        orientation="h",
        marker_color=colores,
        text=[f"{t:,} tok" for t in totales],
        textposition="outside",
        cliponaxis=False,
        customdata=hover,
        hovertemplate="%{y}<br>%{customdata}<extra></extra>",
    ))
    fig.update_layout(
        title={"text": titulo or "Tokens por paso del flujo", "x": 0.05},
        xaxis_title="Tokens (entrada + salida)",
        height=max(360, 48 * len(filas) + 120),
        margin={"l": 10, "r": 120, "t": 72, "b": 44},
        font={"family": "Sora, Inter, sans-serif", "color": "#2A2433"},
        plot_bgcolor="#F7F3FC",
        paper_bgcolor="#F7F3FC",
        xaxis={"gridcolor": "#E4DCEF"},
        showlegend=False,
    )
    fig.update_yaxes(autorange="reversed")  # la mayor queda arriba
    fig.write_html(salida, include_plotlyjs="cdn")
    return salida


def main(argv=None):
    ap = argparse.ArgumentParser(description="Nivel 1 de medición de tokens del flujo IRIS.")
    ap.add_argument("--proyecto", default=None, help="Directorio del proyecto (flujo_estado.json + reporte_*.json)")
    ap.add_argument("--ruta", choices=["completa", "minima", "ambas"], default="ambas")
    ap.add_argument("--decisiones", default=None, help="JSON {paso: [skills]} para resolver los nodos de decisión")
    ap.add_argument("--encoding", default=ENCODING_DEFAULT)
    ap.add_argument("--csv", default=None, help="Escribe la tabla en CSV")
    ap.add_argument("--modelo", default=None,
                    help="Modelo para estimar el costo (ej. 'Claude Sonnet', 'DeepSeek V4 Flash'). "
                         "Si no está en el catálogo se avisa y no se estima.")
    ap.add_argument("--grafica", nargs="?", const="tokens_por_paso.html", default=None,
                    metavar="RUTA",
                    help="Genera una gráfica de barras (Plotly) con los tokens por paso, "
                         "ordenada de mayor a menor. Ruta de salida opcional "
                         "(default: tokens_por_paso.html).")
    ap.add_argument("--precios", action="store_true",
                    help="Lista el catálogo de precios (scripts/precios_modelos.json) y sale.")
    ap.add_argument("--actualizar", action="store_true",
                    help="Con --precios: comprueba online si las fuentes de precios siguen accesibles.")
    args = ap.parse_args(argv)

    precios = cargar_precios()

    if args.precios:
        imprimir_precios(precios, args.actualizar)
        return 0

    pasos = cargar_pasos()
    decisiones = {}
    if args.decisiones:
        decisiones = json.loads(Path(args.decisiones).read_text(encoding="utf-8"))

    e1 = medir_e1(args.encoding)
    e3 = medir_e3(pasos, decisiones, args.encoding)

    filas_proyecto = None
    if args.proyecto:
        filas_proyecto = medir_proyecto(pasos, args.proyecto, args.encoding)
    por_id = {f[0]: f for f in e3}

    print("## E1 — Arranque fijo (una vez por sesión)")
    total_e1 = 0
    for rel, chars, tok in e1:
        total_e1 += tok
        print(f"  {rel:35} {chars:>6} car  {tok:>6} tok")
    print(f"  {'TOTAL E1':35} {'':>6}     {total_e1:>6} tok\n")

    nombres_ruta = ["completa", "minima"] if args.ruta == "ambas" else [args.ruta]

    filas_csv = []
    for ruta in nombres_ruta:
        pasos_ruta = rutas(pasos, ruta)
        e3_ruta = sum(por_id[p["id"]][4] for p in pasos_ruta)
        print(f"## E3 — Sub-skills ({ruta}: {len(pasos_ruta)} pasos)")
        for p in pasos_ruta:
            pid, titulo, skills, chars, tok, detalle = por_id[p["id"]]
            print(f"  {pid} {titulo:38} {chars:>6} car  {tok:>6} tok")
            for s, sc, st in detalle:
                print(f"      · {s}  ({sc} car / {st} tok)")
        print(f"  {'TOTAL E3 ' + ruta:38} {'':>6}     {e3_ruta:>6} tok")
        print(f"  {'E1 + E3 ' + ruta:38} {'':>6}     {total_e1 + e3_ruta:>6} tok\n")

        if filas_proyecto:
            comp = [f for f in filas_proyecto if f["id"] in {p["id"] for p in pasos_ruta}]
            e2_tot = sum((f["E2"] or 0) for f in comp)
            e4d_tot = sum(f["E4_directo"] for f in comp)
            e4c_tot = sum(f["E4_cadena"] for f in comp)
            s1_tot = sum(f["S1"] for f in comp)
            print(f"  (con proyecto: E2 {e2_tot} · E4 directo {e4d_tot} · E4 cadena {e4c_tot} · S1 {s1_tot})")

        for p in pasos_ruta:
            pid = p["id"]
            f = por_id[pid]
            fila = {
                "ruta": ruta,
                "paso": pid,
                "titulo": f[1],
                "E1": total_e1,
                "E3": f[4],
            }
            if filas_proyecto:
                pf = next(x for x in filas_proyecto if x["id"] == pid)
                fila.update({
                    "E2": pf["E2"],
                    "E4_directo": pf["E4_directo"],
                    "E4_declarados": pf["E4_declarados"],
                    "E4_cadena": pf["E4_cadena"],
                    "S1": pf["S1"],
                })
            filas_csv.append(fila)

    if args.csv:
        with open(args.csv, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=filas_csv[0].keys())
            w.writeheader()
            w.writerows(filas_csv)
        print(f"CSV escrito en {args.csv}")

    if args.modelo:
        modelo = buscar_modelo(precios, args.modelo)
        if not modelo:
            print(f"\n## Costo: «{args.modelo}» no está en el catálogo de precios.")
            print("  No hay precios oficiales para este modelo todavía; se irán añadiendo conforme avance la skill.")
            conocidos = [m["nombre"] for m in precios.get("modelos", [])]
            if conocidos:
                print("  Modelos con precio en el catálogo:", ", ".join(conocidos))
        elif modelo.get("entrada") is None or modelo.get("salida") is None:
            print(f"\n## Costo: {modelo['nombre']} ({modelo['proveedor']})")
            print(f"  Precio oficial aún por verificar en la fuente: {modelo.get('url')}")
            print("  No se puede estimar el costo sin precio verificado.")
        else:
            imprimir_costo(modelo, pasos, por_id, filas_proyecto, total_e1, nombres_ruta,
                           aviso=advertencia_caducidad(precios))

    if args.grafica:
        ids_grafica = set()
        for ruta in nombres_ruta:
            ids_grafica.update(p["id"] for p in rutas(pasos, ruta))
        filas_g = filas_grafica(pasos, por_id, filas_proyecto, ids_grafica)
        nombre_proy = None
        if args.proyecto:
            try:
                est = json.loads(
                    (Path(args.proyecto) / "flujo_estado.json").read_text(encoding="utf-8")
                )
                nombre_proy = est.get("proyecto")
            except (OSError, json.JSONDecodeError):
                pass
        titulo = "Tokens por paso" + (f" — {nombre_proy}" if nombre_proy else " del flujo")
        salida = generar_grafica(filas_g, args.grafica, titulo=titulo)
        if salida:
            print(f"\nGráfica de tokens por paso escrita en: {salida}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
