# business-model-navigator

> Fase: 3.Ideación

Recomienda los mejores patterns de modelos de negocio (catálogo de 60 patrones del Business Model Navigator) y experimentos para validar una hipótesis, con lógica de priorización y formato de recomendación estructurado. Usar cuando el usuario quiera explorar modelos de negocio, recomendar patterns de negocio o diseñar experimentos de validación ágil.

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
