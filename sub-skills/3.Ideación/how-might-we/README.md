# how-might-we

> Fase: 3.Ideación

Guía la generación de preguntas "How Might We" (HMW) para desbloquear soluciones innovadoras, enmarcadas en una ambición estratégica y una palanca específicas (Optimizar/Crecer/Expandir/Crear/Reinventar). Usar cuando el usuario quiera reformular un problema o reto de diseño en oportunidades de solución con formato "¿Cómo podríamos...?".

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
