"""
buscar_fuentes.py — búsqueda propia en fuentes públicas y gratuitas.

Complementa (no sustituye) la búsqueda web de la herramienta: consulta por su cuenta
los RSS de medios, los datos abiertos del gobierno de México y la API del Banco
Mundial, y con `--registrar` guarda cada resultado en `fuentes.json` (vía
`fuentes.py`) con su enlace real, listo para citarse como `[Fn]` y verificarse con
`verificar_fuentes.py`. El catálogo está en `_plantilla_html/references/fuentes_publicas.json`:
solo fuentes sin llave y sin muro de pago.

    # notas de medios que mencionan TODAS las palabras, del último año
    python _plantilla_html/scripts/buscar_fuentes.py medios --consulta "remesas México" \
        [--medios eleconomista,expansion] [--dias 365] [--max 15] [--registrar --fuentes fuentes.json]

    # conjuntos de datos abiertos (CONDUSEF, IMSS, Economía, Hacienda… o todo datos.gob.mx)
    python _plantilla_html/scripts/buscar_fuentes.py datos-gob --consulta "quejas" \
        [--organizacion condusef] [--registrar --fuentes fuentes.json]

    # Banco Mundial: buscar el código de un indicador y bajar su serie
    python _plantilla_html/scripts/buscar_fuentes.py banco-mundial --buscar "remittances"
    python _plantilla_html/scripts/buscar_fuentes.py banco-mundial --indicador BX.TRF.PWKR.CD.DT \
        [--pais MX] [--anios 10] [--registrar --fuentes fuentes.json]

    # descubrir comunicados oficiales (CNBV, INEGI, Banxico…): NO citable tal cual
    python _plantilla_html/scripts/buscar_fuentes.py oficiales --consulta "remesas" [--sitio cnbv.gob.mx]

`oficiales` usa Google News: sus enlaces no se pueden descargar, así que solo dice QUÉ
existe y dónde. La URL real se busca con la búsqueda web y se registra con `fuentes.py`.

Salida: 0 con resultados · 4 sin resultados · 1 error.
"""
import argparse
import json
import re
import sys
import unicodedata
import urllib.error
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import date, datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fuentes as F  # noqa: E402 — mismo directorio: la bitácora y la descarga son las de fuentes.py

CATALOGO = Path(__file__).resolve().parent.parent / "references" / "fuentes_publicas.json"


def catalogo():
    return json.loads(CATALOGO.read_text(encoding="utf-8"))


def plano(s):
    s = unicodedata.normalize("NFKD", (s or "").lower())
    return "".join(c for c in s if not unicodedata.combining(c))


def limpiar_html(s):
    ex = F._Extractor()
    ex.feed(s or "")
    return re.sub(r"\s+", " ", ex.texto()).strip()


def de_pago(url, cat):
    host = (urllib.parse.urlparse(url or "").hostname or "").lower()
    return any(host == d or host.endswith("." + d) for d in cat["de_pago_excluidas"])


def obtener(url, timeout=30, intentos=2):
    # Las API públicas (Banco Mundial sobre todo) a veces tardan: un reintento basta.
    for i in range(intentos):
        try:
            crudo, ctype, charset, final = F.descargar(url, timeout=timeout)
            return F.decodificar(crudo, charset), ctype, final
        except (TimeoutError, urllib.error.URLError):
            if i == intentos - 1:
                raise


