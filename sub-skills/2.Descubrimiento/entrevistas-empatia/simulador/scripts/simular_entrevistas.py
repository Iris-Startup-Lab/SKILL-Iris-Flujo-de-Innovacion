"""
simular_entrevistas.py

Simula las respuestas de un panel de entrevistas de empatía 1:1 y escribe **un CSV** en
formato largo, listo para la codificación de
`sub-skills/2.Descubrimiento/entrevistas-empatia`.

DIVISIÓN DEL TRABAJO
--------------------
El plan trae lo cualitativo —quiénes son los entrevistados, qué preguntas se les hace, qué
códigos existen y con qué prevalencia— y **el script decide quién menciona qué** y hace todos
los recuentos. Ninguna cifra se redacta a mano.

POR QUÉ NO HAY PORCENTAJES
--------------------------
Con 5-8 entrevistas no se estiman proporciones de una población: el margen de error de una
muestra de 6 es de ±40 puntos y cualquier porcentaje sería teatro. La justificación de una
muestra cualitativa es la **saturación de códigos**: se entrevista hasta que dejan de aparecer
códigos nuevos. Por eso el script reporta conteos (`4 de 6`) y la curva de saturación, no
porcentajes ni intervalos.

Lo que el script calcula:
  · quién menciona cada código (ensayo Bernoulli con la prevalencia declarada, modulada por
    la actitud del entrevistado si el plan lo declara);
  · conteo por código y por tipo (Job / Pain / Gain);
  · **curva de saturación**: códigos nuevos por entrevista y en cuál dejó de aparecer nada
    nuevo;
  · reparto de la evidencia entre señales que validan, refutan o son neutras;
  · avisos si el panel es corto, si no hay saturación, si un código no aparece o si ningún
    código refuta la hipótesis.

VALIDEZ
-------
Reproducible y correcto dentro de su propio modelo; **validez externa nula**. Ver
`sub-skills/SIMULACION.md`.

Uso (desde la raíz del repositorio):

    python sub-skills/2.Descubrimiento/entrevistas-empatia/simulador/scripts/simular_entrevistas.py \\
        plan.json -o entrevistas_SIMULADO.csv

Esquema del `plan.json`: ver `SIMULADOR.md` (sección «El plan»).
Códigos de salida: 0 ok · 1 error de archivo/uso · 2 plan inválido.
"""
import argparse
import csv
import json
import random
import sys
from collections import Counter, defaultdict

TIPOS = ("job", "pain", "gain")
SENALES = ("valida", "refuta", "neutral")

# Rango de saturación habitual en entrevistas de empatía (Mom Test / product discovery).
PANEL_MINIMO = 5
PANEL_SUGERIDO = 8
# Entrevistas consecutivas sin códigos nuevos que se consideran saturación.
CONSECUTIVAS_SATURACION = 2

SIN_MENCION = "(sin observación codificable en esta pregunta)"


class PlanInvalido(Exception):
    """El plan.json no cumple el esquema mínimo para simular."""


# --------------------------------------------------------------------------- #
# Plan
# --------------------------------------------------------------------------- #

