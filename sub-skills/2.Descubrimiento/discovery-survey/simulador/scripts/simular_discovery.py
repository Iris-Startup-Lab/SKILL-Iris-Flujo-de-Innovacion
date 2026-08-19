"""
simular_discovery.py

Simula las respuestas de una encuesta de descubrimiento (preguntas abiertas sobre Jobs,
Pains y Gains) y escribe **un CSV** en formato largo, listo para el Affinity Sorting de
`sub-skills/2.Descubrimiento/discovery-survey`.

MODELO GENERATIVO
-----------------
Cada tema del plan declara una **prevalencia**: la probabilidad de que un encuestado lo
mencione. Para cada encuestado se hace un ensayo Bernoulli por tema, con la prevalencia del
segmento si el plan la declara. El parámetro `ruido` acerca esa probabilidad a 0.5
(`p_efectiva = (1 - ruido)·p + ruido·0.5`): encoge la señal declarada hacia el azar, que es
lo que hace que la muestra no salga de laboratorio.

Una fila por encuestado × pregunta × tema mencionado. Los encuestados que no mencionan nada
en una pregunta **también dejan fila** (con `tema` vacío): así el denominador de cada
proporción está en el archivo y no hay que suponerlo.

Lo que el script calcula (y por tanto nadie redacta a mano):
  · conteo y proporción por tema, con intervalo de **Wilson** al 95%;
  · contraste entre la prevalencia declarada y la observada;
  · tamaño de muestra requerido para el margen de error pedido (mismas fórmulas que
    `../../scripts/calcular_muestra.py`), ajuste por población finita y envíos necesarios;
  · diferencias entre segmentos con **prueba z de dos proporciones** al 95%;
  · reparto de la evidencia entre señales que validan, refutan o son neutras;
  · avisos cuando `n` no alcanza, cuando un conteo es demasiado pequeño para leerlo, o
    cuando ningún tema refuta la hipótesis.

VALIDEZ
-------
Reproducible y correcto dentro de su propio modelo; **validez externa nula**. Los intervalos
describen la variabilidad del generador, no la de una población. Ver `sub-skills/SIMULACION.md`.

Uso (desde la raíz del repositorio):

    python sub-skills/2.Descubrimiento/discovery-survey/simulador/scripts/simular_discovery.py \\
        plan.json -o discovery_respuestas_SIMULADO.csv

Esquema del `plan.json`: ver `SIMULADOR.md` (sección «El plan»).
Códigos de salida: 0 ok · 1 error de archivo/uso · 2 plan inválido.
"""
import argparse
import csv
import json
import math
import random
import sys
from collections import Counter, defaultdict

TIPOS = ("job", "pain", "gain")
SENALES = ("valida", "refuta", "neutral")
Z95 = 1.96

# Z por nivel de confianza, igual que en `../../scripts/calcular_muestra.py`.
VALORES_Z = {0.80: 1.2816, 0.85: 1.4395, 0.90: 1.6449,
             0.95: 1.9600, 0.98: 2.3263, 0.99: 2.5758}

SIN_MENCION = "No lo veo como un problema en mi caso."


class PlanInvalido(Exception):
    """El plan.json no cumple el esquema mínimo para simular."""


# --------------------------------------------------------------------------- #
# Estadística
# --------------------------------------------------------------------------- #

def wilson(k, n, z=Z95):
    """Intervalo de Wilson al 95% para una proporción."""
    if n <= 0:
        return 0.0, 0.0
    p = k / n
    denom = 1 + z * z / n
    centro = (p + z * z / (2 * n)) / denom
    margen = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return max(0.0, centro - margen), min(1.0, centro + margen)


def margen_error(n, p=0.5, z=Z95):
    if n <= 0:
        return 1.0
    return z * math.sqrt(p * (1 - p) / n)


