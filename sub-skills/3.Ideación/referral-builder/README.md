# referral-builder

> Fase: 3.Ideación

Genera 10 modelos extend sobre la propuesta de valor (5 con inspiración y 5 disruptivos) para validar la deseabilidad de incentivos, generación de referidos y retención, con incentivos no genéricos y evidencia [VERIFICADO]/[ANÁLOGO]. Usar cuando el usuario quiera diseñar programas de referidos, winback o retención ligados a la propuesta de valor de su producto.

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
