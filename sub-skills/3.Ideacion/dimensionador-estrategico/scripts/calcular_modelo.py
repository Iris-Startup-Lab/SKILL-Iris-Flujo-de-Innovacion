"""
calcular_modelo.py

Unidad económica del Dimensionador (Módulos 3 a 8): CLV, cross-selling, CAC,
CLV:CAC, payback, ROI, ARPU, MRR/ARR año 1 a 5, punto de equilibrio y EBITDA
aproximado — por buyer persona y consolidado.

Por qué existe: `xlsx_generator.py` **dibuja** el modelo financiero, no lo calcula.
Los números los hacía el LLM a mano, y con eso el modelo no se puede auditar: si el
CLV:CAC sale 4.2 no hay forma de saber si el error está en el supuesto o en la
multiplicación. Aquí el LLM declara las métricas unitarias con su supuesto; el
script deriva todo lo demás y avisa cuando dos supuestos se contradicen —el caso
más común es una vida del cliente que no cuadra con el churn declarado—.

Cadena de cálculo (por buyer persona):
    ingreso_anual   = ticket × frecuencia_anual
    cross_sell_anual= Σ (ticket_cs × probabilidad_adopcion × frecuencia_cs)
    CLV_neto        = (ingreso_anual + cross_sell_anual) × vida_anios × margen_bruto
    CLV:CAC         = CLV_neto / CAC
    payback_meses   = CAC / (contribución mensual)
    ROI_marketing   = (CLV_neto − CAC) / CAC
    clientes_n      = clientes_{n−1} × (1 − churn) + nuevos_n
    MRR_n           = clientes_n × ARPU_mensual   ·   ARR_n = MRR_n × 12
    EBITDA_n        ≈ ingreso_n × margen − costos_fijos − CAC × nuevos_n

Uso:
    python calcular_modelo.py --plantilla > modelo.json
    python calcular_modelo.py --datos modelo.json [-o unidad_economica.json]
    python calcular_modelo.py --datos modelo.json --seccion-reporte seccion.json

Códigos de salida: 0 ok · 1 error de archivo/uso · 2 entrada inválida.
"""
import argparse
import json
import sys

HORIZONTE = 5
HITOS = (1, 3, 5)

# Calificación del ratio CLV:CAC (Módulo 4 del AGENTE.md).
ESCALA_CLV_CAC = [
    (5.0, "excelente", "Sobra margen para invertir más en adquisición."),
    (3.0, "sano", "Es el rango que se considera sostenible."),
    (1.0, "requiere optimización",
     "Se recupera la inversión, pero queda poco para crecer."),
    (0.0, "insostenible",
     "Cada cliente cuesta más de lo que deja: el modelo pierde dinero al crecer."),
]

# Umbrales de aviso. No bloquean: señalan lo que un lector con experiencia
# preguntaría al ver el número.
PAYBACK_COMODO_MESES = 12
CHURN_ALTO = 0.50
MARGEN_SOSPECHOSO = 0.90
PROB_CROSS_SELL_AGRESIVA = 0.50
# Divergencia tolerada entre la vida declarada y la que implica el churn (1/churn).
DIVERGENCIA_VIDA = 2.0

FORMULAS = {
    "ingreso_anual": {
        "libro": "ingreso_anual = ticket_promedio × frecuencia_anual",
        "palabras": "Lo que deja un cliente al año: cuánto paga cada vez, por cuántas "
                    "veces compra en el año.",
    },
    "clv": {
        "libro": "CLV_neto = (ingreso_anual + cross_sell_anual) × vida_anios × margen_bruto",
        "palabras": "Todo lo que deja un cliente mientras se queda, ya descontado el costo "
                    "de servirlo. Es una expectativa sobre varios años, no dinero en caja.",
    },
    "cross_sell": {
        "libro": "cross_sell_anual = Σ (ticket_i × probabilidad_adopcion_i × frecuencia_i)",
        "palabras": "El ingreso extra por venderle a un cliente que ya se tiene. Se multiplica "
                    "por la probabilidad de que lo compre, así que es un valor esperado: "
                    "ningún cliente paga exactamente eso.",
    },
    "clv_cac": {
        "libro": "CLV:CAC = CLV_neto / CAC",
        "palabras": "Cuántos pesos deja un cliente por cada peso que costó conseguirlo. "
                    "Debajo de 1 se pierde dinero por cada venta nueva.",
    },
    "payback": {
        "libro": "payback_meses = CAC / ((ingreso_anual + cross_sell_anual) × margen / 12)",
        "palabras": "Cuántos meses tarda un cliente en devolver lo que costó traerlo. "
                    "Determina cuánta caja hace falta para crecer, no si el negocio sirve.",
    },
    "roi": {
        "libro": "ROI_marketing = (CLV_neto − CAC) / CAC",
        "palabras": "La ganancia sobre lo invertido en conseguir al cliente. Un 200% quiere "
                    "decir que se recuperan tres pesos por cada uno puesto.",
    },
    "clientes": {
        "libro": "clientes_n = clientes_{n−1} × (1 − churn_anual) + nuevos_n , "
                 "nuevos_n = nuevos_1 × (1 + crecimiento)^(n−1)",
        "palabras": "Cada año se van algunos de los que había y entran los nuevos. No es "
                    "una curva de crecimiento suelta: la fuga se resta primero.",
    },
    "arr": {
        "libro": "ARPU_mensual = (ingreso_anual + cross_sell_anual) / 12 · "
                 "MRR_n = clientes_n × ARPU_mensual · ARR_n = MRR_n × 12",
        "palabras": "El ingreso recurrente: lo que entra cada mes y su equivalente anual. "
                    "Si el modelo no es de suscripción, es el ingreso promedio prorrateado.",
    },
    "equilibrio": {
        "libro": "clientes_equilibrio = costos_fijos_anuales / "
                 "(ingreso_anual × margen_bruto)",
        "palabras": "Cuántos clientes hacen falta para cubrir los costos que existen "
                    "aunque no se venda nada.",
    },
    "ebitda": {
        "libro": "EBITDA_n ≈ ingreso_n × margen_bruto − costos_fijos − CAC × nuevos_n",
        "palabras": "Lo que quedaría en el año antes de impuestos, intereses y "
                    "depreciación, contando el costo de conseguir a los clientes nuevos "
                    "de ese año. Es una aproximación con los supuestos declarados, no un "
                    "estado de resultados.",
    },
}


