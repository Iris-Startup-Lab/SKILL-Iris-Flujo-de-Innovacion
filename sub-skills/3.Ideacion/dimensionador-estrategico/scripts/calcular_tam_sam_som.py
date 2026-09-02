"""
calcular_tam_sam_som.py

Dimensionamiento de mercado del Módulo 1: TAM → SAM por reducciones top-down →
SOM por cuota objetivo, proyectado a 1, 3 y 5 años, con CAGR y contraste contra
el SAM bottom-up.

Por qué existe: era aritmética determinista sobre supuestos declarados y la hacía
el LLM a mano. En el uso real eso se notó («todos los datos fueron supuestos»):
cuando el número y el supuesto salen del mismo texto generado, no hay forma de
auditar cuál de los dos falló. Aquí el LLM aporta la base de mercado, sus fuentes
y los porcentajes de reducción; el script multiplica, proyecta y **contrasta el
top-down contra el bottom-up**, que es la comprobación que nadie hace a mano.

    TAM  = mercado base declarado (con su fuente)
    SAM  = TAM × Π reducciones            (geografía, vertical, canal…)
    SOM_n = SAM_n × cuota_objetivo_n       (SAM_n crece con el mercado)
    CAGR = (valor_final / valor_inicial)^(1/años) − 1

Uso:
    python calcular_tam_sam_som.py --plantilla > mercado.json
    python calcular_tam_sam_som.py --datos mercado.json [-o tam.json]
    python calcular_tam_sam_som.py --datos mercado.json --seccion-reporte seccion.json

Códigos de salida: 0 ok · 1 error de archivo/uso · 2 entrada inválida.
"""
import argparse
import json
import sys

HORIZONTE = 5                      # se proyecta 1..5; los hitos del módulo son 1, 3 y 5
HITOS = (1, 3, 5)

# Una cuota de mercado por encima de esto en el primer año casi siempre es un
# supuesto que nadie sostuvo: no bloquea, pero se dice.
CUOTA_AGRESIVA_ANIO_1 = 0.05
# Divergencia tolerada entre el SAM top-down y el bottom-up antes de avisar.
DIVERGENCIA_TOLERADA = 2.0

FORMULAS = {
    "TAM": {
        "libro": "TAM = tamaño total del mercado declarado, en la moneda y el año de la fuente",
        "palabras": "Todo el dinero que se gasta hoy en resolver este problema, en el mundo "
                    "o en el ámbito que declare la fuente. Es el techo, no la oportunidad.",
    },
    "SAM": {
        "libro": "SAM = TAM × Π (porcentaje_reduccion_i)",
        "palabras": "Del techo se recortan las partes a las que no se puede llegar —otro país, "
                    "otro segmento, otro canal— multiplicando un porcentaje por cada recorte. "
                    "Lo que queda es el mercado al que sí se le podría vender.",
    },
    "SOM": {
        "libro": "SOM_n = SAM_n × cuota_objetivo_n , con SAM_n = SAM × (1+g)^(n−1)",
        "palabras": "La parte del mercado accesible que se espera capturar en el año n. "
                    "El mercado también crece, así que el SAM del año 3 no es el de hoy.",
    },
    "CAGR": {
        "libro": "CAGR = (valor_final / valor_inicial)^(1/años) − 1",
        "palabras": "El crecimiento anual parejo que llevaría del primer valor al último. "
                    "Es un promedio suavizado: aplana los saltos, no los describe.",
    },
    "penetracion": {
        "libro": "penetracion_n = SOM_n / SAM_n",
        "palabras": "Qué porcentaje del mercado accesible representa la meta de ese año. "
                    "Es la forma honesta de leer el SOM: 50 millones suena distinto si es "
                    "el 0.5% del mercado o el 40%.",
    },
    "bottom_up": {
        "libro": "SAM_bottom_up = Σ (clientes_potenciales_bp × ticket_bp × frecuencia_bp)",
        "palabras": "El mismo mercado contado desde abajo: cuántos clientes hay, cuánto paga "
                    "cada uno y cuántas veces al año. Si no se parece al de arriba, uno de "
                    "los dos supuestos está mal.",
    },
}


class EntradaInvalida(Exception):
    pass


