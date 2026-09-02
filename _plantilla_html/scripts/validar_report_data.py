"""
validar_report_data.py — validador del esquema REPORT_DATA.

Un `reporte.json` mal formado no rompe el generador: produce un HTML que abre
en blanco. Con 11 reportes encadenados eso pasa desapercibido. Este validador
convierte ese fallo silencioso en un error explícito antes de escribir el HTML.

`generar_html.py` lo ejecuta por defecto. También se puede usar solo:

    python _plantilla_html/scripts/validar_report_data.py reporte.json
    python _plantilla_html/scripts/validar_report_data.py reporte.json --sin-flujo

Salida: 0 sin errores · 2 con errores · 1 archivo ilegible.
Los avisos (WARN) no bloquean.
"""
import argparse
import json
import sys
from pathlib import Path

VEREDICTOS = {"perseverar", "pivotear", "descartar"}
TIPOS_CHART = {"bar", "horizontalBar", "line", "doughnut", "pie", "scatter"}
ESTADOS_RUTA = {"pendiente", "en_curso", "completado", "omitido", "fallido", "actual"}
COBERTURA = {"si", "sí", "parcial", "no"}       # psf.problemas[].cubre
ORIGENES_DATOS = {"reales", "simulados", "mixtos"}   # meta.origen_datos.tipo


class Hallazgo:
    def __init__(self, nivel, ruta, mensaje, arreglo=None):
        self.nivel = nivel          # "ERROR" | "WARN"
        self.ruta = ruta            # p.ej. secciones[0].items[2]
        self.mensaje = mensaje
        self.arreglo = arreglo

    def __str__(self):
        base = f"[{self.nivel}] {self.ruta}: {self.mensaje}"
        if self.arreglo:
            base += f"\n         → {self.arreglo}"
        return base


def _texto(v):
    return isinstance(v, str) and v.strip() != ""


