"""
Generador determinista de heatmap SVG inline a partir de un JSON de
frecuencias (2 variables categóricas). Reemplaza la generación del
heatmap por parte del LLM, siguiendo la especificación técnica de
SPEC.md seccion 5.

El margen inferior del viewBox se calcula dinámicamente a partir de la
etiqueta de eje X más larga (extensión ~0.707*ancho para rotación de 45°),
de modo que las etiquetas nunca se recorten en grids grandes.

Uso:
    python generar_heatmap.py frecuencias.json [-o salida.svg]

    Si se omite -o, el SVG se imprime por stdout (cuidado con redirecciones
    en consolas que re-codifican UTF-8, p.ej. `>` en PowerShell 5.1: usa -o
    en su lugar para garantizar encoding UTF-8).

Formato esperado de frecuencias.json:
{
  "eje_x": ["Categoría A", "Categoría B", "Categoría C"],
  "eje_y": ["Grupo 1", "Grupo 2"],
  "eje_x_titulo": "Categoría de problema",
  "eje_y_titulo": "Categoría de solución",
  "valores": [[12, 5, 0], [3, 27, 9]]   # valores[fila_y][col_x]
}
"""
import sys
import io
import json

# Escala de 5 niveles, paleta purple (SPEC.md sección 5)
ESCALA_COLORES = ["#D9CCEF", "#B8A3D9", "#7A4E96", "#5A3A8C", "#3D2766"]

CELL_W = 56
CELL_H = 56
CELL_MIN = 50
OFFSET_X = 140
OFFSET_Y = 40
MARGIN_RIGHT = 20
MARGIN_BOTTOM_MIN = 90
# Ancho aprox. por carácter a font-size 11 (Inter). Las etiquetas de eje X
# rotadas 45° descienden ~0.707*ancho desde su ancla: el margen inferior debe
# derivarse de la etiqueta más larga, nunca ser constante.
LABEL_PX_POR_CARACTER = 6.0
LABEL_ROTATION_FACTOR = 0.7071


def color_para_valor(valor, minimo, maximo):
    if maximo == minimo:
        idx = 0
    else:
        frac = (valor - minimo) / (maximo - minimo)
        idx = min(int(frac * len(ESCALA_COLORES)), len(ESCALA_COLORES) - 1)
    return ESCALA_COLORES[idx]


def generar_svg_heatmap(data):
    eje_x = data["eje_x"]
    eje_y = data["eje_y"]
    valores = data["valores"]
    eje_x_titulo = data.get("eje_x_titulo", "")
    eje_y_titulo = data.get("eje_y_titulo", "")

    n_cols = len(eje_x)
    n_rows = len(eje_y)

    cell_w = CELL_W if (n_cols <= 6 and n_rows <= 6) else CELL_MIN
    cell_h = CELL_H if (n_cols <= 6 and n_rows <= 6) else CELL_MIN

    flat = [v for row in valores for v in row]
    minimo, maximo = min(flat), max(flat)

    # Margen inferior dinámico: si hay etiquetas de eje X rotadas 45°, cada una
    # desciende ~0.707 * ancho desde su ancla; además queda el título del eje.
    # Un margen fijo recorta etiquetas largas en grids grandes (8+ columnas).
    max_largo_etiqueta = max((len(e) for e in eje_x), default=0)
    hay_rotadas = any(len(e) > 8 for e in eje_x)
    if hay_rotadas:
        margen_necesario = int(
            LABEL_ROTATION_FACTOR * max_largo_etiqueta * LABEL_PX_POR_CARACTER
            + 40  # 15px de separación + título del eje + holgura
        )
    else:
        margen_necesario = 0
    margin_bottom = max(MARGIN_BOTTOM_MIN, margen_necesario)

    ancho = OFFSET_X + n_cols * cell_w + MARGIN_RIGHT
    alto = OFFSET_Y + n_rows * cell_h + margin_bottom

    partes = []
    partes.append(
        f'<svg viewBox="0 0 {ancho} {alto}" xmlns="http://www.w3.org/2000/svg" '
        f'style="width:100%;max-width:{max(700, ancho)}px;font-family:\'Inter\',sans-serif">'
    )

    # Celdas
    for row_i, fila in enumerate(valores):
        for col_i, valor in enumerate(fila):
            x = OFFSET_X + col_i * cell_w
            y = OFFSET_Y + row_i * cell_h
            color = color_para_valor(valor, minimo, maximo)
            partes.append(
                f'<rect x="{x}" y="{y}" width="{cell_w}" height="{cell_h}" '
                f'fill="{color}" rx="2"><title>{eje_y[row_i]} / {eje_x[col_i]}: {valor}</title></rect>'
            )
            text_color = "#2A2433" if color in ESCALA_COLORES[:2] else "#FFFFFF"
            partes.append(
                f'<text x="{x + cell_w/2}" y="{y + cell_h/2 + 4}" text-anchor="middle" '
                f'font-size="10" fill="{text_color}">{valor}</text>'
            )

    # Etiquetas eje Y (filas)
    for row_i, etiqueta in enumerate(eje_y):
        y = OFFSET_Y + row_i * cell_h + cell_h / 2 + 4
        partes.append(
            f'<text x="{OFFSET_X - 10}" y="{y}" text-anchor="end" '
            f'font-size="11" fill="#5C5468">{etiqueta}</text>'
        )

    # Etiquetas eje X (columnas), rotadas 45° si son largas
    for col_i, etiqueta in enumerate(eje_x):
        x = OFFSET_X + col_i * cell_w + cell_w / 2
        y = OFFSET_Y + n_rows * cell_h + 15
        if len(etiqueta) > 8:
            partes.append(
                f'<text x="{x}" y="{y}" text-anchor="end" font-size="11" '
                f'fill="#5C5468" transform="rotate(-45 {x} {y})">{etiqueta}</text>'
            )
        else:
            partes.append(
                f'<text x="{x}" y="{y}" text-anchor="middle" font-size="11" '
                f'fill="#5C5468">{etiqueta}</text>'
            )

    # Títulos de ejes
    if eje_x_titulo:
        partes.append(
            f'<text x="{OFFSET_X + (n_cols * cell_w) / 2}" y="{alto - 5}" '
            f'text-anchor="middle" font-size="12" font-weight="600" fill="#2A2433">{eje_x_titulo}</text>'
        )
    if eje_y_titulo:
        cy = OFFSET_Y + (n_rows * cell_h) / 2
        partes.append(
            f'<text x="14" y="{cy}" text-anchor="middle" font-size="12" font-weight="600" '
            f'fill="#2A2433" transform="rotate(-90 14 {cy})">{eje_y_titulo}</text>'
        )

    partes.append('</svg>')
    svg = "".join(partes)
    return f'<div class="chart-wrap" style="overflow-x:auto">{svg}</div>'


def main():
    args = sys.argv[1:]
    if not args:
        print("Uso: python generar_heatmap.py frecuencias.json [-o salida.svg]", file=sys.stderr)
        sys.exit(1)

    entrada = args[0]
    salida = None
    if "-o" in args:
        i = args.index("-o")
        if i + 1 >= len(args):
            print("Falta la ruta de salida tras -o", file=sys.stderr)
            sys.exit(1)
        salida = args[i + 1]

    with open(entrada, encoding="utf-8") as f:
        data = json.load(f)

    svg = generar_svg_heatmap(data)

    if salida:
        with io.open(salida, "w", encoding="utf-8", newline="") as f:
            f.write(svg)
    else:
        sys.stdout.buffer.write(svg.encode("utf-8"))
        sys.stdout.buffer.flush()


if __name__ == "__main__":
    main()
