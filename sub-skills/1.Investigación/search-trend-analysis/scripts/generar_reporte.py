"""
generar_reporte.py

Consolida los datos reales de Google Trends (google_trends.py) y los benchmarks
públicos recopilados vía webfetch en un reporte markdown estructurado: tabla de
evidencia por keyword y Testing Card. El LLM añade después la interpretación,
insights y la recomendación final (perseverar/pivotear/descartar).

Uso:
    python generar_reporte.py --trends trends.json --params params.json \
        [--webfetch webfetch.json] -o reporte_tendencias.md

`params.json` mínimo:
{
  "hipotesis": "Creemos que ...",
  "region": "México",
  "periodo": "últimos 12 meses",
  "idioma": "español de México",
  "umbral_exito": "volumen mensual > 1,000 búsquedas o crecimiento > 15% anual",
  "keywords": ["huerto urbano", "composta casera"]
}
"""
import argparse
import json


def _cargar(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _tabla_evidencia(trends, webfetch, params):
    lineas = []
    lineas.append("| Keyword | Interés promedio (0-100) | Tendencia (delta) | Queries relacionadas (top 3) | Volumen/benchmark (webfetch) |")
    lineas.append("|---|---|---|---|---|")
    umbral = params.get("umbral_exito", "")
    for kw in params.get("keywords", []):
        prom = trends.get("promedio", {}).get(kw, "[no disponible]")
        tend = trends.get("tendencia", {}).get(kw, {})
        delta = tend.get("delta_primero_ultimo", "[no disponible]")
        queries = trends.get("queries_relacionadas", {}).get(kw, {}).get("top", [])
        top3 = ", ".join(q.get("query", "") for q in queries[:3]) or "[no disponible]"
        bm = webfetch.get(kw, {}).get("nota", "") if webfetch else "[sin dato webfetch]"
        lineas.append(f"| {kw} | {prom} | {delta} | {top3} | {bm} |")
    lineas.append("")
    lineas.append(f"**Criterio de éxito:** {umbral}")
    return "\n".join(lineas)


def _testing_card(params):
    hip = params.get("hipotesis", "[hipótesis]")
    region = params.get("region", "")
    periodo = params.get("periodo", "")
    idioma = params.get("idioma", "")
    umbral = params.get("umbral_exito", "")
    kws = ", ".join(params.get("keywords", []))
    return "\n".join([
        "## Testing Card",
        "",
        f"- **Hipótesis:** {hip}",
        f"- **Experimento:** análisis de tendencias de búsqueda con Google Trends (+ webfetch) para las keywords `{kws}` durante {periodo} en {region} / {idioma}.",
        "- **Métrica:** interés relativo (0-100), delta de tendencia, queries relacionadas y benchmarks públicos.",
        f"- **Criterio de éxito:** {umbral}.",
    ])


def generar(trends_path, params_path, webfetch_path, output_path):
    trends = _cargar(trends_path)
    params = _cargar(params_path)
    webfetch = _cargar(webfetch_path) if webfetch_path else {}

    secciones = []
    secciones.append("# Search Trend Analysis — Evidencia")
    secciones.append("")
    secciones.append(f"**Región:** {params.get('region', '')} · **Periodo:** {params.get('periodo', '')} · **Idioma:** {params.get('idioma', '')}")
    secciones.append("")
    secciones.append(_testing_card(params))
    secciones.append("")
    secciones.append("## Evidencia recolectada")
    secciones.append("")
    secciones.append(_tabla_evidencia(trends, webfetch, params))
    secciones.append("")
    secciones.append("## Nota sobre los datos")
    secciones.append("")
    secciones.append("Google Trends (pytrends) entrega interés **relativo 0-100**, no volúmenes absolutos. Los benchmarks de volumen vía webfetch son estimaciones públicas y deben marcarse con `*`.")

    contenido = "\n".join(secciones) + "\n"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(contenido)

    print(f"Reporte de evidencia guardado en: {output_path}")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Consolida datos reales en un reporte markdown.")
    parser.add_argument("--trends", required=True, help="JSON de google_trends.py")
    parser.add_argument("--params", required=True, help="JSON de parámetros")
    parser.add_argument("--webfetch", help="JSON opcional de datos webfetch")
    parser.add_argument("-o", "--output", default="reporte_tendencias.md", help="Salida markdown")
    args = parser.parse_args(argv)
    generar(args.trends, args.params, args.webfetch, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
