# email-campaign

> Fase: 5.Validación

Diseña el experimento Email Campaign (Testing Card, estructura del experimento y modelo de email) para validar hipótesis de interés/deseo, calculando significancia estadística de la muestra y cumpliendo compliance de email marketing (opt-in, unsubscribe). Usar cuando el usuario quiera validar una propuesta de valor u oferta con una campaña de correo.

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