class EntradaInvalida(Exception):
    pass


def _texto(v):
    return isinstance(v, str) and v.strip() != ""


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _exigir(cond, mensaje):
    if not cond:
        raise EntradaInvalida(mensaje)


def _proporcion(valor, ruta, permite_cero=True, permite_uno=True):
    _exigir(_num(valor), f"{ruta} debe ser numérico")
    bajo = 0 <= valor if permite_cero else 0 < valor
    alto = valor <= 1 if permite_uno else valor < 1
    _exigir(bajo and alto,
            f"{ruta} = {valor} debe ser una proporción entre 0 y 1 (0.65 es 65%, no 65)")
    return float(valor)


def plantilla():
    return {
        "moneda": "MXN",
        "costos_fijos_anuales": 2400000,
        "buyer_personas": [
            {
                "nombre": "Buyer persona 1",
                "ticket_promedio": 4800,
                "frecuencia_anual": 2,
                "vida_cliente_anios": 3,
                "margen_bruto": 0.65,
                "cac": 3500,
                "clientes_anio_1": 120,
                "crecimiento_clientes_anual": 0.5,
                "churn_anual": 0.30,
                "supuestos": "De dónde salen estas cifras: fuente, benchmark o estimación "
                             "propia (márcala con * en el reporte).",
                "cross_selling": [
                    {"producto": "Producto complementario",
                     "ticket": 900, "probabilidad_adopcion": 0.30,
                     "frecuencia_anual": 1},
                ],
                "canales": [
                    {"nombre": "Canal principal", "cac": 3100, "peso": 0.7},
                    {"nombre": "Canal secundario", "cac": 4400, "peso": 0.3},
                ],
            }
        ],
    }


def _calificar_clv_cac(ratio):
    for corte, etiqueta, lectura in ESCALA_CLV_CAC:
        if ratio >= corte:
            return etiqueta, lectura
    return ESCALA_CLV_CAC[-1][1], ESCALA_CLV_CAC[-1][2]


def _cross_selling(lista, nombre_bp):
    if lista is None:
        return 0.0, []
    _exigir(isinstance(lista, list), f"«{nombre_bp}».cross_selling debe ser una lista")
    _exigir(len(lista) <= 3,
            f"«{nombre_bp}».cross_selling trae {len(lista)} productos y el módulo 3A "
            f"admite hasta 3: más productos es un catálogo, no una hipótesis de "
            f"cross-selling.")
    detalle = []
    total = 0.0
    for i, cs in enumerate(lista):
        r = f"«{nombre_bp}».cross_selling[{i}]"
        _exigir(isinstance(cs, dict), f"{r} no es un objeto")
        _exigir(_texto(cs.get("producto")), f"{r}.producto está vacío")
        _exigir(_num(cs.get("ticket")) and cs["ticket"] >= 0,
                f"{r}.ticket debe ser un número no negativo")
        _exigir(_num(cs.get("frecuencia_anual")) and cs["frecuencia_anual"] >= 0,
                f"{r}.frecuencia_anual debe ser un número no negativo")
        p = _proporcion(cs.get("probabilidad_adopcion"), f"{r}.probabilidad_adopcion")
        ingreso = cs["ticket"] * p * cs["frecuencia_anual"]
        total += ingreso
        detalle.append({
            "producto": cs["producto"],
            "ticket": float(cs["ticket"]),
            "probabilidad_adopcion": p,
            "frecuencia_anual": float(cs["frecuencia_anual"]),
            "ingreso_esperado_anual": round(ingreso, 2),
        })
    return total, detalle