def fecha_rss(txt):
    if not txt:
        return None
    try:
        d = parsedate_to_datetime(txt)
    except (TypeError, ValueError):
        f = F.normalizar_fecha(txt)
        return datetime.fromisoformat(f).replace(tzinfo=timezone.utc) if f else None
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def items_rss(xml):
    """(titulo, enlace, fecha, descripcion, fuente) de un RSS 2.0 o Atom."""
    raiz = ET.fromstring(xml.encode("utf-8") if isinstance(xml, str) else xml)
    ns = {"a": "http://www.w3.org/2005/Atom"}
    for it in raiz.iter("item"):
        src = it.find("source")
        yield (it.findtext("title") or "", (it.findtext("link") or "").strip(),
               fecha_rss(it.findtext("pubDate") or it.findtext("{http://purl.org/dc/elements/1.1/}date")),
               it.findtext("description") or "",
               (src.text if src is not None else None, src.get("url") if src is not None else None))
    for it in raiz.iter("{http://www.w3.org/2005/Atom}entry"):
        l = it.find("a:link", ns)
        yield (it.findtext("a:title", "", ns), l.get("href") if l is not None else "",
               fecha_rss(it.findtext("a:updated", "", ns) or it.findtext("a:published", "", ns)),
               it.findtext("a:summary", "", ns), (None, None))


def emitir(resultados, etiqueta):
    print(json.dumps({"busqueda": etiqueta, "resultados": len(resultados),
                      "items": resultados}, ensure_ascii=False, indent=2))
    return 0 if resultados else 4


# ---------- medios (RSS) ----------

def cmd_medios(a):
    cat = catalogo()
    medios = cat["medios_rss"]
    elegidos = a.medios.split(",") if a.medios else list(medios)
    desconocidos = [m for m in elegidos if m not in medios]
    if desconocidos:
        print(f"ERROR: medios desconocidos {desconocidos}. Disponibles: {', '.join(medios)}",
              file=sys.stderr)
        return 1
    terminos = [plano(t) for t in a.consulta.split() if len(t) > 2]
    limite = datetime.now(timezone.utc) - timedelta(days=a.dias)
    res, vistos = [], set()
    for mid in elegidos:
        m = medios[mid]
        try:
            xml, _, _ = obtener(m["url"])
            items = list(items_rss(xml))
        except Exception as e:  # noqa: BLE001
            print(f"AVISO: {m['nombre']} no respondió ({type(e).__name__}: {e}); sigo con los demás.",
                  file=sys.stderr)
            continue
        for titulo, enlace, fecha, desc, _ in items:
            texto = plano(titulo + " " + limpiar_html(desc))
            if not all(t in texto for t in terminos) or enlace in vistos:
                continue
            if fecha and fecha < limite:
                continue
            if de_pago(enlace, cat):
                continue
            vistos.add(enlace)
            res.append({"medio": m["nombre"], "titulo": titulo.strip(), "url": enlace,
                        "fecha": fecha.date().isoformat() if fecha else None,
                        "resumen": limpiar_html(desc)[:300]})
    res.sort(key=lambda r: r["fecha"] or "", reverse=True)
    res = res[:a.max]
    if a.registrar:
        for r in res:
            r["fuente"] = registrar_pagina(a.fuentes, r["url"], r["titulo"], r["medio"], "medio",
                                           r["fecha"], r["resumen"])
    print(f"Los RSS solo traen las notas recientes de cada medio (decenas, no el archivo "
          f"completo). Para notas más antiguas, usa la búsqueda web.", file=sys.stderr)
    return emitir(res, f"medios: {a.consulta}")


def registrar_pagina(ruta, url, titulo, medio, tipo, fecha, respaldo):
    """Descarga la nota completa; si no se puede, registra al menos el resumen del RSS."""
    try:
        html, ctype, final = obtener(url)
        ex = F._Extractor()
        ex.feed(html)
        texto = ex.texto()
        fecha = fecha or ex.fecha()
        nota = None
    except Exception as e:  # noqa: BLE001
        texto, final = f"{titulo}\n\n{respaldo}", url
        nota = f"solo el resumen del RSS ({type(e).__name__})"
    entrada, _ = F.registrar(ruta, texto, url=final, titulo=titulo, medio=medio, tipo=tipo,
                             fecha=fecha, capturado_por="script")
    return entrada["id"] + (f" — {nota}" if nota else "")


# ---------- datos.gob.mx ----------

