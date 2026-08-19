"""
simular_expo.py

Simula las interacciones de una visita a un evento, feria o expo y escribe **un CSV** en
formato largo, listo para la consolidación de hallazgos de
`sub-skills/2.Descubrimiento/expo-quest`.

DIVISIÓN DEL TRABAJO
--------------------
El plan trae lo cualitativo —el evento ficticio, con quién se habla, qué códigos existen y
con qué prevalencia— y **el script decide quién dice qué** y hace todos los recuentos.

POR QUÉ NO HAY PORCENTAJES
--------------------------
Seis conversaciones de pasillo no son una muestra probabilística: quien se acerca a un stand
ya está autoseleccionado. Aquí no hay proporciones de población; hay conteos (`4 de 6`) y
saturación de códigos. Ese sesgo de autoselección existe también en la visita real, y el
script lo declara en cada ejecución.

Lo que el script calcula:
  · qué códigos menciona cada interlocutor (Bernoulli con la prevalencia declarada);
  · conteo por código y por tipo (Job / Pain / Gain / Competencia);
  · separación entre lo que dicen los asistentes y lo que dicen los expositores;
  · **curva de saturación** por interacción;
  · reparto entre señales que validan, refutan o son neutras, y el contraste de reacciones;
  · avisos si faltan expositores, si no hay hallazgos de competencia, si nadie reacciona con
    escepticismo o si ningún código refuta la hipótesis.

VALIDEZ
-------
Reproducible y correcto dentro de su propio modelo; **validez externa nula**. Ver
`sub-skills/SIMULACION.md`.

Uso (desde la raíz del repositorio):

    python sub-skills/2.Descubrimiento/expo-quest/simulador/scripts/simular_expo.py \\
        plan.json -o expo_interacciones_SIMULADO.csv

Esquema del `plan.json`: ver `SIMULADOR.md` (sección «El plan»).
Códigos de salida: 0 ok · 1 error de archivo/uso · 2 plan inválido.
"""
import argparse
import csv
import json
import random
import sys
from collections import Counter, defaultdict

TIPOS = ("job", "pain", "gain", "competencia")
SENALES = ("valida", "refuta", "neutral")
TIPOS_INTERLOCUTOR = ("asistente", "expositor")
# La reacción se normaliza sin acento: el plan puede escribir «escéptica» o «esceptica».
REACCIONES = ("positiva", "neutral", "esceptica", "negativa")
DIMENSIONES = ("B2B", "B2C")

INTERACCIONES_MINIMAS = 4
CONSECUTIVAS_SATURACION = 2

SIN_HALLAZGO = "(conversación sin hallazgo codificable)"


class PlanInvalido(Exception):
    """El plan.json no cumple el esquema mínimo para simular."""