def tamano_muestra(confianza, error, poblacion=None, tasa_respuesta=None, p=0.5):
    """n = (Z²·p·(1-p))/e², con ajuste por población finita y envíos requeridos."""
    nivel = min(VALORES_Z, key=lambda c: abs(c - confianza))
    z = VALORES_Z[nivel]
    n = (z ** 2 * p * (1 - p)) / (error ** 2)
    n_aj = n / (1 + (n - 1) / poblacion) if poblacion and poblacion > 0 else n
    envios = n_aj / tasa_respuesta if tasa_respuesta else None
    return {"nivel": nivel, "z": z, "n": n, "n_aj": n_aj, "envios": envios}


def z_dos_proporciones(k1, n1, k2, n2):
    """Prueba z de dos proporciones (proporción combinada). Devuelve (z, significativo)."""
    if n1 == 0 or n2 == 0:
        return None, False
    p1, p2 = k1 / n1, k2 / n2
    p_pool = (k1 + k2) / (n1 + n2)
    if p_pool in (0.0, 1.0):
        return 0.0, False
    se = math.sqrt(p_pool * (1 - p_pool) * (1 / n1 + 1 / n2))
    if se == 0:
        return 0.0, False
    z = (p1 - p2) / se
    return z, abs(z) >= Z95


# --------------------------------------------------------------------------- #
# Plan
# --------------------------------------------------------------------------- #

def cargar_plan(ruta):
    with open(ruta, encoding="utf-8") as f:
        plan = json.load(f)
    if not isinstance(plan, dict):
        raise PlanInvalido("el plan debe ser un objeto JSON")

    preguntas = plan.get("preguntas")
    if not isinstance(preguntas, list) or not preguntas:
        raise PlanInvalido("`preguntas` debe ser una lista con al menos una pregunta")
    for i, p in enumerate(preguntas):
        if not isinstance(p, dict) or not str(p.get("pregunta", "")).strip():
            raise PlanInvalido(f"preguntas[{i}].pregunta vacía o ausente")
        p.setdefault("id", f"P{i + 1}")

    ids = [p["id"] for p in preguntas]
    if len(set(ids)) != len(ids):
        raise PlanInvalido(f"hay ids de pregunta repetidos: {ids}")

    temas = plan.get("temas")
    if not isinstance(temas, list) or not temas:
        raise PlanInvalido("`temas` debe ser una lista con al menos un tema")
    for i, t in enumerate(temas):
        if not isinstance(t, dict) or not str(t.get("tema", "")).strip():
            raise PlanInvalido(f"temas[{i}].tema vacío o ausente")
        tipo = str(t.get("tipo", "")).strip().lower()
        if tipo not in TIPOS:
            raise PlanInvalido(
                f"temas[{i}].tipo = {t.get('tipo')!r}; se espera job, pain o gain"
            )
        t["tipo"] = tipo
        try:
            prev = float(t.get("prevalencia"))
        except (TypeError, ValueError):
            raise PlanInvalido(
                f"temas[{i}].prevalencia ausente o no numérica. Es la probabilidad "
                f"declarada de que un encuestado mencione el tema (0 a 1)."
            )
        if not 0.0 <= prev <= 1.0:
            raise PlanInvalido(f"temas[{i}].prevalencia = {prev}; debe estar entre 0 y 1")
        t["prevalencia"] = prev
        senal = str(t.get("senal", "neutral")).strip().lower()
        if senal not in SENALES:
            raise PlanInvalido(
                f"temas[{i}].senal = {t.get('senal')!r}; se espera valida, refuta o neutral"
            )
        t["senal"] = senal
        t["pregunta_id"] = t.get("pregunta_id") or ids[0]
        if t["pregunta_id"] not in ids:
            raise PlanInvalido(
                f"temas[{i}].pregunta_id = {t['pregunta_id']!r} no existe en `preguntas` "
                f"({', '.join(ids)})"
            )
        citas = t.get("citas") or []
        if not isinstance(citas, list) or not citas:
            raise PlanInvalido(
                f"temas[{i}].citas debe traer al menos una frase: es el material "
                f"cualitativo que el script reparte entre los encuestados"
            )
        t["citas"] = [str(c) for c in citas]

    segmentos = plan.get("segmentos") or [{"nombre": "General", "peso": 1.0}]
    for s in segmentos:
        if not str(s.get("nombre", "")).strip():
            raise PlanInvalido("cada segmento necesita `nombre`")
        s["peso"] = float(s.get("peso", 1.0))
    if sum(s["peso"] for s in segmentos) <= 0:
        raise PlanInvalido("los pesos de los segmentos suman 0")
    plan["segmentos"] = segmentos
    return plan