def validar(data, exigir_flujo=True):
    h = []

    if not isinstance(data, dict):
        return [Hallazgo("ERROR", "raíz", "REPORT_DATA debe ser un objeto JSON")]

    # ----------------------------------------------------------------- meta
    meta = data.get("meta")
    if not isinstance(meta, dict):
        h.append(Hallazgo("ERROR", "meta", "falta el objeto `meta`",
                          "meta = {titulo, skill, fase}"))
        meta = {}
    for campo in ("titulo", "skill", "fase"):
        if not _texto(meta.get(campo)):
            h.append(Hallazgo("ERROR", f"meta.{campo}", "vacío u ausente"))
    if not _texto(meta.get("resumen")) and not _texto(meta.get("subtitulo")):
        h.append(Hallazgo("WARN", "meta", "sin `resumen` ni `subtitulo`: el hero "
                                          "del reporte queda sin bajada"))
    elif not _texto(meta.get("resumen")):
        h.append(Hallazgo("WARN", "meta.resumen",
                          "sin `resumen`: el bloque «En resumen» no tendrá conclusión",
                          "escribe 2-3 líneas de qué se concluye del análisis"))

    # ------------------------------------------------------------- secciones
    secciones = data.get("secciones")
    if not isinstance(secciones, list) or not secciones:
        h.append(Hallazgo("ERROR", "secciones",
                          "debe ser una lista con al menos una sección",
                          "sin secciones el HTML abre vacío"))
        secciones = []

    total_items = 0
    for i, sec in enumerate(secciones):
        ruta_s = f"secciones[{i}]"
        if not isinstance(sec, dict):
            h.append(Hallazgo("ERROR", ruta_s, "no es un objeto"))
            continue
        if not _texto(sec.get("titulo")):
            h.append(Hallazgo("ERROR", f"{ruta_s}.titulo", "vacío u ausente"))
        items = sec.get("items")
        if not isinstance(items, list) or not items:
            h.append(Hallazgo("ERROR", f"{ruta_s}.items",
                              "debe ser una lista con al menos un item"))
            continue
        for j, it in enumerate(items):
            ruta_i = f"{ruta_s}.items[{j}]"
            total_items += 1
            if not isinstance(it, dict):
                h.append(Hallazgo("ERROR", ruta_i, "no es un objeto"))
                continue
            if not _texto(it.get("titulo")):
                h.append(Hallazgo("ERROR", f"{ruta_i}.titulo", "vacío u ausente"))
            ver = it.get("veredicto")
            if ver is not None and ver not in VEREDICTOS:
                h.append(Hallazgo("ERROR", f"{ruta_i}.veredicto",
                                  f"«{ver}» no es válido",
                                  f"usa uno de: {', '.join(sorted(VEREDICTOS))}"))
            if it.get("score") is not None and not isinstance(
                it["score"], (int, float)
            ):
                h.append(Hallazgo("ERROR", f"{ruta_i}.score", "debe ser numérico"))
            for k, tag in enumerate(it.get("tags") or []):
                if not _texto(tag):
                    h.append(Hallazgo("WARN", f"{ruta_i}.tags[{k}]", "tag vacío"))
            body = it.get("body")
            if body is not None:
                if not isinstance(body, list):
                    h.append(Hallazgo("ERROR", f"{ruta_i}.body", "debe ser una lista"))
                else:
                    for k, b in enumerate(body):
                        if not isinstance(b, dict) or not _texto(b.get("texto")):
                            h.append(Hallazgo("ERROR", f"{ruta_i}.body[{k}]",
                                              "cada bloque necesita `texto`"))
            if (not body and not _texto(it.get("subtitulo"))
                    and not it.get("persona") and not it.get("psf")
                    and not it.get("tabla")):
                h.append(Hallazgo("WARN", ruta_i,
                                  "sin `body` ni `subtitulo`: la tarjeta se expande vacía"))
            h.extend(_validar_chart(it.get("chart"), f"{ruta_i}.chart"))
            h.extend(_validar_persona(it.get("persona"), f"{ruta_i}.persona"))
            h.extend(_validar_psf(it.get("psf"), f"{ruta_i}.psf"))
            h.extend(_validar_tablas(it.get("tabla"), f"{ruta_i}.tabla"))

    if total_items == 0 and secciones:
        h.append(Hallazgo("ERROR", "secciones", "ninguna sección tiene items"))

    # ------------------------------------------------------------------ kpis
    kpis = data.get("kpis")
    if kpis is not None:
        if not isinstance(kpis, list):
            h.append(Hallazgo("ERROR", "kpis", "debe ser una lista"))
        else:
            for i, k in enumerate(kpis):
                if not isinstance(k, dict) or not _texto(k.get("label")):
                    h.append(Hallazgo("ERROR", f"kpis[{i}].label", "vacío u ausente"))
                elif k.get("value") in (None, ""):
                    h.append(Hallazgo("ERROR", f"kpis[{i}].value", "vacío u ausente"))

    # ------------------------------------------------------------ decisiones
    decs = data.get("decisiones")
    if decs is not None:
        if not isinstance(decs, list):
            h.append(Hallazgo("ERROR", "decisiones", "debe ser una lista"))
        else:
            for i, d in enumerate(decs):
                if not isinstance(d, dict):
                    h.append(Hallazgo("ERROR", f"decisiones[{i}]", "no es un objeto"))
                    continue
                if not _texto(d.get("titulo")):
                    h.append(Hallazgo("ERROR", f"decisiones[{i}].titulo", "vacío"))
                ver = d.get("veredicto")
                if ver is not None and ver not in VEREDICTOS:
                    h.append(Hallazgo("ERROR", f"decisiones[{i}].veredicto",
                                      f"«{ver}» no es válido"))

    for campo in ("advertencias", "fuentes"):
        val = data.get(campo)
        if val is not None:
            if not isinstance(val, list):
                h.append(Hallazgo("ERROR", campo, "debe ser una lista de textos"))
            else:
                for i, s in enumerate(val):
                    if isinstance(s, (dict, list)):
                        # La plantilla las pinta con `esc(s)`: un objeto saldría como
                        # «[object Object]» sin que nadie se enterase. Decir «vacía»
                        # despistaba, porque el problema es el tipo, no la falta de texto.
                        h.append(Hallazgo(
                            "ERROR", f"{campo}[{i}]",
                            f"es un {type(s).__name__}, y aquí van textos planos: "
                            f"escribe la frase completa en una sola cadena"))
                    elif not _texto(s):
                        h.append(Hallazgo("WARN", f"{campo}[{i}]", "entrada vacía"))

    # ----------------------------------------------------------------- flujo
    h.extend(_validar_flujo(data.get("flujo"), exigir_flujo))
    h.extend(_validar_simulacion(data))
    h.extend(_validar_score_justificado(data))
    return h


