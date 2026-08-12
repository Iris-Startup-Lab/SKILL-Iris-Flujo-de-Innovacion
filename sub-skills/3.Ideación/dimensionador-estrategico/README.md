# dimensionador-estrategico

> Fase: 3.Ideación

Dimensiona el potencial de negocio de ideas de innovación con rigor tipo McKinsey/Bain/VC — TAM/SAM/SOM, panorama competitivo, CLV/CAC y cross-selling por buyer persona, score de atractivo /25, riesgos y veredicto (PROTOTIPAR / VALIDAR MÁS / DESCARTAR). Usa esta skill siempre que el usuario pida "dimensionar" ideas, priorizar ideas de negocio o de innovación, evaluar el potencial de una idea, calcular TAM/SAM/SOM, o mencione el "Dimensionador Estratégico" por nombre — incluso si no detalla el formato exacto. También aplica cuando el usuario comparte una lista de ideas filtradas por un equipo de innovación y pide ayuda para decidir cuáles llevar a prototipado.

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
