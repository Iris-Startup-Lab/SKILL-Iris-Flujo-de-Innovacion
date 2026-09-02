"""
analizar_resultados.py

Lee el resultado de un experimento de validación: k éxitos de n intentos →
tasa con intervalo de confianza de Wilson, prueba contra el umbral declarado,
prueba contra el grupo control si existe, veredicto y —cuando no alcanza para
concluir— cuántos intentos más harían falta.

Por qué existe: el flujo **diseñaba** los experimentos (Testing Cards con «≥ X% de
conversión en N visitas») pero no sabía **leerlos** cuando el usuario volvía con los
datos. Solo `email-campaign` calculaba el n requerido, y ninguna skill analizaba el
resultado. Sin esto, «37 de 420» se comparaba a ojo contra el umbral y la decisión
de perseverar o descartar se tomaba sin intervalo.

Y una segunda razón, de la evaluación metodológica: los pasos de validación
comparaban contra un umbral de industria, no contra un **control medido en el mismo
experimento**. Este script acepta el control y, si no lo hay, lo dice en las
advertencias en vez de dejarlo pasar.

Fórmulas (todas con la desviación normal de la stdlib, sin dependencias):
    tasa            p̂ = k / n
    IC de Wilson    centro = (p̂ + z²/2n) / (1 + z²/n)
                    semi   = z/(1+z²/n) · √(p̂(1−p̂)/n + z²/4n²)
    vs. umbral      z = (p̂ − p₀) / √(p₀(1−p₀)/n)
    vs. control     z = (p̂₁ − p̂₂) / √(p̄(1−p̄)(1/n₁ + 1/n₂))
    n para concluir n = z² · p̂(1−p̂) / (p̂ − p₀)²

Uso:
    # un experimento contra su umbral
    python analizar_resultados.py --k 37 --n 420 --umbral 0.06
    # contra un grupo control medido
    python analizar_resultados.py --k 37 --n 420 --control-k 12 --control-n 400
    # varias variantes a la vez (corrige por comparaciones múltiples)
    python analizar_resultados.py --datos experimento.json
    # ANTES de correr el experimento: muestra por brazo para detectar 3pp sobre un 3% base
    python analizar_resultados.py --n-requerido 0.03 0.03

Códigos de salida: 0 ok · 1 error de archivo/uso · 2 entrada inválida.
"""
import argparse
import json
import math
import sys
from statistics import NormalDist

CONFIANZA = 0.95
PODER = 0.80

# Debajo de esto la aproximación normal deja de ser fiable. El IC de Wilson aguanta
# mejor que el de Wald, pero el aviso sigue haciendo falta.
N_MINIMO_FIABLE = 30
EXITOS_MINIMOS_FIABLES = 5

FORMULAS = {
    "tasa": {
        "libro": "p̂ = k / n",
        "palabras": "De cada 100 personas que vieron el experimento, cuántas hicieron lo "
                    "que se quería medir.",
    },
    "wilson": {
        "libro": "IC = (p̂ + z²/2n ± z·√(p̂(1−p̂)/n + z²/4n²)) / (1 + z²/n)",
        "palabras": "El rango donde está la tasa real. Si el experimento se repitiera 100 "
                    "veces, en 95 el resultado caería dentro de este rango. Con pocos datos "
                    "el rango es ancho: eso no es un defecto del cálculo, es la información "
                    "que hay.",
    },
    "vs_umbral": {
        "libro": "z = (p̂ − p₀) / √(p₀(1−p₀)/n) ; p = 2(1 − Φ(|z|))",
        "palabras": "Qué tan raro sería obtener este resultado si la tasa real fuera "
                    "exactamente el umbral. Un p de 0.03 quiere decir que habría un 3% de "
                    "probabilidad de ver algo así por pura casualidad.",
    },
    "vs_control": {
        "libro": "z = (p̂₁ − p̂₂) / √(p̄(1−p̄)(1/n₁ + 1/n₂))",
        "palabras": "Compara las dos versiones medidas al mismo tiempo. Es la comparación "
                    "que de verdad aísla el cambio: el umbral de industria se midió en otro "
                    "mercado, otro momento y otra gente.",
    },
    "n_para_concluir": {
        "libro": "n = z² · p̂(1−p̂) / (p̂ − p₀)²",
        "palabras": "Si la tasa observada se mantiene, cuántos intentos harían falta para "
                    "que el intervalo deje de tocar el umbral. Convierte un «no "
                    "concluyente» en un plan.",
    },
    "bonferroni": {
        "libro": "alpha_corregido = alpha / m , con m = número de comparaciones",
        "palabras": "Al probar varias variantes a la vez, alguna parece ganadora por azar. "
                    "Exigir más de cada una compensa ese efecto.",
    },
}


