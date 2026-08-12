# problem-solution-fit

> Fase: 2.Descubrimiento

Genera un análisis estructurado de Problem-Solution Fit a partir de entrevistas o encuestas: identifica problemas clave, evalúa importancia, satisfacción con la solución actual y costos, valida la solución propuesta y extrae insights JTBD y Blue Ocean, exportando a CSV. Usar cuando el usuario tenga entrevistas/encuestas y quiera evaluar si su solución encaja con los problemas del cliente.

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