def cmd_datos_gob(a):
    cat = catalogo()["datos_gob"]
    params = {"q": a.consulta, "rows": a.max, "sort": "metadata_modified desc"}
    if a.organizacion:
        if a.organizacion not in cat["organizaciones"]:
            print(f"AVISO: «{a.organizacion}» no está en el catálogo "
                  f"({', '.join(cat['organizaciones'])}); se usa tal cual.", file=sys.stderr)
        params["fq"] = f"organization:{a.organizacion}"
    try:
        txt, _, _ = obtener(cat["api"] + "?" + urllib.parse.urlencode(params))
        datos = json.loads(txt)["result"]["results"]
    except Exception as e:  # noqa: BLE001
        print(f"ERROR: datos.gob.mx no respondió: {e}", file=sys.stderr)
        return 1
    res = []
    for d in datos:
        org = (d.get("organization") or {}).get("title") or (d.get("organization") or {}).get("name")
        recursos = [{"nombre": r.get("name"), "formato": r.get("format"), "url": r.get("url")}
                    for r in d.get("resources", [])]
        url = f"https://www.datos.gob.mx/dataset/{d['name']}"
        item = {"titulo": d.get("title"), "organizacion": org, "url": url,
                "actualizado": (d.get("metadata_modified") or "")[:10],
                "descripcion": limpiar_html(d.get("notes"))[:400], "recursos": recursos[:8]}
        if a.registrar:
            texto = "\n".join([f"{item['titulo']}", f"Publica: {org}",
                               f"Actualizado: {item['actualizado']}", item["descripcion"], ""] +
                              [f"- {r['nombre']} ({r['formato']}): {r['url']}" for r in recursos])
            e, _ = F.registrar(a.fuentes, texto, url=url, titulo=item["titulo"],
                               medio=f"datos.gob.mx — {org}", tipo="oficial",
                               fecha=item["actualizado"] or None, capturado_por="script")
            item["fuente"] = e["id"]
        res.append(item)
    print("Para citar cifras de un conjunto, descarga su CSV con "
          "`fuentes.py capturar --url <url del recurso> --tipo oficial`.", file=sys.stderr)
    return emitir(res, f"datos.gob.mx: {a.consulta}")


# ---------- Banco Mundial ----------

def cmd_banco_mundial(a):
    api = catalogo()["banco_mundial"]["api"]
    if a.buscar:
        try:
            txt, _, _ = obtener(f"{api}/indicator?format=json&per_page=20000&source=2", timeout=60)
            todos = json.loads(txt)[1]
        except Exception as e:  # noqa: BLE001
            print(f"ERROR: la API del Banco Mundial no respondió: {e}", file=sys.stderr)
            return 1
        terminos = [plano(t) for t in a.buscar.split()]
        res = [{"codigo": i["id"], "nombre": i["name"]}
               for i in todos if all(t in plano(i["name"]) for t in terminos)][:a.max]
        print("Los nombres de los indicadores están en inglés: busca en inglés.", file=sys.stderr)
        return emitir(res, f"indicadores: {a.buscar}")
    if not a.indicador:
        print("ERROR: usa --buscar <texto> o --indicador <código>.", file=sys.stderr)
        return 1
    url = (f"{api}/country/{a.pais}/indicator/{a.indicador}?format=json&per_page=200"
           f"&date={date.today().year - a.anios}:{date.today().year}")
    try:
        txt, _, _ = obtener(url)
        meta, serie = json.loads(txt)
    except Exception as e:  # noqa: BLE001
        print(f"ERROR: la API del Banco Mundial no respondió o el código no existe: {e}",
              file=sys.stderr)
        return 1
    serie = [s for s in (serie or []) if s.get("value") is not None]
    if not serie:
        return emitir([], f"{a.indicador} {a.pais}")
    nombre, pais = serie[0]["indicator"]["value"], serie[0]["country"]["value"]
    res = [{"anio": s["date"], "valor": s["value"]} for s in serie]
    item = {"indicador": a.indicador, "nombre": nombre, "pais": pais,
            "actualizado": meta.get("lastupdated"), "serie": res,
            "url": f"https://datos.bancomundial.org/indicador/{a.indicador}?locations={a.pais}"}
    if a.registrar:
        # Cada valor en dos escrituras (crudo y con miles) para que verificar_fuentes lo encuentre.
        lineas = [f"{nombre} — {pais}", f"Fuente: Banco Mundial, WDI. Actualizado {meta.get('lastupdated')}", ""]
        for s in res:
            v = s["valor"]
            lineas.append(f"{s['anio']}: {v} ({v:,})" if isinstance(v, (int, float)) else f"{s['anio']}: {v}")
        e, _ = F.registrar(a.fuentes, "\n".join(lineas), url=item["url"],
                           titulo=f"{nombre} — {pais}", medio="Banco Mundial", tipo="oficial",
                           fecha=meta.get("lastupdated"), capturado_por="script")
        item["fuente"] = e["id"]
    return emitir([item], f"{a.indicador} {a.pais}")