class EntradaInvalida(Exception):
    pass


def _exigir(cond, mensaje):
    if not cond:
        raise EntradaInvalida(mensaje)


def _validar_kn(k, n, etiqueta):
    _exigir(isinstance(k, (int, float)) and not isinstance(k, bool),
            f"{etiqueta}: los éxitos (k) deben ser numéricos")
    _exigir(isinstance(n, (int, float)) and not isinstance(n, bool),
            f"{etiqueta}: los intentos (n) deben ser numéricos")
    _exigir(n > 0, f"{etiqueta}: n debe ser mayor que 0")
    _exigir(k >= 0, f"{etiqueta}: k no puede ser negativo")
    _exigir(k <= n,
            f"{etiqueta}: k={k:g} es mayor que n={n:g}. No puede haber más conversiones "
            f"que visitas; probablemente k y n están al revés.")


def wilson(k, n, confianza=CONFIANZA):
    """Intervalo de Wilson: se porta bien con n pequeña y con tasas cerca de 0 o 1."""
    z = NormalDist().inv_cdf(1 - (1 - confianza) / 2)
    p = k / n
    denom = 1 + z ** 2 / n
    centro = (p + z ** 2 / (2 * n)) / denom
    semi = (z / denom) * math.sqrt(p * (1 - p) / n + z ** 2 / (4 * n ** 2))
    return max(0.0, centro - semi), min(1.0, centro + semi)


def prueba_vs_umbral(k, n, p0):
    """z y p (dos colas) de la tasa observada contra un umbral fijo."""
    if not 0 < p0 < 1:
        return None
    p = k / n
    se = math.sqrt(p0 * (1 - p0) / n)
    if se == 0:
        return None
    z = (p - p0) / se
    return {"z": round(z, 4),
            "p_valor": round(2 * (1 - NormalDist().cdf(abs(z))), 6)}


def prueba_dos_proporciones(k1, n1, k2, n2):
    """z y p (dos colas) entre la variante y el control, con varianza agrupada."""
    p1, p2 = k1 / n1, k2 / n2
    p_pool = (k1 + k2) / (n1 + n2)
    se = math.sqrt(p_pool * (1 - p_pool) * (1 / n1 + 1 / n2))
    if se == 0:
        return None
    z = (p1 - p2) / se
    return {
        "z": round(z, 4),
        "p_valor": round(2 * (1 - NormalDist().cdf(abs(z))), 6),
        "diferencia_pp": round((p1 - p2) * 100, 2),
        "lift_relativo": round(p1 / p2 - 1, 4) if p2 > 0 else None,
    }


def n_para_concluir(k, n, p0, confianza=CONFIANZA):
    """Cuántos intentos harían falta si la tasa observada se mantuviera."""
    p = k / n
    if p0 is None or p == p0:
        return None
    z = NormalDist().inv_cdf(1 - (1 - confianza) / 2)
    necesario = z ** 2 * p * (1 - p) / ((p - p0) ** 2)
    return math.ceil(necesario)


def n_requerido_ab(p_control, mde, confianza=CONFIANZA, poder=PODER):
    """Muestra POR brazo para detectar una diferencia `mde` frente al control."""
    if not 0 < p_control < 1 or mde == 0:
        return None
    p2 = min(max(p_control + mde, 0.0001), 0.9999)
    dist = NormalDist()
    z_a = dist.inv_cdf(1 - (1 - confianza) / 2)
    z_b = dist.inv_cdf(poder)
    n = (z_a + z_b) ** 2 * (p_control * (1 - p_control) + p2 * (1 - p2)) / ((p_control - p2) ** 2)
    return math.ceil(n)


