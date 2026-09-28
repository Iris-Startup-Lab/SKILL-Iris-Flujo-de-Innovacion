"""
generar_landing.py — landing.json + estilo + marca + imágenes -> landing_demo.html

La landing de validación ya no la escribe el modelo desde cero: el diseño lo pone la
plantilla (templates/landing_base.html) y este script, y el modelo solo decide el contenido
en un landing.json (bloques, textos, marca, imágenes). Así la calidad visual no depende de
cada ejecución, y funciona para cualquier producto porque la plantilla no sabe de ninguno.

Lo que hace, en orden:

1. Resuelve el estilo (references/estilos.json) y lo ajusta con la marca.
2. Deriva los tonos intermedios y COMPRUEBA EL CONTRASTE (WCAG AA): un texto ilegible es error.
3. Incrusta las imágenes (archivo local o URL descargada) en base64, con su crédito.
   Si una imagen no llega, usa la maqueta de respaldo y lo avisa.
4. Valida el contenido: un solo CTA, titular breve, máximo 3 beneficios, aviso de privacidad
   si hay formulario, aviso transparente si es una prueba de «puerta falsa», y NADA de prueba
   social inventada («10,000 clientes felices», estrellas, «4.9/5») salvo que venga con fuente.
5. Arma el HTML autocontenido.

Uso (desde la raíz del repositorio o desde la carpeta de la skill):

    python sub-skills/4.Prototipado/landing-page/scripts/generar_landing.py \\
        --data landing.json -o landing_demo.html

    python .../generar_landing.py --listar-estilos
    python .../generar_landing.py --listar-iconos

    --sin-red   no descarga imágenes por URL (usa el respaldo)

El esquema completo de landing.json está en references/landing.md.
Salida: 0 ok · 1 error de archivo/uso · 2 contenido inválido.
"""
import argparse
import base64
import datetime as _dt
import html
import json
import mimetypes
import re
import sys
import urllib.request
from pathlib import Path

AQUI = Path(__file__).resolve().parent
SKILL = AQUI.parent
PLANTILLA = SKILL / "templates" / "landing_base.html"
ESTILOS = SKILL / "references" / "estilos.json"

MAX_IMAGEN = 5 * 1024 * 1024        # por imagen, ya en bytes
AVISO_IMAGEN = 900 * 1024
MAX_BENEFICIOS = 3
TIPOS_BLOQUE = {"portada", "problema_solucion", "beneficios", "como_funciona", "destacado",
                "antes_despues", "comparativa", "preguntas", "cta_final"}
TIPOS_VISUAL = {"celular", "navegador", "producto", "ruta", "ilustracion", "imagen"}
ACCIONES_CTA = {"formulario", "puerta_falsa", "enlace"}
TIPOS_MARCA = {"real", "nueva", "neutra"}
FUENTES_IMAGEN = {"usuario", "ia", "banco", "url"}
TIPOS_CAMPO = {"email", "nombre", "telefono", "cp", "texto", "opcion"}

# --------------------------------------------------------------------------- iconos
# Trazos propios de 24×24 (stroke, sin relleno), para que la página no dependa de una fuente
# de iconos externa. `--listar-iconos` los enumera.
ICONOS = {
    "check": '<path d="M20 6 9 17l-5-5"/>',
    "x": '<path d="M18 6 6 18M6 6l12 12"/>',
    "flecha": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "mas": '<path d="M12 5v14M5 12h14"/>',
    "rayo": '<path d="M13 2 4 14h7l-1 8 9-12h-7z"/>',
    "reloj": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "escudo": '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/><path d="m9 12 2 2 4-4"/>',
    "candado": '<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/>',
    "camion": '<path d="M3 6h11v10H3zM14 9h4l3 3v4h-7"/><circle cx="7" cy="18" r="2"/><circle cx="17" cy="18" r="2"/>',
    "dron": '<rect x="9" y="10" width="6" height="4" rx="1"/><path d="M9 11 6 8M15 11l3-3M9 13l-3 3M15 13l3 3"/>'
            '<circle cx="5" cy="7" r="2.5"/><circle cx="19" cy="7" r="2.5"/><circle cx="5" cy="17" r="2.5"/><circle cx="19" cy="17" r="2.5"/>',
    "moto": '<circle cx="5" cy="17" r="3"/><circle cx="19" cy="17" r="3"/><path d="M5 17l4-7h5l3 7M14 10l2-4h3"/>',
    "casa": '<path d="M3 11l9-8 9 8M5 10v10h14V10M10 20v-6h4v6"/>',
    "tienda": '<path d="M4 9l1-5h14l1 5M4 9v11h16V9M4 9h16M9 20v-6h6v6"/>',
    "celular": '<rect x="7" y="2" width="10" height="20" rx="2"/><path d="M11 18h2"/>',
    "tarjeta": '<rect x="2" y="5" width="20" height="14" rx="2"/><path d="M2 10h20M6 15h4"/>',
    "dinero": '<rect x="2" y="6" width="20" height="12" rx="2"/><circle cx="12" cy="12" r="3"/><path d="M6 12h.01M18 12h.01"/>',
    "grafica": '<path d="M3 3v18h18M7 15l4-4 3 3 5-6"/>',
    "usuario": '<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>',
    "grupo": '<circle cx="9" cy="8" r="3.5"/><path d="M2 20a7 7 0 0 1 14 0M16 4.5a3.5 3.5 0 0 1 0 7M18 13.5a7 7 0 0 1 4 6.5"/>',
    "corazon": '<path d="M20.8 5.6a5.5 5.5 0 0 0-7.8 0L12 6.6l-1-1a5.5 5.5 0 0 0-7.8 7.8L12 22l8.8-8.6a5.5 5.5 0 0 0 0-7.8z"/>',
    "hoja": '<path d="M11 20A7 7 0 0 1 4 13C4 6 11 3 20 3c0 9-3 16-9 17zM4 21c4-6 8-9 12-11"/>',
    "chispa": '<path d="M12 3l2 6 6 2-6 2-2 6-2-6-6-2 6-2z"/>',
    "mapa": '<path d="M9 4 3 6v14l6-2 6 2 6-2V4l-6 2zM9 4v14M15 6v14"/>',
    "pin": '<path d="M12 22s7-6.5 7-12a7 7 0 0 0-14 0c0 5.5 7 12 7 12z"/><circle cx="12" cy="10" r="2.5"/>',
    "paquete": '<path d="M21 8l-9-5-9 5v8l9 5 9-5zM3 8l9 5 9-5M12 13v8"/>',
    "carrito": '<circle cx="9" cy="20" r="1.5"/><circle cx="18" cy="20" r="1.5"/><path d="M2 3h3l2.6 12.4a1 1 0 0 0 1 .8h9.6a1 1 0 0 0 1-.8L21 7H6"/>',
    "bolsa": '<path d="M5 8h14l-1 13H6zM9 8V6a3 3 0 0 1 6 0v2"/>',
    "regalo": '<rect x="3" y="8" width="18" height="4" rx="1"/><path d="M5 12v9h14v-9M12 8v13M12 8C10 4 7 4 7 6s3 2 5 2zm0 0c2-4 5-4 5-2s-3 2-5 2z"/>',
    "chat": '<path d="M21 12a8 8 0 0 1-11.6 7.1L4 20l1-4.6A8 8 0 1 1 21 12z"/>',
    "telefono": '<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.5c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2z"/>',
    "correo": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/>',
    "calendario": '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/>',
    "herramienta": '<path d="M14.7 6.3a4.5 4.5 0 0 0-6 6L3 18l3 3 5.7-5.7a4.5 4.5 0 0 0 6-6l-2.8 2.8-2.9-.3-.3-2.9z"/>',
    "foco": '<path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/>',
    "cohete": '<path d="M5 15c-1.5 1.3-2 5-2 5s3.7-.5 5-2M9 15l-3-3c1-5 5-9 12-10-1 7-5 11-10 12z"/><circle cx="14" cy="9" r="1.5"/>',
    "globo": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/>',
    "wifi": '<path d="M2 8.8a15 15 0 0 1 20 0M5 12.5a10 10 0 0 1 14 0M8.5 16a5 5 0 0 1 7 0M12 19.5h.01"/>',
    "mueble": '<path d="M4 11V8a3 3 0 0 1 3-3h10a3 3 0 0 1 3 3v3M2 13a2 2 0 0 1 4 0v2h12v-2a2 2 0 0 1 4 0v5H2zM5 18v2M19 18v2"/>',
    "camara": '<path d="M4 7h3l2-3h6l2 3h3a1 1 0 0 1 1 1v11a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V8a1 1 0 0 1 1-1z"/><circle cx="12" cy="13" r="4"/>',
    "salud": '<path d="M9 3h6v6h6v6h-6v6H9v-6H3V9h6z"/>',
    "libro": '<path d="M4 19V5a2 2 0 0 1 2-2h14v16H6a2 2 0 0 0-2 2 2 2 0 0 0 2 2h14"/>',
    "auto": '<path d="M5 17H3v-5l2-5h14l2 5v5h-2M5 12h14"/><circle cx="7.5" cy="17" r="2"/><circle cx="16.5" cy="17" r="2"/>',
    "sol": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
    "gota": '<path d="M12 3s7 7.5 7 12a7 7 0 0 1-14 0c0-4.5 7-12 7-12z"/>',
    "porcentaje": '<path d="M19 5 5 19"/><circle cx="6.5" cy="6.5" r="2.5"/><circle cx="17.5" cy="17.5" r="2.5"/>',
    "precio": '<path d="M20.6 13.4l-7.2 7.2a2 2 0 0 1-2.8 0L3 13V3h10l7.6 7.6a2 2 0 0 1 0 2.8z"/><circle cx="7.5" cy="7.5" r="1.5"/>',
    "bateria": '<rect x="2" y="7" width="17" height="10" rx="2"/><path d="M22 11v2M6 10v4M10 10v4"/>',
    "avion": '<path d="M17.8 19.2 16 11l3.5-3.5C21 6 21.5 4 21 3c-1-.5-3 0-4.5 1.5L13 8 4.8 6.2c-.5-.1-.9.1-1.1.5l-.3.5c-.2.5-.1 1 .3 1.3L9 12l-2 3H4l-1 1 3 2 2 3 1-1v-3l3-2 3.5 5.3c.3.4.8.5 1.3.3l.5-.2c.4-.3.6-.7.5-1.2z"/>',
    "estudio": '<path d="M22 10 12 5 2 10l10 5zM6 12v5c3 2 9 2 12 0v-5"/>',
    "herramientas_cocina": '<path d="M7 2v8a2 2 0 0 0 4 0V2M9 10v12M17 2c-2 2-3 5-3 8h3v12"/>',
}


