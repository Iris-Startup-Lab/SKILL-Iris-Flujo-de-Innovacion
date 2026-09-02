"""
calcular_score.py

Score de atractivo /25 del Dimensionador Estratégico: suma los cinco criterios,
aplica los umbrales de veredicto y **exige una justificación por criterio**.

Por qué existe: el score lo sumaba el LLM y su desglose se quedaba en la
conversación. En el uso real salió la queja «no me quedó claro de dónde sacó los
datos que estoy marcando (urgencia, diferenciación, escalabilidad…)»: la tarjeta
mostraba 21/25 y el porqué no viajaba al HTML. Aquí el LLM aporta el juicio —los
cinco puntajes y su razón— y el script hace lo determinista: valida, suma, decide,
ordena por score y **entrega el bloque de reporte con la matriz ya armada**, así
que no se puede olvidar de incluirla.

Criterios (los cinco del Módulo 9, cada uno 1-5):
    urgencia · diferenciacion · escalabilidad · velocidad · fit

Umbrales:
    20-25 → PROTOTIPAR                       (veredicto del reporte: perseverar)
    13-19 → VALIDAR MÁS ANTES DE PROTOTIPAR  (pivotear)
     ≤12  → DESCARTAR / REPLANTEAR           (descartar)

Uso:
    python calcular_score.py --plantilla > ideas.json     # esqueleto de entrada
    python calcular_score.py --datos ideas.json [-o score.json]
    python calcular_score.py --datos ideas.json --seccion-reporte seccion.json

Códigos de salida: 0 ok · 1 error de archivo/uso · 2 entrada inválida
(falta un criterio, puntaje fuera de rango o justificación ausente).
"""
import argparse
import json
import sys

# Los cinco criterios del Módulo 9, en el orden en que se presentan.
CRITERIOS = [
    ("urgencia", "Urgencia del problema", "¿El cliente lo sufre hoy y pagaría mañana?"),
    ("diferenciacion", "Diferenciación", "¿Hay algo difícil de copiar?"),
    ("escalabilidad", "Escalabilidad", "¿Puede crecer sin que los costos crezcan igual?"),
    ("velocidad", "Velocidad al mercado", "¿MVP funcional en menos de 90 días?"),
    ("fit", "Fit estratégico", "¿Tiene sentido en el portafolio del equipo?"),
]
CLAVES = [c[0] for c in CRITERIOS]
ETIQUETAS = {c[0]: c[1] for c in CRITERIOS}
PREGUNTAS = {c[0]: c[2] for c in CRITERIOS}

MAXIMO = len(CRITERIOS) * 5          # 25

# Longitud mínima de una justificación. No mide calidad —eso no lo puede medir un
# script—, pero corta el «ok», el «alto» y el «5/5» que dejan el criterio sin
# explicar. Es el mismo espíritu que la regla de integridad: si no hay razón, se
# dice, no se rellena.
MIN_JUSTIFICACION = 25

UMBRALES = [
    (20, "PROTOTIPAR", "perseverar"),
    (13, "VALIDAR MÁS ANTES DE PROTOTIPAR", "pivotear"),
    (0, "DESCARTAR / REPLANTEAR", "descartar"),
]

# Las dos versiones de cada fórmula: la de libro y la de palabras. La segunda no es
# decoración: el flujo lo usan personas que no vienen de análisis, y un número sin
# lectura es un número que se cree o se ignora, pero no se discute.
FORMULAS = {
    "score": {
        "libro": "score = Σ criterio_i , con criterio_i ∈ [1,5] , i = 1..5",
        "palabras": "Se suman los cinco puntajes de 1 a 5, así que el total va de 5 a 25.",
    },
    "veredicto": {
        "libro": "veredicto = PROTOTIPAR si score ≥ 20 · VALIDAR si 13 ≤ score ≤ 19 · "
                 "DESCARTAR si score ≤ 12",
        "palabras": "Los umbrales están fijos de antemano, antes de ver los puntajes: "
                    "así el corte no se mueve para que una idea favorita pase.",
    },
    "brecha": {
        "libro": "brecha = 20 − score",
        "palabras": "Cuántos puntos le faltan a la idea para llegar a prototipado. "
                    "Dice qué tan lejos quedó, no solo que no llegó.",
    },
}