def _pct(x, dec=1):
    return "[no disponible]" if x is None else f"{x * 100:.{dec}f}%"


def analizar_variante(v, alpha_efectivo, confianza=CONFIANZA):
    nombre = v.get("nombre") or "Variante"
    k, n = v.get("k"), v.get("n")
    _validar_kn(k, n, f"«{nombre}»")
    p = k / n
    bajo, alto = wilson(k, n, confianza)

    umbral = v.get("umbral")
    if umbral is not None:
        _exigir(isinstance(umbral, (int, float)) and not isinstance(umbral, bool)
                and 0 < umbral < 1,
                f"«{nombre}».umbral = {umbral} debe ser una proporción entre 0 y 1 "
                f"(0.06 es 6%, no 6)")

    control = v.get("control")
    if control is not None:
        _exigir(isinstance(control, dict), f"«{nombre}».control debe ser un objeto {{k, n}}")
        _validar_kn(control.get("k"), control.get("n"), f"«{nombre}» (control)")

    resultado = {
        "nombre": nombre,
        "k": k, "n": n,
        "tasa": round(p, 6),
        "ic_95": [round(bajo, 6), round(alto, 6)],
        "margen_error_pp": round((alto - bajo) / 2 * 100, 2),
        "umbral": umbral,
        "vs_umbral": prueba_vs_umbral(k, n, umbral) if umbral is not None else None,
        "control": None,
        "vs_control": None,
        "n_para_concluir": None,
        "alpha_efectivo": alpha_efectivo,
    }

    if control is not None:
        ck, cn = control["k"], control["n"]
        c_bajo, c_alto = wilson(ck, cn, confianza)
        resultado["control"] = {
            "k": ck, "n": cn, "tasa": round(ck / cn, 6),
            "ic_95": [round(c_bajo, 6), round(c_alto, 6)],
        }
        resultado["vs_control"] = prueba_dos_proporciones(k, n, ck, cn)

    # Veredicto: se decide con el intervalo, no con el punto. Un 8.8% observado
    # contra un umbral del 6% no dice nada si el intervalo va del 4% al 14%.
    referencia = None
    if control is not None:
        referencia = ("control", control["k"] / control["n"], resultado["vs_control"])
    elif umbral is not None:
        referencia = ("umbral", umbral, resultado["vs_umbral"])

    if referencia is None:
        resultado["veredicto"] = "pivotear"
        resultado["veredicto_lectura"] = (
            "Sin umbral ni control no hay contra qué comparar: la tasa se puede describir, "
            "no juzgar.")
    else:
        tipo, valor, prueba = referencia
        significativo = bool(prueba and prueba["p_valor"] < alpha_efectivo)
        if bajo > valor and significativo:
            resultado["veredicto"] = "perseverar"
            resultado["veredicto_lectura"] = (
                f"El intervalo completo queda por encima del {tipo} "
                f"({_pct(valor)}) y la diferencia es significativa "
                f"(p = {prueba['p_valor']:.4f} < {alpha_efectivo:.4f}).")
        elif alto < valor and significativo:
            resultado["veredicto"] = "descartar"
            resultado["veredicto_lectura"] = (
                f"El intervalo completo queda por debajo del {tipo} "
                f"({_pct(valor)}) y la diferencia es significativa "
                f"(p = {prueba['p_valor']:.4f}). No es falta de datos: es un resultado.")
        else:
            resultado["veredicto"] = "pivotear"
            faltan = n_para_concluir(k, n, valor, confianza)
            resultado["n_para_concluir"] = faltan
            extra = ""
            if faltan and faltan > n:
                extra = (f" Si la tasa observada se mantiene, harían falta ~{faltan} "
                         f"intentos en total ({faltan - int(n)} más) para separarla del "
                         f"{tipo}.")
            resultado["veredicto_lectura"] = (
                f"El intervalo ({_pct(bajo)} a {_pct(alto)}) toca el {tipo} "
                f"({_pct(valor)}): con estos datos no se puede afirmar ni descartar."
                + extra)
    return resultado