def _validar_score_justificado(data):
    """Un puntaje sin explicación de dónde sale.

    Viene de una fricción real del uso: «no me quedó claro de dónde sacó los datos
    que estoy marcando (urgencia, diferenciación, escalabilidad…)». El puntaje
    aparecía en la tarjeta y su desglose se quedaba en la conversación. Es un aviso
    agregado —uno por reporte, no uno por idea— para no sepultar el resto.
    """
    sin_justificar = []
    for sec in data.get("secciones") or []:
        for item in (sec or {}).get("items") or []:
            if not isinstance(item, dict):
                continue
            if not isinstance(item.get("score"), (int, float)) or isinstance(
                item.get("score"), bool
            ):
                continue
            tablas = item.get("tabla")
            tablas = tablas if isinstance(tablas, list) else ([tablas] if tablas else [])
            en_tabla = any(
                any("justific" in str(c).lower() for c in (t or {}).get("columnas") or [])
                for t in tablas if isinstance(t, dict)
            )
            en_body = any(
                "justific" in str(b.get("label", "")).lower()
                or "criterio" in str(b.get("label", "")).lower()
                for b in item.get("body") or [] if isinstance(b, dict)
            )
            if not en_tabla and not en_body:
                sin_justificar.append(str(item.get("titulo") or "sin título"))
    if not sin_justificar:
        return []
    muestra = ", ".join(sin_justificar[:3])
    resto = f" (y {len(sin_justificar) - 3} más)" if len(sin_justificar) > 3 else ""
    return [Hallazgo(
        "WARN", "secciones[].items[].score",
        f"{len(sin_justificar)} item(s) con puntaje y sin decir de dónde sale: "
        f"{muestra}{resto}",
        "añade un bloque `tabla` con las columnas criterio / puntaje / justificación "
        "—o un `body` con label «Justificación»—, para que el desglose viaje al HTML "
        "y no se quede solo en la conversación")]


