# ideacion

> Fase: 3.Ideación

Guía procesos de ideación generando ideas con metodologías SCAMPER, Crazy 8s, Doblin, Analogía y aleatoria, y las evalúa en Novedad/Utilidad/Factibilidad (1-10) con ranking y priorización de 2-3 ideas para prototipar. Usar cuando el usuario quiera generar y evaluar ideas de solución a partir de un "How Might We".

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