def calcular(datos):
    variantes = datos.get("variantes")
    _exigir(isinstance(variantes, list) and variantes,
            "`variantes` debe ser una lista con al menos una variante {nombre, k, n}")
    confianza = datos.get("confianza", CONFIANZA)
    _exigir(isinstance(confianza, (int, float)) and 0.5 < confianza < 1,
            "`confianza` debe estar entre 0.5 y 1 (0.95 por omisión)")
    alpha = 1 - confianza

    # Comparaciones múltiples: con m variantes, exigir alpha/m a cada una (Bonferroni).
    m = len(variantes)
    alpha_efectivo = alpha / m if m > 1 else alpha

    analizadas = [analizar_variante(v, alpha_efectivo, confianza) for v in variantes]

    resultado = {
        "script": "analizar_resultados.py",
        "experimento": datos.get("experimento") or "[no disponible]",
        "metrica": datos.get("metrica") or "conversión",
        "formulas": FORMULAS,
        "parametros": {
            "confianza": confianza,
            "alpha": round(alpha, 6),
            "comparaciones": m,
            "alpha_efectivo": round(alpha_efectivo, 6),
            "correccion": "Bonferroni" if m > 1 else "ninguna (una sola comparación)",
            "poder_para_n_requerido": PODER,
        },
        "resultados": {"variantes": analizadas},
    }
    ganadora = max(analizadas, key=lambda v: v["tasa"])
    resultado["resultados"]["mejor_tasa"] = {
        "nombre": ganadora["nombre"], "tasa": ganadora["tasa"],
        "veredicto": ganadora["veredicto"],
    }
    resultado["explicacion"] = _explicacion(resultado)
    resultado["advertencias"] = _advertencias(resultado)
    resultado["tabla"] = _tabla(resultado)
    resultado["grafica"] = _grafica(resultado)
    return resultado


def _explicacion(r):
    v = r["resultados"]["variantes"][0]
    met = r["metrica"]
    exp = [
        {
            "valor": f"tasa de {met}",
            "formula_libro": FORMULAS["tasa"]["libro"],
            "formula_palabras": FORMULAS["tasa"]["palabras"],
            "lectura": (f"«{v['nombre']}»: {v['k']:g} de {v['n']:g} = {_pct(v['tasa'])}."),
        },
        {
            "valor": "intervalo de confianza del 95%",
            "formula_libro": FORMULAS["wilson"]["libro"],
            "formula_palabras": FORMULAS["wilson"]["palabras"],
            "lectura": (
                f"De {_pct(v['ic_95'][0])} a {_pct(v['ic_95'][1])} "
                f"(± {v['margen_error_pp']} puntos porcentuales). La decisión se toma con "
                f"este rango, no con el {_pct(v['tasa'])} de arriba."
            ),
        },
    ]
    if v["vs_umbral"]:
        exp.append({
            "valor": "prueba contra el umbral",
            "formula_libro": FORMULAS["vs_umbral"]["libro"],
            "formula_palabras": FORMULAS["vs_umbral"]["palabras"],
            "lectura": (
                f"p = {v['vs_umbral']['p_valor']:.4f} contra un umbral de "
                f"{_pct(v['umbral'])}: hay un "
                f"{v['vs_umbral']['p_valor'] * 100:.2f}% de probabilidad de ver una "
                f"diferencia así por azar si la tasa real fuera exactamente el umbral."
            ),
        })
    if v["vs_control"]:
        exp.append({
            "valor": "prueba contra el control",
            "formula_libro": FORMULAS["vs_control"]["libro"],
            "formula_palabras": FORMULAS["vs_control"]["palabras"],
            "lectura": (
                f"{v['vs_control']['diferencia_pp']} puntos porcentuales de diferencia "
                f"({_pct(v['vs_control']['lift_relativo'])} relativo), "
                f"p = {v['vs_control']['p_valor']:.4f}."
            ),
        })
    if v["n_para_concluir"]:
        exp.append({
            "valor": "n para concluir",
            "formula_libro": FORMULAS["n_para_concluir"]["libro"],
            "formula_palabras": FORMULAS["n_para_concluir"]["palabras"],
            "lectura": (
                f"~{v['n_para_concluir']} intentos en total, si la tasa observada se "
                f"mantiene. No garantiza que salga a favor: garantiza que se podrá decidir."
            ),
        })
    if r["parametros"]["comparaciones"] > 1:
        exp.append({
            "valor": "corrección por comparaciones múltiples",
            "formula_libro": FORMULAS["bonferroni"]["libro"],
            "formula_palabras": FORMULAS["bonferroni"]["palabras"],
            "lectura": (
                f"{r['parametros']['comparaciones']} variantes, así que se exige "
                f"p < {r['parametros']['alpha_efectivo']:.4f} en vez de "
                f"p < {r['parametros']['alpha']:.4f}."
            ),
        })
    return exp