def _validar_simulacion(data):
    """Coherencia de la marca de datos simulados.

    La plantilla añade la advertencia por su cuenta si falta, así que esto es un aviso,
    no un error: existe para que la skill no delegue en el HTML algo que también tiene
    que constar en su contrato JSON y en el `base` de sus datos.
    """
    h = []
    meta = data.get("meta") or {}
    flujo = data.get("flujo") or {}
    sim = flujo.get("simulacion") or {}
    activo = bool(sim.get("activo")) or bool(meta.get("simulado"))

    if meta.get("simulado") is not None and not isinstance(meta["simulado"], bool):
        h.append(Hallazgo("ERROR", "meta.simulado",
                          "debe ser true o false (marca de datos simulados)"))

    # Procedencia de los datos DE ESTE PASO. La marca de simulación es del proyecto y
    # viaja a todos los reportes posteriores; esto permite decir «este paso en concreto
    # es real» sin apagarla, en vez de escribirlo a mano en cada reporte.
    org = meta.get("origen_datos")
    if org is not None:
        if not isinstance(org, dict):
            h.append(Hallazgo("ERROR", "meta.origen_datos",
                              "debe ser un objeto {tipo, nota}",
                              f"tipo es uno de: {', '.join(sorted(ORIGENES_DATOS))}"))
        else:
            tipo = org.get("tipo")
            if tipo not in ORIGENES_DATOS:
                h.append(Hallazgo("ERROR", "meta.origen_datos.tipo",
                                  f"«{tipo}» no es válido",
                                  f"usa uno de: {', '.join(sorted(ORIGENES_DATOS))}"))
            elif tipo in ("reales", "mixtos") and not _texto(org.get("nota")):
                h.append(Hallazgo(
                    "WARN", "meta.origen_datos.nota",
                    f"declara «{tipo}» pero no dice con qué",
                    "escribe la evidencia concreta (p. ej. «42 entrevistas reales de tres "
                    "perfiles»): la afirmación sin el dato no se puede comprobar"))

    if not activo:
        if org is not None:
            h.append(Hallazgo(
                "WARN", "meta.origen_datos",
                "el proyecto no arrastra marca de simulación, así que este campo no se "
                "renderiza",
                "solo se pinta cuando hay simulación en el proyecto y hay que aclarar la "
                "procedencia de este paso en concreto"))
        return h

    if org is None:
        h.append(Hallazgo(
            "WARN", "meta.origen_datos",
            "el proyecto arrastra marca de simulación y este reporte no declara de dónde "
            "salen SUS datos",
            "añade meta.origen_datos = {tipo: reales|simulados|mixtos, nota: \"…\"}; si no, "
            "el lector supone que todo el paso es simulado"))

    advertencias = data.get("advertencias")
    textos = [str(a) for a in advertencias] if isinstance(advertencias, list) else []
    if not any("simulad" in t.lower() for t in textos):
        h.append(Hallazgo(
            "WARN", "advertencias",
            "el reporte es de datos simulados y ninguna advertencia lo dice",
            "añade una que declare qué se simuló, con qué n y con qué semilla; la "
            "plantilla pone una genérica, pero la específica es la que sirve"))

    etiquetados = 0
    total_items = 0
    for sec in data.get("secciones") or []:
        for item in (sec or {}).get("items") or []:
            if not isinstance(item, dict):
                continue
            total_items += 1
            tags = [str(t).lower() for t in (item.get("tags") or [])]
            if any("simulad" in t for t in tags):
                etiquetados += 1
    if total_items and not etiquetados:
        h.append(Hallazgo(
            "WARN", "secciones[].items[].tags",
            "ningún item lleva el tag SIMULADO",
            "los filtros del reporte se navegan por tags: sin él, un item simulado se "
            "lee igual que uno con evidencia real"))
    return h


