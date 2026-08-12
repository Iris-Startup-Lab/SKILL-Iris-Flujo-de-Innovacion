# persona-profile

> Fase: 2.Descubrimiento

Desarrolla protopersonas con atributos detallados integrando Job To Be Done (JTBD) con Momentos Vitales. Distingue entre protopersona hipotética (supuestos) y persona validada con datos reales. Usar cuando el usuario quiera crear perfiles de cliente/persona, protopersonas o buyer personas para estrategias y nuevos productos.

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
