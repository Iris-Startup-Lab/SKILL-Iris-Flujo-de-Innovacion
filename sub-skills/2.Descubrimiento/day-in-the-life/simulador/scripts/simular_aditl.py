"""
simular_aditl.py

Simula sesiones de observación etnográfica «A Day In The Life» y escribe **un CSV** en
formato largo, listo para la codificación de
`sub-skills/2.Descubrimiento/day-in-the-life`.

DIVISIÓN DEL TRABAJO
--------------------
El plan trae lo cualitativo —quiénes son los sujetos observados, en qué bloques se divide su
jornada, qué códigos existen y con qué prevalencia— y **el script decide qué se observa en
cada sesión** y hace todos los recuentos. Ninguna cifra se redacta a mano.

POR QUÉ NO HAY PORCENTAJES
--------------------------
Con 2-4 sesiones de observación no se estiman proporciones de nada. La justificación de una
muestra etnográfica es la **saturación de códigos**: se observa hasta que las jornadas dejan
de traer fricciones nuevas. El script reporta conteos (`2 de 3`) y la curva de saturación.

Lo que el script calcula:
  · qué códigos aparecen en cada sesión y en qué bloque de la jornada;
  · conteo por código y por tipo (Job / Pain / Gain / Workaround);
  · **curva de saturación** por sesión;
  · reparto entre señales que validan, refutan o son neutras;
  · avisos si faltan fricciones o workarounds (una jornada sin tropiezos no aporta nada),
    si un sujeto no registra ninguna fricción, si no hay saturación o si ningún código
    refuta la hipótesis.

VALIDEZ
-------
Reproducible y correcto dentro de su propio modelo; **validez externa nula**. Ver
`sub-skills/SIMULACION.md`.

Uso (desde la raíz del repositorio):

    python sub-skills/2.Descubrimiento/day-in-the-life/simulador/scripts/simular_aditl.py \\
        plan.json -o aditl_observaciones_SIMULADO.csv

Esquema del `plan.json`: ver `SIMULADOR.md` (sección «El plan»).
Códigos de salida: 0 ok · 1 error de archivo/uso · 2 plan inválido.
"""
import argparse
import csv
import json
import random
import sys
from collections import Counter, defaultdict

TIPOS = ("job", "pain", "gain", "workaround")
SENALES = ("valida", "refuta", "neutral")

SESIONES_MINIMAS = 2
SESIONES_SUGERIDAS = 4
CONSECUTIVAS_SATURACION = 2

SIN_OBSERVACION = "(bloque sin observación codificable)"


class PlanInvalido(Exception):
    """El plan.json no cumple el esquema mínimo para simular."""