def _validar_persona(p, ruta):
    """Ficha con la estructura del template Persona Profile."""
    if p is None:
        return []
    if not isinstance(p, dict):
        return [Hallazgo("ERROR", ruta, "debe ser un objeto")]
    h = []

    if not _texto(p.get("jtbd")):
        h.append(Hallazgo("ERROR", f"{ruta}.jtbd", "vacío u ausente",
                          "es el corazón de la ficha: «Cuando…, quiero…, para…»"))
    elif not all(k in p["jtbd"].lower() for k in ("cuando", "quiero", "para")):
        h.append(Hallazgo("WARN", f"{ruta}.jtbd",
                          "no sigue el formato «Cuando… quiero… para…» del template"))

    ident = p.get("identidad")
    if not isinstance(ident, dict):
        h.append(Hallazgo("ERROR", f"{ruta}.identidad",
                          "falta el objeto con nombre, edad y rango de ingresos"))
    else:
        for k in ("nombre", "edad", "ingresos"):
            if not _texto(ident.get(k)):
                h.append(Hallazgo("WARN", f"{ruta}.identidad.{k}",
                                  "vacío: usa `[no disponible]` si no se sabe"))

    if not _texto(p.get("base")):
        h.append(Hallazgo("WARN", f"{ruta}.base",
                          "sin «Con base en»: no se sabe si la persona es validada "
                          "o hipotética"))

    for campo in ("metas", "momentos_vitales", "accionables", "anexo"):
        val = p.get(campo)
        if val is None:
            if campo in ("metas", "momentos_vitales"):
                h.append(Hallazgo("ERROR", f"{ruta}.{campo}",
                                  "falta; es una sección obligatoria del template"))
            continue
        if not isinstance(val, list):
            h.append(Hallazgo("ERROR", f"{ruta}.{campo}", "debe ser una lista de textos"))
        elif not val:
            h.append(Hallazgo("WARN", f"{ruta}.{campo}", "lista vacía"))

    for campo, etiqueta in (("donde_esta", "¿Dónde está?"),
                            ("confianza", "¿En quién confía?")):
        par = p.get(campo)
        if par is None:
            h.append(Hallazgo("ERROR", f"{ruta}.{campo}",
                              f"falta el par físico/digital de «{etiqueta}»"))
            continue
        if not isinstance(par, dict):
            h.append(Hallazgo("ERROR", f"{ruta}.{campo}",
                              "debe ser un objeto con `fisico` y `digital`"))
            continue
        for lado in ("fisico", "digital"):
            v = par.get(lado)
            if v is None:
                h.append(Hallazgo("WARN", f"{ruta}.{campo}.{lado}",
                                  "sin canal declarado"))
            elif not isinstance(v, list):
                h.append(Hallazgo("ERROR", f"{ruta}.{campo}.{lado}",
                                  "debe ser una lista de textos"))

    # Pains: la lista de dolores es de la persona. Su evaluación (solución actual,
    # costo, importancia y satisfacción) la produce problem-solution-fit en el paso
    # siguiente, así que aquí es opcional: solo se exige coherencia si viene.
    pains = p.get("pains")
    if not isinstance(pains, list) or not pains:
        h.append(Hallazgo("ERROR", f"{ruta}.pains",
                          "debe listar al menos un pain",
                          "cada pain necesita `texto`; la evaluación (`solucion`, "
                          "`costo`, `importancia`, `satisfaccion`) es opcional: sale "
                          "de problem-solution-fit"))
        return h
    con_evaluacion = 0
    for i, d in enumerate(pains):
        r = f"{ruta}.pains[{i}]"
        if not isinstance(d, dict):
            h.append(Hallazgo("ERROR", r, "no es un objeto"))
            continue
        if not _texto(d.get("texto")):
            h.append(Hallazgo("ERROR", f"{r}.texto", "vacío u ausente"))
        if any(d.get(k) is not None and d.get(k) != ""
               for k in ("solucion", "costo", "importancia", "satisfaccion")):
            con_evaluacion += 1
        for k in ("importancia", "satisfaccion"):
            v = d.get(k)
            if v is None:
                continue
            if not isinstance(v, (int, float)) or isinstance(v, bool):
                h.append(Hallazgo("ERROR", f"{r}.{k}", "debe ser numérico (0 a 5)"))
            elif not 0 <= v <= 5:
                h.append(Hallazgo("ERROR", f"{r}.{k}", f"{v} está fuera del rango 0–5"))
        if (d.get("importancia") is None) != (d.get("satisfaccion") is None):
            h.append(Hallazgo("WARN", r,
                              "tiene solo uno de `importancia` / `satisfaccion`",
                              "van en par: con uno solo el pain no entra en la matriz"))
    if 0 < con_evaluacion < len(pains):
        h.append(Hallazgo("WARN", f"{ruta}.pains",
                          f"{con_evaluacion} de {len(pains)} pains traen evaluación",
                          "o la traen todos (viene de problem-solution-fit) o ninguno: "
                          "mezclarlos deja la tabla y la matriz incompletas"))
    return h


