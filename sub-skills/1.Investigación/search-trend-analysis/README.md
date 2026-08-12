# search-trend-analysis

> Fase: 1.Investigación

Analiza tendencias de búsqueda online (Google Trends vía pytrends + webfetch) para validar demanda temprana de una idea con enfoque C.R.A.F.T. Genera Testing Card, keywords primarias/secundarias, evidencia con datos reales y recomendación perseverar/pivotear/descartar. Usar cuando el usuario quiera validar si existe interés/demanda de búsqueda para su propuesta de valor, segmento o producto antes de invertir, o pida análisis de tendencias, volumen de búsqueda o Search Trend Analysis.

## Salida principal — HTML interactivo

Esta skill entrega su resultado como un **reporte HTML autocontenido** con el diseño corporativo IRIS (logo oficial + paleta morado/dorado, tipografías Sora/Inter).

### Generar el HTML

1. Estructura el resultado en `reporte.json` (esquema `REPORT_DATA` de `_plantilla_html/README.md`).
2. Ejecuta:
   ```bash
   python ../../../_plantilla_html/scripts/generar_html.py --data reporte.json -o reporte.html
   ```
3. Entrega `reporte.html`.

El logo oficial (`assets/logo.png`) se embebe automáticamente en base64. Diseño de referencia: `Designs_files/Design_iris_main_colors.md`.