class EntradaInvalida(Exception):
    """La entrada no permite calcular: falta un criterio o una justificación."""


def _texto(v):
    return isinstance(v, str) and v.strip() != ""


def plantilla():
    """Esqueleto de entrada, para que el LLM sepa exactamente qué rellenar."""
    return {
        "proyecto": "Nombre del proyecto",
        "objetivo_estrategico": (
            "Incrementar mercado | Incrementar CLV | Otro (del Paso 0A del AGENTE.md). "
            "Ajusta la narrativa, no la escala."
        ),
        "ideas": [
            {
                "numero": 1,
                "nombre": "Nombre de la idea tal como salió del paso de ideación",
                "criterios": {
                    clave: {
                        "puntaje": 3,
                        "justificacion": f"Por qué ese puntaje. {PREGUNTAS[clave]}",
                    }
                    for clave in CLAVES
                },
            }
        ],
    }


def _validar_idea(idea, pos):
    """Devuelve (numero, nombre, criterios) o levanta EntradaInvalida."""
    if not isinstance(idea, dict):
        raise EntradaInvalida(f"ideas[{pos}] no es un objeto")
    nombre = idea.get("nombre")
    if not _texto(nombre):
        raise EntradaInvalida(f"ideas[{pos}].nombre está vacío")
    crit = idea.get("criterios")
    if not isinstance(crit, dict):
        raise EntradaInvalida(f"ideas[{pos}] «{nombre}» no trae el objeto `criterios`")

    faltan = [c for c in CLAVES if c not in crit]
    if faltan:
        raise EntradaInvalida(
            f"«{nombre}»: faltan los criterios {', '.join(faltan)}. "
            f"El score es /25 porque son los cinco; con cuatro no es comparable "
            f"con las demás ideas."
        )
    sobran = [c for c in crit if c not in CLAVES]
    if sobran:
        raise EntradaInvalida(
            f"«{nombre}»: criterios que no son del Módulo 9: {', '.join(sobran)}. "
            f"Los cinco son {', '.join(CLAVES)}; añadir otros rompe la escala /25."
        )

    limpio = {}
    for clave in CLAVES:
        c = crit[clave]
        if not isinstance(c, dict):
            raise EntradaInvalida(
                f"«{nombre}».{clave} debe ser un objeto "
                f"{{puntaje, justificacion}}, no un número suelto: el puntaje sin "
                f"su razón es justo lo que esta skill dejó de aceptar."
            )
        p = c.get("puntaje")
        if isinstance(p, bool) or not isinstance(p, (int, float)):
            raise EntradaInvalida(f"«{nombre}».{clave}.puntaje debe ser un número 1-5")
        if not 1 <= p <= 5:
            raise EntradaInvalida(
                f"«{nombre}».{clave}.puntaje = {p} está fuera del rango 1-5"
            )
        j = c.get("justificacion")
        if not _texto(j):
            raise EntradaInvalida(
                f"«{nombre}».{clave} no trae justificación. {PREGUNTAS[clave]} "
                f"Sin respuesta, el puntaje no es evaluable por quien lea el reporte."
            )
        if len(j.strip()) < MIN_JUSTIFICACION:
            raise EntradaInvalida(
                f"«{nombre}».{clave}: la justificación «{j.strip()}» tiene "
                f"{len(j.strip())} caracteres y el mínimo son {MIN_JUSTIFICACION}. "
                f"Di en una frase por qué ese puntaje y con qué evidencia."
            )
        limpio[clave] = {"puntaje": p, "justificacion": j.strip()}
    return idea.get("numero"), nombre.strip(), limpio


