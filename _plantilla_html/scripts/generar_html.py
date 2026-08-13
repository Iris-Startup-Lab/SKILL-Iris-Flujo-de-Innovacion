"""
generar_html.py

Genera un reporte HTML interactivo con el diseño corporativo IRIS a partir de
un JSON estructurado (window.REPORT_DATA) y la plantilla base. Embebe el logo
oficial en base64 para que el HTML resultante sea 100% autocontenido (funciona
sin conexión y sin archivos externos, salvo Google Fonts y Chart.js por CDN).

Hace tres cosas antes de escribir el archivo:

1. **Inyecta el contexto del flujo.** Con `--estado` y `--paso`, construye el
   bloque `flujo` desde `flujo_estado.json` + `pasos.json`. Así cada HTML sabe
   qué paso es, qué se decidió antes y qué pasos se omitieron — sin depender de
   que nadie se acuerde de escribirlo a mano.
2. **Valida el esquema** (`validar_report_data.py`). Un reporte incompleto falla
   con un error explícito en lugar de abrir en blanco.
3. **Embebe el logo** en base64: el oficial del repositorio si está, y si no la
   copia `assets/logo.png` de la sub-skill, para que una skill extraída del repo
   siga generando su HTML por su cuenta (ver `resolver_logo`).

Uso desde la raíz del repositorio:

    # paso del flujo (recomendado): el contexto se inyecta solo
    python _plantilla_html/scripts/generar_html.py --data reporte.json \
        --estado flujo_estado.json --paso html_4 -o html_4.html

    # skill suelta, fuera de un proyecto del flujo
    python _plantilla_html/scripts/generar_html.py --data reporte.json \
        --sin-flujo -o reporte.html

Placeholders reemplazados en la plantilla:
    __REPORT_DATA__  -> objeto JSON del análisis (incluye el bloque `flujo`)
    __LOGO_BASE64__  -> data URI del logo (data:image/png;base64,...)

Códigos de salida: 0 ok · 1 error de archivo/uso · 2 esquema o flujo inválido.
"""
import argparse
import base64
import importlib.util
import json
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent          # _plantilla_html/scripts
_PLANTILLA_DIR = _HERE.parent / "templates"       # _plantilla_html/templates
_REPO_ROOT = _HERE.parents[1]                     # raíz del proyecto

LOGO_DEFAULT = _REPO_ROOT / "imagenes_iconos_etc" / "Logos_GS_Iris_transparent.png"
TEMPLATE_DEFAULT = _PLANTILLA_DIR / "reporte_base.html"
ESTADO_DEFAULT = _REPO_ROOT / "flujo_estado.json"
PASOS_DEFAULT = _REPO_ROOT / "pasos.json"
ESTADO_FLUJO_PY = _REPO_ROOT / "scripts" / "estado_flujo.py"

sys.path.insert(0, str(_HERE))
from validar_report_data import validar, reportar  # noqa: E402


def _cargar_estado_flujo():
    """Carga scripts/estado_flujo.py por ruta absoluta (sin depender del CWD)."""
    if not ESTADO_FLUJO_PY.is_file():
        raise FileNotFoundError(
            f"No encuentro {ESTADO_FLUJO_PY}. Es el módulo que construye el "
            f"contexto del flujo."
        )
    spec = importlib.util.spec_from_file_location("estado_flujo", ESTADO_FLUJO_PY)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def resolver_logo(logo_path=None, data_path=None):
    """Localiza el logo. Con el repo completo es el oficial; con una sub-skill
    extraída (solo la skill + `_plantilla_html/`) cae en su copia `assets/logo.png`,
    para que la skill siga siendo ejecutable por su cuenta."""
    if logo_path:
        return Path(logo_path), "--logo"
    if LOGO_DEFAULT.is_file():
        return LOGO_DEFAULT, "logo oficial del repositorio"

    candidatos = [Path("assets/logo.png")]
    if data_path:
        candidatos.append(Path(data_path).resolve().parent / "assets" / "logo.png")
    candidatos += sorted(Path().glob("*/assets/logo.png"))
    for c in candidatos:
        if c.is_file():
            return c, "copia local de la sub-skill"

    raise FileNotFoundError(
        f"Logo no encontrado. Busqué el oficial en {LOGO_DEFAULT} y una copia de "
        f"sub-skill en assets/logo.png y */assets/logo.png. Pasa --logo <ruta.png>."
    )