def _validar_psf(p, ruta):
    """Análisis del template Problem-Solution Fit (evaluación de los pains)."""
    if p is None:
        return []
    if not isinstance(p, dict):
        return [Hallazgo("ERROR", ruta, "debe ser un objeto")]
    h = []

    if not _texto(p.get("base")):
        h.append(Hallazgo("WARN", f"{ruta}.base",
                          "sin «Con base en»: no se sabe de qué evidencia sale la "
                          "evaluación (`N entrevistas` / `N encuestas` / `SIMULADO`)"))
    if not _texto(p.get("solucion_propuesta")):
        h.append(Hallazgo("WARN", f"{ruta}.solucion_propuesta",
                          "sin solución declarada: `cubre` queda sin referente"))

    problemas = p.get("problemas")
    if not isinstance(problemas, list) or not problemas:
        return h + [Hallazgo("ERROR", f"{ruta}.problemas",
                             "debe listar al menos un problema evaluado",
                             "cada problema lleva `problema`, `importancia`, "
                             "`satisfaccion`, `costo_tiempo`, `costo_dinero` y `cubre`")]

    for i, d in enumerate(problemas):
        r = f"{ruta}.problemas[{i}]"
        if not isinstance(d, dict):
            h.append(Hallazgo("ERROR", r, "no es un objeto"))
            continue
        if not _texto(d.get("problema")) and not _texto(d.get("texto")):
            h.append(Hallazgo("ERROR", f"{r}.problema", "vacío u ausente"))
        for k in ("importancia", "satisfaccion"):
            v = d.get(k)
            if v is None:
                h.append(Hallazgo("WARN", f"{r}.{k}",
                                  "sin valor: el problema no aparecerá en la matriz "
                                  "Importancia × Satisfacción"))
            elif not isinstance(v, (int, float)) or isinstance(v, bool):
                h.append(Hallazgo("ERROR", f"{r}.{k}", "debe ser numérico (0 a 5)"))
            elif not 0 <= v <= 5:
                h.append(Hallazgo("ERROR", f"{r}.{k}", f"{v} está fuera del rango 0–5"))
        for k in ("costo_tiempo", "costo_dinero", "solucion_actual"):
            if not _texto(d.get(k)):
                h.append(Hallazgo("WARN", f"{r}.{k}",
                                  "vacío: usa `N/D` si no hubo cita explícita, o "
                                  "`[ESTIMACIÓN]` si se infiere"))
        cubre = d.get("cubre")
        if cubre is None:
            h.append(Hallazgo("WARN", f"{r}.cubre",
                              "sin veredicto de encaje: usa `si` / `parcial` / `no`"))
        elif str(cubre).strip().lower() not in COBERTURA:
            h.append(Hallazgo("ERROR", f"{r}.cubre", f"«{cubre}» no es válido",
                              f"usa uno de: {', '.join(sorted(COBERTURA))}"))

    for campo in ("patrones", "blue_ocean"):
        val = p.get(campo)
        if val is None:
            h.append(Hallazgo("WARN", f"{ruta}.{campo}",
                              "falta; es una sección del análisis"))
        elif not isinstance(val, list):
            h.append(Hallazgo("ERROR", f"{ruta}.{campo}", "debe ser una lista de textos"))
        elif not val:
            h.append(Hallazgo("WARN", f"{ruta}.{campo}", "lista vacía"))

    if not _texto(p.get("jtbd")):
        h.append(Hallazgo("WARN", f"{ruta}.jtbd",
                          "sin JTBD: el análisis pierde el «trabajo» que el usuario "
                          "intenta resolver"))
    return h