def _veredicto(score):
    for corte, etiqueta, mapeado in UMBRALES:
        if score >= corte:
            return etiqueta, mapeado
    return UMBRALES[-1][1], UMBRALES[-1][2]


def calcular(datos):
    ideas_in = datos.get("ideas")
    if not isinstance(ideas_in, list) or not ideas_in:
        raise EntradaInvalida("`ideas` debe ser una lista con al menos una idea")

    calculadas = []
    for pos, idea in enumerate(ideas_in):
        numero, nombre, crit = _validar_idea(idea, pos)
        score = sum(crit[c]["puntaje"] for c in CLAVES)
        etiqueta, mapeado = _veredicto(score)
        # El criterio más flojo es la palanca concreta: dice qué hay que mejorar
        # para que la idea suba, en vez de dejar el «no llegó» sin salida.
        peor = min(CLAVES, key=lambda c: crit[c]["puntaje"])
        mejor = max(CLAVES, key=lambda c: crit[c]["puntaje"])
        calculadas.append({
            "numero_original": numero if numero is not None else pos + 1,
            "nombre": nombre,
            "score": score,
            "maximo": MAXIMO,
            "veredicto_dimensionador": etiqueta,
            "veredicto_reporte": mapeado,
            "brecha_a_prototipar": max(0, UMBRALES[0][0] - score),
            "criterio_mas_fuerte": ETIQUETAS[mejor],
            "criterio_mas_debil": ETIQUETAS[peor],
            "criterios": crit,
        })

    # Fricción 8 del uso real: las ideas salían en el HTML como 1, 2, 3, 7, 4, 6, 11…
    # —una mezcla del número del paso de ideación con el orden por score— y parecía
    # desorden en vez de priorización. El orden de presentación se decide aquí:
    # score descendente, y el número original viaja como dato, no como posición.
    orden = sorted(calculadas, key=lambda x: (-x["score"], x["numero_original"]))
    for i, idea in enumerate(orden, 1):
        idea["posicion"] = i

    return {
        "script": "calcular_score.py",
        "proyecto": datos.get("proyecto"),
        "objetivo_estrategico": datos.get("objetivo_estrategico"),
        "formulas": FORMULAS,
        "parametros": {
            "criterios": CLAVES,
            "maximo": MAXIMO,
            "umbrales": {
                "PROTOTIPAR": ">= 20",
                "VALIDAR MÁS ANTES DE PROTOTIPAR": "13 a 19",
                "DESCARTAR / REPLANTEAR": "<= 12",
            },
            "minimo_caracteres_justificacion": MIN_JUSTIFICACION,
        },
        "resultados": {
            "ideas": orden,
            "conteo_por_veredicto": {
                etiqueta: sum(1 for x in orden if x["veredicto_dimensionador"] == etiqueta)
                for _, etiqueta, _ in UMBRALES
            },
            "score_promedio": round(sum(x["score"] for x in orden) / len(orden), 2),
        },
        "explicacion": _explicacion(orden),
        "advertencias": _advertencias(orden),
        "tabla_resumen": _tabla_resumen(orden),
        "grafica": _grafica(orden),
    }


def _explicacion(orden):
    """Lectura en palabras de cada número que emite el script."""
    lider = orden[0]
    return [
        {
            "valor": "score /25",
            "formula_libro": FORMULAS["score"]["libro"],
            "formula_palabras": FORMULAS["score"]["palabras"],
            "lectura": (
                f"«{lider['nombre']}» suma {lider['score']} de {MAXIMO}. No es un "
                f"porcentaje de éxito ni una probabilidad: es la suma de cinco juicios "
                f"declarados, y sirve para ordenar ideas entre sí, no para prometer "
                f"resultados."
            ),
        },
        {
            "valor": "veredicto",
            "formula_libro": FORMULAS["veredicto"]["libro"],
            "formula_palabras": FORMULAS["veredicto"]["palabras"],
            "lectura": (
                f"«{lider['nombre']}» queda en {lider['veredicto_dimensionador']}. "
                f"El corte no se decide después de ver los números."
            ),
        },
        {
            "valor": "brecha a prototipar",
            "formula_libro": FORMULAS["brecha"]["libro"],
            "formula_palabras": FORMULAS["brecha"]["palabras"],
            "lectura": (
                "Una idea a 2 puntos del corte no es lo mismo que una a 10: la primera "
                "puede subir mejorando un criterio; la segunda tiene un problema de "
                "fondo."
            ),
        },
    ]


