# senales-debiles

> Fase: 1.Investigación

Protocolo de 5 fases para detectar señales débiles en datos mixtos multi-formato (CSV, TXT, PDF, DOCX, XLSX, PPTX). El agente determina por contenido semántico si cada fuente aplica a análisis cuanti o cuali. Orden de filtrado unificado (exclusiones→novedad→redundancia), verificación de citas, rúbrica de calibración con modo fallback, blindaje de cruces transpoblacionales.

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