def icono(nombre, clase="ico"):
    trazo = ICONOS.get(nombre) or ICONOS["chispa"]
    return (f'<svg class="{clase}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
            f'{trazo}</svg>')


# --------------------------------------------------------------------------- colores
def _hex(c):
    c = str(c or "").strip().lstrip("#")
    if len(c) == 3:
        c = "".join(x * 2 for x in c)
    if not re.fullmatch(r"[0-9a-fA-F]{6}", c):
        raise ValueError(f"color «{c}» no es un hexadecimal #RRGGBB")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def _a_hex(rgb):
    return "#" + "".join(f"{max(0, min(255, round(v))):02X}" for v in rgb)


def mezclar(a, b, t):
    """t = cuánto de `b` entra (0 = a puro, 1 = b puro)."""
    ra, rb = _hex(a), _hex(b)
    return _a_hex(tuple(x + (y - x) * t for x, y in zip(ra, rb)))


def luminancia(c):
    def canal(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (canal(v) for v in _hex(c))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contraste(a, b):
    la, lb = sorted((luminancia(a), luminancia(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def texto_sobre(fondo, claro="#FFFFFF", oscuro="#0F172A"):
    return claro if contraste(fondo, claro) >= contraste(fondo, oscuro) else oscuro


# --------------------------------------------------------------------------- utilidades
class Hallazgos:
    def __init__(self):
        self.errores, self.avisos = [], []

    def error(self, ruta, msg):
        self.errores.append(f"[ERROR] {ruta}: {msg}")

    def aviso(self, ruta, msg):
        self.avisos.append(f"[AVISO] {ruta}: {msg}")


def e(s):
    return html.escape(str(s if s is not None else ""), quote=True)


def con_enfasis(s):
    """*palabra* -> <em>palabra</em> (resalta con el degradado del acento en la portada)."""
    return re.sub(r"\*(.+?)\*", r"<em>\1</em>", e(s))


def sin_enfasis(s):
    return re.sub(r"\*(.+?)\*", r"\1", str(s or ""))


def palabras(s):
    return len(re.findall(r"\w+", sin_enfasis(s)))


def _texto(v):
    return isinstance(v, str) and v.strip() != ""


# --------------------------------------------------------------------------- imágenes
def resolver_imagenes(data, base_dir, h, sin_red):
    """Devuelve {clave: {src, alt, credito, fuente}} con cada imagen incrustada en base64."""
    salida = {}
    for clave, im in (data.get("imagenes") or {}).items():
        ruta = f"imagenes.{clave}"
        if not isinstance(im, dict):
            h.error(ruta, "debe ser un objeto {fuente, archivo|url, alt, …}")
            continue
        fuente = im.get("fuente")
        if fuente not in FUENTES_IMAGEN:
            h.error(f"{ruta}.fuente", f"«{fuente}» no es válido; usa uno de: {', '.join(sorted(FUENTES_IMAGEN))}")
            continue
        if not _texto(im.get("alt")):
            h.error(f"{ruta}.alt", "describe la imagen en una frase: la leen los lectores de pantalla")
        if fuente == "banco":
            if not _texto(im.get("credito")) or not _texto(im.get("licencia")):
                h.error(ruta, "una foto de banco libre necesita `credito` (autor y banco) y `licencia` "
                              "(p. ej. «Licencia Unsplash: uso comercial permitido»)")
        if fuente == "ia" and not _texto(im.get("generada_con")):
            h.aviso(f"{ruta}.generada_con", "di con qué herramienta se generó; queda en el crédito")

        datos, mime = None, None
        if _texto(im.get("archivo")):
            p = Path(im["archivo"])
            if not p.is_absolute():
                p = (base_dir / p) if (base_dir / p).exists() else Path.cwd() / p
            if not p.exists():
                h.aviso(f"{ruta}.archivo", f"no encuentro {im['archivo']}: se usa la maqueta de respaldo")
            else:
                datos = p.read_bytes()
                mime = mimetypes.guess_type(p.name)[0]
        elif _texto(im.get("url")):
            if sin_red:
                h.aviso(f"{ruta}.url", "--sin-red: no se descarga, se usa la maqueta de respaldo")
            else:
                try:
                    req = urllib.request.Request(im["url"], headers={"User-Agent": "Mozilla/5.0 landing-iris"})
                    with urllib.request.urlopen(req, timeout=20) as r:
                        datos = r.read(MAX_IMAGEN + 1)
                        mime = (r.headers.get_content_type() or "").lower()
                except Exception as exc:  # noqa: BLE001 — cualquier fallo de red cae al respaldo
                    h.aviso(f"{ruta}.url", f"no se pudo descargar ({exc}): se usa la maqueta de respaldo")
        else:
            h.error(ruta, "falta `archivo` (ruta local) o `url`")
            continue

        if datos is None:
            continue
        if not mime or not mime.startswith("image/"):
            h.aviso(ruta, f"el contenido no es una imagen ({mime or 'tipo desconocido'}): se usa el respaldo")
            continue
        if len(datos) > MAX_IMAGEN:
            h.error(ruta, f"pesa más de {MAX_IMAGEN // 1024 // 1024} MB: redúcela antes de incrustarla")
            continue
        if len(datos) > AVISO_IMAGEN:
            h.aviso(ruta, f"pesa {len(datos) // 1024} KB: la página cargará lento en móvil; conviene "
                          f"reducirla a menos de {AVISO_IMAGEN // 1024} KB")
        credito = im.get("credito") or ""
        if fuente == "ia":
            credito = credito or ("Imagen generada con " + im.get("generada_con", "inteligencia artificial"))
        salida[clave] = {
            "src": f"data:{mime};base64,{base64.b64encode(datos).decode('ascii')}",
            "alt": im.get("alt", ""), "credito": credito, "licencia": im.get("licencia", ""),
            "fuente": fuente, "peso": len(datos),
        }
    return salida


# --------------------------------------------------------------------------- visuales
def chips_html(chips):
    out = []
    for i, c in enumerate((chips or [])[:3]):
        out.append(f'<div class="chip c{i}"><span class="i">{icono(c.get("icono", "check"))}</span>'
                   f'<span>{e(c.get("texto"))}</span></div>')
    return "".join(out)


def visual_html(v, ctx, ruta, h):
    """Dibuja un visual. Si es una imagen que no llegó, cae a su `respaldo` o a una ilustración."""
    if not v:
        return ""
    if not isinstance(v, dict) or v.get("tipo") not in TIPOS_VISUAL:
        h.error(ruta, f"`tipo` debe ser uno de: {', '.join(sorted(TIPOS_VISUAL))}")
        return ""
    t = v["tipo"]
    marca = ctx["marca_nombre"]
    if t == "imagen":
        im = ctx["imagenes"].get(v.get("imagen"))
        if not im:
            resp = v.get("respaldo") or {"tipo": "ilustracion", "icono": v.get("icono", "chispa"),
                                         "chips": v.get("chips")}
            if v.get("imagen") not in ctx["imagenes_declaradas"]:
                h.error(f"{ruta}.imagen", f"«{v.get('imagen')}» no está en `imagenes`")
            return visual_html(resp, ctx, f"{ruta}.respaldo", h)
        marco = " marco-celular" if v.get("marco") == "celular" else ""
        cred = f'<span class="credito">{e(im["credito"])}</span>' if im["credito"] and v.get("credito_visible") else ""
        cuerpo = f'<div class="mq-img{marco}"><img src="{im["src"]}" alt="{e(im["alt"])}" loading="lazy">{cred}</div>'
    elif t == "celular":
        filas = "".join(
            f'<div class="fila"><span class="i">{icono(f.get("icono", "check"))}</span>'
            f'<div><b>{e(f.get("titulo"))}</b><span>{e(f.get("detalle"))}</span></div></div>'
            for f in (v.get("filas") or [])[:4])
        cuerpo = (f'<div class="mq-cel" role="img" aria-label="{e(v.get("alt") or "Vista de la aplicación")}"><div class="pant">'
                  f'<div class="app-cab"><small>{e(v.get("saludo") or marca)}</small><b>{e(v.get("titulo"))}</b></div>'
                  f'<div class="app-cuerpo">{filas}'
                  f'{"<div class=app-btn>" + e(v["boton"]) + "</div>" if v.get("boton") else ""}'
                  f'</div></div></div>')
    elif t == "navegador":
        tarjetas = "".join(f'<div class="tj">{e(x)}<b class="{"a" if i == 0 else ""}"></b></div>'
                           for i, x in enumerate((v.get("tarjetas") or [])[:3]))
        lista = "".join(f'<div>{icono("check")}{e(x)}</div>' for x in (v.get("lista") or [])[:3])
        barras = "".join(f'<i style="height:{hgt}%"></i>' for hgt in (38, 55, 47, 70, 62, 84, 76))
        cuerpo = (f'<div class="mq-nav" role="img" aria-label="{e(v.get("alt") or "Vista de la plataforma")}">'
                  f'<div class="barra"><i></i><i></i><i></i><span class="url">{e(v.get("url") or "")}</span></div>'
                  f'<div class="cuerpo"><div class="lat"><i></i><i></i><i></i><i></i><i></i></div>'
                  f'<div class="area"><h4>{e(v.get("titulo"))}</h4>'
                  f'{"<div class=tarjetas>" + tarjetas + "</div>" if tarjetas else ""}'
                  f'<div class="graf">{barras}</div>'
                  f'{"<div class=lista>" + lista + "</div>" if lista else ""}'
                  f'</div></div></div>')
    elif t == "producto":
        sello = f'<div class="sello">{e(v["sello"])}</div>' if v.get("sello") else ""
        cuerpo = (f'<div class="mq-prod" role="img" aria-label="{e(v.get("alt") or v.get("nombre") or "Producto")}">{sello}'
                  f'<div class="caja"><div class="frente"><span class="m">{e(marca)}</span>'
                  f'<span class="big">{icono(v.get("icono", "paquete"))}</span>'
                  f'<span class="nom">{e(v.get("nombre"))}</span>'
                  f'<span class="var">{e(v.get("variante"))}</span></div><div class="lado"></div></div>'
                  f'<div class="piso"></div></div>')
    elif t == "ruta":
        trazo = "M60 240 C 190 250, 210 70, 460 60"
        mov = ICONOS.get(v.get("icono_movil", "camion"), ICONOS["camion"])
        ini = ICONOS.get(v.get("icono_origen", "tienda"), ICONOS["tienda"])
        fin = ICONOS.get(v.get("icono_destino", "casa"), ICONOS["casa"])

        def pin(x, y, ic, etiqueta, lleno):
            fondo = "var(--c-pri)" if lleno else "var(--c-sup)"
            tinta = "var(--c-sobre-pri)" if lleno else "var(--c-pri)"
            return (f'<g transform="translate({x} {y})"><circle r="22" style="fill:{fondo};stroke:var(--c-pri)" stroke-width="2.5"/>'
                    f'<g transform="translate(-12 -12)" fill="none" style="stroke:{tinta}" stroke-width="2" '
                    f'stroke-linecap="round" stroke-linejoin="round">{ic}</g>'
                    f'<text y="42" text-anchor="middle" style="fill:var(--c-tinta);font:700 13px var(--f-txt),sans-serif">{e(etiqueta)}</text></g>')
        svg = (f'<svg class="linea" viewBox="0 0 520 300" preserveAspectRatio="xMidYMid meet" aria-hidden="true">'
               f'<path d="{trazo}" fill="none" style="stroke:var(--c-pri)" stroke-width="4" stroke-dasharray="2 12" stroke-linecap="round" opacity=".55"/>'
               f'{pin(60, 240, ini, v.get("origen", ""), False)}{pin(460, 60, fin, v.get("destino", ""), True)}'
               f'<g><circle r="24" style="fill:var(--c-acento)" opacity=".25"><animate attributeName="r" values="20;30;20" dur="2s" repeatCount="indefinite"/></circle>'
               f'<circle r="18" style="fill:var(--c-acento)"/><g transform="translate(-10 -10) scale(.84)" fill="none" style="stroke:var(--c-sobre-acento)" '
               f'stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">{mov}</g>'
               f'<animateMotion dur="6s" repeatCount="indefinite" path="{trazo}" rotate="0"/></g></svg>')
        estado = ""
        if v.get("estado_titulo"):
            estado = (f'<div class="estado"><span class="i">{icono(v.get("icono_movil", "camion"))}</span>'
                      f'<div style="flex:1"><b>{e(v["estado_titulo"])}</b><span>{e(v.get("estado_texto"))}</span>'
                      f'<div class="barra-av"><i></i></div></div></div>')
        cuerpo = (f'<div class="mq-ruta" role="img" aria-label="{e(v.get("alt") or "Ruta de entrega")}">'
                  f'<div class="mapa">{svg}</div>{estado}</div>')
    else:  # ilustracion
        cuerpo = (f'<div class="mq-ilus" aria-hidden="true"><div class="anillo"></div><div class="blob"></div>'
                  f'<div class="centro">{icono(v.get("icono", "chispa"))}</div></div>')
    return f'<div class="visual">{cuerpo}{chips_html(v.get("chips"))}</div>'


# --------------------------------------------------------------------------- bloques
def boton_cta(ctx, ubicacion, extra=""):
    cta = ctx["cta"]
    etiqueta = e(cta.get("texto"))
    if cta.get("accion") == "enlace" and cta.get("url"):
        return (f'<a class="btn btn-pri js-cta {extra}" data-ubicacion="{ubicacion}" href="{e(cta["url"])}" '
                f'rel="noopener">{etiqueta}{icono("flecha")}</a>')
    return (f'<button type="button" class="btn btn-pri js-cta {extra}" data-ubicacion="{ubicacion}">'
            f'{etiqueta}{icono("flecha")}</button>')


def formulario_html(ctx):
    f = ctx["formulario"]
    if not f:
        return ""
    tipos = {"email": ("email", "email"), "telefono": ("tel", "tel"), "nombre": ("text", "name"),
             "cp": ("text", "postal-code"), "texto": ("text", "off")}
    campos = []
    for i, c in enumerate(f.get("campos") or []):
        req = " required" if c.get("requerido", True) else ""
        nombre = e(c.get("nombre") or c.get("tipo") or f"campo_{i}")
        etiqueta = e(c.get("etiqueta") or c.get("tipo"))
        if c.get("tipo") == "opcion":
            ops = "".join(f"<option>{e(o)}</option>" for o in c.get("opciones") or [])
            campos.append(f'<label>{etiqueta}<select name="{nombre}"{req}><option value="">Elige una opción</option>{ops}</select></label>')
        else:
            tipo, auto = tipos.get(c.get("tipo"), ("text", "off"))
            extra = ' inputmode="numeric" pattern="[0-9]{5}"' if c.get("tipo") == "cp" else ""
            campos.append(f'<label>{etiqueta}<input type="{tipo}" name="{nombre}" autocomplete="{auto}" '
                          f'placeholder="{e(c.get("ejemplo") or "")}"{extra}{req}></label>')
    priv = ctx["privacidad"] or {}
    enlace = (f' <a href="{e(priv["url"])}" target="_blank" rel="noopener">Aviso de privacidad</a>.'
              if priv.get("url") else "")
    campos.append(f'<label class="priv"><input type="checkbox" name="acepta_privacidad" required>'
                  f'<span>{e(priv.get("texto"))}{enlace}</span></label>')
    boton = e(f.get("boton") or ctx["cta"].get("texto"))
    return (f'<form class="form" id="registro" novalidate>{"".join(campos)}'
            f'<p class="err" role="alert">Revisa los campos marcados.</p>'
            f'<button type="submit" class="btn btn-pri btn-bloque">{boton}{icono("flecha")}</button></form>')


def bloque_html(b, i, ctx, h):
    t = b.get("tipo")
    ruta = f"bloques[{i}]"
    bid = f"b-{t}-{i}"
    alt = " alt" if b.get("fondo") == "superficie" else ""
    enc = ""
    if b.get("titulo") and t not in ("portada", "cta_final", "destacado"):
        centro = " centro" if b.get("centrado", True) else ""
        enc = (f'<div class="enc{centro}">{"<span class=etiqueta>" + e(b["etiqueta"]) + "</span>" if b.get("etiqueta") else ""}'
               f'<h2>{e(b["titulo"])}</h2>{"<p>" + e(b["texto"]) + "</p>" if b.get("texto") else ""}</div>')

    if t == "portada":
        variante = b.get("variante", "dividida")
        clases = {"dividida": "", "centrada": " centrada", "inmersiva": " inmersiva"}.get(variante, "")
        estilo = ""
        if variante == "inmersiva":
            im = ctx["imagenes"].get(b.get("imagen_fondo"))
            if im:
                estilo = (f' style="background-image:linear-gradient(90deg,rgba(8,10,18,.82),rgba(8,10,18,.35)),'
                          f'url({im["src"]});--portada-tinta:#FFFFFF;--portada-tinta-suave:rgba(255,255,255,.82)"')
            else:
                clases = ""
                h.aviso(f"{ruta}.imagen_fondo", "la portada inmersiva necesita una imagen: se dibuja dividida")
        nota = "".join(f"<span>{icono(n.get('icono', 'check'))}{e(n.get('texto'))}</span>"
                       for n in (b.get("puntos") or [])[:3])
        titular_b = f' data-b="{e(sin_enfasis(b["titular_b"]))}"' if b.get("titular_b") else ""
        sub_b = f' data-b="{e(b["subtitulo_b"])}"' if b.get("subtitulo_b") else ""
        secundario = ""
        if b.get("enlace_secundario"):
            destino = next((f"b-{x.get('tipo')}-{j}" for j, x in enumerate(ctx["bloques"])
                            if x.get("tipo") == b["enlace_secundario"].get("bloque")), "")
            if destino:
                secundario = (f'<button type="button" class="btn btn-sec" data-ir="{destino}">'
                              f'{e(b["enlace_secundario"].get("texto", "Ver cómo funciona"))}</button>')
        texto = (f'<div class="texto">{"<span class=etiqueta>" + e(b["etiqueta"]) + "</span>" if b.get("etiqueta") else ""}'
                 f'<h1{titular_b}>{con_enfasis(b.get("titular"))}</h1>'
                 f'<p class="sub"{sub_b}>{e(b.get("subtitulo"))}</p>'
                 f'<div class="acciones">{boton_cta(ctx, "portada")}{secundario}</div>'
                 f'{"<div class=nota>" + nota + "</div>" if nota else ""}</div>')
        vis = visual_html(b.get("visual"), ctx, f"{ruta}.visual", h) if variante != "inmersiva" or not estilo else ""
        return (f'<section class="portada{clases}" id="{bid}" data-seccion="portada"{estilo}>'
                f'<div class="envoltura"><div class="rejilla">{texto}{vis}</div></div></section>')

    if t == "problema_solucion":
        prob, sol = b.get("problema") or {}, b.get("solucion") or {}
        lp = "".join(f"<li>{icono('x')}<span>{e(x)}</span></li>" for x in prob.get("puntos") or [])
        ls = "".join(f"<li>{icono('check')}<span>{e(x)}</span></li>" for x in sol.get("puntos") or [])
        cuerpo = (f'<div class="ps"><div class="lado prob"><h3>{e(prob.get("titulo", "Hoy"))}</h3><ul>{lp}</ul></div>'
                  f'<div class="lado sol"><h3>{e(sol.get("titulo", "Con nosotros"))}</h3><ul>{ls}</ul></div></div>')
    elif t == "beneficios":
        items = b.get("items") or []
        if len(items) > MAX_BENEFICIOS:
            h.error(f"{ruta}.items", f"{len(items)} beneficios; el máximo es {MAX_BENEFICIOS}: más de tres no se escanean")
        cuerpo = '<div class="benef">' + "".join(
            f'<div class="b"><div class="i">{icono(x.get("icono", "check"))}</div><h3>{e(x.get("titulo"))}</h3>'
            f'<p>{e(x.get("texto"))}</p></div>' for x in items[:MAX_BENEFICIOS]) + "</div>"
    elif t == "como_funciona":
        cuerpo = '<div class="pasos">' + "".join(
            f'<div class="p"><div class="n">{k + 1}</div><h3>{e(x.get("titulo"))}'
            f'{icono(x["icono"]) if x.get("icono") else ""}</h3><p>{e(x.get("texto"))}</p></div>'
            for k, x in enumerate((b.get("pasos") or [])[:4])) + "</div>"
    elif t == "destacado":
        pts = "".join(f"<li>{icono('check')}<span>{e(x)}</span></li>" for x in b.get("puntos") or [])
        inv = " inv" if b.get("invertir") else ""
        cuerpo = (f'<div class="dest{inv}"><div class="dest-txt">'
                  f'{"<span class=etiqueta>" + e(b["etiqueta"]) + "</span>" if b.get("etiqueta") else ""}'
                  f'<h2>{e(b.get("titulo"))}</h2><p>{e(b.get("texto"))}</p>{"<ul>" + pts + "</ul>" if pts else ""}</div>'
                  f'{visual_html(b.get("visual"), ctx, f"{ruta}.visual", h)}</div>')
    elif t == "antes_despues":
        la = "".join(f"<li>{icono('x')}<span>{e(x)}</span></li>" for x in b.get("antes") or [])
        ld = "".join(f"<li>{icono('check')}<span>{e(x)}</span></li>" for x in b.get("despues") or [])
        cuerpo = (f'<div class="ad"><div class="col antes"><h3>{e(b.get("titulo_antes", "Antes"))}</h3><ul>{la}</ul></div>'
                  f'<div class="flecha">{icono("flecha")}</div>'
                  f'<div class="col despues"><h3>{e(b.get("titulo_despues", "Ahora"))}</h3><ul>{ld}</ul></div></div>')
    elif t == "comparativa":
        cols = b.get("columnas") or ["", "La alternativa de hoy", ctx["marca_nombre"]]
        if len(cols) != 3:
            h.error(f"{ruta}.columnas", "van exactamente 3: criterio, la alternativa de hoy y nuestra opción")
            cols = (cols + ["", "", ""])[:3]

        def celda(v, nos):
            s = str(v).strip().lower()
            clase = ' class="nos"' if nos else ""
            if s in ("si", "sí"):
                return f'<td{clase}><span class="si">{icono("check")}</span></td>'
            if s == "no":
                return f'<td{clase}><span class="no">{icono("x")}</span></td>'
            return f"<td{clase}>{e(v)}</td>"
        filas = ""
        for k, f in enumerate(b.get("filas") or []):
            if not isinstance(f, list) or len(f) != 3:
                h.error(f"{ruta}.filas[{k}]", "cada fila es [criterio, alternativa, nosotros]")
                continue
            filas += f"<tr><td><b>{e(f[0])}</b></td>{celda(f[1], False)}{celda(f[2], True)}</tr>"
        cuerpo = (f'<div class="comp-wrap"><table class="comp"><thead><tr><th>{e(cols[0])}</th><th>{e(cols[1])}</th>'
                  f'<th class="nos">{e(cols[2])}</th></tr></thead><tbody>{filas}</tbody></table></div>')
    elif t == "preguntas":
        cuerpo = '<div class="faq">' + "".join(
            f'<details><summary>{e(x.get("pregunta"))}{icono("mas")}</summary><div class="r">{e(x.get("respuesta"))}</div></details>'
            for x in b.get("items") or []) + "</div>"
    elif t == "cta_final":
        form = formulario_html(ctx)
        sin = "" if form else " sin-form"
        cuerpo = (f'<div class="final{sin}"><div><h2>{e(b.get("titulo"))}</h2>'
                  f'{"<p>" + e(b["texto"]) + "</p>" if b.get("texto") else ""}'
                  f'{"" if form else "<div class=acciones>" + boton_cta(ctx, "final") + "</div>"}</div>{form}</div>')
    else:
        h.error(f"{ruta}.tipo", f"«{t}» no es un bloque; usa uno de: {', '.join(sorted(TIPOS_BLOQUE))}")
        return ""
    return (f'<section class="bloque{alt}" id="{bid}" data-seccion="{t}"><div class="envoltura">'
            f'{enc}{cuerpo}</div></section>')


# --------------------------------------------------------------------------- integridad
# Prueba social que el producto todavía no puede tener. Si es real, se declara en `evidencia`
# con su fuente y deja de ser error.
PATRONES_PRUEBA_SOCIAL = [
    (r"\b\d[\d.,]*\s*(mil\s+|k\s+)?\+?\s*(usuarios|clientes|personas|familias|empresas|negocios|compradores)"
     r"[^.]{0,30}\b(felices|satisfech\w*|conf[ií]an|nos eligen|ya (lo )?usan|lo prefieren|recomiendan)",
     "cifra de clientes satisfechos"),
    (r"[★⭐]", "estrellas de calificación"),
    (r"\b[1-5][.,]\d\s*/\s*5\b", "calificación sobre 5"),
    (r"\b\d{2,3}\s*%\s*de\s*(nuestros\s+)?(clientes|usuarios)", "porcentaje de clientes"),
    (r"\b(el|la)\s+m[aá]s\s+vendid[oa]\b|\bn[uú]mero\s+(1|uno)\b|#\s?1\b|\bl[ií]der\s+del?\s+mercado\b",
     "superlativo de mercado"),
]


def textos(obj, ruta=""):
    if isinstance(obj, str):
        yield ruta, obj
    elif isinstance(obj, dict):
        for k, v in obj.items():
            if k in ("imagenes", "medicion", "evidencia"):
                continue
            yield from textos(v, f"{ruta}.{k}" if ruta else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from textos(v, f"{ruta}[{i}]")


def revisar_integridad(data, h):
    respaldadas = [str(x.get("texto", "")).lower() for x in data.get("evidencia") or []
                   if isinstance(x, dict) and _texto(x.get("fuente"))]
    for ruta, s in textos(data):
        for patron, que in PATRONES_PRUEBA_SOCIAL:
            m = re.search(patron, s, re.I)
            if m and not any(m.group(0).lower() in r or r in s.lower() for r in respaldadas if r):
                h.error(ruta, f"{que} sin fuente («{m.group(0)}»). Un producto en validación no tiene "
                              f"todavía esa prueba social: quítala o declárala en `evidencia` con su fuente")
    for k in ("testimonios", "resenas", "reseñas", "logos_clientes"):
        if k in data:
            h.error(k, "no hay bloque de testimonios ni logos de clientes: en una prueba serían inventados")


# --------------------------------------------------------------------------- estilo
def resolver_estilo(data, h):
    catalogo = json.loads(ESTILOS.read_text(encoding="utf-8"))["estilos"]
    clave = data.get("estilo") or ("neutro" if (data.get("marca") or {}).get("tipo") == "neutra" else "tecnologico")
    if clave not in catalogo:
        h.error("estilo", f"«{clave}» no existe; usa uno de: {', '.join(catalogo)}")
        clave = "neutro"
    est = json.loads(json.dumps(catalogo[clave]))
    marca = data.get("marca") or {}
    for k, v in (marca.get("colores") or {}).items():
        if k in est["colores"]:
            est["colores"][k] = v
        else:
            h.aviso(f"marca.colores.{k}", f"no se usa; los colores ajustables son: {', '.join(est['colores'])}")
    for k in ("titulos", "texto"):
        if (marca.get("tipografias") or {}).get(k):
            est["fuentes"][k] = marca["tipografias"][k]
    if marca.get("radio") is not None:
        est["radio"] = marca["radio"]
    if data.get("portada_tono"):
        est["portada"] = data["portada_tono"]
    return clave, est


def variables_css(est, h):
    c = {}
    try:
        c = {k: _a_hex(_hex(v)) for k, v in est["colores"].items()}
    except ValueError as exc:
        h.error("marca.colores", str(exc))
        return "", {}
    pri, acento = c["primario"], c["acento"]
    derivados = {
        "--c-pri": pri,
        "--c-pri-osc": mezclar(pri, "#000000", .28),
        "--c-pri-cl": mezclar(pri, c["superficie"], .88),
        "--c-sobre-pri": texto_sobre(pri),
        "--c-acento": acento,
        "--c-sobre-acento": texto_sobre(acento),
        "--c-fondo": c["fondo"], "--c-sup": c["superficie"], "--c-tinta": c["tinta"],
        "--c-tinta-suave": c["tinta_suave"], "--c-linea": c["linea"],
    }
    tono = est.get("portada", "clara")
    if tono == "oscura":
        a, b = mezclar(pri, "#05060A", .80), mezclar(pri, "#05060A", .58)
        bg, pt, pts = f"linear-gradient(150deg,{a},{b})", "#FFFFFF", "rgba(255,255,255,.80)"
        fondos_portada = [a, b]
    elif tono == "degradado":
        a, b = mezclar(pri, "#000000", .12), mezclar(acento, "#000000", .12)
        bg, pt, pts = f"linear-gradient(135deg,{a},{b})", "#FFFFFF", "rgba(255,255,255,.88)"
        fondos_portada = [a, b]
    else:
        a = mezclar(pri, c["fondo"], .93)
        bg, pt, pts = f"linear-gradient(180deg,{a},{c['fondo']})", c["tinta"], c["tinta_suave"]
        fondos_portada = [a, c["fondo"]]
    derivados.update({"--portada-bg": bg, "--portada-tinta": pt, "--portada-tinta-suave": pts,
                      "--radio": f"{int(est.get('radio', 12))}px",
                      "--f-tit": f"'{est['fuentes']['titulos']}'", "--f-txt": f"'{est['fuentes']['texto']}'"})

    # Contraste (WCAG AA): 4.5:1 texto normal, 3:1 texto grande y botones en negrita.
    medidas = {}

    def exigir(nombre, fg, bgc, minimo, grave=3.0):
        r = contraste(fg, bgc)
        medidas[nombre] = round(r, 2)
        if r < grave:
            h.error("contraste", f"{nombre}: {r:.2f}:1 — ilegible (mínimo {minimo}:1). Ajusta los colores de la marca")
        elif r < minimo:
            h.aviso("contraste", f"{nombre}: {r:.2f}:1, por debajo de {minimo}:1 recomendado")
    exigir("texto sobre fondo", c["tinta"], c["fondo"], 4.5, 4.5)
    exigir("texto secundario sobre fondo", c["tinta_suave"], c["fondo"], 4.5)
    exigir("texto sobre tarjetas", c["tinta"], c["superficie"], 4.5, 4.5)
    exigir("botón principal", derivados["--c-sobre-pri"], pri, 4.5)
    exigir("etiquetas (primario sobre su tinte)", pri, derivados["--c-pri-cl"], 4.5)
    if tono in ("oscura", "degradado"):
        for f in fondos_portada:
            exigir("titular de la portada", "#FFFFFF", f, 4.5, 3.0)
    else:
        exigir("titular de la portada", c["tinta"], fondos_portada[0], 4.5, 4.5)
    vars_txt = "\n".join(f"    {k}:{v};" for k, v in derivados.items())
    return vars_txt, medidas


def fuentes_link(est):
    fams = []
    for fam, pesos in ((est["fuentes"]["titulos"], "700"), (est["fuentes"]["texto"], "400;600;700")):
        if fam and fam not in [f for f, _ in fams]:
            fams.append((fam, pesos))
    # Un <link> por familia: si una no existe en Google Fonts, las demás cargan igual.
    return "\n".join(
        f'<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family='
        f'{fam.replace(" ", "+")}:wght@{pesos}&display=swap">' for fam, pesos in fams)


# --------------------------------------------------------------------------- armado
def validar_basico(data, h):
    marca = data.get("marca")
    if not isinstance(marca, dict):
        h.error("marca", "falta el objeto {tipo, nombre, …}")
        marca = {}
    if marca.get("tipo") not in TIPOS_MARCA:
        h.error("marca.tipo", f"usa uno de: {', '.join(sorted(TIPOS_MARCA))} (la decisión «Marca de la landing»)")
    if not _texto(marca.get("nombre")):
        h.error("marca.nombre", "vacío: es lo que se lee en la cabecera (en una marca neutra, un nombre descriptivo)")
    if marca.get("tipo") == "real" and not _texto(marca.get("origen")):
        h.aviso("marca.origen", "di de dónde salen el logo y los colores (el usuario, o la URL del sitio oficial "
                                "o de la guía de marca): así se puede comprobar")
    if marca.get("tipo") == "nueva" and not _texto(marca.get("origen")):
        h.aviso("marca.origen", "anota que la marca la propuso el agente y la aprobó el usuario")

    cta = data.get("cta")
    if not isinstance(cta, dict) or not _texto(cta.get("texto")):
        h.error("cta.texto", "falta: una sola llamada a la acción, la misma en toda la página")
        cta = cta if isinstance(cta, dict) else {}
    if cta.get("accion") not in ACCIONES_CTA:
        h.error("cta.accion", f"usa uno de: {', '.join(sorted(ACCIONES_CTA))}")
    if cta.get("accion") == "enlace" and not _texto(cta.get("url")):
        h.error("cta.url", "una llamada de tipo enlace necesita la URL de destino")
    if palabras(cta.get("texto")) > 6:
        h.aviso("cta.texto", "más de 6 palabras: un botón se lee de un vistazo")

    if cta.get("accion") == "puerta_falsa":
        av = data.get("aviso_transparente") or {}
        if not _texto(av.get("titulo")) or not _texto(av.get("texto")):
            h.error("aviso_transparente", "una prueba de «puerta falsa» exige decir, al hacer clic, que el producto "
                                          "aún no existe y qué pasa con los datos: {titulo, texto}")

    form = data.get("formulario")
    if form:
        campos = form.get("campos") or []
        if not campos:
            h.error("formulario.campos", "lista vacía")
        for k, c in enumerate(campos):
            if c.get("tipo") not in TIPOS_CAMPO:
                h.error(f"formulario.campos[{k}].tipo", f"usa uno de: {', '.join(sorted(TIPOS_CAMPO))}")
        if len(campos) > 4:
            h.aviso("formulario.campos", f"{len(campos)} campos: cada campo de más baja la conversión; para validar "
                                         "interés basta el correo")
        priv = data.get("privacidad") or {}
        if not _texto(priv.get("texto")):
            h.error("privacidad.texto", "un formulario que pide datos personales necesita aviso de privacidad "
                                        "(en México, LFPDPPP): quién los recibe y para qué")
    if cta.get("accion") == "formulario" and not form:
        h.error("formulario", "la llamada es de tipo formulario y no hay formulario")

    bloques = data.get("bloques")
    if not isinstance(bloques, list) or not bloques:
        h.error("bloques", "lista vacía")
        return
    if bloques[0].get("tipo") != "portada":
        h.error("bloques[0]", "el primer bloque es la portada")
    if not any(b.get("tipo") == "cta_final" for b in bloques):
        h.aviso("bloques", "sin bloque `cta_final`: quien llega al final no tiene dónde actuar")
    if form and not any(b.get("tipo") == "cta_final" for b in bloques):
        h.error("bloques", "hay formulario pero ningún bloque `cta_final` donde mostrarlo")
    if len(bloques) > 9:
        h.aviso("bloques", f"{len(bloques)} bloques: una landing de validación rinde mejor corta (5-7)")
    p = bloques[0]
    n = palabras(p.get("titular"))
    if n == 0:
        h.error("bloques[0].titular", "vacío")
    elif n > 20:
        h.error("bloques[0].titular", f"{n} palabras: el titular se entiende en 5 segundos o no funciona (máx. 12)")
    elif n > 12:
        h.aviso("bloques[0].titular", f"{n} palabras; lo recomendable es 12 o menos")
    if palabras(p.get("subtitulo")) > 35:
        h.aviso("bloques[0].subtitulo", "más de 35 palabras: recórtalo; el detalle va en los bloques")
    edad = data.get("edad") or {}
    if edad.get("activa") and not _texto(edad.get("texto")):
        h.aviso("edad.texto", "sin texto: se usará «Este contenido es solo para mayores de edad»")
    med = data.get("medicion") or {}
    if not med.get("ga4_id") and not med.get("gtm_id"):
        h.aviso("medicion", "sin GA4 ni GTM: los eventos solo quedan en el navegador de quien prueba "
                            "(?panel=1). Antes de lanzar, pon el identificador de GA4 o GTM")


def cabecera(data, ctx):
    marca = data.get("marca") or {}
    logo = ctx["imagenes"].get(marca.get("logo")) if marca.get("logo") else None
    if logo:
        m = f'<img src="{logo["src"]}" alt="{e(marca.get("nombre"))}">'
    else:
        m = f'<span class="simbolo">{icono(marca.get("icono", "chispa"))}</span>{e(marca.get("nombre"))}'
    nav = []
    etiquetas = {"como_funciona": "Cómo funciona", "beneficios": "Beneficios", "comparativa": "Comparar",
                 "preguntas": "Preguntas"}
    for i, b in enumerate(ctx["bloques"]):
        if b.get("tipo") in etiquetas:
            nav.append(f'<button type="button" data-ir="b-{b["tipo"]}-{i}">{etiquetas[b["tipo"]]}</button>')
    return (f'<header class="cab"><div class="envoltura"><span class="marca">{m}</span>'
            f'<nav aria-label="Secciones">{"".join(nav)}</nav>{boton_cta(ctx, "cabecera", "btn-sm")}</div></header>')


def pie(data, ctx):
    marca = data.get("marca") or {}
    anio = _dt.date.today().year
    creditos = [f'{e(im["credito"])}{" · " + e(im["licencia"]) if im["licencia"] else ""}'
                for im in ctx["imagenes"].values() if im["credito"]]
    priv = data.get("privacidad") or {}
    enlace_priv = (f' · <a href="{e(priv["url"])}" target="_blank" rel="noopener">Aviso de privacidad</a>'
                   if priv.get("url") else "")
    cred = f'<div class="creditos">Imágenes: {" — ".join(creditos)}</div>' if creditos else ""
    return (f'<footer class="pie"><div class="envoltura"><div>© {anio} {e(marca.get("nombre"))}{enlace_priv}</div>'
            f'{cred}</div></footer>')


def ventanas(data, ctx):
    g = data.get("gracias") or {}
    av = data.get("aviso_transparente") or {}
    edad = data.get("edad") or {}
    out = [
        f'<div class="velo" id="v-gracias" role="dialog" aria-modal="true" aria-labelledby="t-gracias"><div class="caja-m">'
        f'<div class="i">{icono("check")}</div><h3 id="t-gracias">{e(g.get("titulo") or "¡Listo! Ya estás en la lista")}</h3>'
        f'<p>{e(g.get("texto") or "Te escribiremos en cuanto esté disponible.")}</p>'
        f'<div class="acciones"><button type="button" class="btn btn-pri" data-cerrar>Entendido</button></div></div></div>'
    ]
    if av:
        out.append(
            f'<div class="velo" id="v-aviso" role="dialog" aria-modal="true" aria-labelledby="t-aviso"><div class="caja-m">'
            f'<div class="i">{icono("foco")}</div><h3 id="t-aviso">{e(av.get("titulo"))}</h3><p>{e(av.get("texto"))}</p>'
            f'<div class="acciones"><button type="button" class="btn btn-pri" data-cerrar>Entendido</button></div></div></div>')
    if edad.get("activa"):
        minima = int(edad.get("minima", 18))
        out.append(
            f'<div class="velo" id="v-edad" role="dialog" aria-modal="true" aria-labelledby="t-edad"><div class="caja-m">'
            f'<div class="i">{icono("escudo")}</div><h3 id="t-edad">¿Tienes {minima} años o más?</h3>'
            f'<p>{e(edad.get("texto") or "Este contenido es solo para mayores de edad.")}</p>'
            f'<div class="acciones"><button type="button" class="btn btn-pri" id="edad-si">Sí, tengo {minima} o más</button>'
            f'<button type="button" class="btn btn-sec" id="edad-no">No</button></div>'
            f'<p id="edad-msg" style="display:none;margin-top:14px">Gracias por tu honestidad. Esta página no es para ti todavía.</p>'
            f'</div></div>')
    out.append(f'<div class="barra-cta">{boton_cta(ctx, "barra_movil", "btn-bloque")}</div>')
    return "".join(out)


def generar(data_path, salida, sin_red=False):
    data_path = Path(data_path)
    data = json.loads(data_path.read_text(encoding="utf-8"))
    h = Hallazgos()
    validar_basico(data, h)
    revisar_integridad(data, h)
    clave_estilo, est = resolver_estilo(data, h)
    vars_txt, medidas = variables_css(est, h)
    imagenes = resolver_imagenes(data, data_path.parent, h, sin_red)
    ctx = {
        "marca_nombre": (data.get("marca") or {}).get("nombre", ""),
        "cta": data.get("cta") or {}, "formulario": data.get("formulario"),
        "privacidad": data.get("privacidad"), "imagenes": imagenes,
        "imagenes_declaradas": set((data.get("imagenes") or {}).keys()),
        "bloques": data.get("bloques") or [],
    }
    cuerpo = [cabecera(data, ctx), "<main>"]
    for i, b in enumerate(ctx["bloques"]):
        if not isinstance(b, dict):
            h.error(f"bloques[{i}]", "no es un objeto")
            continue
        cuerpo.append(bloque_html(b, i, ctx, h))
    cuerpo += ["</main>", pie(data, ctx), ventanas(data, ctx)]

    for linea in h.errores + h.avisos:
        print(linea, file=sys.stderr)
    if h.errores:
        print(f"\n{len(h.errores)} error(es) en {data_path.name}. No se generó la landing.", file=sys.stderr)
        return 2

    config = {
        "id": re.sub(r"[^a-z0-9]+", "-", (data.get("id") or ctx["marca_nombre"] or "demo").lower()).strip("-"),
        "cta": {"accion": ctx["cta"].get("accion"), "url": ctx["cta"].get("url")},
        "formulario": ({"endpoint": data["formulario"].get("endpoint")} if data.get("formulario") else None),
        "edad": data.get("edad") or {},
        "medicion": data.get("medicion") or {},
        "variante_param": "v",
    }
    seo = data.get("seo") or {}
    titulo = seo.get("titulo") or f'{ctx["marca_nombre"]} — {sin_enfasis(ctx["bloques"][0].get("titular", ""))}'
    plantilla = PLANTILLA.read_text(encoding="utf-8")
    html_final = (plantilla
                  .replace("__TITULO__", e(titulo))
                  .replace("__DESCRIPCION__", e(seo.get("descripcion") or ctx["bloques"][0].get("subtitulo", "")))
                  .replace("__FUENTES__", fuentes_link(est))
                  .replace("__VARS__", vars_txt)
                  .replace("__CUERPO__", "\n".join(cuerpo))
                  .replace("__CONFIG__", json.dumps(config, ensure_ascii=False).replace("</", "<\\/")))
    Path(salida).write_text(html_final, encoding="utf-8")

    peso = len(html_final.encode("utf-8"))
    print(f"Landing generada: {salida}  ({peso // 1024} KB)")
    print(f"  estilo: {clave_estilo} ({est['nombre']}) · fuentes: {est['fuentes']['titulos']} / {est['fuentes']['texto']}")
    print(f"  marca: {ctx['marca_nombre']} ({(data.get('marca') or {}).get('tipo')})")
    print("  contraste: " + " · ".join(f"{k} {v}:1" for k, v in medidas.items()))
    if imagenes:
        print("  imágenes incrustadas: " + ", ".join(f"{k} ({v['fuente']}, {v['peso'] // 1024} KB)" for k, v in imagenes.items()))
    print(f"  llamada a la acción: «{ctx['cta'].get('texto')}» ({ctx['cta'].get('accion')})")
    print("  variante B: añade ?v=b a la URL · panel de medición: ?panel=1")
    if h.avisos:
        print(f"  {len(h.avisos)} aviso(s) arriba.")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="Genera la landing de validación desde landing.json.")
    ap.add_argument("--data", help="landing.json (esquema en references/landing.md)")
    ap.add_argument("-o", "--output", default="landing_demo.html")
    ap.add_argument("--sin-red", action="store_true", help="No descargar imágenes por URL")
    ap.add_argument("--listar-estilos", action="store_true")
    ap.add_argument("--listar-iconos", action="store_true")
    a = ap.parse_args(argv)
    if a.listar_estilos:
        for k, v in json.loads(ESTILOS.read_text(encoding="utf-8"))["estilos"].items():
            print(f"{k:12} {v['nombre']:24} {v['para']}")
        return 0
    if a.listar_iconos:
        print(", ".join(sorted(ICONOS)))
        return 0
    if not a.data:
        ap.error("falta --data landing.json")
    try:
        return generar(a.data, a.output, a.sin_red)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"Error: JSON inválido — {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
