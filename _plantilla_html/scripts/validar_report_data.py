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
            if not body and not _texto(it.get("subtitulo")) and not it.get("persona"):
                h.append(Hallazgo("WARN", ruta_i,
                                  "sin `body` ni `subtitulo`: la tarjeta se expande vacía"))
            h.extend(_validar_chart(it.get("chart"), f"{ruta_i}.chart"))
            h.extend(_validar_persona(it.get("persona"), f"{ruta_i}.persona"))

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
                    if not _texto(s):
                        h.append(Hallazgo("WARN", f"{campo}[{i}]", "entrada vacía"))

    # ----------------------------------------------------------------- flujo
    h.extend(_validar_flujo(data.get("flujo"), exigir_flujo))
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

    pains = p.get("pains")
    if not isinstance(pains, list) or not pains:
        h.append(Hallazgo("ERROR", f"{ruta}.pains",
                          "debe listar al menos un pain",
                          "cada pain lleva `texto`, `solucion`, `costo`, "
                          "`importancia` y `satisfaccion`"))
        return h
    for i, d in enumerate(pains):
        r = f"{ruta}.pains[{i}]"
        if not isinstance(d, dict):
            h.append(Hallazgo("ERROR", r, "no es un objeto"))
            continue
        if not _texto(d.get("texto")):
            h.append(Hallazgo("ERROR", f"{r}.texto", "vacío u ausente"))
        for k in ("solucion", "costo"):
            if not _texto(d.get(k)):
                h.append(Hallazgo("WARN", f"{r}.{k}",
                                  "vacío: usa `[no disponible]` si no se sabe"))
        for k in ("importancia", "satisfaccion"):
            v = d.get(k)
            if v is None:
                h.append(Hallazgo("WARN", f"{r}.{k}",
                                  "sin valor: el pain no aparecerá en la matriz "
                                  "Importancia × Satisfacción"))
            elif not isinstance(v, (int, float)):
                h.append(Hallazgo("ERROR", f"{r}.{k}", "debe ser numérico (0 a 5)"))
            elif not 0 <= v <= 5:
                h.append(Hallazgo("ERROR", f"{r}.{k}", f"{v} está fuera del rango 0–5"))
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
