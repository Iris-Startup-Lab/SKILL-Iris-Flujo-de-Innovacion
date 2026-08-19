"""
simular_kano.py

Simula las respuestas de una encuesta Kano (pregunta funcional × disfuncional por
característica) y escribe **un CSV** con la forma exacta que consume
`sub-skills/2.Descubrimiento/encuesta-kano/scripts/clasificar_kano.py`: el análisis
posterior no distingue —ni necesita distinguir— si el dato vino de campo o de aquí.

MODELO GENERATIVO
-----------------
Cada característica del plan declara una **categoría latente** (`categoria_objetivo`:
M/O/A/I/R). Para cada encuestado se sortea la pareja de respuestas desde la distribución
típica de esa categoría y, con probabilidad `ruido`, desde una uniforme sobre las 5
opciones. El ruido es lo que evita el resultado de laboratorio: produce disidentes,
categorías minoritarias y algún caso contradictorio (Q), como una encuesta real.

Lo que el script calcula (y por tanto nadie redacta a mano):
  · clasificación con la matriz Kano oficial, idéntica a la de `clasificar_kano.py`;
  · conteo por categoría y categoría ganadora (moda) por característica;
  · intervalo de **Wilson** al 95% sobre la proporción de la categoría ganadora;
  · coeficientes de Berger CS (satisfacción) y DS (insatisfacción);
  · tasa Q+R como control de calidad del enunciado;
  · margen de error de la muestra y avisos cuando `n` no sostiene lo que se quiere afirmar;
  · si la categoría recuperada coincide con la declarada en el plan.

VALIDEZ
-------
Reproducible y correcto dentro de su propio modelo; **validez externa nula**. El intervalo
describe la variabilidad del generador, no la de una población. Ver `sub-skills/SIMULACION.md`.

Uso (desde la raíz del repositorio):

    python sub-skills/2.Descubrimiento/encuesta-kano/simulador/scripts/simular_kano.py \\
        plan.json -o kano_respuestas_SIMULADO.csv

    # sobrescribir parámetros del plan
    ... plan.json --n 60 --seed 7 --ruido 0.2 -o kano_respuestas_SIMULADO.csv

Esquema del `plan.json`: ver `SIMULADOR.md` (sección «El plan»).
Códigos de salida: 0 ok · 1 error de archivo/uso · 2 plan inválido.
"""
import argparse
import csv
import json
import math
import random
import sys
from collections import Counter

# --- Opciones de respuesta (los literales que entiende clasificar_kano.py) ---
ETIQUETA = {
    "like": "Me gusta que sea así",
    "expect": "Espero que sea así",
    "neutral": "Indiferente",
    "tolerate": "Lo tolero",
    "dislike": "No me gusta",
}
OPCIONES = list(ETIQUETA)

# --- Matriz Kano oficial: (funcional, disfuncional) -> categoría ---------------
# Idéntica a la de `../../scripts/clasificar_kano.py`. Si una cambia, cambian las dos.
MATRIZ = {
    ("like", "like"): "Q", ("like", "expect"): "A", ("like", "neutral"): "A",
    ("like", "tolerate"): "A", ("like", "dislike"): "O",
    ("expect", "like"): "R", ("expect", "expect"): "I", ("expect", "neutral"): "I",
    ("expect", "tolerate"): "I", ("expect", "dislike"): "M",
    ("neutral", "like"): "R", ("neutral", "expect"): "R", ("neutral", "neutral"): "I",
    ("neutral", "tolerate"): "I", ("neutral", "dislike"): "M",
    ("tolerate", "like"): "R", ("tolerate", "expect"): "R", ("tolerate", "neutral"): "I",
    ("tolerate", "tolerate"): "I", ("tolerate", "dislike"): "M",
    ("dislike", "like"): "Q", ("dislike", "expect"): "R", ("dislike", "neutral"): "R",
    ("dislike", "tolerate"): "R", ("dislike", "dislike"): "Q",
}