def _validar_tablas(tabla, ruta):
    """Bloque `tabla`: una tabla o una lista de tablas dentro de un item.

    Existe para el contenido que como párrafo se lee mal —la matriz criterio →
    puntaje → justificación del score, una proyección año a año, un desglose por
    buyer persona—. Una fila con menos celdas que columnas sale desalineada sin
    que el HTML se queje, así que eso es error, no aviso.
    """
    if tabla is None:
        return []
    tablas = tabla if isinstance(tabla, list) else [tabla]
    if isinstance(tabla, list) and not tablas:
        return [Hallazgo("WARN", ruta, "lista de tablas vacía")]
    h = []
    for i, t in enumerate(tablas):
        r = ruta if not isinstance(tabla, list) else f"{ruta}[{i}]"
        if not isinstance(t, dict):
            h.append(Hallazgo("ERROR", r, "debe ser un objeto "
                                          "{titulo, columnas, filas}"))
            continue
        cols = t.get("columnas")
        if not isinstance(cols, list) or not cols:
            h.append(Hallazgo("ERROR", f"{r}.columnas",
                              "debe ser una lista no vacía de encabezados"))
            cols = []
        else:
            for j, c in enumerate(cols):
                if not _texto(c):
                    h.append(Hallazgo("WARN", f"{r}.columnas[{j}]",
                                      "encabezado vacío"))
        filas = t.get("filas")
        if not isinstance(filas, list) or not filas:
            h.append(Hallazgo("ERROR", f"{r}.filas",
                              "debe ser una lista no vacía de filas",
                              "cada fila es una lista de celdas, en el orden de "
                              "`columnas`"))
            continue
        for j, fila in enumerate(filas):
            if not isinstance(fila, list):
                h.append(Hallazgo("ERROR", f"{r}.filas[{j}]",
                                  "debe ser una lista de celdas"))
                continue
            if cols and len(fila) != len(cols):
                h.append(Hallazgo("ERROR", f"{r}.filas[{j}]",
                                  f"{len(fila)} celdas contra {len(cols)} columnas",
                                  "la tabla sale desalineada; usa \"\" en las celdas "
                                  "que no apliquen"))
            for k, celda in enumerate(fila):
                if isinstance(celda, (dict, list)):
                    h.append(Hallazgo("ERROR", f"{r}.filas[{j}][{k}]",
                                      f"es un {type(celda).__name__}; en una celda "
                                      "van texto o números"))
        if t.get("fila_total") is not None and not isinstance(t["fila_total"], bool):
            h.append(Hallazgo("ERROR", f"{r}.fila_total",
                              "debe ser true o false (resalta la última fila)"))
        if t.get("nota") is not None and not _texto(t.get("nota")):
            h.append(Hallazgo("WARN", f"{r}.nota", "nota vacía"))
    return h


def _validar_chart(chart, ruta):
    if chart is None:
        return []
    h = []
    if not isinstance(chart, dict):
        return [Hallazgo("ERROR", ruta, "debe ser un objeto")]
    tipo = chart.get("tipo", "bar")
    if tipo not in TIPOS_CHART:
        h.append(Hallazgo("ERROR", f"{ruta}.tipo", f"«{tipo}» no está soportado",
                          f"usa uno de: {', '.join(sorted(TIPOS_CHART))}"))

    if tipo == "scatter":
        puntos = chart.get("puntos")
        if not isinstance(puntos, list) or not puntos:
            h.append(Hallazgo("ERROR", f"{ruta}.puntos",
                              "un scatter necesita `puntos` con `x` e `y`"))
            return h
        for i, pt in enumerate(puntos):
            if not isinstance(pt, dict):
                h.append(Hallazgo("ERROR", f"{ruta}.puntos[{i}]", "no es un objeto"))
                continue
            for k in ("x", "y"):
                if not isinstance(pt.get(k), (int, float)):
                    h.append(Hallazgo("ERROR", f"{ruta}.puntos[{i}].{k}",
                                      "debe ser numérico"))
        return h

    labels = chart.get("labels")
    if not isinstance(labels, list) or not labels:
        h.append(Hallazgo("ERROR", f"{ruta}.labels",
                          "debe ser una lista no vacía"))
        labels = []
    datasets = chart.get("datasets")
    if datasets is None:
        if not isinstance(chart.get("data"), list):
            h.append(Hallazgo("ERROR", f"{ruta}.datasets",
                              "falta `datasets` (o `data` como atajo)"))
        return h
    if not isinstance(datasets, list) or not datasets:
        h.append(Hallazgo("ERROR", f"{ruta}.datasets", "debe ser una lista no vacía"))
        return h
    for i, ds in enumerate(datasets):
        if not isinstance(ds, dict):
            h.append(Hallazgo("ERROR", f"{ruta}.datasets[{i}]", "no es un objeto"))
            continue
        data = ds.get("data")
        if not isinstance(data, list) or not data:
            h.append(Hallazgo("ERROR", f"{ruta}.datasets[{i}].data",
                              "debe ser una lista de números"))
            continue
        no_num = [k for k, v in enumerate(data) if not isinstance(v, (int, float))
                  and v is not None]
        if no_num:
            h.append(Hallazgo("ERROR", f"{ruta}.datasets[{i}].data",
                              f"valores no numéricos en las posiciones {no_num}"))
        if labels and len(data) != len(labels):
            h.append(Hallazgo("ERROR", f"{ruta}.datasets[{i}].data",
                              f"{len(data)} valores contra {len(labels)} labels",
                              "la gráfica se dibuja desalineada"))
    return h