def _canales(lista, nombre_bp, cac_total):
    if lista is None:
        return []
    _exigir(isinstance(lista, list), f"«{nombre_bp}».canales debe ser una lista")
    detalle = []
    suma_pesos = 0.0
    for i, c in enumerate(lista):
        r = f"«{nombre_bp}».canales[{i}]"
        _exigir(isinstance(c, dict), f"{r} no es un objeto")
        _exigir(_texto(c.get("nombre")), f"{r}.nombre está vacío")
        _exigir(_num(c.get("cac")) and c["cac"] > 0, f"{r}.cac debe ser positivo")
        peso = _proporcion(c.get("peso"), f"{r}.peso")
        suma_pesos += peso
        detalle.append({"nombre": c["nombre"], "cac": float(c["cac"]), "peso": peso})
    if detalle:
        _exigir(abs(suma_pesos - 1.0) < 0.01,
                f"«{nombre_bp}»: los pesos de los canales suman {suma_pesos:.2f} y deben "
                f"sumar 1. Son la mezcla de adquisición, así que reparten el 100%.")
        mezcla = sum(c["cac"] * c["peso"] for c in detalle)
        for c in detalle:
            c["cac_ponderado"] = round(c["cac"] * c["peso"], 2)
        detalle.append({
            "nombre": "CAC de la mezcla (calculado)",
            "cac": round(mezcla, 2), "peso": 1.0, "cac_ponderado": round(mezcla, 2),
        })
    return detalle


def _proyectar(clientes_1, crecimiento, churn, arpu_mensual, ingreso_anual_cliente,
               margen, cac, costos_fijos_bp):
    """Cohortes año a año: se resta la fuga y se suman los nuevos."""
    filas = []
    clientes_prev = 0.0
    for n in range(1, HORIZONTE + 1):
        nuevos = clientes_1 * (1 + crecimiento) ** (n - 1)
        clientes = clientes_prev * (1 - churn) + nuevos
        mrr = clientes * arpu_mensual
        ingreso_anual = clientes * ingreso_anual_cliente
        ebitda = None
        if costos_fijos_bp is not None:
            ebitda = ingreso_anual * margen - costos_fijos_bp - cac * nuevos
        filas.append({
            "anio": n,
            "clientes_nuevos": round(nuevos, 1),
            "clientes_activos": round(clientes, 1),
            "arpu_mensual": round(arpu_mensual, 2),
            "mrr": round(mrr, 2),
            "arr": round(mrr * 12, 2),
            "ingreso_anual": round(ingreso_anual, 2),
            "ebitda_aproximado": round(ebitda, 2) if ebitda is not None else None,
        })
        clientes_prev = clientes
    return filas


def _calcular_bp(bp, pos, costos_fijos_bp, moneda):
    nombre = bp.get("nombre") or f"Buyer persona {pos + 1}"
    _exigir(isinstance(bp, dict), f"buyer_personas[{pos}] no es un objeto")
    for campo in ("ticket_promedio", "frecuencia_anual", "vida_cliente_anios", "cac"):
        _exigir(_num(bp.get(campo)) and bp[campo] > 0,
                f"«{nombre}».{campo} es obligatorio y debe ser positivo")
    margen = _proporcion(bp.get("margen_bruto"), f"«{nombre}».margen_bruto",
                         permite_cero=False)
    churn = _proporcion(bp.get("churn_anual", 0.0), f"«{nombre}».churn_anual",
                        permite_uno=False)
    clientes_1 = bp.get("clientes_anio_1")
    _exigir(_num(clientes_1) and clientes_1 > 0,
            f"«{nombre}».clientes_anio_1 es obligatorio y debe ser positivo")
    crecimiento = bp.get("crecimiento_clientes_anual", 0.0)
    _exigir(_num(crecimiento) and crecimiento > -1,
            f"«{nombre}».crecimiento_clientes_anual debe ser numérico y mayor que −1")

    ingreso_anual = bp["ticket_promedio"] * bp["frecuencia_anual"]
    cs_anual, cs_detalle = _cross_selling(bp.get("cross_selling"), nombre)
    ingreso_total_anual = ingreso_anual + cs_anual
    vida = bp["vida_cliente_anios"]
    cac = bp["cac"]

    clv_bruto = ingreso_anual * vida
    clv_neto_base = clv_bruto * margen
    clv_neto = ingreso_total_anual * vida * margen
    contribucion_mensual = ingreso_total_anual * margen / 12
    ratio = clv_neto / cac
    calificacion, lectura_ratio = _calificar_clv_cac(ratio)
    payback = cac / contribucion_mensual if contribucion_mensual > 0 else None
    arpu_mensual = ingreso_total_anual / 12

    equilibrio = None
    if costos_fijos_bp is not None and ingreso_anual * margen > 0:
        equilibrio = costos_fijos_bp / (ingreso_total_anual * margen)

    proyeccion = _proyectar(clientes_1, crecimiento, churn, arpu_mensual,
                            ingreso_total_anual, margen, cac, costos_fijos_bp)

    return {
        "nombre": nombre,
        "supuestos": bp.get("supuestos") or "[no disponible]",
        "entradas": {
            "ticket_promedio": float(bp["ticket_promedio"]),
            "frecuencia_anual": float(bp["frecuencia_anual"]),
            "vida_cliente_anios": float(vida),
            "margen_bruto": margen,
            "cac": float(cac),
            "clientes_anio_1": float(clientes_1),
            "crecimiento_clientes_anual": float(crecimiento),
            "churn_anual": churn,
        },
        "resultados": {
            "ingreso_anual_por_cliente": round(ingreso_anual, 2),
            "cross_sell_anual_por_cliente": round(cs_anual, 2),
            "pct_incremento_por_cross_sell": (
                round(cs_anual / ingreso_anual, 4) if ingreso_anual else None),
            "clv_bruto": round(clv_bruto, 2),
            "clv_neto_sin_cross_sell": round(clv_neto_base, 2),
            "clv_neto_ajustado": round(clv_neto, 2),
            "pct_incremento_clv_por_cross_sell": (
                round(clv_neto / clv_neto_base - 1, 4) if clv_neto_base else None),
            "clv_cac": round(ratio, 2),
            "calificacion_clv_cac": calificacion,
            "payback_meses": round(payback, 1) if payback is not None else None,
            "roi_marketing": round((clv_neto - cac) / cac, 4),
            "roas_anio_1": round(ingreso_total_anual / cac, 2),
            "arpu_mensual": round(arpu_mensual, 2),
            "contribucion_mensual_por_cliente": round(contribucion_mensual, 2),
            "clientes_punto_equilibrio": (
                round(equilibrio, 1) if equilibrio is not None else None),
            "vida_implicita_por_churn": round(1 / churn, 2) if churn > 0 else None,
        },
        "cross_selling": cs_detalle,
        "canales": _canales(bp.get("canales"), nombre, cac),
        "proyeccion": proyeccion,
        "lectura_ratio": lectura_ratio,
        "moneda": moneda,
    }