CATEGORIAS = ["M", "O", "A", "I", "R", "Q"]
NOMBRE_CAT = {
    "M": "Must-be / Obligatorio",
    "O": "Unidimensional / Rendimiento",
    "A": "Atractivo",
    "I": "Indiferente",
    "R": "Inverso",
    "Q": "Cuestionable",
}

# --- Distribuciones por categoría latente -------------------------------------
# Cada patrón es (dist. funcional, dist. disfuncional). Los pesos no necesitan sumar 1:
# se normalizan al sortear. Elegidos para que la pareja modal caiga en la categoría
# declarada, con cola suficiente para que aparezcan minoritarias.
PATRON = {
    "M": ({"expect": 0.65, "neutral": 0.20, "like": 0.10, "tolerate": 0.05},
          {"dislike": 0.80, "tolerate": 0.12, "neutral": 0.08}),
    "O": ({"like": 0.75, "expect": 0.20, "neutral": 0.05},
          {"dislike": 0.75, "tolerate": 0.15, "neutral": 0.10}),
    "A": ({"like": 0.80, "expect": 0.12, "neutral": 0.08},
          {"neutral": 0.45, "tolerate": 0.35, "expect": 0.12, "dislike": 0.08}),
    "I": ({"neutral": 0.55, "tolerate": 0.20, "expect": 0.15, "like": 0.10},
          {"neutral": 0.50, "tolerate": 0.30, "expect": 0.12, "dislike": 0.08}),
    "R": ({"dislike": 0.55, "tolerate": 0.30, "neutral": 0.15},
          {"expect": 0.50, "neutral": 0.38, "like": 0.12}),
}

Z95 = 1.96


class PlanInvalido(Exception):
    """El plan.json no cumple el esquema mínimo para simular."""


# --------------------------------------------------------------------------- #
# Estadística
# --------------------------------------------------------------------------- #

def wilson(k, n, z=Z95):
    """Intervalo de Wilson al 95% para una proporción.

    Preferido sobre la aproximación normal porque con `n` pequeña o proporciones
    cerca de 0 o 1 la normal se sale del [0,1] y subestima el intervalo.
    """
    if n <= 0:
        return 0.0, 0.0
    p = k / n
    denom = 1 + z * z / n
    centro = (p + z * z / (2 * n)) / denom
    margen = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return max(0.0, centro - margen), min(1.0, centro + margen)


def margen_error(n, p=0.5, z=Z95):
    """Margen de error de una proporción. p=0.5 es el caso conservador (peor caso)."""
    if n <= 0:
        return 1.0
    return z * math.sqrt(p * (1 - p) / n)


def coeficientes_berger(conteo):
    """CS (satisfacción) y DS (insatisfacción) de Berger.

    CS = (A+O)/(A+O+M+I) · DS = -(O+M)/(A+O+M+I)
    Q y R quedan fuera del denominador: son respuestas descartadas, no preferencias.
    """
    base = conteo["A"] + conteo["O"] + conteo["M"] + conteo["I"]
    if base == 0:
        return None, None
    cs = (conteo["A"] + conteo["O"]) / base
    ds = -(conteo["O"] + conteo["M"]) / base
    return cs, ds


# --------------------------------------------------------------------------- #
# Plan
# --------------------------------------------------------------------------- #