def _validar_flujo(flujo, exigir):
    if flujo is None:
        if exigir:
            return [Hallazgo(
                "ERROR", "flujo",
                "falta el bloque de contexto del flujo",
                "genera el HTML con --estado flujo_estado.json --paso html_N, "
                "o pasa --sin-flujo si el reporte es de una skill suelta")]
        return []
    h = []
    if not isinstance(flujo, dict):
        return [Hallazgo("ERROR", "flujo", "debe ser un objeto")]
    if not _texto(flujo.get("paso_actual")):
        h.append(Hallazgo("ERROR", "flujo.paso_actual", "vacío u ausente"))
    ruta = flujo.get("ruta")
    if not isinstance(ruta, list) or not ruta:
        h.append(Hallazgo("ERROR", "flujo.ruta",
                          "debe listar los pasos del flujo con su estado"))
        return h
    ids = set()
    for i, p in enumerate(ruta):
        r = f"flujo.ruta[{i}]"
        if not isinstance(p, dict):
            h.append(Hallazgo("ERROR", r, "no es un objeto"))
            continue
        if not _texto(p.get("id")):
            h.append(Hallazgo("ERROR", f"{r}.id", "vacío u ausente"))
        else:
            ids.add(p["id"])
        est = p.get("estado")
        if est not in ESTADOS_RUTA:
            h.append(Hallazgo("ERROR", f"{r}.estado", f"«{est}» no es válido",
                              f"usa uno de: {', '.join(sorted(ESTADOS_RUTA))}"))
        if est == "omitido" and not _texto(p.get("impacto")):
            h.append(Hallazgo("WARN", f"{r}.impacto",
                              "paso omitido sin impacto declarado: el lector no "
                              "sabe qué le falta a este reporte"))
    actual = flujo.get("paso_actual")
    if actual and ids and actual not in ids:
        h.append(Hallazgo("ERROR", "flujo.paso_actual",
                          f"«{actual}» no aparece en flujo.ruta"))
    if sum(1 for p in ruta if isinstance(p, dict) and p.get("estado") == "actual") > 1:
        h.append(Hallazgo("ERROR", "flujo.ruta",
                          "más de un paso marcado como `actual`"))
    return h


def reportar(hallazgos, destino=sys.stderr):
    errores = [x for x in hallazgos if x.nivel == "ERROR"]
    avisos = [x for x in hallazgos if x.nivel == "WARN"]
    for x in errores + avisos:
        print(str(x), file=destino)
    if errores:
        print(f"\n{len(errores)} error(es) en reporte.json. No se generó el HTML.",
              file=destino)
    elif avisos:
        print(f"\n{len(avisos)} aviso(s). El HTML se generó igualmente.",
              file=destino)
    return errores


def main(argv=None):
    ap = argparse.ArgumentParser(description="Valida un reporte.json (REPORT_DATA).")
    ap.add_argument("data", help="Ruta del reporte.json")
    ap.add_argument("--sin-flujo", action="store_true",
                    help="No exigir el bloque `flujo` de contexto")
    args = ap.parse_args(argv)

    ruta = Path(args.data)
    try:
        data = json.loads(ruta.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"Error: no encuentro {ruta}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"Error: {ruta} no es JSON válido — {exc}", file=sys.stderr)
        return 1

    hallazgos = validar(data, exigir_flujo=not args.sin_flujo)
    errores = reportar(hallazgos)
    if errores:
        return 2
    if not hallazgos:
        print(f"{ruta.name}: esquema válido.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