def calcular(datos):
    bps = datos.get("buyer_personas")
    _exigir(isinstance(bps, list) and bps,
            "`buyer_personas` debe ser una lista con al menos un buyer persona")
    moneda = datos.get("moneda") or "[no disponible]"

    costos_fijos = datos.get("costos_fijos_anuales")
    if costos_fijos is not None:
        _exigir(_num(costos_fijos) and costos_fijos >= 0,
                "`costos_fijos_anuales` debe ser un número no negativo")
        # Los costos fijos son del negocio, no de un buyer persona. Para el punto de
        # equilibrio y el EBITDA por segmento se reparten en partes iguales, y se dice.
        costos_fijos_bp = float(costos_fijos) / len(bps)
    else:
        costos_fijos_bp = None

    calculados = [_calcular_bp(bp, i, costos_fijos_bp, moneda)
                  for i, bp in enumerate(bps)]

    consolidado = _consolidar(calculados, costos_fijos)
    resultado = {
        "script": "calcular_modelo.py",
        "moneda": moneda,
        "formulas": FORMULAS,
        "parametros": {
            "horizonte_anios": HORIZONTE,
            "costos_fijos_anuales": costos_fijos,
            "costos_fijos_repartidos_por_bp": (
                round(costos_fijos_bp, 2) if costos_fijos_bp is not None else None),
            "escala_clv_cac": {e[1]: f">= {e[0]}" for e in ESCALA_CLV_CAC},
        },
        "resultados": {"buyer_personas": calculados, "consolidado": consolidado},
    }
    resultado["explicacion"] = _explicacion(resultado)
    resultado["advertencias"] = _advertencias(resultado)
    resultado["tabla_unidad_economica"] = _tabla_unidad(resultado)
    resultado["tabla_proyeccion"] = _tabla_proyeccion(resultado)
    resultado["grafica"] = _grafica(resultado)
    return resultado


def _consolidar(calculados, costos_fijos):
    """Totales del negocio. El CLV:CAC se pondera por clientes, no se promedia:
    promediar ratios da un número que no corresponde a ningún negocio real."""
    por_anio = []
    for n in range(HORIZONTE):
        clientes = sum(bp["proyeccion"][n]["clientes_activos"] for bp in calculados)
        nuevos = sum(bp["proyeccion"][n]["clientes_nuevos"] for bp in calculados)
        arr = sum(bp["proyeccion"][n]["arr"] for bp in calculados)
        mrr = sum(bp["proyeccion"][n]["mrr"] for bp in calculados)
        ingreso = sum(bp["proyeccion"][n]["ingreso_anual"] for bp in calculados)
        ebitdas = [bp["proyeccion"][n]["ebitda_aproximado"] for bp in calculados]
        por_anio.append({
            "anio": n + 1,
            "clientes_activos": round(clientes, 1),
            "clientes_nuevos": round(nuevos, 1),
            "mrr": round(mrr, 2),
            "arr": round(arr, 2),
            "ingreso_anual": round(ingreso, 2),
            "ebitda_aproximado": (round(sum(ebitdas), 2)
                                  if all(x is not None for x in ebitdas) else None),
        })

    clientes_1 = sum(bp["entradas"]["clientes_anio_1"] for bp in calculados)
    clv_total = sum(bp["resultados"]["clv_neto_ajustado"] * bp["entradas"]["clientes_anio_1"]
                    for bp in calculados)
    cac_total = sum(bp["entradas"]["cac"] * bp["entradas"]["clientes_anio_1"]
                    for bp in calculados)
    mejor = max(calculados, key=lambda b: b["resultados"]["clv_cac"])
    mas_cross = max(calculados,
                    key=lambda b: b["resultados"]["pct_incremento_clv_por_cross_sell"] or 0)
    anio_positivo = next((x["anio"] for x in por_anio
                          if x["ebitda_aproximado"] is not None
                          and x["ebitda_aproximado"] > 0), None)
    return {
        "clv_cac_ponderado": round(clv_total / cac_total, 2) if cac_total else None,
        "clientes_anio_1": round(clientes_1, 1),
        "arr_hitos": {f"arr_anio_{n}": por_anio[n - 1]["arr"] for n in HITOS},
        "por_anio": por_anio,
        "buyer_persona_mas_atractivo": {
            "nombre": mejor["nombre"], "clv_cac": mejor["resultados"]["clv_cac"]},
        "buyer_persona_mas_beneficiado_por_cross_sell": {
            "nombre": mas_cross["nombre"],
            "pct_incremento_clv": mas_cross["resultados"]["pct_incremento_clv_por_cross_sell"]},
        "primer_anio_con_ebitda_positivo": anio_positivo,
        "costos_fijos_anuales": costos_fijos,
    }


