# entrevistas-empatia

> Fase: 2.Descubrimiento

Diseña entrevistas de empatía estratégicas aplicando The Mom Test, Design Thinking y Empathic Communication. Genera Testing Card, guía de entrevista por secciones y plantilla de notas/codificación post-entrevista. Usar cuando el usuario quiera diseñar guías de entrevista, planificar entrevistas de descubrimiento o validar hipótesis con entrevistas de empatía.

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
