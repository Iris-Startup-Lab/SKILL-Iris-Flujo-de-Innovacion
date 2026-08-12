# online-ads

> Fase: 5.Validación

Genera campañas de anuncios online (copy + descripción de arte visual + prompts de imagen listos para Midjourney/DALL·E/Adobe Firefly) en modos Estándar y Disruptivo para validar hipótesis de deseabilidad, con Testing Card, presupuesto mínimo viable y checklist de compliance. Usar cuando el usuario quiera crear copys/artes de anuncios para validar una propuesta en Meta, TikTok o Google Ads.

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