def _pct(x, dec=1):
    return "[no disponible]" if x is None else f"{x * 100:.{dec}f}%"


def _explicacion(r):
    c = r["resultados"]["consolidado"]
    bp = r["resultados"]["buyer_personas"][0]
    res = bp["resultados"]
    m = r["moneda"]
    exp = [
        {
            "valor": "CLV neto ajustado",
            "formula_libro": FORMULAS["clv"]["libro"],
            "formula_palabras": FORMULAS["clv"]["palabras"],
            "lectura": (
                f"«{bp['nombre']}»: {res['clv_neto_ajustado']:,.0f} {m} por cliente a lo "
                f"largo de {bp['entradas']['vida_cliente_anios']:.0f} año(s). Es una "
                f"expectativa construida sobre supuestos, no caja comprometida."
            ),
        },
        {
            "valor": "CLV:CAC",
            "formula_libro": FORMULAS["clv_cac"]["libro"],
            "formula_palabras": FORMULAS["clv_cac"]["palabras"],
            "lectura": (
                f"{res['clv_cac']}:1 ({res['calificacion_clv_cac']}). {bp['lectura_ratio']} "
                f"Consolidado del negocio, ponderado por clientes: "
                f"{c['clv_cac_ponderado']}:1."
            ),
        },
        {
            "valor": "payback",
            "formula_libro": FORMULAS["payback"]["libro"],
            "formula_palabras": FORMULAS["payback"]["palabras"],
            "lectura": (
                f"{res['payback_meses']} meses. Hasta ese mes el cliente todavía no ha "
                f"pagado lo que costó traerlo: es el dinero que hay que tener disponible "
                f"para crecer."
            ),
        },
        {
            "valor": "ARR",
            "formula_libro": FORMULAS["arr"]["libro"],
            "formula_palabras": FORMULAS["arr"]["palabras"],
            "lectura": (
                f"Año 1: {c['arr_hitos']['arr_anio_1']:,.0f} {m} · "
                f"Año 3: {c['arr_hitos']['arr_anio_3']:,.0f} · "
                f"Año 5: {c['arr_hitos']['arr_anio_5']:,.0f}."
            ),
        },
        {
            "valor": "clientes activos",
            "formula_libro": FORMULAS["clientes"]["libro"],
            "formula_palabras": FORMULAS["clientes"]["palabras"],
            "lectura": (
                f"La base no es la suma de todos los clientes captados: la fuga anual se "
                f"resta cada año antes de sumar los nuevos."
            ),
        },
    ]
    if res["cross_sell_anual_por_cliente"]:
        exp.insert(1, {
            "valor": "cross-selling",
            "formula_libro": FORMULAS["cross_sell"]["libro"],
            "formula_palabras": FORMULAS["cross_sell"]["palabras"],
            "lectura": (
                f"Añade {res['cross_sell_anual_por_cliente']:,.0f} {m} al año por cliente, "
                f"un {_pct(res['pct_incremento_clv_por_cross_sell'])} más de CLV. Es un "
                f"valor esperado: se cumple en promedio sobre muchos clientes, no en cada uno."
            ),
        })
    if c["primer_anio_con_ebitda_positivo"] is not None:
        exp.append({
            "valor": "EBITDA aproximado",
            "formula_libro": FORMULAS["ebitda"]["libro"],
            "formula_palabras": FORMULAS["ebitda"]["palabras"],
            "lectura": (
                f"El primer año con EBITDA positivo es el {c['primer_anio_con_ebitda_positivo']}. "
                f"Cuenta el CAC de los clientes nuevos de cada año, que es lo que suele "
                f"quedar fuera y adelantar el punto de rentabilidad."
            ),
        })
    elif c["costos_fijos_anuales"] is not None:
        exp.append({
            "valor": "EBITDA aproximado",
            "formula_libro": FORMULAS["ebitda"]["libro"],
            "formula_palabras": FORMULAS["ebitda"]["palabras"],
            "lectura": (
                f"Ningún año de los {HORIZONTE} proyectados llega a EBITDA positivo con "
                f"estos supuestos. Eso no invalida la idea, pero sí obliga a decir cuánta "
                f"caja hace falta para llegar más lejos."
            ),
        })
    return exp