# --------------------------------------------------------------------------- #
# Simulación
# --------------------------------------------------------------------------- #

def _p_efectiva(p, ruido):
    """Encoge la prevalencia declarada hacia 0.5 en proporción al ruido."""
    return (1 - ruido) * p + ruido * 0.5


def simular(plan, n=None, seed=None, ruido=None):
    n = int(n if n is not None else plan.get("n", 30))
    seed = int(seed if seed is not None else plan.get("seed", 20260819))
    ruido = float(ruido if ruido is not None else plan.get("ruido", 0.15))
    if n < 1:
        raise PlanInvalido("`n` debe ser al menos 1")
    if not 0.0 <= ruido <= 1.0:
        raise PlanInvalido("`ruido` debe estar entre 0 y 1")

    rng = random.Random(seed)
    preguntas = plan["preguntas"]
    temas = plan["temas"]
    segmentos = plan["segmentos"]
    edades = plan.get("rango_edad") or [25, 55]

    nombres = [s["nombre"] for s in segmentos]
    pesos = [s["peso"] for s in segmentos]
    asignacion = rng.choices(nombres, weights=pesos, k=n)

    por_pregunta = defaultdict(list)
    for t in temas:
        por_pregunta[t["pregunta_id"]].append(t)

    filas = []
    menciones = defaultdict(set)          # tema -> {respondent_id}
    menciones_seg = defaultdict(Counter)  # tema -> Counter(segmento)
    n_por_segmento = Counter(asignacion)

    for i in range(n):
        rid = f"E{i + 1:03d}"
        segmento = asignacion[i]
        edad = rng.randint(int(edades[0]), int(edades[1]))
        for p in preguntas:
            mencionados = []
            for t in por_pregunta.get(p["id"], []):
                prev = t.get("prevalencia_por_segmento", {}).get(
                    segmento, t["prevalencia"]
                )
                if rng.random() < _p_efectiva(float(prev), ruido):
                    mencionados.append(t)

            if not mencionados:
                filas.append({
                    "respondent_id": rid, "segmento": segmento, "edad": edad,
                    "pregunta_id": p["id"], "pregunta": p["pregunta"],
                    "respuesta": plan.get("respuesta_sin_mencion", SIN_MENCION),
                    "tema": "", "tipo": "", "senal": "neutral",
                    "simulado": "si", "seed": seed,
                })
                continue

            for t in mencionados:
                menciones[t["tema"]].add(rid)
                menciones_seg[t["tema"]][segmento] += 1
                filas.append({
                    "respondent_id": rid, "segmento": segmento, "edad": edad,
                    "pregunta_id": p["id"], "pregunta": p["pregunta"],
                    "respuesta": rng.choice(t["citas"]),
                    "tema": t["tema"], "tipo": t["tipo"], "senal": t["senal"],
                    "simulado": "si", "seed": seed,
                })

    params = {"n": n, "seed": seed, "ruido": ruido, "segmentos": segmentos,
              "n_por_segmento": n_por_segmento}
    return filas, menciones, menciones_seg, params


def escribir_csv(filas, ruta):
    columnas = ["respondent_id", "segmento", "edad", "pregunta_id", "pregunta",
                "respuesta", "tema", "tipo", "senal", "simulado", "seed"]
    with open(ruta, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columnas, extrasaction="ignore")
        writer.writeheader()
        for fila in filas:
            writer.writerow(fila)
    return columnas


# --------------------------------------------------------------------------- #
# Reporte a stdout (el único artefacto es el CSV)
# --------------------------------------------------------------------------- #