def _advertencias(r):
    adv = []
    sin_control = [v["nombre"] for v in r["resultados"]["variantes"] if not v["control"]]
    if sin_control:
        adv.append(
            "Sin grupo control medido en el mismo experimento, la comparación es contra un "
            "umbral externo (objetivo declarado o referencia de industria), que se midió en "
            "otro mercado, otro momento y otra gente. La lectura es exploratoria: sirve para "
            "decidir el siguiente paso, no para atribuir el resultado al cambio. "
            f"Afecta a: {', '.join(sin_control)}.")
    for v in r["resultados"]["variantes"]:
        if v["n"] < N_MINIMO_FIABLE:
            adv.append(
                f"«{v['nombre']}»: n = {v['n']:g}, por debajo de {N_MINIMO_FIABLE}. El "
                f"intervalo de Wilson aguanta mejor que otros con muestras chicas, pero el "
                f"resultado es orientativo: un caso más o menos mueve la tasa varios puntos.")
        if v["k"] < EXITOS_MINIMOS_FIABLES:
            adv.append(
                f"«{v['nombre']}»: solo {v['k']:g} éxito(s). Con tan pocos casos la tasa es "
                f"inestable por construcción, sea cual sea el n.")
        if v["k"] == 0:
            adv.append(
                f"«{v['nombre']}»: 0 éxitos. El intervalo llega hasta "
                f"{_pct(v['ic_95'][1])}, así que «no funcionó» todavía no está probado: "
                f"está sin medir.")
        elif v["k"] == v["n"]:
            adv.append(
                f"«{v['nombre']}»: todos los intentos fueron éxito. Suele indicar que se "
                f"midió a gente ya convencida (muestra de conveniencia), no que la tasa "
                f"real sea del 100%.")
        if v["margen_error_pp"] > 10:
            adv.append(
                f"«{v['nombre']}»: el margen de error es de ± {v['margen_error_pp']} puntos. "
                f"Con esa amplitud, la tasa observada casi no restringe el valor real.")
    if r["parametros"]["comparaciones"] > 1:
        adv.append(
            f"{r['parametros']['comparaciones']} variantes comparadas a la vez: se aplicó "
            f"Bonferroni (alpha = {r['parametros']['alpha_efectivo']:.4f}). Sin corregir, "
            f"con varias variantes alguna sale «ganadora» por azar más o menos una vez de "
            f"cada veinte.")
    adv.append(
        "La significancia estadística no es relevancia de negocio: una diferencia real de "
        "0.3 puntos puede ser significativa con mucho tráfico y no cambiar ninguna decisión.")
    return adv