def _texto(v):
    return isinstance(v, str) and v.strip() != ""


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def plantilla():
    return {
        "moneda": "USD",
        "mercado_base": {
            "concepto": "Qué mide exactamente esta cifra",
            "valor": 12000000000,
            "anio": 2025,
            "fuente": "Fuente citable. Si es estimación propia, escribe la cifra con * "
                      "y dilo aquí.",
        },
        "reducciones": [
            {"concepto": "México (% del mercado global)", "porcentaje": 0.04,
             "fuente": "De dónde sale ese porcentaje"},
            {"concepto": "Segmento PyME B2B (% del mercado nacional)", "porcentaje": 0.35,
             "fuente": "De dónde sale ese porcentaje"},
        ],
        "crecimiento_mercado_anual": 0.08,
        "cuota_objetivo": {"anio_1": 0.005, "anio_3": 0.02, "anio_5": 0.05},
        "bottom_up": {
            "buyer_personas": [
                {"nombre": "Buyer persona 1", "clientes_potenciales": 12000,
                 "ticket_promedio": 4800, "frecuencia_anual": 1},
            ]
        },
    }


def _cuota_por_anio(cuota):
    """Interpola linealmente la cuota entre los hitos declarados (1, 3 y 5)."""
    if not isinstance(cuota, dict):
        raise EntradaInvalida(
            "`cuota_objetivo` debe ser un objeto con anio_1, anio_3 y anio_5")
    puntos = {}
    for anio in HITOS:
        v = cuota.get(f"anio_{anio}")
        if v is None:
            raise EntradaInvalida(
                f"falta `cuota_objetivo.anio_{anio}`: los tres hitos del módulo son "
                f"1, 3 y 5 años")
        if not _num(v) or not 0 < v <= 1:
            raise EntradaInvalida(
                f"`cuota_objetivo.anio_{anio}` = {v} debe ser una proporción entre 0 y 1 "
                f"(0.02 es 2%, no 2)")
        puntos[anio] = float(v)
    if not puntos[1] <= puntos[3] <= puntos[5]:
        raise EntradaInvalida(
            f"la cuota objetivo baja con el tiempo ({puntos[1]:.4f} → {puntos[3]:.4f} → "
            f"{puntos[5]:.4f}). Si es intencional (se cede mercado), dilo como supuesto "
            f"y usa tres valores crecientes o iguales; si no, revisa los números.")

    serie = {}
    for n in range(1, HORIZONTE + 1):
        if n in puntos:
            serie[n] = puntos[n]
        elif n < 3:
            serie[n] = puntos[1] + (puntos[3] - puntos[1]) * (n - 1) / 2
        else:
            serie[n] = puntos[3] + (puntos[5] - puntos[3]) * (n - 3) / 2
    return serie, puntos


def _cagr(inicial, final, anios):
    if inicial <= 0 or final <= 0 or anios <= 0:
        return None
    return (final / inicial) ** (1 / anios) - 1