def cargar_plan(ruta):
    with open(ruta, encoding="utf-8") as f:
        plan = json.load(f)
    if not isinstance(plan, dict):
        raise PlanInvalido("el plan debe ser un objeto JSON")

    features = plan.get("features")
    if not isinstance(features, list) or not features:
        raise PlanInvalido("`features` debe ser una lista con al menos una característica")

    for i, f in enumerate(features):
        if not isinstance(f, dict) or not str(f.get("feature", "")).strip():
            raise PlanInvalido(f"features[{i}].feature vacío o ausente")
        cat = str(f.get("categoria_objetivo", "")).strip().upper()
        if cat not in PATRON:
            raise PlanInvalido(
                f"features[{i}].categoria_objetivo = {f.get('categoria_objetivo')!r}; "
                f"se espera una de M/O/A/I/R (Q no se declara: es una respuesta "
                f"contradictoria, no un objetivo de diseño)"
            )
        f["categoria_objetivo"] = cat

    segmentos = plan.get("segmentos") or [{"nombre": "General", "peso": 1.0}]
    for s in segmentos:
        if not str(s.get("nombre", "")).strip():
            raise PlanInvalido("cada segmento necesita `nombre`")
        s["peso"] = float(s.get("peso", 1.0))
    if sum(s["peso"] for s in segmentos) <= 0:
        raise PlanInvalido("los pesos de los segmentos suman 0")
    plan["segmentos"] = segmentos
    return plan


def _sortear(rng, dist):
    opciones = list(dist)
    pesos = [dist[o] for o in opciones]
    return rng.choices(opciones, weights=pesos, k=1)[0]


def _dist_feature(feature, categoria):
    """Distribuciones de la feature: las del patrón, salvo override explícito del plan."""
    func, disf = PATRON[categoria]
    override = feature.get("distribuciones") or {}
    return override.get("funcional", func), override.get("disfuncional", disf)


# --------------------------------------------------------------------------- #
# Simulación
# --------------------------------------------------------------------------- #

def simular(plan, n=None, seed=None, ruido=None):
    n = int(n if n is not None else plan.get("n", 40))
    seed = int(seed if seed is not None else plan.get("seed", 20260819))
    ruido = float(ruido if ruido is not None else plan.get("ruido", 0.15))
    if n < 1:
        raise PlanInvalido("`n` debe ser al menos 1")
    if not 0.0 <= ruido <= 1.0:
        raise PlanInvalido("`ruido` debe estar entre 0 y 1")

    rng = random.Random(seed)
    features = plan["features"]
    segmentos = plan["segmentos"]
    con_importancia = bool(plan.get("importancia")) or any(
        f.get("importancia_media") for f in features
    )

    # Reparto de encuestados por segmento, proporcional al peso declarado.
    nombres = [s["nombre"] for s in segmentos]
    pesos = [s["peso"] for s in segmentos]
    asignacion = rng.choices(nombres, weights=pesos, k=n)

    filas = []
    for i in range(n):
        rid = f"R{i + 1:03d}"
        segmento = asignacion[i]
        for f in features:
            cat_objetivo = f["categoria_objetivo"]
            dist_f, dist_d = _dist_feature(f, cat_objetivo)
            if rng.random() < ruido:
                # Respuesta fuera del patrón: uniforme sobre las 5 opciones.
                clave_f = rng.choice(OPCIONES)
                clave_d = rng.choice(OPCIONES)
            else:
                clave_f = _sortear(rng, dist_f)
                clave_d = _sortear(rng, dist_d)

            fila = {
                "respondent_id": rid,
                "segmento": segmento,
                "feature": f["feature"],
                "funcional": ETIQUETA[clave_f],
                "disfuncional": ETIQUETA[clave_d],
                "simulado": "si",
                "seed": seed,
                "_categoria": MATRIZ[(clave_f, clave_d)],
                "_objetivo": cat_objetivo,
            }
            if con_importancia:
                media = float(f.get("importancia_media", 3.0))
                valor = round(rng.gauss(media, 0.8))
                fila["importancia"] = max(1, min(5, valor))
            filas.append(fila)

    return filas, {"n": n, "seed": seed, "ruido": ruido,
                   "con_importancia": con_importancia,
                   "segmentos": segmentos}