def _advertencias(r):
    adv = [
        "Las métricas unitarias (ticket, frecuencia, vida, margen, CAC, churn) son "
        "supuestos declarados: el script deriva el modelo, no lo valida. Un CLV:CAC "
        "excelente sobre supuestos optimistas sigue siendo un supuesto optimista.",
    ]
    c = r["resultados"]["consolidado"]
    for bp in r["resultados"]["buyer_personas"]:
        n, e, res = bp["nombre"], bp["entradas"], bp["resultados"]
        if res["clv_cac"] < 1:
            adv.append(
                f"«{n}»: CLV:CAC de {res['clv_cac']}:1 — cada cliente cuesta más de lo que "
                f"deja. Crecer con este segmento aumenta la pérdida; no es un problema de "
                f"volumen.")
        elif res["clv_cac"] < 3:
            adv.append(
                f"«{n}»: CLV:CAC de {res['clv_cac']}:1, por debajo del 3:1 que se considera "
                f"sano. Se sostiene, pero deja poco para reinvertir.")
        if res["payback_meses"] is not None:
            vida_meses = e["vida_cliente_anios"] * 12
            if res["payback_meses"] > vida_meses:
                adv.append(
                    f"«{n}»: el payback ({res['payback_meses']} meses) es mayor que la vida "
                    f"del cliente ({vida_meses:.0f} meses). El cliente se va antes de haber "
                    f"pagado su adquisición: el CLV:CAC de arriba y esto no pueden ser "
                    f"ciertos a la vez, revisa los supuestos.")
            elif res["payback_meses"] > PAYBACK_COMODO_MESES:
                adv.append(
                    f"«{n}»: payback de {res['payback_meses']} meses (más de "
                    f"{PAYBACK_COMODO_MESES}). Cada cliente nuevo consume caja durante más "
                    f"de un año, así que el crecimiento hay que financiarlo.")
        vida_churn = res["vida_implicita_por_churn"]
        if vida_churn:
            razon = e["vida_cliente_anios"] / vida_churn
            if razon > DIVERGENCIA_VIDA or razon < 1 / DIVERGENCIA_VIDA:
                adv.append(
                    f"«{n}»: la vida declarada ({e['vida_cliente_anios']:.1f} años) y la que "
                    f"implica el churn del {_pct(e['churn_anual'])} (1/churn = "
                    f"{vida_churn} años) no cuadran. Son dos formas de decir lo mismo, así "
                    f"que una de las dos está mal y el CLV depende de cuál.")
        elif e["churn_anual"] == 0:
            adv.append(
                f"«{n}»: churn declarado en 0%, o sea que ningún cliente se va nunca. Si es "
                f"un supuesto simplificador, dilo; el modelo lo toma literal y la proyección "
                f"de clientes sale optimista.")
        if e["churn_anual"] > CHURN_ALTO:
            adv.append(
                f"«{n}»: churn del {_pct(e['churn_anual'])} anual. Con esa fuga la base "
                f"apenas crece aunque entren clientes nuevos: la palanca está en retención, "
                f"no en adquisición.")
        if e["margen_bruto"] > MARGEN_SOSPECHOSO:
            adv.append(
                f"«{n}»: margen bruto del {_pct(e['margen_bruto'])}. Solo es realista en "
                f"software puro sin soporte; si hay operación, personas o logística, revisa "
                f"qué costos quedaron fuera.")
        agresivos = [cs["producto"] for cs in bp["cross_selling"]
                     if cs["probabilidad_adopcion"] > PROB_CROSS_SELL_AGRESIVA]
        if agresivos:
            adv.append(
                f"«{n}»: probabilidad de adopción por encima del "
                f"{_pct(PROB_CROSS_SELL_AGRESIVA, 0)} en {', '.join(agresivos)}. Que más de "
                f"la mitad de los clientes compre el producto complementario es una hipótesis "
                f"fuerte, y el CLV ajustado cuelga de ella.")
    if c["costos_fijos_anuales"] is None:
        adv.append(
            "Sin `costos_fijos_anuales` no hay punto de equilibrio ni EBITDA: el modelo "
            "queda a nivel de unidad económica. Un CLV:CAC sano no dice si el negocio "
            "completo gana dinero.")
    else:
        adv.append(
            f"Los costos fijos ({c['costos_fijos_anuales']:,.0f} {r['moneda']}) se reparten "
            f"en partes iguales entre los buyer personas para el punto de equilibrio y el "
            f"EBITDA. Si un segmento consume más operación que otro, ese reparto lo favorece.")
    return adv


