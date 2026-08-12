"""
logo_base64.py

Helper para convertir el logo oficial de IRIS a base64. Útil para inspección
manual o para incrustar el logo en otros artefactos (HTML, correos, etc.).
El script generar_html.py ya embebe el logo automáticamente; este helper es
opcional.

Uso:
    python logo_base64.py [ruta_png]            # imprime el data URI
    python logo_base64.py [ruta_png] -o logo.txt # guarda el data URI en archivo
"""
import argparse
import base64
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LOGO = _REPO_ROOT / "imagenes_iconos_etc" / "Logos_GS_Iris_transparent.png"


def main(argv=None):
    parser = argparse.ArgumentParser(description="Convierte el logo a base64.")
    parser.add_argument("logo", nargs="?", default=str(DEFAULT_LOGO), help="Ruta del PNG")
    parser.add_argument("-o", "--output", default=None, help="Archivo donde guardar el data URI")
    args = parser.parse_args(argv)

    path = Path(args.logo)
    if not path.is_file():
        print(f"Error: no se encontró '{path}'", file=sys.stderr)
        return 1

    data = path.read_bytes()
    mime = "image/png" if path.suffix.lower() == ".png" else "image/*"
    uri = f"data:{mime};base64," + base64.b64encode(data).decode("ascii")

    if args.output:
        with open(args.output, "w", encoding="ascii") as f:
            f.write(uri)
        print(f"Data URI guardado en: {args.output} ({len(uri)//1024} KB)")
    else:
        print(uri)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