def escribir_csv(filas, ruta, con_importancia):
    columnas = ["respondent_id", "segmento", "feature", "funcional", "disfuncional"]
    if con_importancia:
        columnas.append("importancia")
    columnas += ["simulado", "seed"]

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
    print("=" * 78)
    print("SIMULACIÓN KANO — DATOS SIMULADOS, NO SON EVIDENCIA DE CAMPO")
    print("=" * 78)
    print(f"CSV: {ruta_csv}  ({len(filas)} filas = {n} encuestados × "
          f"{len(plan['features'])} características)")
    print(f"Semilla: {params['seed']}  ·  ruido: {params['ruido']:.0%}  ·  n = {n}")
    seg = ", ".join(f"{s['nombre']} (peso {s['peso']:g})" for s in params["segmentos"])
    print(f"Segmentos: {seg}")
    print()

    e = margen_error(n)
    print("SUPUESTOS ESTADÍSTICOS")
    print(f"  · Margen de error de la muestra: ±{e * 100:.1f} pp "
          f"(95%, p=0.5, caso conservador)")
    print("  · Intervalos por categoría: Wilson al 95%")
    print("  · Reproducible: misma semilla + mismo plan = CSV idéntico")
    print()

    avisos = []
    if n < 20:
        avisos.append(
            f"n = {n} es demasiado bajo para leer proporciones por característica "
            f"(margen ±{e * 100:.0f} pp). La práctica Kano pide 20-30 por segmento; "
            f"por debajo de eso la categoría ganadora puede cambiar solo por el sorteo."
        )
    if len(params["segmentos"]) > 1:
        nf = len(plan["features"])
        por_seg = Counter(f["segmento"] for f in filas)
        chicos = [s for s, c in por_seg.items() if c / nf < 20]
        if chicos:
            avisos.append(
                "segmentos con menos de 20 encuestados (no se pueden comparar entre sí): "
                + ", ".join(sorted(chicos))
            )

    print("RESULTADOS POR CARACTERÍSTICA")
    print(f"  {'característica':<34} {'cat':>4} {'obj':>4}  {'conteo M/O/A/I/R/Q':<24} "
          f"{'IC95 ganadora':<18} {'CS':>6} {'DS':>6}")
    recuperadas = 0
    for f in plan["features"]:
        nombre = f["feature"]
        propias = [x for x in filas if x["feature"] == nombre]
        crudo = Counter(x["_categoria"] for x in propias)
        conteo = {c: crudo.get(c, 0) for c in CATEGORIAS}
        ganadora = max(CATEGORIAS, key=lambda c: conteo[c])
        lo, hi = wilson(conteo[ganadora], len(propias))
        cs, ds = coeficientes_berger(conteo)
        objetivo = f["categoria_objetivo"]
        if ganadora == objetivo:
            recuperadas += 1
        marca = " " if ganadora == objetivo else "!"
        conteo_txt = "/".join(str(conteo[c]) for c in CATEGORIAS)

        # Berger se calcula sobre A+O+M+I. Si la mayoría de las respuestas cayó en R o Q,
        # el coeficiente describe a una minoría y engaña más de lo que informa.
        base_berger = conteo["A"] + conteo["O"] + conteo["M"] + conteo["I"]
        berger_fiable = base_berger >= len(propias) / 2
        if cs is None or not berger_fiable:
            cs_txt, ds_txt = "  n/d", "  n/d"
        else:
            cs_txt, ds_txt = f"{cs:+.2f}", f"{ds:+.2f}"
        if cs is not None and not berger_fiable:
            avisos.append(
                f"«{nombre}»: CS/DS no se reportan. Solo {base_berger} de {len(propias)} "
                f"respuestas caen en A/O/M/I —el resto es R o Q— y los coeficientes de "
                f"Berger se calculan sobre esa base: describirían a una minoría."
            )
        print(f"{marca} {nombre[:34]:<34} {ganadora:>4} {objetivo:>4}  {conteo_txt:<24} "
              f"[{lo * 100:4.1f}%, {hi * 100:5.1f}%] {cs_txt:>6} {ds_txt:>6}")

        empate = [c for c in CATEGORIAS if conteo[c] == conteo[ganadora]]
        if len(empate) > 1:
            avisos.append(
                f"«{nombre}»: empate entre {', '.join(empate)} ({conteo[ganadora]} cada una). "
                f"La moda no decide; hace falta más n o revisar el enunciado."
            )
        # Control de calidad del enunciado. En una feature declarada `R` la respuesta
        # inversa es la esperada, así que ahí solo Q cuenta como respuesta descartable.
        if objetivo == "R":
            descartables, etiqueta_qr = conteo["Q"], "Q"
        else:
            descartables, etiqueta_qr = conteo["Q"] + conteo["R"], "Q+R"
        if descartables / len(propias) > 0.10:
            avisos.append(
                f"«{nombre}»: {etiqueta_qr} = {descartables}/{len(propias)} "
                f"({descartables / len(propias):.0%}). Por encima del 10% se interpreta como "
                f"enunciado ambiguo; aquí significa que el ruido ({params['ruido']:.0%}) o el "
                f"patrón declarado no son coherentes."
            )
    print()
    print(f"  Categoría declarada recuperada en {recuperadas}/{len(plan['features'])} "
          f"características.")
    if recuperadas < len(plan["features"]):
        print("  Las marcadas con «!» no recuperaron su categoría objetivo: es lo que pasa "
              "cuando el ruido supera la señal declarada.")
    print()

    print("LEYENDA")
    for c in CATEGORIAS:
        print(f"  {c} = {NOMBRE_CAT[c]}")
    print("  CS = coeficiente de satisfacción (0 a 1) · DS = de insatisfacción (-1 a 0), Berger")
    print()

    if avisos:
        print("AVISOS")
        for a in avisos:
            print(f"  · {a}")
        print()

    print("VALIDEZ EXTERNA: NULA")
    print("  Los intervalos describen la variabilidad del generador sintético, no la de una")
    print("  población. Estos números dicen cómo se leerían los resultados si el mundo se")
    print("  pareciera a las categorías declaradas en el plan; no dicen que se les parezca.")
    print("  Toda salida que use este CSV debe ir etiquetada SIMULADO.")
    print()
    print("SIGUIENTE PASO")
    print("  python sub-skills/2.Descubrimiento/encuesta-kano/scripts/clasificar_kano.py \\")
    print(f"      {ruta_csv} -o clasificacion_kano_SIMULADO.csv")


