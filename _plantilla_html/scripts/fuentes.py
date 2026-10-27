"""
fuentes.py — bitácora de fuentes verificables (`fuentes.json`).

Una cifra citada vale lo que vale el documento del que salió. Si ese documento
nadie lo descargó, la cita puede ser inventada y nada lo detecta. Este script
descarga la fuente por su cuenta —sin depender del buscador de la herramienta—,
guarda su texto y le asigna un identificador `F1`, `F2`… que el reporte cita
entre corchetes: «El mercado creció 8.4% en 2025 [F3]». Después,
`verificar_fuentes.py` comprueba que cada cifra y cada cita textual estén de
verdad en el texto descargado.

Solo stdlib. Se ejecuta desde la raíz del repositorio:

    # ¿hay red en este entorno? (en algunos sandbox la salida está bloqueada)
    python _plantilla_html/scripts/fuentes.py probar

    # descargar y registrar una página
    python _plantilla_html/scripts/fuentes.py capturar --fuentes fuentes.json \
        --url "https://www.inegi.org.mx/..." [--tipo oficial] [--titulo "..."]

    # registrar material propio del usuario (txt, md, html, csv)
    python _plantilla_html/scripts/fuentes.py archivo --fuentes fuentes.json \
        --ruta estudio_interno.md --titulo "Estudio interno 2026" --tipo propia

    # sin red en el sandbox: registrar lo que trajo la búsqueda web de la herramienta
    python _plantilla_html/scripts/fuentes.py agregar --fuentes fuentes.json \
        --url "https://..." --titulo "..." --texto-archivo pagina.txt [--fecha 2026-05-02]

    python _plantilla_html/scripts/fuentes.py listar --fuentes fuentes.json

El texto de cada fuente se guarda en `<carpeta de fuentes.json>/fuentes/Fn.txt`.
`capturado_por` dice cómo llegó: `script` (descarga directa, la más fiable),
`archivo` (material del usuario) o `herramienta_web` (texto copiado desde la
búsqueda de la herramienta: válido, pero no lo descargó este script).

Salida: 0 bien · 1 error de uso o de descarga.
"""
import argparse
import gzip
import hashlib
import json
import re
import sys
import urllib.error
import urllib.request
import zlib
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

TIPOS = ("oficial", "medio", "consultora", "academica", "empresa", "propia", "otro")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36 iris-fuentes/1.0")
URL_PRUEBA = "https://www.inegi.org.mx/"
MAX_BYTES = 8_000_000

# Dominios que se reconocen como oficiales sin que nadie lo declare.
RE_OFICIAL = re.compile(
    r"(\.gob\.mx|\.gov(\.[a-z]{2})?|\.gob\.[a-z]{2}|inegi\.org\.mx|banxico\.org\.mx|"
    r"worldbank\.org|imf\.org|oecd\.org|cepal\.org|un\.org|europa\.eu)$", re.I)

# Metadatos de fecha de publicación más comunes, por orden de preferencia.
META_FECHA = ("article:published_time", "og:published_time", "datepublished",
              "date", "dc.date", "dc.date.issued", "pubdate", "publish-date",
              "sailthru.date", "parsely-pub-date", "article:modified_time")


