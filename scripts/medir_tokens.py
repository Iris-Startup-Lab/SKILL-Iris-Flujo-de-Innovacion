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
"""

import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

E1_FILES = [
    "SKILL.md",
    "pasos.json",
    "AGENTS.md",
    "_plantilla_html/README.md",
    "sub-skills/CONTRATO_JSON.md",
]

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
    salida = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
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


def main(argv=None):
    ap = argparse.ArgumentParser(description="Nivel 1 de medición de tokens del flujo IRIS.")
    ap.add_argument("--proyecto", default=None, help="Directorio del proyecto (flujo_estado.json + reporte_*.json)")
    ap.add_argument("--ruta", choices=["completa", "minima", "ambas"], default="ambas")
    ap.add_argument("--decisiones", default=None, help="JSON {paso: [skills]} para resolver los nodos de decisión")
    ap.add_argument("--encoding", default=ENCODING_DEFAULT)
    ap.add_argument("--csv", default=None, help="Escribe la tabla en CSV")
    args = ap.parse_args(argv)

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
        e3_ruta = sum(por_id[p["id"]][3] for p in pasos_ruta)
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
                "E3": f[3],
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