def _tabla_unidad(r):
    m = r["moneda"]
    filas = []
    for bp in r["resultados"]["buyer_personas"]:
        res, e = bp["resultados"], bp["entradas"]
        filas.append([
            bp["nombre"],
            f"{res['clv_neto_sin_cross_sell']:,.0f}",
            f"{res['clv_neto_ajustado']:,.0f}",
            _pct(res["pct_incremento_clv_por_cross_sell"]),
            f"{e['cac']:,.0f}",
            f"{res['clv_cac']}:1",
            (f"{res['payback_meses']} m" if res["payback_meses"] is not None
             else "[no disponible]"),
            _pct(res["roi_marketing"], 0),
        ])
    c = r["resultados"]["consolidado"]
    filas.append(["CONSOLIDADO (ponderado por clientes)", "", "", "", "",
                  f"{c['clv_cac_ponderado']}:1", "", ""])
    return {
        "titulo": f"Unidad económica por buyer persona ({m})",
        "columnas": ["Buyer persona", "CLV neto base", "CLV neto ajustado",
                     "Δ por cross-sell", "CAC", "CLV:CAC", "Payback", "ROI marketing"],
        "filas": filas,
        "fila_total": True,
        "nota": ("El CLV:CAC consolidado se pondera por clientes del año 1, no se promedia: "
                 "el promedio de dos ratios no corresponde a ningún negocio. "
                 "Δ por cross-sell = cuánto sube el CLV al añadir los productos "
                 "complementarios."),
    }


def _tabla_proyeccion(r):
    m = r["moneda"]
    c = r["resultados"]["consolidado"]
    hay_ebitda = any(x["ebitda_aproximado"] is not None for x in c["por_anio"])
    cols = ["Horizonte", "Clientes nuevos", "Clientes activos", f"MRR ({m})",
            f"ARR ({m})"]
    if hay_ebitda:
        cols.append(f"EBITDA aprox. ({m})")
    filas = []
    for x in c["por_anio"]:
        fila = [f"Año {x['anio']}", f"{x['clientes_nuevos']:,.0f}",
                f"{x['clientes_activos']:,.0f}", f"{x['mrr']:,.0f}", f"{x['arr']:,.0f}"]
        if hay_ebitda:
            fila.append(f"{x['ebitda_aproximado']:,.0f}"
                        if x["ebitda_aproximado"] is not None else "[no disponible]")
        filas.append(fila)
    return {
        "titulo": f"Proyección consolidada a {HORIZONTE} años",
        "columnas": cols,
        "filas": filas,
        "nota": ("Los clientes activos no son la suma de los nuevos: cada año se resta la "
                 "fuga (churn) de la base anterior. El EBITDA es aproximado e incluye el "
                 "CAC de los clientes nuevos de cada año."),
    }


def _grafica(r):
    c = r["resultados"]["consolidado"]
    return {
        "tipo": "line",
        "titulo": f"ARR y clientes activos por año ({r['moneda']})",
        "eje_x": "Año",
        "eje_y": r["moneda"],
        "labels": [f"Año {x['anio']}" for x in c["por_anio"]],
        "datasets": [
            {"label": f"ARR ({r['moneda']})", "data": [x["arr"] for x in c["por_anio"]]},
            {"label": "Clientes activos",
             "data": [x["clientes_activos"] for x in c["por_anio"]]},
        ],
    }