def cargar_plan(ruta):
    with open(ruta, encoding="utf-8") as f:
        plan = json.load(f)
    if not isinstance(plan, dict):
        raise PlanInvalido("el plan debe ser un objeto JSON")

    sujetos = plan.get("sujetos")
    if not isinstance(sujetos, list) or not sujetos:
        raise PlanInvalido(
            "`sujetos` debe ser una lista de personas observadas. Las inventa el LLM "
            "(nombre ficticio, rol, entorno, actitud): son el material cualitativo."
        )
    for i, s in enumerate(sujetos):
        if not isinstance(s, dict) or not str(s.get("nombre", "")).strip():
            raise PlanInvalido(f"sujetos[{i}].nombre vacío o ausente")
        s.setdefault("actitud", "sin declarar")

    bloques = plan.get("bloques")
    if not isinstance(bloques, list) or not bloques:
        raise PlanInvalido(
            "`bloques` debe ser una lista de tramos de la jornada "
            "(por ejemplo: 07:00 apertura, 10:00 operación, 15:00 cierre)"
        )
    for i, b in enumerate(bloques):
        if not isinstance(b, dict) or not str(b.get("hora", "")).strip():
            raise PlanInvalido(f"bloques[{i}].hora vacía o ausente")
        b.setdefault("id", f"B{i + 1}")
        b.setdefault("actividad", "")
    ids = [b["id"] for b in bloques]
    if len(set(ids)) != len(ids):
        raise PlanInvalido(f"hay ids de bloque repetidos: {ids}")

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
                f"o workaround"
            )
        c["tipo"] = tipo
        try:
            prev = float(c.get("prevalencia"))
        except (TypeError, ValueError):
            raise PlanInvalido(
                f"codigos[{i}].prevalencia ausente o no numérica: es la probabilidad "
                f"declarada de observarlo en una sesión (0 a 1)."
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
        c["bloque_id"] = c.get("bloque_id") or ids[0]
        if c["bloque_id"] not in ids:
            raise PlanInvalido(
                f"codigos[{i}].bloque_id = {c['bloque_id']!r} no existe en `bloques` "
                f"({', '.join(ids)})"
            )
        obs = c.get("observaciones") or c.get("citas") or []
        if not isinstance(obs, list) or not obs:
            raise PlanInvalido(
                f"codigos[{i}].observaciones debe traer al menos una frase: es lo que se "
                f"registra en la libreta de campo y el script solo la reparte"
            )
        c["observaciones"] = [str(x) for x in obs]
        c.setdefault("herramienta", "")
    return plan


def curva_saturacion(orden_ids, codigos_por_sesion):
    """Códigos nuevos por sesión y sesión en la que se alcanza la saturación."""
    acumulado = set()
    curva = []
    ultima_novedad = 0
    for i, sid in enumerate(orden_ids, 1):
        nuevos = [c for c in codigos_por_sesion.get(sid, ()) if c not in acumulado]
        acumulado.update(nuevos)
        curva.append({"orden": i, "id": sid, "nuevos": len(nuevos),
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
    sujetos = plan["sujetos"]
    bloques = plan["bloques"]

    por_bloque = defaultdict(list)
    for c in plan["codigos"]:
        por_bloque[c["bloque_id"]].append(c)

    filas = []
    codigos_por_sesion = defaultdict(list)
    orden_ids = []

    for i, sujeto in enumerate(sujetos):
        sid = f"S{i + 1:02d}"
        orden_ids.append(sid)
        actitud = sujeto.get("actitud", "sin declarar")
        for b in bloques:
            observados = []
            for c in por_bloque.get(b["id"], []):
                prev = c.get("prevalencia_por_actitud", {}).get(actitud, c["prevalencia"])
                if rng.random() < _p_efectiva(float(prev), ruido):
                    observados.append(c)

            base = {
                "sesion_id": sid,
                "sujeto": sujeto["nombre"],
                "rol": sujeto.get("rol", ""),
                "entorno": sujeto.get("entorno", ""),
                "actitud": actitud,
                "bloque_id": b["id"],
                "hora": b["hora"],
                "actividad": b.get("actividad", ""),
                "simulado": "si",
                "seed": seed,
            }

            if not observados:
                filas.append(dict(base, herramienta="", codigo="", tipo="",
                                  senal="neutral",
                                  observacion=plan.get("observacion_sin_hallazgo",
                                                        SIN_OBSERVACION)))
                continue

            for c in observados:
                codigos_por_sesion[sid].append(c["codigo"])
                filas.append(dict(base,
                                  herramienta=c.get("herramienta", ""),
                                  codigo=c["codigo"],
                                  tipo=c["tipo"],
                                  senal=c["senal"],
                                  observacion=rng.choice(c["observaciones"])))

    params = {"n": len(sujetos), "seed": seed, "ruido": ruido,
              "orden_ids": orden_ids, "codigos_por_sesion": codigos_por_sesion}
    return filas, params


def escribir_csv(filas, ruta):
    columnas = ["sesion_id", "sujeto", "rol", "entorno", "actitud", "bloque_id", "hora",
                "actividad", "herramienta", "codigo", "tipo", "senal", "observacion",
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

    print("=" * 78)
    print("SIMULACIÓN A DAY IN THE LIFE — DATOS SIMULADOS, NO SON OBSERVACIÓN REAL")
    print("=" * 78)
    print(f"CSV: {ruta_csv}  ({len(filas)} filas · {n} sesiones · "
          f"{len(plan['bloques'])} bloques · {len(plan['codigos'])} códigos)")
    print(f"Semilla: {params['seed']}  ·  ruido: {params['ruido']:.0%}")
    print()

    print("SUPUESTOS ESTADÍSTICOS")
    print(f"  · Muestra etnográfica (n = {n} sesiones): se justifica por **saturación de "
          f"códigos**, no por margen de error.")
    print("  · Sin porcentajes: con esta n un porcentaje no significa nada. Se reportan "
          "conteos («2 de 3»).")
    print("  · Observaciones: ensayo Bernoulli con la prevalencia declarada, encogida hacia "
          "0.5 por el ruido.")
    print("  · Reproducible: misma semilla + mismo plan = CSV idéntico")
    print()

    if n < SESIONES_MINIMAS:
        avisos.append(
            f"solo {n} sesión: sin una segunda jornada no hay con qué contrastar, y la "
            f"saturación no se puede evaluar."
        )
    elif n > SESIONES_SUGERIDAS + 2:
        avisos.append(
            f"{n} sesiones: por encima de ~{SESIONES_SUGERIDAS} la observación etnográfica "
            f"deja de rendir; si buscas frecuencias, el instrumento correcto es una encuesta."
        )

    conteo_codigo = Counter(f["codigo"] for f in filas if f["codigo"])
    print(f"CÓDIGOS (sesiones en las que se observó, sobre {n})")
    print(f"  {'código':<18} {'tipo':<11} {'k/n':>7}  {'declarada':>9}  señal   bloque")
    for c in plan["codigos"]:
        k = conteo_codigo.get(c["codigo"], 0)
        print(f"  {c['codigo'][:18]:<18} {c['tipo']:<11} {k:>3}/{n:<3}  "
              f"{c['prevalencia'] * 100:8.0f}%  {c['senal']:<7} {c['bloque_id']}")
        if k == 0:
            avisos.append(
                f"código «{c['codigo']}»: no se observó en ninguna sesión pese a una "
                f"prevalencia declarada de {c['prevalencia']:.0%}."
            )
    print()

    por_tipo = Counter()
    for f in filas:
        if f["codigo"]:
            por_tipo[f["tipo"]] += 1
    print("OBSERVACIONES POR TIPO")
    for t in TIPOS:
        print(f"  · {t:<11} {por_tipo[t]:>4}")
    if not any(c["tipo"] == "workaround" for c in plan["codigos"]):
        avisos.append(
            "el plan no declara ningún `workaround`. La solución improvisada es el hallazgo "
            "más valioso de una observación: es la prueba de que el problema existe y de "
            "cuánto vale resolverlo."
        )
    if not any(c["tipo"] == "pain" for c in plan["codigos"]):
        avisos.append(
            "el plan no declara ninguna fricción (`pain`). Una jornada sin tropiezos no "
            "aporta nada: revisa el plan."
        )
    print()

    curva, ultima, saturado = curva_saturacion(
        params["orden_ids"], params["codigos_por_sesion"]
    )
    print("CURVA DE SATURACIÓN")
    print(f"  {'sesión':<10} {'códigos nuevos':>15} {'acumulado':>11}")
    for punto in curva:
        print(f"  {punto['id']:<10} {punto['nuevos']:>15} {punto['acumulado']:>11}")
    print(f"  Último código nuevo: sesión {ultima} de {n} "
          f"({curva[-1]['acumulado']} de {len(plan['codigos'])} códigos del plan "
          f"aparecieron).")
    if saturado:
        print(f"  Saturación alcanzada: las últimas {n - ultima} sesiones no trajeron nada "
              f"nuevo.")
    else:
        print("  Saturación NO alcanzada.")
        avisos.append(
            f"saturación no alcanzada: la sesión {ultima} todavía trajo códigos nuevos. En "
            f"campo eso significa «sigue observando»; aquí, que faltan sesiones para los "
            f"códigos declarados."
        )
    print()

    # Sujetos sin fricción observada: una jornada plana no sirve de material.
    for i, s in enumerate(plan["sujetos"]):
        sid = params["orden_ids"][i]
        tipos_sujeto = {f["tipo"] for f in filas
                        if f["sesion_id"] == sid and f["codigo"]}
        if not tipos_sujeto & {"pain", "workaround"}:
            avisos.append(
                f"{sid} ({s['nombre']}): jornada sin fricciones ni workarounds observados. "
                f"Sube la prevalencia de esos códigos o revisa el reparto por bloques."
            )

    conteo_senal = Counter()
    for c in plan["codigos"]:
        conteo_senal[c["senal"]] += conteo_codigo.get(c["codigo"], 0)
    total = sum(conteo_senal.values()) or 1
    print("EVIDENCIA FRENTE A LA HIPÓTESIS (observaciones)")
    for s in SENALES:
        print(f"  · {s:<8} {conteo_senal[s]:>4}  ({conteo_senal[s] / total:.0%})")
    if not any(c["senal"] == "refuta" for c in plan["codigos"]):
        avisos.append(
            "ningún código del plan refuta la hipótesis. Una simulación que solo confirma "
            "no es una prueba, es un espejo: añade al menos un código con senal «refuta»."
        )
    print()

    print("SUJETOS OBSERVADOS")
    for i, s in enumerate(plan["sujetos"]):
        sid = params["orden_ids"][i]
        k = len(params["codigos_por_sesion"].get(sid, ()))
        rol = f" · {s['rol']}" if s.get("rol") else ""
        ent = f" · {s['entorno']}" if s.get("entorno") else ""
        print(f"  {sid}  {s['nombre']}{rol}{ent} · actitud: {s.get('actitud')} "
              f"· {k} observaciones")
    print()

    if avisos:
        print("AVISOS")
        for a in avisos:
            print(f"  · {a}")
        print()

    print("VALIDEZ EXTERNA: NULA")
    print("  Los sujetos, sus jornadas y sus frases son inventados. La saturación indica que")
    print("  las sesiones cubrieron los códigos que TÚ declaraste, no la realidad de un")
    print("  puesto de trabajo. Toda salida que use este CSV va etiquetada SIMULADO.")


def main(argv=None):
    p = argparse.ArgumentParser(
        description="Simula sesiones de observación ADITL y escribe un CSV (datos SIMULADOS)."
    )
    p.add_argument("plan", help="plan.json con sujetos, bloques y codigos")
    p.add_argument("-o", "--output", default="aditl_observaciones_SIMULADO.csv",
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