def main(argv=None):
    p = argparse.ArgumentParser(
        description="Simula respuestas de encuesta Kano y escribe un CSV (datos SIMULADOS)."
    )
    p.add_argument("plan", help="plan.json con features, categoria_objetivo y parámetros")
    p.add_argument("-o", "--output", default="kano_respuestas_SIMULADO.csv",
                   help="CSV de salida (debe terminar en _SIMULADO.csv)")
    p.add_argument("--n", type=int, default=None, help="Encuestados (default: el del plan, o 40)")
    p.add_argument("--seed", type=int, default=None, help="Semilla (default: la del plan)")
    p.add_argument("--ruido", type=float, default=None,
                   help="Prob. de respuesta fuera del patrón (default: la del plan, o 0.15)")
    args = p.parse_args(argv)

    if not args.output.endswith("_SIMULADO.csv"):
        print(f"Aviso: «{args.output}» no termina en _SIMULADO.csv. La convención del flujo "
              f"pide ese sufijo para que el archivo declare por sí solo que es sintético.",
              file=sys.stderr)

    try:
        plan = cargar_plan(args.plan)
        filas, params = simular(plan, args.n, args.seed, args.ruido)
    except FileNotFoundError:
        print(f"Error: no se encontró '{args.plan}'", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"Error: plan.json inválido — {exc}", file=sys.stderr)
        return 1
    except PlanInvalido as exc:
        print(f"Plan inválido: {exc}", file=sys.stderr)
        return 2

    escribir_csv(filas, args.output, params["con_importancia"])
    reportar(filas, plan, params, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