def _tabla(r):
    filas = []
    for v in r["resultados"]["variantes"]:
        filas.append([
            v["nombre"],
            f"{v['k']:g}/{v['n']:g}",
            _pct(v["tasa"]),
            f"{_pct(v['ic_95'][0])} a {_pct(v['ic_95'][1])}",
            _pct(v["umbral"]) if v["umbral"] is not None else "—",
            (f"{v['control']['tasa'] * 100:.1f}%" if v["control"] else "sin control"),
            (f"{v['vs_control']['p_valor']:.4f}" if v["vs_control"]
             else (f"{v['vs_umbral']['p_valor']:.4f}" if v["vs_umbral"] else "—")),
            v["veredicto"],
        ])
    return {
        "titulo": f"Resultado del experimento — {r['experimento']}",
        "columnas": ["Variante", "Éxitos / intentos", f"Tasa de {r['metrica']}",
                     "IC 95%", "Umbral", "Control", "p", "Veredicto"],
        "filas": filas,
        "nota": (
            f"El veredicto se decide con el intervalo, no con la tasa puntual. "
            f"Se exige p < {r['parametros']['alpha_efectivo']:.4f} "
            f"({r['parametros']['correccion']})."
        ),
    }


def _grafica(r):
    vs = r["resultados"]["variantes"]
    datasets = [{"label": f"Tasa de {r['metrica']} (%)",
                 "data": [round(v["tasa"] * 100, 2) for v in vs]},
                {"label": "Límite inferior del IC 95% (%)",
                 "data": [round(v["ic_95"][0] * 100, 2) for v in vs]},
                {"label": "Límite superior del IC 95% (%)",
                 "data": [round(v["ic_95"][1] * 100, 2) for v in vs]}]
    if any(v["umbral"] is not None for v in vs):
        datasets.append({
            "label": "Umbral (%)",
            "data": [round((v["umbral"] or 0) * 100, 2) for v in vs]})
    return {
        "tipo": "bar",
        "titulo": f"Tasa observada con su intervalo de confianza — {r['experimento']}",
        "eje_x": "Variante", "eje_y": "%",
        "labels": [v["nombre"] for v in vs],
        "datasets": datasets,
    }


