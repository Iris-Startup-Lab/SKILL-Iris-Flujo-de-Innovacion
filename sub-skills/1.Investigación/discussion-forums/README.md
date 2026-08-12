# discussion-forums

> Fase: 1.Investigación

Diseña y planea el experimento Discussion Forums para descubrir jobs, pains y gains no resueltos analizando foros y comunidades (Reddit, Quora, Discord). Genera Testing Card, plan de ejecución con taxonomía Jobs/Pains/Gains/Workarounds y recomendaciones éticas. Usar cuando el usuario quiera descubrir problemas reales, deseos insatisfechos o workarounds de un producto/competencia a partir de conversaciones en foros, o pida diseñar un experimento de análisis de foros/comunidades.

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
