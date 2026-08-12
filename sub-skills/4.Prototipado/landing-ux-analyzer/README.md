# landing-ux-analyzer

> Fase: 4.Prototipado

Audita la UX/UI de una landing page (jerarquía visual, tipografía, contraste WCAG 2.2 AA, white space, touch targets, responsividad) generando una lista priorizada de hallazgos y quick wins. Usar cuando el usuario quiera identificar áreas de mejora de UX/UI en una landing, a partir de URL o capturas.

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
