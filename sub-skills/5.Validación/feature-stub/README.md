# feature-stub

> Fase: 5.Validación

Diseña el experimento Feature Stub (fake-door ético) para validar interés y demanda de una funcionalidad antes de construirla: Testing Card con umbral de interés, instrumentación de medición de clics y regla de transparencia post-clic. Usar cuando el usuario quiera validar una funcionalidad simulada sin desarrollarla.

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