class _Extractor(HTMLParser):
    """Texto visible + título + fecha de publicación de una página."""

    OMITIR = {"script", "style", "noscript", "svg", "template", "iframe"}
    BLOQUE = {"p", "div", "br", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6",
              "section", "article", "td", "th", "table", "ul", "ol"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.partes, self.titulo, self.og_titulo = [], "", ""
        self.fechas, self._omitir, self._en_titulo = {}, 0, False
        self._ld = False
        self.ld_textos = []

    def handle_starttag(self, tag, attrs):
        a = {k.lower(): (v or "") for k, v in attrs}
        if tag == "script" and a.get("type", "").lower() == "application/ld+json":
            self._ld = True
        if tag in self.OMITIR:
            self._omitir += 1
        elif tag == "title":
            self._en_titulo = True
        elif tag == "meta":
            clave = (a.get("property") or a.get("name") or a.get("itemprop") or "").lower()
            if clave == "og:title":
                self.og_titulo = a.get("content", "")
            elif clave in META_FECHA and a.get("content"):
                self.fechas.setdefault(clave, a["content"])
        elif tag == "time" and a.get("datetime"):
            self.fechas.setdefault("time", a["datetime"])
        if tag in self.BLOQUE:
            self.partes.append("\n")

    def handle_endtag(self, tag):
        if tag in self.OMITIR and self._omitir:
            self._omitir -= 1
        if tag == "script":
            self._ld = False
        if tag == "title":
            self._en_titulo = False
        if tag in self.BLOQUE:
            self.partes.append("\n")

    def handle_data(self, data):
        if self._ld:
            self.ld_textos.append(data)
        if self._omitir:
            return
        if self._en_titulo:
            self.titulo += data
        else:
            self.partes.append(data)

    def texto(self):
        t = "".join(self.partes)
        t = re.sub(r"[ \t\r\f\v ]+", " ", t)
        return re.sub(r"\n\s*\n+", "\n\n", t).strip()

    def fecha(self):
        for clave in META_FECHA + ("time",):
            if clave in self.fechas:
                f = normalizar_fecha(self.fechas[clave])
                if f:
                    return f
        m = re.search(r'"datePublished"\s*:\s*"([^"]+)"', " ".join(self.ld_textos))
        return normalizar_fecha(m.group(1)) if m else None


def normalizar_fecha(valor):
    """AAAA-MM-DD a partir de lo que traiga la página, o None."""
    if not valor:
        return None
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", valor)
    if m:
        return "-".join(m.groups())
    m = re.search(r"(\d{4})(\d{2})(\d{2})", valor)
    if m and 1990 <= int(m.group(1)) <= 2100:
        return "-".join(m.groups())
    return None


def tipo_por_dominio(url, declarado):
    if declarado:
        return declarado
    host = urlparse(url).hostname or ""
    return "oficial" if RE_OFICIAL.search(host) else "otro"


def descargar(url, timeout=25):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA, "Accept": "text/html,application/xhtml+xml,text/plain;q=0.9,*/*;q=0.5",
        "Accept-Language": "es-MX,es;q=0.9,en;q=0.7", "Accept-Encoding": "gzip, deflate"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        crudo = r.read(MAX_BYTES + 1)
        if len(crudo) > MAX_BYTES:
            raise ValueError(f"la página pesa más de {MAX_BYTES // 1_000_000} MB")
        enc = (r.headers.get("Content-Encoding") or "").lower()
        if enc == "gzip":
            crudo = gzip.decompress(crudo)
        elif enc == "deflate":
            crudo = zlib.decompress(crudo)
        ctype = (r.headers.get("Content-Type") or "").lower()
        charset = r.headers.get_content_charset() or "utf-8"
        return crudo, ctype, charset, r.geturl()


def decodificar(crudo, charset):
    for enc in (charset, "utf-8", "latin-1"):
        try:
            return crudo.decode(enc)
        except (LookupError, UnicodeDecodeError):
            continue
    return crudo.decode("utf-8", "replace")


# ---------- bitácora ----------

def cargar(ruta):
    p = Path(ruta)
    if not p.exists():
        return {"version": 1, "fuentes": []}
    return json.loads(p.read_text(encoding="utf-8"))


def guardar(ruta, bitacora):
    Path(ruta).write_text(json.dumps(bitacora, ensure_ascii=False, indent=2), encoding="utf-8")


def registrar(ruta, texto, **campos):
    """Añade una fuente (o devuelve la existente si la URL ya está)."""
    bitacora = cargar(ruta)
    url = campos.get("url")
    for f in bitacora["fuentes"]:
        if url and f.get("url") == url:
            return f, False
    n = 1 + max((int(f["id"][1:]) for f in bitacora["fuentes"]), default=0)
    fid = f"F{n}"
    carpeta = Path(ruta).resolve().parent / "fuentes"
    carpeta.mkdir(exist_ok=True)
    (carpeta / f"{fid}.txt").write_text(texto, encoding="utf-8")
    entrada = {
        "id": fid,
        "titulo": campos.get("titulo") or "[sin título]",
        "url": url,
        "medio": campos.get("medio") or (urlparse(url).hostname if url else None),
        "tipo": campos.get("tipo") or "otro",
        "fecha_publicacion": campos.get("fecha"),
        "fecha_consulta": date.today().isoformat(),
        "capturado_por": campos["capturado_por"],
        "archivo_texto": f"fuentes/{fid}.txt",
        "caracteres": len(texto),
        "sha256": hashlib.sha256(texto.encode("utf-8")).hexdigest(),
    }
    bitacora["fuentes"].append(entrada)
    guardar(ruta, bitacora)
    return entrada, True


def _imprimir(entrada, nueva):
    print(json.dumps({"nueva": nueva, **entrada}, ensure_ascii=False, indent=2))
    if entrada["caracteres"] < 400:
        print(f"AVISO: {entrada['id']} trae solo {entrada['caracteres']} caracteres de texto. "
              "Puede ser una página que se arma con JavaScript o un muro de pago: "
              "revisa fuentes/" + entrada["id"] + ".txt antes de citarla.", file=sys.stderr)
    if not entrada.get("fecha_publicacion"):
        print(f"AVISO: {entrada['id']} no declara fecha de publicación. Si la conoces, "
              "pásala con --fecha; sin ella, la antigüedad no se puede comprobar.", file=sys.stderr)


# ---------- comandos ----------

def cmd_probar(_):
    try:
        _, ctype, _, final = descargar(URL_PRUEBA, timeout=12)
        print(json.dumps({"red": True, "url": final, "tipo": ctype}, ensure_ascii=False))
        return 0
    except Exception as e:  # noqa: BLE001 — el motivo exacto es lo que hay que reportar
        print(json.dumps({"red": False, "motivo": f"{type(e).__name__}: {e}",
                          "que_hacer": "Usa la búsqueda web de la herramienta y registra cada "
                                       "página con `fuentes.py agregar`."}, ensure_ascii=False))
        return 1


def cmd_capturar(a):
    try:
        crudo, ctype, charset, final = descargar(a.url)
    except (urllib.error.URLError, ValueError, OSError) as e:
        print(f"ERROR: no se pudo descargar {a.url}: {e}\n"
              "Si el entorno no tiene red, registra la página con `fuentes.py agregar`.",
              file=sys.stderr)
        return 1
    if "pdf" in ctype or crudo[:5] == b"%PDF-":
        print("ERROR: es un PDF y este script no extrae texto de PDF (solo stdlib). "
              "Copia el texto relevante a un .txt y regístralo con `fuentes.py agregar "
              "--capturado-por script` indicando la URL.", file=sys.stderr)
        return 1
    html = decodificar(crudo, charset)
    if "html" in ctype or "<html" in html[:2000].lower():
        ex = _Extractor()
        ex.feed(html)
        texto, titulo = ex.texto(), (ex.og_titulo or ex.titulo).strip()
        fecha = a.fecha or ex.fecha()
    else:
        texto, titulo, fecha = html.strip(), "", a.fecha
    entrada, nueva = registrar(
        a.fuentes, texto, url=final, titulo=a.titulo or titulo, medio=a.medio,
        tipo=tipo_por_dominio(final, a.tipo), fecha=normalizar_fecha(fecha) or fecha,
        capturado_por="script")
    _imprimir(entrada, nueva)
    return 0


def cmd_archivo(a):
    p = Path(a.ruta)
    if not p.exists():
        print(f"ERROR: no existe {p}", file=sys.stderr)
        return 1
    bruto = decodificar(p.read_bytes(), "utf-8")
    if p.suffix.lower() in (".html", ".htm"):
        ex = _Extractor()
        ex.feed(bruto)
        bruto = ex.texto()
    entrada, nueva = registrar(
        a.fuentes, bruto, url=a.url, titulo=a.titulo or p.name, medio=a.medio or "material del usuario",
        tipo=a.tipo or "propia", fecha=a.fecha, capturado_por="archivo")
    _imprimir(entrada, nueva)
    return 0


def cmd_agregar(a):
    if a.texto_archivo:
        texto = decodificar(Path(a.texto_archivo).read_bytes(), "utf-8")
    elif a.texto:
        texto = a.texto
    else:
        print("ERROR: hace falta --texto-archivo o --texto: sin el texto de la fuente no hay "
              "contra qué verificar las cifras.", file=sys.stderr)
        return 1
    entrada, nueva = registrar(
        a.fuentes, texto.strip(), url=a.url, titulo=a.titulo, medio=a.medio,
        tipo=tipo_por_dominio(a.url or "", a.tipo), fecha=normalizar_fecha(a.fecha) or a.fecha,
        capturado_por=a.capturado_por)
    _imprimir(entrada, nueva)
    return 0


def cmd_listar(a):
    b = cargar(a.fuentes)
    if not b["fuentes"]:
        print("La bitácora está vacía.")
    for f in b["fuentes"]:
        print(f"[{f['id']}] {f['titulo']} — {f.get('medio') or 's/medio'} · {f['tipo']} · "
              f"publicada {f.get('fecha_publicacion') or 's/fecha'} · {f['capturado_por']} · "
              f"{f['caracteres']} car.\n      {f.get('url') or '(sin URL)'}")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("probar", help="comprueba si el entorno tiene salida a internet")

    def comunes(p):
        p.add_argument("--fuentes", default="fuentes.json", help="ruta de la bitácora")
        p.add_argument("--titulo")
        p.add_argument("--medio", help="nombre del medio o institución")
        p.add_argument("--tipo", choices=TIPOS)
        p.add_argument("--fecha", help="fecha de publicación AAAA-MM-DD, si la página no la trae")

    p = sub.add_parser("capturar", help="descarga una URL y la registra")
    p.add_argument("--url", required=True)
    comunes(p)

    p = sub.add_parser("archivo", help="registra material propio del usuario")
    p.add_argument("--ruta", required=True)
    p.add_argument("--url")
    comunes(p)

    p = sub.add_parser("agregar", help="registra texto ya obtenido (sin red en el sandbox)")
    p.add_argument("--url")
    p.add_argument("--texto-archivo")
    p.add_argument("--texto")
    p.add_argument("--capturado-por", default="herramienta_web",
                   choices=("herramienta_web", "script", "archivo"))
    comunes(p)

    p = sub.add_parser("listar", help="muestra la bitácora")
    p.add_argument("--fuentes", default="fuentes.json")

    a = ap.parse_args(argv)
    return {"probar": cmd_probar, "capturar": cmd_capturar, "archivo": cmd_archivo,
            "agregar": cmd_agregar, "listar": cmd_listar}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
