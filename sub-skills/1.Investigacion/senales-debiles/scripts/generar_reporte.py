#!/usr/bin/env python3
"""
generar_reporte.py — Genera reporte_ejecutivo.html desde fase4_output.json + plantilla.

Uso:
    python generar_reporte.py <directorio_proyecto> [-o reporte_ejecutivo.html]

El directorio debe contener fase4_output.json con bloque 'reporte' que incluye:
- titulo, fecha, pregunta_investigacion, resumen_ejecutivo
- señales: lista con objetos {titulo, dato, expectativa, pregunta, hipotesis,
    grafica?: {type, data, options}, heatmap_svg_path?: "heatmap.svg"}
- decisiones: lista con {exploracion, basado_en: "Señal Débil N", resultado_esperado}
- footer: {limitaciones: [...], fuentes: [...], metodologia: [...]}

La plantilla está en scripts/plantilla_reporte.html (tokens {{TOKEN}}).
"""
import sys
import json
import io
import re
from pathlib import Path

# Altura del contenedor de gráficas Chart.js (design-system §3.3).
# Con maintainAspectRatio:false, Chart.js requiere un contenedor con altura
# definida; sin ella, el canvas crece en bucle infinito de resize. Las barras
# horizontales amplifican el problema porque su altura crece con el número de
# categorías. El piso es el token del design system; el script escala hacia
# arriba según las categorías reales.
CHART_PX_PER_ROW = 48
CHART_MIN_HEIGHT_PX = 260


def _normalizar_labels(labels):
    """Convierte labels con saltos ('\\n' o '\n' literal) en arrays de strings
    para Chart.js: cada elemento del array es una línea del tick. No altera
    labels ya correctos (strings simples o arrays)."""
    if not isinstance(labels, list):
        return labels
    out = []
    for lbl in labels:
        if isinstance(lbl, str) and ("\n" in lbl or "\\n" in lbl):
            partes = [p for p in re.split(r"\\n|\n", lbl) if p]
            out.append(partes if len(partes) > 1 else partes[0])
        else:
            out.append(lbl)
    return out


def load_template():
    tpl_path = Path(__file__).with_name("plantilla_reporte.html")
    with open(tpl_path, encoding="utf-8-sig") as f:
        return f.read()


def build_senales_html(senales, proyecto_dir):
    """Genera HTML de tarjetas de señal a partir de lista de dicts."""
    cards = []
    graficas = {}
    for i, s in enumerate(senales, start=1):
        titulo = s.get("titulo", f"Señal {i}")
        dato = s.get("dato", "")
        expectativa = s.get("expectativa", "")
        pregunta = s.get("pregunta", "")
        hipotesis = s.get("hipotesis", "")
        validacion_pendiente = s.get("validacion_pendiente", "")

        # Heatmap SVG incrustado si existe
        heatmap_html = ""
        hm_path = s.get("heatmap_svg_path")
        if hm_path:
            hm_file = Path(proyecto_dir) / hm_path
            if hm_file.exists():
                with open(hm_file, encoding="utf-8-sig") as f:
                    svg_content = f.read()
                # El script generar_heatmap.py ya devuelve <div class="chart-wrap">...</div>
                # Extraer solo el <svg>...</svg> para incrustar limpio
                import re
                m = re.search(r'(<svg[^>]*>.*?</svg>)', svg_content, re.DOTALL)
                if m:
                    heatmap_html = f'<div class="chart-wrap" style="overflow-x:auto">{m.group(1)}</div>'

        # Gráfica Chart.js (canvas + config)
        grafica_html = ""
        g = s.get("grafica")
        if g:
            canvas_id = f"chart-senal-{i}"
            # Config normalizada para Chart.js
            chart_type = g.get("type", "bar")
            data = dict(g.get("data", {}) or {})
            if isinstance(data.get("labels"), list):
                data["labels"] = _normalizar_labels(data["labels"])
            options = g.get("options", {})
            # Asegurar opciones base
            if "responsive" not in options:
                options["responsive"] = True
            if "maintainAspectRatio" not in options:
                options["maintainAspectRatio"] = False
            if "plugins" not in options:
                options["plugins"] = {}
            if "tooltip" not in options["plugins"]:
                options["plugins"]["tooltip"] = {"enabled": True}
            graficas[canvas_id] = {"type": chart_type, "data": data, "options": options}
            # Altura ancla del contenedor (design-system §3.3): sin ella,
            # maintainAspectRatio:false + contenedor auto = bucle de resize.
            n_labels = len(data["labels"]) if isinstance(data.get("labels"), list) else 0
            min_h = max(CHART_MIN_HEIGHT_PX, n_labels * CHART_PX_PER_ROW)
            grafica_html = (
                f'<div class="chart-wrap" style="height:{min_h}px;overflow-x:auto">'
                f'<canvas id="{canvas_id}" aria-label="Gráfica: {titulo}"></canvas></div>'
            )

        # Construir tarjeta
        card = f"""      <article class="card senal-debil">
        <h3>Señal Débil {i}: {titulo}</h3>
        <p class="campo"><strong>Dato:</strong> {dato}</p>
        <p class="campo"><strong>Expectativa:</strong> {expectativa}</p>
        <p class="campo"><strong>Pregunta:</strong> {pregunta}</p>
        <div class="hipotesis"><strong>Hipótesis:</strong> {hipotesis}</div>"""
        if validacion_pendiente:
            card += f'\n        <div class="campo" style="font-size:0.85rem;color:var(--ink-soft)"><strong>Validación pendiente:</strong> {validacion_pendiente}</div>'
        if grafica_html:
            card += f"\n        {grafica_html}"
        if heatmap_html:
            card += f"\n        {heatmap_html}"
        card += "\n      </article>"
        cards.append(card)

    return "\n".join(cards), graficas