# ---------- descubrimiento oficial (Google News) ----------

def cmd_oficiales(a):
    cat = catalogo()
    disc = cat["descubrimiento_oficial"]
    sitios = [a.sitio] if a.sitio else list(disc["sitios"])
    filtro = " OR ".join(f"site:{s}" for s in sitios)
    q = f"{a.consulta} ({filtro}) when:{a.dias}d"
    url = disc["api"] + "?" + urllib.parse.urlencode(
        {"q": q, "hl": "es-419", "gl": "MX", "ceid": "MX:es-419"})
    try:
        xml, _, _ = obtener(url)
        items = list(items_rss(xml))
    except Exception as e:  # noqa: BLE001
        print(f"ERROR: Google News no respondió: {e}", file=sys.stderr)
        return 1
    res = []
    for titulo, _enlace, fecha, _desc, (fuente, fuente_url) in items[:a.max]:
        res.append({"titulo": titulo.strip(), "fuente": fuente, "sitio": fuente_url,
                    "fecha": fecha.date().isoformat() if fecha else None,
                    "citable": False,
                    "siguiente": "Busca este título con la búsqueda web, abre la página oficial y "
                                 "regístrala con fuentes.py (capturar o agregar)."})
    print("Estos resultados NO son citables tal cual: el enlace de Google News no lleva a la "
          "página original. Úsalos para saber qué publicó cada dependencia.", file=sys.stderr)
    return emitir(res, f"oficiales: {a.consulta}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    def reg(p):
        p.add_argument("--registrar", action="store_true", help="guarda cada resultado en fuentes.json")
        p.add_argument("--fuentes", default="fuentes.json")
        p.add_argument("--max", type=int, default=15)

    p = sub.add_parser("medios", help="notas de medios por RSS")
    p.add_argument("--consulta", required=True)
    p.add_argument("--medios", help="ids del catálogo separados por coma (todos por defecto)")
    p.add_argument("--dias", type=int, default=365)
    reg(p)

    p = sub.add_parser("datos-gob", help="conjuntos de datos abiertos de datos.gob.mx")
    p.add_argument("--consulta", required=True)
    p.add_argument("--organizacion")
    reg(p)

    p = sub.add_parser("banco-mundial", help="indicadores del Banco Mundial")
    p.add_argument("--buscar")
    p.add_argument("--indicador")
    p.add_argument("--pais", default="MX")
    p.add_argument("--anios", type=int, default=10)
    reg(p)

    p = sub.add_parser("oficiales", help="descubre comunicados oficiales (no citable tal cual)")
    p.add_argument("--consulta", required=True)
    p.add_argument("--sitio")
    p.add_argument("--dias", type=int, default=365)
    p.add_argument("--max", type=int, default=15)

    a = ap.parse_args(argv)
    return {"medios": cmd_medios, "datos-gob": cmd_datos_gob, "banco-mundial": cmd_banco_mundial,
            "oficiales": cmd_oficiales}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