def seccion_reporte(r):
    """Sección de REPORT_DATA lista para pegar en el `reporte.json` del paso."""
    peor = min(r["resultados"]["variantes"],
               key=lambda v: {"descartar": 0, "pivotear": 1, "perseverar": 2}[v["veredicto"]])
    items = [{
        "titulo": f"Resultado — {r['experimento']}",
        "subtitulo": (
            f"{r['resultados']['mejor_tasa']['nombre']}: "
            f"{_pct(r['resultados']['mejor_tasa']['tasa'])} de {r['metrica']} · "
            f"veredicto {peor['veredicto']}"
        ),
        "tags": ["validación", r["metrica"]],
        "veredicto": peor["veredicto"],
        "body": [{"label": e["valor"],
                  "texto": f"{e['lectura']}\n\nCómo se calcula: {e['formula_palabras']}\n"
                           f"Fórmula: {e['formula_libro']}"}
                 for e in r["explicacion"]]
                + [{"label": "Lectura del veredicto", "texto": v["veredicto_lectura"]}
                   for v in r["resultados"]["variantes"]],
        "tabla": r["tabla"],
        "chart": r["grafica"],
    }]
    return {"titulo": "Resultado del experimento", "items": items}


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Analiza el resultado de un experimento: tasa, IC de Wilson, "
                    "prueba contra umbral o control, veredicto y n para concluir.")
    ap.add_argument("--datos", help="JSON con varias variantes (ver docstring)")
    ap.add_argument("--k", type=float, help="Éxitos observados")
    ap.add_argument("--n", type=float, help="Intentos observados")
    ap.add_argument("--umbral", type=float,
                    help="Umbral declarado de la Testing Card (0.06 = 6%%)")
    ap.add_argument("--control-k", type=float, help="Éxitos del grupo control")
    ap.add_argument("--control-n", type=float, help="Intentos del grupo control")
    ap.add_argument("--nombre", default="Variante", help="Nombre de la variante")
    ap.add_argument("--experimento", default="Experimento de validación")
    ap.add_argument("--metrica", default="conversión")
    ap.add_argument("--confianza", type=float, default=CONFIANZA)
    ap.add_argument("--poder", type=float, default=PODER,
                    help="Poder estadístico para --n-requerido (0.80 por omisión)")
    ap.add_argument("--n-requerido", nargs=2, type=float,
                    metavar=("TASA_BASE", "DIFERENCIA"),
                    help="No analiza nada: dice la muestra POR BRAZO que hace falta para "
                         "detectar DIFERENCIA sobre TASA_BASE (0.03 0.03 = detectar 3 "
                         "puntos sobre un 3%%). Úsalo al diseñar la Testing Card.")
    ap.add_argument("-o", "--output", default="resultado_experimento.json")
    ap.add_argument("--seccion-reporte",
                    help="Escribe además la sección lista para REPORT_DATA")
    args = ap.parse_args(argv)

    if args.n_requerido:
        base, mde = args.n_requerido
        if not 0 < base < 1:
            print(f"La tasa base ({base}) debe ser una proporción entre 0 y 1 "
                  f"(0.03 es 3%, no 3)", file=sys.stderr)
            return 2
        if mde == 0:
            print("La diferencia a detectar no puede ser 0: sin diferencia objetivo no "
                  "hay muestra que la detecte.", file=sys.stderr)
            return 2
        n = n_requerido_ab(base, mde, args.confianza, args.poder)
        if n is None:
            print("No se puede calcular con esos valores (la tasa objetivo sale fuera "
                  "del rango 0-1).", file=sys.stderr)
            return 2
        print(f"{n} por brazo ({2 * n} en total) para detectar {mde * 100:.2f} puntos "
              f"porcentuales sobre una base del {base * 100:.2f}%, "
              f"con {args.confianza * 100:.0f}% de confianza y {args.poder * 100:.0f}% "
              f"de poder.")
        print("\nFórmula: n = (z_alfa/2 + z_beta)² · (p₁(1−p₁) + p₂(1−p₂)) / (p₁−p₂)²")
        print("En palabras: cuanto más pequeña sea la diferencia que se quiere detectar, "
              "más muestra hace falta, y crece con el cuadrado: detectar la mitad de "
              "diferencia cuesta cuatro veces más tráfico.")
        return 0

    if args.datos:
        try:
            datos = json.loads(open(args.datos, encoding="utf-8").read())
        except FileNotFoundError:
            print(f"Error: no encuentro {args.datos}", file=sys.stderr)
            return 1
        except json.JSONDecodeError as exc:
            print(f"Error: {args.datos} no es JSON válido — {exc}", file=sys.stderr)
            return 1
    else:
        if args.k is None or args.n is None:
            ap.error("hacen falta --k y --n (o --datos con varias variantes)")
        variante = {"nombre": args.nombre, "k": args.k, "n": args.n}
        if args.umbral is not None:
            variante["umbral"] = args.umbral
        if args.control_k is not None or args.control_n is not None:
            if args.control_k is None or args.control_n is None:
                ap.error("el control necesita --control-k y --control-n")
            variante["control"] = {"k": args.control_k, "n": args.control_n}
        datos = {"experimento": args.experimento, "metrica": args.metrica,
                 "confianza": args.confianza, "variantes": [variante]}

    try:
        r = calcular(datos)
    except EntradaInvalida as exc:
        print(f"Entrada inválida: {exc}", file=sys.stderr)
        return 2

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(r, f, ensure_ascii=False, indent=2)
    if args.seccion_reporte:
        with open(args.seccion_reporte, "w", encoding="utf-8") as f:
            json.dump(seccion_reporte(r), f, ensure_ascii=False, indent=2)

    for v in r["resultados"]["variantes"]:
        print(f"{v['nombre']}: {v['k']:g}/{v['n']:g} = {_pct(v['tasa'])} "
              f"(IC 95% {_pct(v['ic_95'][0])} a {_pct(v['ic_95'][1])}) "
              f"→ {v['veredicto'].upper()}")
        print(f"   {v['veredicto_lectura']}")
    for a in r["advertencias"]:
        print(f"\n[AVISO] {a}")
    print(f"\nAnálisis guardado en: {args.output}")
    if args.seccion_reporte:
        print(f"Sección para el reporte en: {args.seccion_reporte}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