def calcular(datos):
    base = datos.get("mercado_base")
    if not isinstance(base, dict) or not _num(base.get("valor")):
        raise EntradaInvalida(
            "`mercado_base.valor` es obligatorio y numérico: es el TAM, el punto de "
            "partida de todo el cálculo")
    if base["valor"] <= 0:
        raise EntradaInvalida(f"`mercado_base.valor` = {base['valor']} debe ser positivo")
    tam = float(base["valor"])

    reducciones = datos.get("reducciones") or []
    if not isinstance(reducciones, list):
        raise EntradaInvalida("`reducciones` debe ser una lista")

    factor = 1.0
    detalle_reducciones = []
    valor = tam
    for i, r in enumerate(reducciones):
        if not isinstance(r, dict):
            raise EntradaInvalida(f"reducciones[{i}] no es un objeto")
        p = r.get("porcentaje")
        if not _num(p) or not 0 < p <= 1:
            raise EntradaInvalida(
                f"reducciones[{i}].porcentaje = {p} debe ser una proporción entre 0 y 1 "
                f"(0.04 es 4%, no 4)")
        if not _texto(r.get("concepto")):
            raise EntradaInvalida(
                f"reducciones[{i}] no dice qué recorta. Un porcentaje sin concepto no se "
                f"puede auditar: escribe «México (% del global)», «Segmento PyME», etc.")
        factor *= float(p)
        valor *= float(p)
        detalle_reducciones.append({
            "concepto": r["concepto"],
            "porcentaje": float(p),
            "valor_resultante": round(valor, 2),
            "fuente": r.get("fuente") or "[no disponible]",
        })
    sam = tam * factor

    g = datos.get("crecimiento_mercado_anual", 0.0)
    if not _num(g):
        raise EntradaInvalida("`crecimiento_mercado_anual` debe ser numérico (0.08 = 8%)")
    if g <= -1:
        raise EntradaInvalida(
            f"`crecimiento_mercado_anual` = {g} implica que el mercado desaparece")

    cuotas, hitos_cuota = _cuota_por_anio(datos.get("cuota_objetivo"))

    proyeccion = []
    for n in range(1, HORIZONTE + 1):
        sam_n = sam * (1 + g) ** (n - 1)
        som_n = sam_n * cuotas[n]
        proyeccion.append({
            "anio": n,
            "sam": round(sam_n, 2),
            "cuota_objetivo": round(cuotas[n], 6),
            "som": round(som_n, 2),
            "penetracion_sobre_sam": round(som_n / sam_n, 6) if sam_n else None,
        })

    som1 = proyeccion[0]["som"]
    som5 = proyeccion[-1]["som"]
    cagr_som = _cagr(som1, som5, HORIZONTE - 1)

    bottom = _bottom_up(datos.get("bottom_up"), sam)

    resultado = {
        "script": "calcular_tam_sam_som.py",
        "moneda": datos.get("moneda") or "[no disponible]",
        "formulas": FORMULAS,
        "parametros": {
            "mercado_base": {
                "concepto": base.get("concepto") or "[no disponible]",
                "valor": tam,
                "anio": base.get("anio"),
                "fuente": base.get("fuente") or "[no disponible]",
            },
            "reducciones": detalle_reducciones,
            "factor_total_reduccion": round(factor, 8),
            "crecimiento_mercado_anual": float(g),
            "cuota_objetivo_declarada": {f"anio_{k}": v for k, v in hitos_cuota.items()},
            "horizonte_anios": HORIZONTE,
        },
        "resultados": {
            "tam": round(tam, 2),
            "sam": round(sam, 2),
            "sam_como_pct_del_tam": round(factor, 6),
            "proyeccion": proyeccion,
            "hitos": {f"som_anio_{n}": proyeccion[n - 1]["som"] for n in HITOS},
            "cagr_som_1_a_5": round(cagr_som, 6) if cagr_som is not None else None,
            "bottom_up": bottom,
        },
    }
    resultado["explicacion"] = _explicacion(resultado)
    resultado["advertencias"] = _advertencias(resultado, hitos_cuota)
    resultado["tabla_proyeccion"] = _tabla(resultado)
    resultado["tabla_embudo"] = _tabla_embudo(resultado)
    resultado["grafica"] = _grafica(resultado)
    return resultado


def _bottom_up(bloque, sam_top_down):
    """SAM contado desde abajo, y su contraste con el top-down."""
    if not isinstance(bloque, dict):
        return None
    bps = bloque.get("buyer_personas")
    if not isinstance(bps, list) or not bps:
        return None
    detalle = []
    total = 0.0
    for i, bp in enumerate(bps):
        if not isinstance(bp, dict):
            raise EntradaInvalida(f"bottom_up.buyer_personas[{i}] no es un objeto")
        for campo in ("clientes_potenciales", "ticket_promedio", "frecuencia_anual"):
            if not _num(bp.get(campo)) or bp[campo] < 0:
                raise EntradaInvalida(
                    f"bottom_up.buyer_personas[{i}].{campo} debe ser un número no negativo")
        sub = bp["clientes_potenciales"] * bp["ticket_promedio"] * bp["frecuencia_anual"]
        total += sub
        detalle.append({
            "nombre": bp.get("nombre") or f"Buyer persona {i + 1}",
            "clientes_potenciales": bp["clientes_potenciales"],
            "ticket_promedio": bp["ticket_promedio"],
            "frecuencia_anual": bp["frecuencia_anual"],
            "sam_parcial": round(sub, 2),
        })
    razon = (total / sam_top_down) if sam_top_down else None
    return {
        "buyer_personas": detalle,
        "sam_bottom_up": round(total, 2),
        "sam_top_down": round(sam_top_down, 2),
        "razon_bottom_up_sobre_top_down": round(razon, 4) if razon else None,
        "concuerdan": bool(razon and 1 / DIVERGENCIA_TOLERADA <= razon <= DIVERGENCIA_TOLERADA),
    }


def _pct(x, dec=2):
    return f"{x * 100:.{dec}f}%"