def _advertencias(orden):
    """Lo que el score no dice, dicho antes de que alguien lo dé por dicho."""
    adv = [
        "Los cinco puntajes son juicio declarado del analista, no una medición: el "
        "script suma y aplica los umbrales, no evalúa la idea. La justificación de "
        "cada criterio es la evidencia que sostiene el número.",
    ]
    empates = {}
    for idea in orden:
        empates.setdefault(idea["score"], []).append(idea["nombre"])
    repetidos = {s: n for s, n in empates.items() if len(n) > 1}
    if repetidos:
        detalle = "; ".join(
            f"{s}/25: {', '.join(nombres)}" for s, nombres in sorted(repetidos.items(), reverse=True)
        )
        adv.append(
            f"Hay empates de score ({detalle}). El orden entre ideas empatadas no "
            f"significa nada: para desempatar hace falta un criterio explícito "
            f"(por ejemplo CLV:CAC del modelo, o velocidad al mercado)."
        )
    if len(orden) > 1:
        rango = orden[0]["score"] - orden[-1]["score"]
        if rango <= 3:
            adv.append(
                f"Los scores están a {rango} punto(s) unos de otros: la escala no está "
                f"separando las ideas. O los criterios no discriminan en este conjunto, "
                f"o los puntajes se están asignando por defecto en la parte media."
            )
    limite = [x["nombre"] for x in orden if x["score"] in (12, 13, 19, 20)]
    if limite:
        adv.append(
            f"En el borde de un umbral: {', '.join(limite)}. Un punto de diferencia en "
            f"un solo criterio les cambia el veredicto, así que conviene revisar esa "
            f"justificación antes de decidir."
        )
    return adv


def _tabla_resumen(orden):
    """Tabla resumen lista para el bloque `tabla` del reporte y para el chat."""
    filas = [
        [
            str(x["posicion"]),
            f"#{x['numero_original']} {x['nombre']}",
            f"{x['score']}/{MAXIMO}",
            *[str(x["criterios"][c]["puntaje"]) for c in CLAVES],
            x["veredicto_dimensionador"],
        ]
        for x in orden
    ]
    return {
        "titulo": f"Score de atractivo por idea — {len(orden)} idea(s), ordenadas por score",
        "columnas": ["#", "Idea", "Score", "Urg.", "Dif.", "Esc.", "Vel.", "Fit",
                     "Veredicto"],
        "filas": filas,
        "nota": (
            "El número que sigue a «#» dentro de la celda «Idea» es el de la idea en el "
            "paso de ideación; la primera columna es su posición por score. "
            "Urg. = urgencia · Dif. = diferenciación · Esc. = escalabilidad · "
            "Vel. = velocidad al mercado · Fit = fit estratégico. Cada puntaje va de 1 "
            "a 5 y su justificación está en la ficha de la idea."
        ),
    }


def _grafica(orden):
    """Chart.js listo para `item.chart`: score por idea, en orden de score."""
    return {
        "tipo": "horizontalBar",
        "titulo": "Score de atractivo por idea (de 5 a 25)",
        "eje_x": "Score /25",
        "eje_y": "Idea",
        "labels": [f"#{x['numero_original']} {x['nombre']}" for x in orden],
        "datasets": [{
            "label": "Score /25",
            "data": [x["score"] for x in orden],
        }],
    }


