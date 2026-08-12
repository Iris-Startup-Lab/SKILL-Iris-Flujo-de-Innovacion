# caressing-client

> Fase: 3.Ideación

Encuentra modelos de relación con el cliente (con inspiración en marcas reales y modelos disruptivos) para un producto/servicio, con evidencia [VERIFICADO]/[ESTIMACIÓN], priorización por factibilidad e hipótesis de validación testables. Usar cuando el usuario quiera diseñar o validar cómo tratar a su cliente y qué modelo de relación experimentar.

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