def cargar_plan(ruta):
    with open(ruta, encoding="utf-8") as f:
        plan = json.load(f)
    if not isinstance(plan, dict):
        raise PlanInvalido("el plan debe ser un objeto JSON")

    panel = plan.get("panel")
    if not isinstance(panel, list) or not panel:
        raise PlanInvalido(
            "`panel` debe ser una lista de entrevistados. Los inventa el LLM (nombre "
            "ficticio, edad, ocupación, actitud): son el material cualitativo, no algo "
            "que deba sortear el script."
        )
    for i, p in enumerate(panel):
        if not isinstance(p, dict) or not str(p.get("nombre", "")).strip():
            raise PlanInvalido(f"panel[{i}].nombre vacío o ausente")
        p.setdefault("actitud", "sin declarar")

    guia = plan.get("guia")
    if not isinstance(guia, list) or not guia:
        raise PlanInvalido("`guia` debe ser una lista de preguntas")
    for i, g in enumerate(guia):
        if not isinstance(g, dict) or not str(g.get("pregunta", "")).strip():
            raise PlanInvalido(f"guia[{i}].pregunta vacía o ausente")
        g.setdefault("id", f"P{i + 1}")
    ids = [g["id"] for g in guia]
    if len(set(ids)) != len(ids):
        raise PlanInvalido(f"hay ids de pregunta repetidos: {ids}")

    codigos = plan.get("codigos")
    if not isinstance(codigos, list) or not codigos:
        raise PlanInvalido("`codigos` debe ser una lista con al menos un código")
    vistos = set()
    for i, c in enumerate(codigos):
        if not isinstance(c, dict) or not str(c.get("codigo", "")).strip():
            raise PlanInvalido(f"codigos[{i}].codigo vacío o ausente")
        if c["codigo"] in vistos:
            raise PlanInvalido(f"código repetido: {c['codigo']}")
        vistos.add(c["codigo"])
        tipo = str(c.get("tipo", "")).strip().lower()
        if tipo not in TIPOS:
            raise PlanInvalido(
                f"codigos[{i}].tipo = {c.get('tipo')!r}; se espera job, pain o gain"
            )
        c["tipo"] = tipo
        try:
            prev = float(c.get("prevalencia"))
        except (TypeError, ValueError):
            raise PlanInvalido(
                f"codigos[{i}].prevalencia ausente o no numérica: es la probabilidad "
                f"declarada de que un entrevistado lo mencione (0 a 1)."
            )
        if not 0.0 <= prev <= 1.0:
            raise PlanInvalido(f"codigos[{i}].prevalencia = {prev}; debe estar entre 0 y 1")
        c["prevalencia"] = prev
        senal = str(c.get("senal", "neutral")).strip().lower()
        if senal not in SENALES:
            raise PlanInvalido(
                f"codigos[{i}].senal = {c.get('senal')!r}; se espera valida, refuta o neutral"
            )
        c["senal"] = senal
        c["pregunta_id"] = c.get("pregunta_id") or ids[0]
        if c["pregunta_id"] not in ids:
            raise PlanInvalido(
                f"codigos[{i}].pregunta_id = {c['pregunta_id']!r} no existe en `guia` "
                f"({', '.join(ids)})"
            )
        citas = c.get("citas") or []
        if not isinstance(citas, list) or not citas:
            raise PlanInvalido(
                f"codigos[{i}].citas debe traer al menos una frase literal: es lo que se "
                f"cita en el reporte y el script solo la reparte"
            )
        c["citas"] = [str(x) for x in citas]
    return plan


# --------------------------------------------------------------------------- #
# Saturación
# --------------------------------------------------------------------------- #

def curva_saturacion(orden_ids, codigos_por_sujeto):
    """Códigos nuevos por entrevista y entrevista en la que se alcanza la saturación.

    Saturación = `CONSECUTIVAS_SATURACION` entrevistas seguidas sin ningún código nuevo.
    Es el criterio estándar de una muestra cualitativa: sustituye al margen de error, que
    con n pequeña no significa nada.
    """
    acumulado = set()
    curva = []
    ultima_novedad = 0
    for i, sid in enumerate(orden_ids, 1):
        nuevos = [c for c in codigos_por_sujeto.get(sid, ()) if c not in acumulado]
        acumulado.update(nuevos)
        curva.append({"orden": i, "id": sid, "nuevos": len(nuevos),
                      "acumulado": len(acumulado)})
        if nuevos:
            ultima_novedad = i
    saturado = (len(orden_ids) - ultima_novedad) >= CONSECUTIVAS_SATURACION
    return curva, ultima_novedad, saturado


# --------------------------------------------------------------------------- #
# Simulación
# --------------------------------------------------------------------------- #

def _p_efectiva(p, ruido):
    """Encoge la prevalencia declarada hacia 0.5 en proporción al ruido."""
    return (1 - ruido) * p + ruido * 0.5