def logo_data_uri(logo_path):
    logo_path = Path(logo_path)
    if not logo_path.is_file():
        raise FileNotFoundError(f"Logo no encontrado: {logo_path}")
    data = logo_path.read_bytes()
    mime = "image/png" if logo_path.suffix.lower() == ".png" else "image/*"
    return f"data:{mime};base64," + base64.b64encode(data).decode("ascii")


def inyectar_flujo(data, paso, estado_path=None, pasos_path=None):
    """Añade/reemplaza data['flujo'] con el contexto real del proyecto."""
    ef = _cargar_estado_flujo()
    estado = ef.cargar_estado(estado_path or ESTADO_DEFAULT)
    pasos = ef.cargar_pasos(pasos_path or PASOS_DEFAULT)
    try:
        data["flujo"] = ef.construir_bloque_flujo(estado, pasos, paso)
    except ef.ReglaDelFlujo as exc:
        raise ValueError(str(exc)) from exc
    return data


def generar(
    data_path,
    output_path,
    template_path=None,
    logo_path=None,
    paso=None,
    estado_path=None,
    pasos_path=None,
    sin_flujo=False,
    validar_esquema=True,
):
    with open(data_path, encoding="utf-8") as f:
        data = json.load(f)

    if paso:
        data = inyectar_flujo(data, paso, estado_path, pasos_path)
    elif not sin_flujo and "flujo" not in data:
        print(
            "Error: falta el contexto del flujo.\n"
            "  Genera el HTML con --estado flujo_estado.json --paso html_N para que\n"
            "  el reporte lleve el contexto completo (avance, decisiones, omisiones),\n"
            "  o pasa --sin-flujo si es una skill suelta fuera de un proyecto.",
            file=sys.stderr,
        )
        return 2

    if validar_esquema:
        hallazgos = validar(data, exigir_flujo=not sin_flujo)
        if reportar(hallazgos):
            return 2

    template_path = Path(template_path) if template_path else TEMPLATE_DEFAULT
    logo_path, logo_origen = resolver_logo(logo_path, data_path)

    with open(template_path, encoding="utf-8") as f:
        html = f.read()

    data_js = json.dumps(data, ensure_ascii=False, indent=2)
    uri = logo_data_uri(logo_path)

    if "__REPORT_DATA__" not in html:
        raise ValueError("La plantilla no contiene el placeholder __REPORT_DATA__")
    if "__LOGO_BASE64__" not in html:
        raise ValueError("La plantilla no contiene el placeholder __LOGO_BASE64__")

    html = html.replace("__REPORT_DATA__", data_js)
    html = html.replace("__LOGO_BASE64__", uri)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    size_kb = len(uri) // 1024
    print(f"Reporte generado: {output_path}")
    print(f"  datos: {data_path}")
    print(f"  logo embebido: {size_kb} KB (base64) · {logo_origen}")
    flujo = data.get("flujo")
    if flujo:
        av = flujo.get("avance", {})
        print(
            f"  contexto del flujo: {flujo.get('paso_actual')} "
            f"({flujo.get('paso_orden')}/{flujo.get('total_pasos')}) · "
            f"{av.get('completados', 0)} completados · "
            f"{av.get('omitidos', 0)} omitidos"
        )
    else:
        print("  contexto del flujo: no incluido (--sin-flujo)")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description="Genera reporte HTML interactivo IRIS.")
    parser.add_argument("--data", required=True, help="JSON del análisis (window.REPORT_DATA)")
    parser.add_argument("--template", default=None, help="Plantilla HTML (default: reporte_base.html)")
    parser.add_argument("--logo", default=None,
                        help="Ruta del logo PNG (default: el oficial del repo; si no está, "
                             "assets/logo.png de la sub-skill)")
    parser.add_argument("-o", "--output", default="reporte.html", help="Ruta de salida HTML")
    parser.add_argument("--paso", default=None,
                        help="Paso del flujo (html_1 … html_11): inyecta el contexto")
    parser.add_argument("--estado", default=None,
                        help="flujo_estado.json (default: raíz del repo)")
    parser.add_argument("--pasos", default=None,
                        help="pasos.json (default: raíz del repo)")
    parser.add_argument("--sin-flujo", action="store_true",
                        help="Skill suelta: no exigir contexto del flujo")
    parser.add_argument("--no-strict", action="store_true",
                        help="Omitir la validación del esquema (no recomendado)")
    args = parser.parse_args(argv)

    try:
        return generar(
            args.data,
            args.output,
            args.template,
            args.logo,
            paso=args.paso,
            estado_path=args.estado,
            pasos_path=args.pasos,
            sin_flujo=args.sin_flujo,
            validar_esquema=not args.no_strict,
        )
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"Error: JSON inválido — {exc}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
