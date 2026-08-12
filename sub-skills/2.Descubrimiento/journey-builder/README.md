# journey-builder

> Fase: 2.Descubrimiento

Genera User y Customer Journeys estructurados por pasos (default 10, flexible) con acciones clave, costos, obstáculos e insights, marcando el "momento de la verdad" y etiquetando suposiciones. Usar cuando el usuario quiera crear un customer journey, user journey o mapa de experiencia del cliente a partir de entrevistas o encuestas.

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