def build_decisiones_html(decisiones):
    """Genera HTML de tarjetas de decisión."""
    cards = []
    for d in decisiones:
        basada = d.get("basado_en", "")
        exploracion = d.get("exploracion", "")
        resultado = d.get("resultado_esperado", "")
        # El validador espera "Basado en: Señal Débil N"
        card = f"""      <article class="decision">
        <h3>Basado en: {basada}</h3>
        <p>{exploracion} {resultado}</p>
      </article>"""
        cards.append(card)
    return "\n".join(cards)


def build_footer_html(footer):
    """Genera <li> para cada columna del footer."""
    lim = "\n".join(f"          <li>{x}</li>" for x in footer.get("limitaciones", []))
    fu = "\n".join(f"          <li>{x}</li>" for x in footer.get("fuentes", []))
    met = "\n".join(f"          <li>{x}</li>" for x in footer.get("metodologia", []))
    return lim, fu, met


def main():
    if len(sys.argv) < 2:
        print("Uso: python generar_reporte.py <directorio_proyecto> [-o salida.html]", file=sys.stderr)
        sys.exit(1)
    if sys.argv[1] in ("-h", "--help"):
        # El docstring del modulo ya documenta el uso y el bloque 'reporte' esperado.
        print((__doc__ or "").strip())
        sys.exit(0)

    proyecto_dir = Path(sys.argv[1])
    salida = None
    if "-o" in sys.argv:
        i = sys.argv.index("-o")
        if i + 1 >= len(sys.argv):
            print("Falta ruta de salida tras -o", file=sys.stderr)
            sys.exit(1)
        salida = Path(sys.argv[i + 1])
    else:
        salida = proyecto_dir / "reporte_ejecutivo.html"

    fase4_path = proyecto_dir / "fase4_output.json"
    if not fase4_path.exists():
        print(f"ERROR: No existe {fase4_path}", file=sys.stderr)
        sys.exit(1)

    with open(fase4_path, encoding="utf-8-sig") as f:
        fase4 = json.load(f)

    reporte = fase4.get("reporte")
    if not reporte:
        print("ERROR: fase4_output.json no contiene bloque 'reporte'", file=sys.stderr)
        sys.exit(1)

    # Leer plantilla
    tpl = load_template()

    # Construir partes
    senales_html, graficas = build_senales_html(reporte.get("senales", []), proyecto_dir)
    decisiones_html = build_decisiones_html(reporte.get("decisiones", []))
    lim_html, fu_html, met_html = build_footer_html(reporte.get("footer", {}))

    # Reemplazar tokens
    resumen = reporte.get("resumen_ejecutivo", "")
    if isinstance(resumen, list):
        resumen = "<br>".join(resumen)
    html = tpl.replace("{{TITULO}}", reporte.get("titulo", "Reporte de Señales Débiles"))
    html = html.replace("{{FECHA}}", reporte.get("fecha", ""))
    html = html.replace("{{PREGUNTA}}", reporte.get("pregunta_investigacion", ""))
    html = html.replace("{{RESUMEN_EJECUTIVO}}", resumen)
    html = html.replace("{{SENALES_HTML}}", senales_html)
    html = html.replace("{{DECISIONES_HTML}}", decisiones_html)
    html = html.replace("{{LIMITACIONES_HTML}}", lim_html)
    html = html.replace("{{FUENTES_HTML}}", fu_html)
    html = html.replace("{{METODOLOGIA_HTML}}", met_html)

    # Inyectar graficas en window.REPORT_GRAFICAS antes del script final
    if graficas:
        graficas_json = json.dumps(graficas, ensure_ascii=False)
        inject = f"    window.REPORT_GRAFICAS = {graficas_json};\n  "
        html = html.replace("    // Render Chart.js gráficas embebidas", inject + "    // Render Chart.js gráficas embebidas")

    # Escribir salida
    with io.open(salida, "w", encoding="utf-8", newline="") as f:
        f.write(html)

    print(f"Reporte generado: {salida}")


if __name__ == "__main__":
    main()
