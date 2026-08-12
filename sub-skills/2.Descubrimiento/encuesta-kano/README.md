# encuesta-kano

> Fase: 2.Descubrimiento

Genera una encuesta modelo Kano para evaluar el valor percibido y la deseabilidad de cada feature de una propuesta de valor, y clasifica las respuestas (funcional x disfuncional) en categorías M/O/A/I/R/Q. Usar cuando el usuario quiera crear una encuesta Kano, evaluar la deseabilidad de características/funcionalidades de un producto, o clasificar respuestas Kano.

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