def _explicacion(r):
    res = r["resultados"]
    p = r["parametros"]
    som1 = res["proyeccion"][0]
    som5 = res["proyeccion"][-1]
    exp = [
        {
            "valor": "TAM",
            "formula_libro": FORMULAS["TAM"]["libro"],
            "formula_palabras": FORMULAS["TAM"]["palabras"],
            "lectura": (
                f"{res['tam']:,.0f} {r['moneda']} — {p['mercado_base']['concepto']}. "
                f"Fuente: {p['mercado_base']['fuente']}. Nadie captura el TAM: sirve para "
                f"saber si el problema es grande, no para proyectar ingresos."
            ),
        },
        {
            "valor": "SAM",
            "formula_libro": FORMULAS["SAM"]["libro"],
            "formula_palabras": FORMULAS["SAM"]["palabras"],
            "lectura": (
                f"{res['sam']:,.0f} {r['moneda']}, el {_pct(res['sam_como_pct_del_tam'], 3)} "
                f"del TAM tras {len(p['reducciones'])} recorte(s). Cada recorte multiplica: "
                f"dos recortes del 10% dejan el 1%, no el 80%."
            ),
        },
        {
            "valor": "SOM",
            "formula_libro": FORMULAS["SOM"]["libro"],
            "formula_palabras": FORMULAS["SOM"]["palabras"],
            "lectura": (
                f"Año 1: {som1['som']:,.0f} {r['moneda']} "
                f"({_pct(som1['cuota_objetivo'], 2)} del mercado accesible). "
                f"Año 5: {som5['som']:,.0f} ({_pct(som5['cuota_objetivo'], 2)})."
            ),
        },
        {
            "valor": "penetración sobre el SAM",
            "formula_libro": FORMULAS["penetracion"]["libro"],
            "formula_palabras": FORMULAS["penetracion"]["palabras"],
            "lectura": (
                f"La meta del año 5 equivale a {_pct(som5['penetracion_sobre_sam'], 2)} del "
                f"mercado accesible de ese año. Esa es la cifra que hay que defender ante "
                f"quien decide, no el valor absoluto."
            ),
        },
    ]
    if res["cagr_som_1_a_5"] is not None:
        exp.append({
            "valor": "CAGR del SOM (año 1 → 5)",
            "formula_libro": FORMULAS["CAGR"]["libro"],
            "formula_palabras": FORMULAS["CAGR"]["palabras"],
            "lectura": (
                f"{_pct(res['cagr_som_1_a_5'])} anual. Es el ritmo parejo equivalente entre "
                f"los dos extremos: no dice que se crecerá así cada año."
            ),
        })
    bu = res.get("bottom_up")
    if bu:
        exp.append({
            "valor": "SAM bottom-up",
            "formula_libro": FORMULAS["bottom_up"]["libro"],
            "formula_palabras": FORMULAS["bottom_up"]["palabras"],
            "lectura": (
                f"{bu['sam_bottom_up']:,.0f} {r['moneda']} contando clientes × ticket × "
                f"frecuencia, contra {bu['sam_top_down']:,.0f} del top-down: una razón de "
                f"{bu['razon_bottom_up_sobre_top_down']}×. "
                + ("Los dos métodos concuerdan razonablemente."
                   if bu["concuerdan"] else
                   "No concuerdan, y esa diferencia es el hallazgo: uno de los dos supuestos "
                   "está mal planteado.")
            ),
        })
    return exp


