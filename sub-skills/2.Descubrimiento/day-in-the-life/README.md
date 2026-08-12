# day-in-the-life

> Fase: 2.Descubrimiento

Diseña y planea el experimento "A Day In The Life" (ADITL) con enfoque C.R.A.F.T.: Testing Card, plan de observación etnográfica, plantilla estandarizada de captura y esquema de codificación Jobs/Pains/Gains/Workarounds, con consentimiento informado. Usar cuando el usuario quiera planear una observación etnográfica o un experimento A Day In The Life para validar hipótesis de comportamiento.

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
