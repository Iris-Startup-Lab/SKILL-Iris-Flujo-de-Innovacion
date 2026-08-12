"""
estado_flujo.py — máquina de estados del flujo de innovación IRIS.

Mantiene `flujo_estado.json` (fuente de verdad del avance de un proyecto) y
genera `STATE.md` como vista humana. La macro-skill nunca edita el estado a
mano: lo hace con este script, para que el histórico sea siempre parseable y
el contexto que viaja a cada HTML sea idéntico paso a paso.

La definición del flujo (qué pasos existen, qué skills invoca cada uno, qué se
puede omitir) vive en `pasos.json` y este script solo la lee.

Uso típico de la macro-skill:

    python scripts/estado_flujo.py init --proyecto "Huertos urbanos MX" \
        --objetivo "Validar demanda" --audiencia "Familias urbanas 28-45"

    python scripts/estado_flujo.py mostrar --paso html_1
    python scripts/estado_flujo.py iniciar --paso html_1
    python scripts/estado_flujo.py decision --paso html_1 \
        --nodo "¿Cómo quieres iniciar?" --opcion "Estado actual"
    python scripts/estado_flujo.py completar --paso html_1 \
        --skills 1.Investigación/benchmark-mercado \
        --resumen "TAM MX 4.2 mil M* y 3 huecos de oferta" \
        --veredicto perseverar --outputs html_1.html

    python scripts/estado_flujo.py omitir --paso html_2 \
        --motivo "El usuario ya tiene 12 entrevistas hechas"

    python scripts/estado_flujo.py contexto --paso html_4 -o contexto.json
    python scripts/estado_flujo.py render          # reescribe STATE.md

Códigos de salida: 0 ok · 1 error de uso/archivo · 2 regla del flujo violada.
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

_HERE = Path(__file__).resolve().parent
REPO_ROOT = _HERE.parent

PASOS_JSON = REPO_ROOT / "pasos.json"
ESTADO_JSON = REPO_ROOT / "flujo_estado.json"
STATE_MD = REPO_ROOT / "STATE.md"

ESTADOS = ["pendiente", "en_curso", "completado", "omitido", "fallido"]
VEREDICTOS = ["perseverar", "pivotear", "descartar"]

ICONO = {
    "completado": "[x]",
    "omitido": "[-]",
    "en_curso": "[>]",
    "fallido": "[!]",
    "pendiente": "[ ]",
}


class ReglaDelFlujo(Exception):
    """Se intentó una transición que el flujo no permite."""


# --------------------------------------------------------------------------- #
# Carga
# --------------------------------------------------------------------------- #

def cargar_pasos(ruta=None):
    ruta = Path(ruta) if ruta else PASOS_JSON
    if not ruta.is_file():
        raise FileNotFoundError(f"No encuentro la definición del flujo: {ruta}")
    return json.loads(ruta.read_text(encoding="utf-8"))


def cargar_estado(ruta=None):
    ruta = Path(ruta) if ruta else ESTADO_JSON
    if not ruta.is_file():
        raise FileNotFoundError(
            f"No encuentro {ruta.name}. Inicia el proyecto con:\n"
            f"    python scripts/estado_flujo.py init --proyecto \"<nombre>\""
        )
    return json.loads(ruta.read_text(encoding="utf-8"))


def guardar_estado(estado, ruta=None):
    ruta = Path(ruta) if ruta else ESTADO_JSON
    estado["actualizado"] = datetime.now().isoformat(timespec="seconds")
    ruta.write_text(
        json.dumps(estado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def def_paso(pasos, paso_id):
    for p in pasos["pasos"]:
        if p["id"] == paso_id:
            return p
    validos = ", ".join(p["id"] for p in pasos["pasos"])
    raise ReglaDelFlujo(f"Paso desconocido: {paso_id}. Válidos: {validos}")


def estado_paso(estado, paso_id):
    for p in estado["pasos"]:
        if p["id"] == paso_id:
            return p
    raise ReglaDelFlujo(f"El paso {paso_id} no está en flujo_estado.json")


# --------------------------------------------------------------------------- #
# init
# --------------------------------------------------------------------------- #

def cmd_init(args):
    pasos = cargar_pasos(args.pasos)
    destino = Path(args.estado) if args.estado else ESTADO_JSON

    if destino.is_file() and not args.forzar:
        estado = json.loads(destino.read_text(encoding="utf-8"))
        print(
            f"Ya existe {destino.name} para el proyecto «{estado.get('proyecto')}».\n"
            "Continúa ese proyecto, o usa --forzar para empezar de cero "
            "(se pierde el histórico)."
        )
        return 2

    ahora = datetime.now().isoformat(timespec="seconds")
    ruta_minima = args.ruta == "minima"

    estado = {
        "version": 1,
        "proyecto": args.proyecto,
        "objetivo": args.objetivo or "",
        "audiencia": args.audiencia or "",
        "creado": ahora,
        "actualizado": ahora,
        "ruta": args.ruta,
        "paso_actual": None,
        "pasos": [],
        "decisiones": [],
    }

    for p in pasos["pasos"]:
        entrada = {
            "id": p["id"],
            "titulo": p["titulo"],
            "etapa": p["etapa"],
            "estado": "pendiente",
            "skills": [],
            "outputs": [],
            "resumen": "",
            "veredicto": None,
        }
        if ruta_minima and not p.get("en_ruta_minima"):
            if p.get("omitible"):
                entrada["estado"] = "omitido"
                entrada["motivo"] = "Ruta mínima: paso fuera del recorrido express"
                entrada["impacto"] = p.get("si_omitido", "")
        estado["pasos"].append(entrada)

    primero = next(
        (p["id"] for p in estado["pasos"] if p["estado"] == "pendiente"), None
    )
    estado["paso_actual"] = primero

    guardar_estado(estado, destino)
    render_state_md(estado, pasos, destino)
    print(f"Proyecto «{args.proyecto}» iniciado en {destino.name}.")
    if ruta_minima:
        omitidos = [p["id"] for p in estado["pasos"] if p["estado"] == "omitido"]
        print(f"  Ruta mínima: {' → '.join(pasos['ruta_minima'])}")
        print(f"  Omitidos de entrada: {', '.join(omitidos)}")
    print(f"  Primer paso: {primero}")
    print(f"  STATE.md actualizado.")
    return 0


# --------------------------------------------------------------------------- #
# Transiciones
# --------------------------------------------------------------------------- #

def _transicion(args, nuevo_estado):
    pasos = cargar_pasos(args.pasos)
    estado = cargar_estado(args.estado)
    definicion = def_paso(pasos, args.paso)
    entrada = estado_paso(estado, args.paso)

    if nuevo_estado == "omitido" and not definicion.get("omitible", True):
        if not args.forzar:
            raise ReglaDelFlujo(
                f"{args.paso} ({definicion['titulo']}) no se puede omitir.\n"
                f"  Motivo: {definicion.get('razon_no_omitible', 'dependencia dura del flujo')}\n"
                f"  Si el usuario insiste, repite con --forzar y quedará registrado como "
                f"omisión forzada."
            )
        entrada["omision_forzada"] = True

    entrada["estado"] = nuevo_estado
    entrada["cerrado"] = datetime.now().isoformat(timespec="seconds")

    if nuevo_estado == "completado":
        entrada["skills"] = args.skills or []
        entrada["outputs"] = args.outputs or []
        entrada["resumen"] = args.resumen or ""
        if args.veredicto:
            entrada["veredicto"] = args.veredicto
        # Los outputs viven junto al estado del proyecto, no en la raíz del repo.
        base = Path(args.estado).resolve().parent if args.estado else REPO_ROOT
        faltantes = [
            f for f in args.outputs or []
            if not (base / f).is_file() and not Path(f).is_file()
        ]
        if faltantes:
            print(
                "Aviso: estos outputs no existen en disco todavía: "
                + ", ".join(faltantes),
                file=sys.stderr,
            )
    elif nuevo_estado in ("omitido", "fallido"):
        entrada["motivo"] = args.motivo or ""
        # Un paso no omitible no declara `si_omitido`: su impacto es exactamente la
        # razón por la que no debía omitirse.
        entrada["impacto"] = definicion.get("si_omitido") or definicion.get(
            "razon_no_omitible", ""
        )

    # Avanza el puntero al primer paso no cerrado.
    pendiente = next(
        (p["id"] for p in estado["pasos"] if p["estado"] in ("pendiente", "en_curso")),
        None,
    )
    estado["paso_actual"] = pendiente

    guardar_estado(estado, args.estado)
    render_state_md(estado, pasos, args.estado)

    print(f"{args.paso} → {nuevo_estado}")
    if nuevo_estado == "omitido":
        print(f"  Impacto declarado: {entrada['impacto'] or '(sin impacto declarado)'}")
    print(f"  Siguiente paso: {pendiente or 'flujo completo'}")
    return 0


def cmd_iniciar(args):
    return _transicion(args, "en_curso")


def cmd_completar(args):
    return _transicion(args, "completado")


def cmd_omitir(args):
    return _transicion(args, "omitido")


def cmd_fallar(args):
    return _transicion(args, "fallido")


def cmd_decision(args):
    pasos = cargar_pasos(args.pasos)
    estado = cargar_estado(args.estado)
    def_paso(pasos, args.paso)  # valida que el paso exista

    estado["decisiones"] = [
        d
        for d in estado["decisiones"]
        if not (d["paso"] == args.paso and d["nodo"] == args.nodo)
    ]
    estado["decisiones"].append(
        {
            "paso": args.paso,
            "nodo": args.nodo,
            "opcion": args.opcion,
            "registrado": datetime.now().isoformat(timespec="seconds"),
        }
    )
    guardar_estado(estado, args.estado)
    render_state_md(estado, pasos, args.estado)
    print(f"Decisión registrada · {args.paso} · {args.nodo} → {args.opcion}")
    return 0


# --------------------------------------------------------------------------- #
# Bloque de contexto que viaja a cada HTML
# --------------------------------------------------------------------------- #

def construir_bloque_flujo(estado, pasos, paso_id):
    """Devuelve el bloque `flujo` de REPORT_DATA para `paso_id`.

    Es el contexto completo del flujo: dónde está este reporte dentro de los
    11 pasos, qué se decidió antes, qué se omitió y con qué consecuencia.
    """
    definicion = def_paso(pasos, paso_id)
    actual = estado_paso(estado, paso_id)

    ruta = []
    for p in estado["pasos"]:
        d = def_paso(pasos, p["id"])
        item = {
            "id": p["id"],
            "titulo": p["titulo"],
            "etapa": p["etapa"],
            "estado": "actual" if p["id"] == paso_id else p["estado"],
            "objetivo": d.get("objetivo", ""),
        }
        if p.get("resumen"):
            item["resumen"] = p["resumen"]
        if p.get("outputs"):
            item["archivo"] = p["outputs"][0]
        if p.get("veredicto"):
            item["veredicto"] = p["veredicto"]
        if p.get("skills"):
            item["skills"] = p["skills"]
        if p["estado"] == "omitido":
            item["motivo"] = p.get("motivo", "")
            item["impacto"] = p.get("impacto", "")
        ruta.append(item)

    omitidos = [
        {
            "id": p["id"],
            "titulo": p["titulo"],
            "motivo": p.get("motivo", ""),
            "impacto": p.get("impacto", ""),
            "forzada": bool(p.get("omision_forzada")),
        }
        for p in estado["pasos"]
        if p["estado"] == "omitido"
    ]

    completados = [p for p in estado["pasos"] if p["estado"] == "completado"]

    return {
        "proyecto": estado.get("proyecto", ""),
        "objetivo_proyecto": estado.get("objetivo", ""),
        "audiencia": estado.get("audiencia", ""),
        "paso_actual": paso_id,
        "paso_titulo": definicion["titulo"],
        "paso_objetivo": definicion.get("objetivo", ""),
        "paso_orden": definicion.get("orden"),
        "total_pasos": len(estado["pasos"]),
        "avance": {
            "completados": len(completados),
            "omitidos": len(omitidos),
            "pendientes": sum(
                1 for p in estado["pasos"] if p["estado"] == "pendiente"
            ),
        },
        "predecesores": definicion.get("predecesores", []),
        "skills_del_paso": actual.get("skills", []),
        "ruta": ruta,
        "decisiones": estado.get("decisiones", []),
        "omitidos": omitidos,
    }


def cmd_contexto(args):
    pasos = cargar_pasos(args.pasos)
    estado = cargar_estado(args.estado)
    bloque = construir_bloque_flujo(estado, pasos, args.paso)
    texto = json.dumps(bloque, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(texto + "\n", encoding="utf-8")
        print(f"Bloque `flujo` escrito en {args.output}")
    else:
        print(texto)
    return 0


# --------------------------------------------------------------------------- #
# mostrar — briefing del paso para la macro-skill
# --------------------------------------------------------------------------- #

def cmd_mostrar(args):
    pasos = cargar_pasos(args.pasos)
    estado = cargar_estado(args.estado)

    if not args.paso:
        paso_id = estado.get("paso_actual")
        if not paso_id:
            print("El flujo está completo: no queda ningún paso pendiente.")
            return 0
    else:
        paso_id = args.paso

    d = def_paso(pasos, paso_id)
    e = estado_paso(estado, paso_id)

    print(f"# {paso_id} · {d['titulo']}  ({d['etapa']})")
    print(f"Proyecto: {estado.get('proyecto')}")
    print(f"Objetivo del paso: {d.get('objetivo','')}")
    print(f"Estado actual: {e['estado']}")
    print()

    print("## Histórico relevante (predecesores)")
    if not d["predecesores"]:
        print("- (es el primer paso del flujo)")
    for pid in d["predecesores"]:
        pe = estado_paso(estado, pid)
        linea = f"- {ICONO[pe['estado']]} {pid} {pe['titulo']}: {pe['estado']}"
        if pe.get("resumen"):
            linea += f" — {pe['resumen']}"
        if pe["estado"] == "omitido":
            linea += f" — IMPACTO: {pe.get('impacto','')}"
        print(linea)
    print()

    if estado.get("decisiones"):
        print("## Decisiones ya tomadas (no volver a preguntar)")
        for dec in estado["decisiones"]:
            print(f"- [{dec['paso']}] {dec['nodo']} → {dec['opcion']}")
        print()

    omitidos = [p for p in estado["pasos"] if p["estado"] == "omitido"]
    if omitidos:
        print("## Pasos omitidos (usar supuestos marcados * donde falte su input)")
        for p in omitidos:
            print(f"- {p['id']} {p['titulo']}: {p.get('impacto','')}")
        print()

    print("## Decisiones a presentar en este paso")
    if not d["decisiones"]:
        print("- (ninguna: este paso no tiene nodo de decisión)")
    for dec in d["decisiones"]:
        marca = " [condicional]" if dec.get("solo_si") else ""
        print(f"- {dec['nodo']} ({dec['tipo']}){marca}")
        if dec.get("solo_si"):
            print(f"    solo si: {dec['solo_si']}")
        if dec.get("opciones_desde"):
            print(f"    opciones desde: {dec['opciones_desde']}")
        for o in dec.get("opciones", []):
            extra = ""
            if o.get("skills"):
                extra = "  → " + ", ".join(o["skills"])
            elif o.get("palancas"):
                extra = "  → palancas: " + ", ".join(o["palancas"])
            print(f"    · {o['opcion']}{extra}")
        if dec.get("auto_si"):
            print(
                f"    auto: si {dec['auto_si']['condicion']} → "
                f"«{dec['auto_si']['opcion']}»"
            )
    print()

    print("## Sub-skills invocables en este paso")
    for s in d["skills_posibles"]:
        print(f"- sub-skills/{s}/SKILL.md")
    if d.get("cadenas"):
        for cadena in d["cadenas"]:
            print("- cadena obligatoria: " + " → ".join(cadena))
    if d.get("paralelo"):
        print("- (se ejecutan en paralelo y se consolidan en un solo HTML)")
    print()

    print("## Omisión")
    if d.get("omitible"):
        print(f"- Se puede omitir. Si se omite: {d.get('si_omitido','')}")
    else:
        print(f"- NO se puede omitir. {d.get('razon_no_omitible','')}")
    print()
    print(f"## Entrega esperada\n- {d['entrega']} (validado por el generador)")
    return 0


# --------------------------------------------------------------------------- #
# render — STATE.md como vista humana
# --------------------------------------------------------------------------- #

def render_state_md(estado, pasos, estado_path=None):
    destino = STATE_MD
    if estado_path:
        destino = Path(estado_path).resolve().parent / "STATE.md"

    L = []
    L.append("# STATE — Flujo de Innovación IRIS")
    L.append("")
    L.append(
        "> Vista humana **generada** desde `flujo_estado.json`. No la edites a mano: "
        "se reescribe en cada paso. Para cambiar el estado usa "
        "`python scripts/estado_flujo.py <comando>`."
    )
    L.append("")
    L.append(f"- proyecto: {estado.get('proyecto') or '(sin iniciar)'}")
    if estado.get("objetivo"):
        L.append(f"- objetivo: {estado['objetivo']}")
    if estado.get("audiencia"):
        L.append(f"- audiencia: {estado['audiencia']}")
    L.append(f"- ruta: {estado.get('ruta', 'completa')}")
    L.append(f"- paso_actual: {estado.get('paso_actual') or 'flujo completo'}")
    L.append(f"- actualizado: {estado.get('actualizado','')}")
    L.append("")

    comp = sum(1 for p in estado["pasos"] if p["estado"] == "completado")
    omit = sum(1 for p in estado["pasos"] if p["estado"] == "omitido")
    total = len(estado["pasos"])
    L.append(f"**Avance:** {comp} completados · {omit} omitidos · {total} pasos.")
    L.append("")

    L.append("## Ruta")
    L.append("")
    L.append("| | Paso | Etapa | Estado | Resumen / motivo |")
    L.append("|---|---|---|---|---|")
    for p in estado["pasos"]:
        nota = p.get("resumen") or ""
        if p["estado"] == "omitido":
            nota = f"omitido: {p.get('motivo','')}"
        elif p["estado"] == "fallido":
            nota = f"falló: {p.get('motivo','')}"
        nota = nota.replace("|", "\\|")
        L.append(
            f"| {ICONO[p['estado']]} | `{p['id']}` {p['titulo']} | {p['etapa']} "
            f"| {p['estado']} | {nota} |"
        )
    L.append("")

    L.append("## Decisiones")
    L.append("")
    if estado.get("decisiones"):
        for d in estado["decisiones"]:
            L.append(f"- `{d['paso']}` **{d['nodo']}** → {d['opcion']}")
    else:
        L.append("_(ninguna registrada todavía)_")
    L.append("")

    L.append("## Historial")
    L.append("")
    hechos = [
        p for p in estado["pasos"] if p["estado"] in ("completado", "fallido")
    ]
    if hechos:
        for p in hechos:
            skills = ", ".join(p.get("skills", [])) or "—"
            outs = ", ".join(p.get("outputs", [])) or "—"
            L.append(f"- **`{p['id']}`** {p['titulo']}")
            L.append(f"  - skills: {skills}")
            L.append(f"  - resumen: {p.get('resumen') or '—'}")
            L.append(f"  - veredicto: {p.get('veredicto') or '—'}")
            L.append(f"  - outputs: {outs}")
    else:
        L.append("_(sin pasos ejecutados todavía)_")
    L.append("")

    omitidos = [p for p in estado["pasos"] if p["estado"] == "omitido"]
    L.append("## Pasos omitidos y su impacto")
    L.append("")
    if omitidos:
        for p in omitidos:
            forzada = " **(omisión forzada)**" if p.get("omision_forzada") else ""
            L.append(f"- **`{p['id']}`** {p['titulo']}{forzada}")
            L.append(f"  - motivo: {p.get('motivo') or '—'}")
            L.append(f"  - impacto: {p.get('impacto') or '—'}")
    else:
        L.append("_(ninguno)_")
    L.append("")

    L.append("## Siguiente paso")
    L.append("")
    siguiente = estado.get("paso_actual")
    if siguiente:
        d = def_paso(pasos, siguiente)
        L.append(f"- `{siguiente}` — {d['titulo']} ({d['etapa']})")
        L.append(f"- objetivo: {d.get('objetivo','')}")
        L.append(
            f"- sub-skills: "
            + ", ".join(f"`sub-skills/{s}`" for s in d["skills_posibles"])
        )
    else:
        L.append("- Flujo completo.")
    L.append("")

    destino.write_text("\n".join(L), encoding="utf-8")
    return destino


def cmd_render(args):
    pasos = cargar_pasos(args.pasos)
    estado = cargar_estado(args.estado)
    destino = render_state_md(estado, pasos, args.estado)
    print(f"STATE.md regenerado: {destino}")
    return 0


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def _comunes(sp):
    sp.add_argument("--estado", default=None, help="Ruta de flujo_estado.json")
    sp.add_argument("--pasos", default=None, help="Ruta de pasos.json")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Máquina de estados del flujo de innovación IRIS."
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("init", help="Crea flujo_estado.json para un proyecto nuevo")
    p.add_argument("--proyecto", required=True)
    p.add_argument("--objetivo", default=None)
    p.add_argument("--audiencia", default=None)
    p.add_argument(
        "--ruta",
        choices=["completa", "minima"],
        default="completa",
        help="minima = solo los 5 pasos de ruta_minima; el resto queda omitido",
    )
    p.add_argument("--forzar", action="store_true", help="Sobreescribe un estado existente")
    _comunes(p)
    p.set_defaults(func=cmd_init)

    p = sub.add_parser("mostrar", help="Briefing del paso: histórico, decisiones y skills")
    p.add_argument("--paso", default=None, help="Por defecto, el paso_actual")
    _comunes(p)
    p.set_defaults(func=cmd_mostrar)

    p = sub.add_parser("iniciar", help="Marca un paso como en_curso")
    p.add_argument("--paso", required=True)
    _comunes(p)
    p.set_defaults(func=cmd_iniciar, skills=None, outputs=None, resumen=None,
                   veredicto=None, motivo=None, forzar=False)

    p = sub.add_parser("completar", help="Marca un paso como completado")
    p.add_argument("--paso", required=True)
    p.add_argument("--skills", nargs="*", default=[], help="Rutas de sub-skills usadas")
    p.add_argument("--outputs", nargs="*", default=[], help="Archivos generados")
    p.add_argument("--resumen", default="", help="Una línea: qué se aprendió")
    p.add_argument("--veredicto", choices=VEREDICTOS, default=None)
    _comunes(p)
    p.set_defaults(func=cmd_completar, motivo=None, forzar=False)

    p = sub.add_parser("omitir", help="Marca un paso como omitido por decisión del usuario")
    p.add_argument("--paso", required=True)
    p.add_argument("--motivo", required=True, help="Por qué lo omite el usuario")
    p.add_argument("--forzar", action="store_true",
                   help="Omitir un paso marcado como no omitible")
    _comunes(p)
    p.set_defaults(func=cmd_omitir, skills=None, outputs=None, resumen=None,
                   veredicto=None)

    p = sub.add_parser("fallar", help="Marca un paso como fallido")
    p.add_argument("--paso", required=True)
    p.add_argument("--motivo", required=True)
    _comunes(p)
    p.set_defaults(func=cmd_fallar, skills=None, outputs=None, resumen=None,
                   veredicto=None, forzar=False)

    p = sub.add_parser("decision", help="Registra la elección de un nodo de decisión")
    p.add_argument("--paso", required=True)
    p.add_argument("--nodo", required=True)
    p.add_argument("--opcion", required=True)
    _comunes(p)
    p.set_defaults(func=cmd_decision)

    p = sub.add_parser("contexto", help="Imprime el bloque `flujo` para un reporte.json")
    p.add_argument("--paso", required=True)
    p.add_argument("-o", "--output", default=None)
    _comunes(p)
    p.set_defaults(func=cmd_contexto)

    p = sub.add_parser("render", help="Regenera STATE.md desde flujo_estado.json")
    _comunes(p)
    p.set_defaults(func=cmd_render)

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except ReglaDelFlujo as exc:
        print(f"Regla del flujo: {exc}", file=sys.stderr)
        return 2
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"Error: JSON inválido — {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