def _advertencias(r, hitos_cuota):
    res, p = r["resultados"], r["parametros"]
    adv = [
        "El TAM, las reducciones y la cuota objetivo son supuestos declarados, no "
        "mediciones: el script multiplica y proyecta, no valida el mercado. La calidad "
        "del resultado es la de su fuente peor sostenida.",
    ]
    if p["mercado_base"]["fuente"] == "[no disponible]":
        adv.append(
            "El mercado base no trae fuente. Todo el TAM/SAM/SOM cuelga de esa cifra, así "
            "que márcala con * en el reporte y dilo en el resumen: sin fuente, el "
            "dimensionamiento es una hipótesis, no evidencia.")
    sin_fuente = [x["concepto"] for x in p["reducciones"]
                  if x["fuente"] == "[no disponible]"]
    if sin_fuente:
        adv.append(
            f"Reducciones sin fuente: {', '.join(sin_fuente)}. Cada porcentaje sin respaldo "
            f"multiplica el error, y multiplicar dos estimaciones no da una estimación mejor.")
    if not p["reducciones"]:
        adv.append(
            "No hay ninguna reducción, así que el SAM es igual al TAM. Eso solo es correcto "
            "si de verdad se puede vender a todo el mercado declarado; casi nunca es el caso.")
    if hitos_cuota[1] > CUOTA_AGRESIVA_ANIO_1:
        adv.append(
            f"La cuota del año 1 es {_pct(hitos_cuota[1])} del mercado accesible. Para un "
            f"producto nuevo eso es muy alto: revisa si el SAM está mal recortado (demasiado "
            f"pequeño) o si la meta está puesta al revés, desde el ingreso deseado.")
    if p["crecimiento_mercado_anual"] == 0:
        adv.append(
            "El crecimiento del mercado quedó en 0%: el SAM es plano los cinco años. Si es "
            "un supuesto conservador deliberado, dilo; si es un dato que falta, márcalo.")
    elif p["crecimiento_mercado_anual"] > 0.30:
        adv.append(
            f"El mercado crece {_pct(p['crecimiento_mercado_anual'])} anual en el supuesto. "
            f"Sostenerlo cinco años seguidos es excepcional: conviene una fuente explícita o "
            f"un escenario alternativo más bajo.")
    bu = res.get("bottom_up")
    if bu and not bu["concuerdan"]:
        razon = bu["razon_bottom_up_sobre_top_down"]
        cual = "mayor" if razon and razon > 1 else "menor"
        adv.append(
            f"El SAM bottom-up es {razon}× el top-down ({cual}). Con una divergencia así, "
            f"presentar solo uno de los dos es elegir el que conviene: revisa el número de "
            f"clientes potenciales o el porcentaje de reducción, y declara con qué método se "
            f"decidió.")
    if not bu:
        adv.append(
            "Sin bottom-up no hay contraste: el SAM top-down queda sin comprobación "
            "independiente. Con el desglose por buyer persona (clientes × ticket × "
            "frecuencia) el script lo compara solo.")
    return adv


def _tabla(r):
    res = r["resultados"]
    filas = [
        [f"Año {x['anio']}", f"{x['sam']:,.0f}", _pct(x["cuota_objetivo"], 2),
         f"{x['som']:,.0f}", _pct(x["penetracion_sobre_sam"], 2)]
        for x in res["proyeccion"]
    ]
    return {
        "titulo": f"Proyección de mercado a {r['parametros']['horizonte_anios']} años "
                  f"({r['moneda']})",
        "columnas": ["Horizonte", "SAM", "Cuota objetivo", "SOM",
                     "Penetración sobre el SAM"],
        "filas": filas,
        "nota": (
            f"El SAM crece {_pct(r['parametros']['crecimiento_mercado_anual'])} al año por "
            f"supuesto declarado. La cuota de los años 2 y 4 se interpola entre los hitos "
            f"declarados (1, 3 y 5), no es un dato aparte."
        ),
    }


def _tabla_embudo(r):
    """El embudo TAM → SAM: cada recorte con su porcentaje, su valor y su fuente."""
    p = r["parametros"]
    filas = [["TAM — " + p["mercado_base"]["concepto"], "100%",
              f"{p['mercado_base']['valor']:,.0f}", p["mercado_base"]["fuente"]]]
    for x in p["reducciones"]:
        filas.append([x["concepto"], _pct(x["porcentaje"], 2),
                      f"{x['valor_resultante']:,.0f}", x["fuente"]])
    filas.append(["SAM — mercado accesible",
                  _pct(r["resultados"]["sam_como_pct_del_tam"], 3),
                  f"{r['resultados']['sam']:,.0f}", "resultado del cálculo"])
    return {
        "titulo": f"Del TAM al SAM, recorte por recorte ({r['moneda']})",
        "columnas": ["Concepto", "% que se conserva", "Valor", "Fuente"],
        "filas": filas,
        "fila_total": True,
        "nota": "Los porcentajes se multiplican entre sí, no se suman: conservar el 4% y "
                "luego el 35% deja el 1.4% del TAM.",
    }