def seccion_reporte(resultado):
    """Sección de `REPORT_DATA` con la matriz de justificación ya armada.

    Es la pieza que cierra la fricción: la matriz criterio → puntaje →
    justificación no depende de que el agente se acuerde de escribirla, porque
    sale del mismo script que calculó el score.
    """
    ideas = resultado["resultados"]["ideas"]
    items = []
    for x in ideas:
        filas = [
            [ETIQUETAS[c], f"{x['criterios'][c]['puntaje']}/5",
             x["criterios"][c]["justificacion"]]
            for c in CLAVES
        ]
        filas.append(["TOTAL", f"{x['score']}/{MAXIMO}", x["veredicto_dimensionador"]])
        items.append({
            "titulo": x["nombre"],
            "subtitulo": (
                f"Posición {x['posicion']} por score · {x['score']}/{MAXIMO} · "
                f"{x['veredicto_dimensionador']}"
            ),
            "tags": ["score", f"idea {x['numero_original']}"],
            "score": x["score"],
            "veredicto": x["veredicto_reporte"],
            "body": [
                {"label": "Criterio más fuerte", "texto": x["criterio_mas_fuerte"]},
                {"label": "Criterio más débil",
                 "texto": (f"{x['criterio_mas_debil']} — es la palanca concreta para "
                           f"subir el score")},
            ] + ([] if x["brecha_a_prototipar"] == 0 else [
                {"label": "Brecha a prototipar",
                 "texto": (f"{x['brecha_a_prototipar']} punto(s) por debajo de 20, el "
                           f"umbral de PROTOTIPAR")},
            ]),
            "tabla": {
                "titulo": "Criterio → puntaje → justificación",
                "columnas": ["Criterio", "Puntaje", "Justificación"],
                "filas": filas,
                "fila_total": True,
            },
        })

    items.append({
        "titulo": "Tabla resumen — score por idea",
        "subtitulo": (
            f"{len(ideas)} idea(s) ordenadas por score · promedio "
            f"{resultado['resultados']['score_promedio']}/{MAXIMO}"
        ),
        "tags": ["resumen", "score"],
        "body": [{"label": "Cómo leer el score",
                  "texto": resultado["explicacion"][0]["lectura"]}],
        "tabla": resultado["tabla_resumen"],
        "chart": resultado["grafica"],
    })

    return {"titulo": "Score de atractivo y priorización", "items": items}


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Score de atractivo /25 con justificación obligatoria por criterio.")
    ap.add_argument("--datos", help="JSON de entrada con las ideas y sus criterios")
    ap.add_argument("--plantilla", action="store_true",
                    help="Imprime el esqueleto de entrada y termina")
    ap.add_argument("-o", "--output", default="score.json", help="Ruta de salida JSON")
    ap.add_argument("--seccion-reporte",
                    help="Escribe además la sección lista para REPORT_DATA")
    args = ap.parse_args(argv)

    if args.plantilla:
        print(json.dumps(plantilla(), ensure_ascii=False, indent=2))
        return 0
    if not args.datos:
        ap.error("hace falta --datos (o --plantilla para ver el esqueleto)")

    try:
        datos = json.loads(open(args.datos, encoding="utf-8").read())
    except FileNotFoundError:
        print(f"Error: no encuentro {args.datos}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"Error: {args.datos} no es JSON válido — {exc}", file=sys.stderr)
        return 1

    try:
        resultado = calcular(datos)
    except EntradaInvalida as exc:
        print(f"Entrada inválida: {exc}", file=sys.stderr)
        return 2

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    if args.seccion_reporte:
        with open(args.seccion_reporte, "w", encoding="utf-8") as f:
            json.dump(seccion_reporte(resultado), f, ensure_ascii=False, indent=2)

    for x in resultado["resultados"]["ideas"]:
        print(f"{x['posicion']:>2}. #{x['numero_original']} {x['nombre']}: "
              f"{x['score']}/{MAXIMO} → {x['veredicto_dimensionador']}")
    for a in resultado["advertencias"][1:]:
        print(f"\n[AVISO] {a}")
    print(f"\nCálculo guardado en: {args.output}")
    if args.seccion_reporte:
        print(f"Sección para el reporte en: {args.seccion_reporte}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