def reportar(filas, menciones, menciones_seg, plan, params, ruta_csv):
    n = params["n"]
    avisos = []

    print("=" * 78)
    print("SIMULACIÓN DISCOVERY SURVEY — DATOS SIMULADOS, NO SON EVIDENCIA DE CAMPO")
    print("=" * 78)
    print(f"CSV: {ruta_csv}  ({len(filas)} filas · {n} encuestados · "
          f"{len(plan['preguntas'])} preguntas · {len(plan['temas'])} temas)")
    print(f"Semilla: {params['seed']}  ·  ruido: {params['ruido']:.0%}  ·  n = {n}")
    seg_txt = ", ".join(f"{s}: {c}" for s, c in sorted(params["n_por_segmento"].items()))
    print(f"Segmentos: {seg_txt}")
    print()

    # --- Tamaño de muestra ---------------------------------------------------
    muestra = plan.get("muestra") or {}
    confianza = float(muestra.get("confianza", 0.95))
    error = float(muestra.get("error", 0.10))
    poblacion = muestra.get("poblacion")
    tasa = muestra.get("tasa_respuesta")
    calc = tamano_muestra(confianza, error, poblacion, tasa)
    requerido = math.ceil(calc["n_aj"])

    print("SUPUESTOS ESTADÍSTICOS")
    print(f"  · Margen de error con n = {n}: ±{margen_error(n) * 100:.1f} pp "
          f"(95%, p=0.5, caso conservador)")
    print(f"  · n requerido para ±{error * 100:.0f} pp al "
          f"{int(calc['nivel'] * 100)}% (Z={calc['z']}): {requerido}"
          + (f" (ajustado a población {poblacion:g})" if poblacion else ""))
    if calc["envios"]:
        print(f"  · Con tasa de respuesta {tasa:.0%}: ~{math.ceil(calc['envios'])} "
              f"invitaciones en un estudio real")
    print("  · Proporciones por tema: intervalo de Wilson al 95%")
    print("  · Prevalencia efectiva: p_ef = (1 - ruido)·p_declarada + ruido·0.5")
    print("  · Reproducible: misma semilla + mismo plan = CSV idéntico")
    print()

    if n < requerido:
        avisos.append(
            f"n = {n} queda por debajo de los {requerido} que pide un margen de "
            f"±{error * 100:.0f} pp. Con esta muestra el margen real es "
            f"±{margen_error(n) * 100:.0f} pp: sirve para ordenar temas por magnitud, "
            f"no para afirmar porcentajes."
        )

    # --- Temas --------------------------------------------------------------
    print("TEMAS (proporción sobre los", n, "encuestados)")
    print(f"  {'tema':<38} {'tipo':<6} {'k/n':>7} {'obs':>7} {'declarada':>10} "
          f"{'IC95':<18} señal")
    for t in plan["temas"]:
        k = len(menciones.get(t["tema"], ()))
        p_obs = k / n
        lo, hi = wilson(k, n)
        p_dec = t["prevalencia"]
        p_ef = _p_efectiva(p_dec, params["ruido"])
        dentro = lo <= p_ef <= hi
        marca = " " if dentro else "!"
        print(f"{marca} {t['tema'][:38]:<38} {t['tipo']:<6} {k:>3}/{n:<3} "
              f"{p_obs * 100:6.1f}% {p_dec * 100:9.0f}% "
              f"[{lo * 100:4.1f}%, {hi * 100:5.1f}%] {t['senal']}")
        if not dentro:
            avisos.append(
                f"«{t['tema']}»: la prevalencia efectiva ({p_ef:.0%}) cae fuera del IC95 "
                f"observado [{lo:.0%}, {hi:.0%}]. Con n = {n} pasa por azar de vez en "
                f"cuando; si te importa esa cifra, sube n o fija otra semilla y compara."
            )
        if 0 < k < 5:
            avisos.append(
                f"«{t['tema']}»: solo {k} menciones. Por debajo de 5 el porcentaje es "
                f"inestable —una mención más lo mueve varios puntos—: repórtalo como "
                f"conteo ({k} de {n}), no como porcentaje."
            )
        if k == 0:
            avisos.append(
                f"«{t['tema']}»: 0 menciones pese a una prevalencia declarada de "
                f"{p_dec:.0%}. Revisa el plan o sube n."
            )
    print()

    # --- Señal vs. hipótesis ------------------------------------------------
    conteo_senal = Counter()
    for t in plan["temas"]:
        conteo_senal[t["senal"]] += len(menciones.get(t["tema"], ()))
    total_senal = sum(conteo_senal.values()) or 1
    print("EVIDENCIA FRENTE A LA HIPÓTESIS (menciones, no encuestados)")
    for s in SENALES:
        print(f"  · {s:<8} {conteo_senal[s]:>4}  ({conteo_senal[s] / total_senal:.0%})")
    if not any(t["senal"] == "refuta" for t in plan["temas"]):
        avisos.append(
            "ningún tema del plan refuta la hipótesis. Una simulación que solo confirma no "
            "es una prueba, es un espejo: añade al menos un tema con senal «refuta»."
        )
    print()

    # --- Segmentos ----------------------------------------------------------
    nombres = [s["nombre"] for s in params["segmentos"]]
    if len(nombres) == 2:
        a, b = nombres
        na, nb = params["n_por_segmento"][a], params["n_por_segmento"][b]
        print(f"DIFERENCIAS ENTRE SEGMENTOS — {a} (n={na}) vs {b} (n={nb})")
        print("  prueba z de dos proporciones al 95%")
        for t in plan["temas"]:
            ka = menciones_seg[t["tema"]][a]
            kb = menciones_seg[t["tema"]][b]
            z, sig = z_dos_proporciones(ka, na, kb, nb)
            if z is None:
                continue
            veredicto = "DIFERENCIA" if sig else "sin diferencia"
            pa = ka / na * 100 if na else 0
            pb = kb / nb * 100 if nb else 0
            print(f"  {t['tema'][:38]:<38} {pa:5.1f}% vs {pb:5.1f}%  "
                  f"z={z:+5.2f}  {veredicto}")
        if min(na, nb) < 20:
            avisos.append(
                f"el segmento más pequeño tiene {min(na, nb)} encuestados: la prueba z "
                f"entre segmentos es orientativa, no concluyente (se pide ~20 por grupo)."
            )
        print()
    elif len(nombres) > 2:
        print("DIFERENCIAS ENTRE SEGMENTOS")
        print(f"  {len(nombres)} segmentos: la prueba z de este script compara dos. "
              f"Para más, ejecuta la simulación por pares.")
        print()

    if avisos:
        print("AVISOS")
        for a_ in avisos:
            print(f"  · {a_}")
        print()

    print("VALIDEZ EXTERNA: NULA")
    print("  Los intervalos y la prueba z describen la variabilidad del generador sintético,")
    print("  no la de una población: contrastan lo observado con las prevalencias que tú")
    print("  declaraste. Estos números dicen cómo se leerían los resultados si el mundo se")
    print("  pareciera al plan; no dicen que se le parezca.")
    print("  Toda salida que use este CSV debe ir etiquetada SIMULADO.")


def main(argv=None):
    p = argparse.ArgumentParser(
        description="Simula respuestas de una encuesta de descubrimiento (datos SIMULADOS)."
    )
    p.add_argument("plan", help="plan.json con preguntas, temas y prevalencias")
    p.add_argument("-o", "--output", default="discovery_respuestas_SIMULADO.csv",
                   help="CSV de salida (debe terminar en _SIMULADO.csv)")
    p.add_argument("--n", type=int, default=None, help="Encuestados (default: el del plan, o 30)")
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
        filas, menciones, menciones_seg, params = simular(
            plan, args.n, args.seed, args.ruido
        )
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
    reportar(filas, menciones, menciones_seg, plan, params, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