def cargar_plan(ruta):
    with open(ruta, encoding="utf-8") as f:
        plan = json.load(f)
    if not isinstance(plan, dict):
        raise PlanInvalido("el plan debe ser un objeto JSON")

    dimension = str(plan.get("dimension", "")).strip().upper()
    if dimension not in DIMENSIONES:
        raise PlanInvalido(
            f"`dimension` = {plan.get('dimension')!r}; se espera B2B o B2C. Es "
            f"indispensable: cambia el lenguaje, el interlocutor y lo que se pregunta."
        )
    plan["dimension"] = dimension

    evento = plan.get("evento")
    if not isinstance(evento, dict) or not str(evento.get("nombre", "")).strip():
        raise PlanInvalido(
            "`evento` debe traer al menos `nombre` (ficticio). No uses el nombre de un "
            "evento real: nadie asistió."
        )

    interlocutores = plan.get("interlocutores")
    if not isinstance(interlocutores, list) or not interlocutores:
        raise PlanInvalido(
            "`interlocutores` debe ser una lista. Los inventa el LLM (rol, perfil, "
            "reacción): son el material cualitativo."
        )
    for i, p in enumerate(interlocutores):
        if not isinstance(p, dict) or not str(p.get("rol", "")).strip():
            raise PlanInvalido(
                f"interlocutores[{i}].rol vacío o ausente (ej. «Comprador de empaque»). "
                f"Usa el rol, no un nombre propio: en una feria no se piden nombres."
            )
        tipo = str(p.get("tipo", "asistente")).strip().lower()
        if tipo not in TIPOS_INTERLOCUTOR:
            raise PlanInvalido(
                f"interlocutores[{i}].tipo = {p.get('tipo')!r}; se espera asistente "
                f"o expositor"
            )
        p["tipo"] = tipo
        reaccion = str(p.get("reaccion", "neutral")).strip().lower()
        reaccion = reaccion.replace("é", "e").replace("á", "a").replace("í", "i")
        if reaccion not in REACCIONES:
            raise PlanInvalido(
                f"interlocutores[{i}].reaccion = {p.get('reaccion')!r}; se espera "
                f"positiva, neutral, escéptica o negativa"
            )
        p["reaccion"] = reaccion

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
                f"codigos[{i}].tipo = {c.get('tipo')!r}; se espera job, pain, gain "
                f"o competencia"
            )
        c["tipo"] = tipo
        try:
            prev = float(c.get("prevalencia"))
        except (TypeError, ValueError):
            raise PlanInvalido(
                f"codigos[{i}].prevalencia ausente o no numérica: es la probabilidad "
                f"declarada de que un interlocutor lo mencione (0 a 1)."
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
        solo = c.get("solo_tipo")
        if solo is not None:
            solo = str(solo).strip().lower()
            if solo not in TIPOS_INTERLOCUTOR:
                raise PlanInvalido(
                    f"codigos[{i}].solo_tipo = {c.get('solo_tipo')!r}; se espera "
                    f"asistente o expositor"
                )
            c["solo_tipo"] = solo
        citas = c.get("citas") or []
        if not isinstance(citas, list) or not citas:
            raise PlanInvalido(
                f"codigos[{i}].citas debe traer al menos una frase literal: es lo que se "
                f"cita en el reporte y el script solo la reparte"
            )
        c["citas"] = [str(x) for x in citas]
    return plan


def curva_saturacion(orden_ids, codigos_por_interaccion):
    acumulado = set()
    curva = []
    ultima_novedad = 0
    for i, iid in enumerate(orden_ids, 1):
        nuevos = [c for c in codigos_por_interaccion.get(iid, ()) if c not in acumulado]
        acumulado.update(nuevos)
        curva.append({"orden": i, "id": iid, "nuevos": len(nuevos),
                      "acumulado": len(acumulado)})
        if nuevos:
            ultima_novedad = i
    saturado = (len(orden_ids) - ultima_novedad) >= CONSECUTIVAS_SATURACION
    return curva, ultima_novedad, saturado


def _p_efectiva(p, ruido):
    return (1 - ruido) * p + ruido * 0.5


def simular(plan, seed=None, ruido=None):
    seed = int(seed if seed is not None else plan.get("seed", 20260819))
    ruido = float(ruido if ruido is not None else plan.get("ruido", 0.15))
    if not 0.0 <= ruido <= 1.0:
        raise PlanInvalido("`ruido` debe estar entre 0 y 1")

    rng = random.Random(seed)
    interlocutores = plan["interlocutores"]
    codigos = plan["codigos"]
    evento = plan["evento"]

    filas = []
    codigos_por_interaccion = defaultdict(list)
    orden_ids = []

    for i, quien in enumerate(interlocutores):
        iid = f"I{i + 1:02d}"
        orden_ids.append(iid)
        base = {
            "interaccion_id": iid,
            "interlocutor": quien["rol"],
            "tipo_interlocutor": quien["tipo"],
            "perfil": quien.get("perfil", ""),
            "reaccion": quien["reaccion"],
            "dimension": plan["dimension"],
            "evento": evento["nombre"],
            "simulado": "si",
            "seed": seed,
        }

        mencionados = []
        for c in codigos:
            if c.get("solo_tipo") and c["solo_tipo"] != quien["tipo"]:
                continue
            prev = c.get("prevalencia_por_reaccion", {}).get(
                quien["reaccion"], c["prevalencia"]
            )
            if rng.random() < _p_efectiva(float(prev), ruido):
                mencionados.append(c)

        if not mencionados:
            filas.append(dict(base, codigo="", tipo="", senal="neutral",
                              cita=plan.get("cita_sin_hallazgo", SIN_HALLAZGO)))
            continue

        for c in mencionados:
            codigos_por_interaccion[iid].append(c["codigo"])
            filas.append(dict(base, codigo=c["codigo"], tipo=c["tipo"],
                              senal=c["senal"], cita=rng.choice(c["citas"])))

    params = {"n": len(interlocutores), "seed": seed, "ruido": ruido,
              "orden_ids": orden_ids,
              "codigos_por_interaccion": codigos_por_interaccion}
    return filas, params


def escribir_csv(filas, ruta):
    columnas = ["interaccion_id", "interlocutor", "tipo_interlocutor", "perfil",
                "reaccion", "dimension", "evento", "codigo", "tipo", "senal", "cita",
                "simulado", "seed"]
    with open(ruta, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columnas, extrasaction="ignore")
        writer.writeheader()
        for fila in filas:
            writer.writerow(fila)
    return columnas


def reportar(filas, plan, params, ruta_csv):
    n = params["n"]
    avisos = []
    tipos_int = Counter(p["tipo"] for p in plan["interlocutores"])

    print("=" * 78)
    print("SIMULACIÓN EXPO QUEST — DATOS SIMULADOS, NO HUBO ASISTENCIA REAL")
    print("=" * 78)
    print(f"CSV: {ruta_csv}  ({len(filas)} filas · {n} interacciones · "
          f"{len(plan['codigos'])} códigos)")
    print(f"Evento ficticio: «{plan['evento']['nombre']}» · dimensión {plan['dimension']}")
    print(f"Interlocutores: {tipos_int['asistente']} asistentes, "
          f"{tipos_int['expositor']} expositores")
    print(f"Semilla: {params['seed']}  ·  ruido: {params['ruido']:.0%}")
    print()

    print("SUPUESTOS ESTADÍSTICOS")
    print(f"  · Muestra de conveniencia (n = {n}): quien se acerca a un stand ya está "
          f"autoseleccionado.")
    print("  · Sin porcentajes de población: se reportan conteos («4 de 6») y saturación.")
    print("  · Menciones: ensayo Bernoulli con la prevalencia declarada, encogida hacia 0.5 "
          "por el ruido.")
    print("  · Reproducible: misma semilla + mismo plan = CSV idéntico")
    print()

    if n < INTERACCIONES_MINIMAS:
        avisos.append(
            f"solo {n} interacciones. Por debajo de {INTERACCIONES_MINIMAS} no hay con qué "
            f"contrastar: una conversación suelta es una anécdota."
        )
    if not tipos_int["expositor"]:
        avisos.append(
            "ningún expositor entre los interlocutores. La mitad del valor de una feria es "
            "lo que se aprende de quien ya vende a este mercado: añade al menos uno."
        )

    conteo_codigo = Counter(f["codigo"] for f in filas if f["codigo"])
    print(f"CÓDIGOS (interacciones en las que apareció, sobre {n})")
    print(f"  {'código':<18} {'tipo':<12} {'k/n':>7}  {'declarada':>9}  señal   restringido a")
    for c in plan["codigos"]:
        k = conteo_codigo.get(c["codigo"], 0)
        solo = c.get("solo_tipo") or "—"
        print(f"  {c['codigo'][:18]:<18} {c['tipo']:<12} {k:>3}/{n:<3}  "
              f"{c['prevalencia'] * 100:8.0f}%  {c['senal']:<7} {solo}")
        if k == 0:
            avisos.append(
                f"código «{c['codigo']}»: no apareció en ninguna interacción pese a una "
                f"prevalencia declarada de {c['prevalencia']:.0%}."
            )
    print()

    print("ASISTENTES vs EXPOSITORES (menciones por tipo de código)")
    print(f"  {'tipo de código':<14} {'asistentes':>11} {'expositores':>12}")
    for t in TIPOS:
        a = sum(1 for f in filas
                if f["codigo"] and f["tipo"] == t and f["tipo_interlocutor"] == "asistente")
        e = sum(1 for f in filas
                if f["codigo"] and f["tipo"] == t and f["tipo_interlocutor"] == "expositor")
        print(f"  {t:<14} {a:>11} {e:>12}")
    if not any(c["tipo"] == "competencia" for c in plan["codigos"]):
        avisos.append(
            "el plan no declara ningún código de `competencia`. Es lo único que solo se "
            "consigue en una feria: quién más está vendiendo esto y cómo lo cuenta."
        )
    print()

    curva, ultima, saturado = curva_saturacion(
        params["orden_ids"], params["codigos_por_interaccion"]
    )
    print("CURVA DE SATURACIÓN")
    print(f"  {'interacción':<13} {'códigos nuevos':>15} {'acumulado':>11}")
    for punto in curva:
        print(f"  {punto['id']:<13} {punto['nuevos']:>15} {punto['acumulado']:>11}")
    print(f"  Último código nuevo: interacción {ultima} de {n} "
          f"({curva[-1]['acumulado']} de {len(plan['codigos'])} códigos del plan "
          f"aparecieron).")
    if saturado:
        print(f"  Saturación alcanzada: las últimas {n - ultima} interacciones no trajeron "
              f"nada nuevo.")
    else:
        print("  Saturación NO alcanzada.")
        avisos.append(
            f"saturación no alcanzada: la interacción {ultima} todavía trajo códigos "
            f"nuevos. Con las conversaciones planificadas no se cubren los códigos "
            f"declarados."
        )
    print()

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

    reacciones = Counter(p["reaccion"] for p in plan["interlocutores"])
    print()
    print("REACCIONES DECLARADAS")
    for r, c in sorted(reacciones.items()):
        print(f"  · {r:<10} {c:>3}")
    if not (reacciones["esceptica"] + reacciones["negativa"]):
        avisos.append(
            "ningún interlocutor reacciona con escepticismo ni en contra. En una feria real "
            "siempre hay alguien a quien no le interesa: sin esa reacción el ensayo no "
            "sirve de prueba."
        )
    print()

    if avisos:
        print("AVISOS")
        for a in avisos:
            print(f"  · {a}")
        print()

    print("VALIDEZ EXTERNA: NULA")
    print("  El evento, los interlocutores y sus reacciones son inventados. Ni el nombre del")
    print("  evento ni las cifras de asistencia corresponden a algo que ocurrió. Toda salida")
    print("  que use este CSV va etiquetada SIMULADO.")


def main(argv=None):
    p = argparse.ArgumentParser(
        description="Simula interacciones en un evento y escribe un CSV (datos SIMULADOS)."
    )
    p.add_argument("plan", help="plan.json con evento, dimension, interlocutores y codigos")
    p.add_argument("-o", "--output", default="expo_interacciones_SIMULADO.csv",
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
