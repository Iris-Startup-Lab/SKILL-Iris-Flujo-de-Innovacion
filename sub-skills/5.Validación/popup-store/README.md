# popup-store

> Fase: 5.Validación

Diseña el experimento Pop-Up Store (Testing Business Ideas) para validar hipótesis de mercado, compra y experiencia física: Testing Card con KPIs de compra y percepción, diseño del espacio por presupuesto, protocolo de captura de datos in situ y checklist de compliance. Usar cuando el usuario quiera diseñar una pop-up store o activación física temporal para validar su propuesta.

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