def simular(plan, seed=None, ruido=None):
    seed = int(seed if seed is not None else plan.get("seed", 20260819))
    ruido = float(ruido if ruido is not None else plan.get("ruido", 0.15))
    if not 0.0 <= ruido <= 1.0:
        raise PlanInvalido("`ruido` debe estar entre 0 y 1")

    rng = random.Random(seed)
    panel = plan["panel"]
    guia = plan["guia"]
    codigos = plan["codigos"]

    por_pregunta = defaultdict(list)
    for c in codigos:
        por_pregunta[c["pregunta_id"]].append(c)

    filas = []
    codigos_por_sujeto = defaultdict(list)
    orden_ids = []

    for i, persona in enumerate(panel):
        eid = f"E{i + 1:02d}"
        orden_ids.append(eid)
        actitud = persona.get("actitud", "sin declarar")
        for g in guia:
            mencionados = []
            for c in por_pregunta.get(g["id"], []):
                prev = c.get("prevalencia_por_actitud", {}).get(
                    actitud, c["prevalencia"]
                )
                if rng.random() < _p_efectiva(float(prev), ruido):
                    mencionados.append(c)

            if not mencionados:
                filas.append({
                    "entrevistado_id": eid,
                    "nombre": persona["nombre"],
                    "edad": persona.get("edad", ""),
                    "ocupacion": persona.get("ocupacion", ""),
                    "actitud": actitud,
                    "pregunta_id": g["id"],
                    "pregunta": g["pregunta"],
                    "respuesta": plan.get("respuesta_sin_mencion", SIN_MENCION),
                    "codigo": "", "tipo": "", "senal": "neutral",
                    "simulado": "si", "seed": seed,
                })
                continue

            for c in mencionados:
                codigos_por_sujeto[eid].append(c["codigo"])
                filas.append({
                    "entrevistado_id": eid,
                    "nombre": persona["nombre"],
                    "edad": persona.get("edad", ""),
                    "ocupacion": persona.get("ocupacion", ""),
                    "actitud": actitud,
                    "pregunta_id": g["id"],
                    "pregunta": g["pregunta"],
                    "respuesta": rng.choice(c["citas"]),
                    "codigo": c["codigo"],
                    "tipo": c["tipo"],
                    "senal": c["senal"],
                    "simulado": "si", "seed": seed,
                })

    params = {"n": len(panel), "seed": seed, "ruido": ruido,
              "orden_ids": orden_ids, "codigos_por_sujeto": codigos_por_sujeto}
    return filas, params


def escribir_csv(filas, ruta):
    columnas = ["entrevistado_id", "nombre", "edad", "ocupacion", "actitud",
                "pregunta_id", "pregunta", "respuesta", "codigo", "tipo", "senal",
                "simulado", "seed"]
    with open(ruta, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columnas, extrasaction="ignore")
        writer.writeheader()
        for fila in filas:
            writer.writerow(fila)
    return columnas


# --------------------------------------------------------------------------- #
# Reporte a stdout (el único artefacto es el CSV)
# --------------------------------------------------------------------------- #