def _grafica(r):
    res = r["resultados"]
    return {
        "tipo": "line",
        "titulo": f"Trayectoria SAM vs. SOM ({r['moneda']})",
        "eje_x": "Año",
        "eje_y": r["moneda"],
        "labels": [f"Año {x['anio']}" for x in res["proyeccion"]],
        "datasets": [
            {"label": "SAM (mercado accesible)",
             "data": [x["sam"] for x in res["proyeccion"]]},
            {"label": "SOM (meta de captura)",
             "data": [x["som"] for x in res["proyeccion"]]},
        ],
    }


def seccion_reporte(r):
    res = r["resultados"]
    som = res["hitos"]
    items = [
        {
            "titulo": "Dimensionamiento de mercado — TAM / SAM / SOM",
            "subtitulo": (
                f"TAM {res['tam']:,.0f} · SAM {res['sam']:,.0f} · "
                f"SOM año 1 {som['som_anio_1']:,.0f} {r['moneda']}"
            ),
            "tags": ["mercado", "TAM/SAM/SOM"],
            "body": [{"label": e["valor"],
                      "texto": f"{e['lectura']}\n\nCómo se calcula: {e['formula_palabras']}\n"
                               f"Fórmula: {e['formula_libro']}"}
                     for e in r["explicacion"]],
            "tabla": [r["tabla_embudo"], r["tabla_proyeccion"]],
            "chart": r["grafica"],
            "fuentes": [r["parametros"]["mercado_base"]["fuente"]]
                       + [x["fuente"] for x in r["parametros"]["reducciones"]],
        }
    ]
    bu = res.get("bottom_up")
    if bu:
        filas = [[x["nombre"], f"{x['clientes_potenciales']:,.0f}",
                  f"{x['ticket_promedio']:,.0f}", str(x["frecuencia_anual"]),
                  f"{x['sam_parcial']:,.0f}"] for x in bu["buyer_personas"]]
        filas.append(["TOTAL bottom-up", "", "", "", f"{bu['sam_bottom_up']:,.0f}"])
        items.append({
            "titulo": "Contraste top-down vs. bottom-up",
            "subtitulo": (
                f"Razón {bu['razon_bottom_up_sobre_top_down']}× — "
                + ("concuerdan" if bu["concuerdan"] else "NO concuerdan")
            ),
            "tags": ["mercado", "comprobación"],
            "veredicto": "perseverar" if bu["concuerdan"] else "pivotear",
            "body": [{"label": "Por qué importa",
                      "texto": FORMULAS["bottom_up"]["palabras"]}],
            "tabla": {
                "titulo": f"SAM bottom-up por buyer persona ({r['moneda']})",
                "columnas": ["Buyer persona", "Clientes potenciales", "Ticket promedio",
                             "Frecuencia anual", "SAM parcial"],
                "filas": filas,
                "fila_total": True,
            },
        })
    return {"titulo": "Dimensionamiento de mercado", "items": items}


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="TAM/SAM/SOM con reducciones top-down, proyección 1/3/5 y CAGR.")
    ap.add_argument("--datos", help="JSON de entrada con el mercado base y las reducciones")
    ap.add_argument("--plantilla", action="store_true",
                    help="Imprime el esqueleto de entrada y termina")
    ap.add_argument("-o", "--output", default="tam_sam_som.json",
                    help="Ruta de salida JSON")
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
        r = calcular(datos)
    except EntradaInvalida as exc:
        print(f"Entrada inválida: {exc}", file=sys.stderr)
        return 2

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(r, f, ensure_ascii=False, indent=2)
    if args.seccion_reporte:
        with open(args.seccion_reporte, "w", encoding="utf-8") as f:
            json.dump(seccion_reporte(r), f, ensure_ascii=False, indent=2)

    res = r["resultados"]
    print(f"TAM  {res['tam']:>18,.0f} {r['moneda']}")
    print(f"SAM  {res['sam']:>18,.0f} {r['moneda']}  "
          f"({_pct(res['sam_como_pct_del_tam'], 3)} del TAM)")
    for n in HITOS:
        print(f"SOM año {n}: {res['hitos'][f'som_anio_{n}']:>13,.0f} {r['moneda']}")
    if res["cagr_som_1_a_5"] is not None:
        print(f"CAGR del SOM 1→5: {_pct(res['cagr_som_1_a_5'])}")
    for a in r["advertencias"][1:]:
        print(f"\n[AVISO] {a}")
    print(f"\nCálculo guardado en: {args.output}")
    if args.seccion_reporte:
        print(f"Sección para el reporte en: {args.seccion_reporte}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