def seccion_reporte(r):
    m = r["moneda"]
    c = r["resultados"]["consolidado"]
    items = [{
        "titulo": "Unidad económica consolidada",
        "subtitulo": (
            f"CLV:CAC {c['clv_cac_ponderado']}:1 · ARR año 1 "
            f"{c['arr_hitos']['arr_anio_1']:,.0f} {m} · año 5 "
            f"{c['arr_hitos']['arr_anio_5']:,.0f} {m}"
        ),
        "tags": ["modelo", "unidad económica"],
        "body": [{"label": e["valor"],
                  "texto": f"{e['lectura']}\n\nCómo se calcula: {e['formula_palabras']}\n"
                           f"Fórmula: {e['formula_libro']}"}
                 for e in r["explicacion"]],
        "tabla": [r["tabla_unidad_economica"], r["tabla_proyeccion"]],
        "chart": r["grafica"],
    }]
    for bp in r["resultados"]["buyer_personas"]:
        res, e = bp["resultados"], bp["entradas"]
        tablas = [{
            "titulo": f"Métricas unitarias — {bp['nombre']} ({m})",
            "columnas": ["Métrica", "Valor", "De dónde sale"],
            "filas": [
                ["Ticket promedio", f"{e['ticket_promedio']:,.0f}", "supuesto declarado"],
                ["Frecuencia anual", f"{e['frecuencia_anual']:g}", "supuesto declarado"],
                ["Vida del cliente (años)", f"{e['vida_cliente_anios']:g}",
                 "supuesto declarado"],
                ["Margen bruto", _pct(e["margen_bruto"]), "supuesto declarado"],
                ["Ingreso anual por cliente", f"{res['ingreso_anual_por_cliente']:,.0f}",
                 "ticket × frecuencia"],
                ["Cross-selling anual", f"{res['cross_sell_anual_por_cliente']:,.0f}",
                 "Σ ticket × probabilidad × frecuencia"],
                ["CLV neto ajustado", f"{res['clv_neto_ajustado']:,.0f}",
                 "(ingreso + cross-sell) × vida × margen"],
                ["CAC", f"{e['cac']:,.0f}", "supuesto declarado"],
                ["CLV:CAC", f"{res['clv_cac']}:1 ({res['calificacion_clv_cac']})",
                 "CLV neto ajustado / CAC"],
                ["Payback",
                 (f"{res['payback_meses']} meses" if res["payback_meses"] is not None
                  else "[no disponible]"), "CAC / contribución mensual"],
                ["Churn anual", _pct(e["churn_anual"]), "supuesto declarado"],
                ["Vida implícita por churn",
                 (f"{res['vida_implicita_por_churn']} años"
                  if res["vida_implicita_por_churn"] else "[no disponible]"),
                 "1 / churn — comprobación contra la vida declarada"],
            ],
            "nota": f"Supuestos: {bp['supuestos']}",
        }]
        if bp["cross_selling"]:
            tablas.append({
                "titulo": f"Cross-selling — {bp['nombre']} ({m})",
                "columnas": ["Producto", "Ticket", "Probabilidad de adopción",
                             "Frecuencia anual", "Ingreso esperado anual"],
                "filas": [[cs["producto"], f"{cs['ticket']:,.0f}",
                           _pct(cs["probabilidad_adopcion"]),
                           f"{cs['frecuencia_anual']:g}",
                           f"{cs['ingreso_esperado_anual']:,.0f}"]
                          for cs in bp["cross_selling"]]
                         + [["TOTAL", "", "", "",
                             f"{res['cross_sell_anual_por_cliente']:,.0f}"]],
                "fila_total": True,
                "nota": "El ingreso esperado ya está multiplicado por la probabilidad de "
                        "adopción: es un promedio sobre muchos clientes, no lo que paga uno.",
            })
        if bp["canales"]:
            tablas.append({
                "titulo": f"CAC por canal — {bp['nombre']} ({m})",
                "columnas": ["Canal", "CAC", "Peso en la mezcla", "CAC ponderado"],
                "filas": [[ch["nombre"], f"{ch['cac']:,.0f}", _pct(ch["peso"], 0),
                           f"{ch.get('cac_ponderado', 0):,.0f}"] for ch in bp["canales"]],
                "fila_total": True,
            })
        items.append({
            "titulo": bp["nombre"],
            "subtitulo": (
                f"CLV {res['clv_neto_ajustado']:,.0f} {m} · CAC {e['cac']:,.0f} · "
                f"CLV:CAC {res['clv_cac']}:1 ({res['calificacion_clv_cac']})"
            ),
            "tags": ["modelo", res["calificacion_clv_cac"]],
            "veredicto": ("perseverar" if res["clv_cac"] >= 3
                          else "pivotear" if res["clv_cac"] >= 1 else "descartar"),
            "body": [
                {"label": "Lectura del ratio", "texto": bp["lectura_ratio"]},
                {"label": "Supuestos declarados", "texto": bp["supuestos"]},
            ],
            "tabla": tablas,
            "chart": {
                "tipo": "line",
                "titulo": f"ARR y clientes activos — {bp['nombre']}",
                "eje_x": "Año", "eje_y": m,
                "labels": [f"Año {x['anio']}" for x in bp["proyeccion"]],
                "datasets": [
                    {"label": f"ARR ({m})", "data": [x["arr"] for x in bp["proyeccion"]]},
                    {"label": "Clientes activos",
                     "data": [x["clientes_activos"] for x in bp["proyeccion"]]},
                ],
            },
        })
    return {"titulo": "Modelo de negocio y unidad económica", "items": items}


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Unidad económica del Dimensionador: CLV, CAC, payback, ARR, EBITDA.")
    ap.add_argument("--datos", help="JSON con las métricas unitarias por buyer persona")
    ap.add_argument("--plantilla", action="store_true",
                    help="Imprime el esqueleto de entrada y termina")
    ap.add_argument("-o", "--output", default="unidad_economica.json",
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

    m = r["moneda"]
    for bp in r["resultados"]["buyer_personas"]:
        res = bp["resultados"]
        print(f"{bp['nombre']}: CLV {res['clv_neto_ajustado']:,.0f} {m} · "
              f"CLV:CAC {res['clv_cac']}:1 ({res['calificacion_clv_cac']}) · "
              f"payback {res['payback_meses']} meses")
    c = r["resultados"]["consolidado"]
    print(f"\nConsolidado: CLV:CAC {c['clv_cac_ponderado']}:1 · "
          f"ARR año 1 {c['arr_hitos']['arr_anio_1']:,.0f} · "
          f"año 5 {c['arr_hitos']['arr_anio_5']:,.0f} {m}")
    for a in r["advertencias"][1:]:
        print(f"\n[AVISO] {a}")
    print(f"\nCálculo guardado en: {args.output}")
    if args.seccion_reporte:
        print(f"Sección para el reporte en: {args.seccion_reporte}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