def reportar(filas, plan, params, ruta_csv):
    n = params["n"]
    avisos = []

    print("=" * 78)
    print("SIMULACIÓN DE ENTREVISTAS DE EMPATÍA — DATOS SIMULADOS, NO SON EVIDENCIA")
    print("=" * 78)
    print(f"CSV: {ruta_csv}  ({len(filas)} filas · {n} entrevistas · "
          f"{len(plan['guia'])} preguntas · {len(plan['codigos'])} códigos)")
    print(f"Semilla: {params['seed']}  ·  ruido: {params['ruido']:.0%}")
    print()

    print("SUPUESTOS ESTADÍSTICOS")
    print(f"  · Muestra cualitativa (n = {n}): se justifica por **saturación de códigos**, "
          f"no por margen de error.")
    print("  · Sin porcentajes: con esta n un porcentaje no significa nada. Se reportan "
          "conteos («4 de 6»).")
    print("  · Menciones: ensayo Bernoulli con la prevalencia declarada, encogida hacia 0.5 "
          "por el ruido.")
    print("  · Reproducible: misma semilla + mismo plan = CSV idéntico")
    print()

    if n < PANEL_MINIMO:
        avisos.append(
            f"el panel tiene {n} entrevistas. Por debajo de {PANEL_MINIMO} no se puede "
            f"hablar de saturación: cada entrevista nueva seguiría trayendo códigos nuevos."
        )
    elif n > PANEL_SUGERIDO + 4:
        avisos.append(
            f"el panel tiene {n} entrevistas. Más allá de ~{PANEL_SUGERIDO} el rendimiento "
            f"decae: si buscas proporciones, el instrumento correcto es una encuesta."
        )

    # --- Conteo por código ---------------------------------------------------
    print(f"CÓDIGOS (menciones sobre {n} entrevistas)")
    print(f"  {'código':<18} {'tipo':<6} {'k/n':>7}  {'declarada':>9}  señal   descripción")
    conteo_codigo = Counter()
    for f in filas:
        if f["codigo"]:
            conteo_codigo[f["codigo"]] += 1
    for c in plan["codigos"]:
        k = conteo_codigo.get(c["codigo"], 0)
        desc = (c.get("texto") or "")[:34]
        print(f"  {c['codigo'][:18]:<18} {c['tipo']:<6} {k:>3}/{n:<3}  "
              f"{c['prevalencia'] * 100:8.0f}%  {c['senal']:<7} {desc}")
        if k == 0:
            avisos.append(
                f"código «{c['codigo']}»: 0 menciones pese a una prevalencia declarada de "
                f"{c['prevalencia']:.0%}. Con n = {n} pasa; si ese código importa, súbele "
                f"la prevalencia o alarga el panel."
            )
    print()

    # --- Saturación ----------------------------------------------------------
    curva, ultima, saturado = curva_saturacion(
        params["orden_ids"], params["codigos_por_sujeto"]
    )
    print("CURVA DE SATURACIÓN")
    print(f"  {'entrevista':<12} {'códigos nuevos':>15} {'acumulado':>11}")
    for punto in curva:
        print(f"  {punto['id']:<12} {punto['nuevos']:>15} {punto['acumulado']:>11}")
    total_codigos = len(plan["codigos"])
    print(f"  Último código nuevo: entrevista {ultima} de {n} "
          f"({curva[-1]['acumulado']} de {total_codigos} códigos del plan aparecieron).")
    if saturado:
        print(f"  Saturación alcanzada: las últimas {n - ultima} entrevistas no trajeron "
              f"nada nuevo.")
    else:
        print("  Saturación NO alcanzada.")
        avisos.append(
            f"saturación no alcanzada: la entrevista {ultima} (la última o penúltima) "
            f"todavía trajo códigos nuevos. En un estudio real esto significa «sigue "
            f"entrevistando»; aquí, que el panel es corto para los códigos declarados."
        )
    print()

    # --- Señal vs. hipótesis -------------------------------------------------
    conteo_senal = Counter()
    for c in plan["codigos"]:
        conteo_senal[c["senal"]] += conteo_codigo.get(c["codigo"], 0)
    total = sum(conteo_senal.values()) or 1
    print("EVIDENCIA FRENTE A LA HIPÓTESIS (menciones)")
    for s in SENALES:
        print(f"  · {s:<8} {conteo_senal[s]:>4}  ({conteo_senal[s] / total:.0%})")
    if not any(c["senal"] == "refuta" for c in plan["codigos"]):
        avisos.append(
            "ningún código del plan refuta la hipótesis. Una simulación que solo confirma "
            "no es una prueba, es un espejo: añade al menos un código con senal «refuta»."
        )
    print()

    # --- Panel ---------------------------------------------------------------
    print("PANEL SINTÉTICO")
    for i, p in enumerate(plan["panel"]):
        eid = params["orden_ids"][i]
        k = len(params["codigos_por_sujeto"].get(eid, ()))
        edad = f", {p['edad']}" if p.get("edad") else ""
        ocup = f" · {p['ocupacion']}" if p.get("ocupacion") else ""
        print(f"  {eid}  {p['nombre']}{edad}{ocup} · actitud: {p.get('actitud')} "
              f"· {k} menciones")
    print()

    if avisos:
        print("AVISOS")
        for a in avisos:
            print(f"  · {a}")
        print()

    print("VALIDEZ EXTERNA: NULA")
    print("  Las personas, sus respuestas y sus citas son inventadas. La saturación indica")
    print("  que el panel cubrió los códigos que TÚ declaraste, no que haya cubierto la")
    print("  realidad. No hay hallazgo aquí: hay un ensayo del instrumento y de cómo se")
    print("  leerían los resultados. Toda salida que use este CSV va etiquetada SIMULADO.")


def main(argv=None):
    p = argparse.ArgumentParser(
        description="Simula entrevistas de empatía y escribe un CSV (datos SIMULADOS)."
    )
    p.add_argument("plan", help="plan.json con panel, guia y codigos")
    p.add_argument("-o", "--output", default="entrevistas_SIMULADO.csv",
                   help="CSV de salida (debe terminar en _SIMULADO.csv)")
    p.add_argument("--seed", type=int, default=None, help="Semilla (default: la del plan)")
    p.add_argument("--ruido", type=float, default=None,
                   help="Encogimiento de la prevalencia hacia 0.5 (default: 0.15)")
    args = p.parse_args(argv)

    if not args.output.endswith("_SIMULADO.csv"):
        print(f"Aviso: «{args.output}» no termina en _SIMULADO.csv. La convención del flujo "
              f"pide ese sufijo para que el archivo declare por sí solo que es sintético.",
              file=sys.stderr)

    try:
        plan = cargar_plan(args.plan)
        filas, params = simular(plan, args.seed, args.ruido)
    except FileNotFoundError:
        print(f"Error: no se encontró '{args.plan}'", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"Error: plan.json inválido — {exc}", file=sys.stderr)
        return 1
    except PlanInvalido as exc:
        print(f"Plan inválido: {exc}", file=sys.stderr)
        return 2

    escribir_csv(filas, args.output)
    reportar(filas, plan, params, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
