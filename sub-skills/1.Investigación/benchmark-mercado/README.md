# benchmark-mercado

> Fase: 1.Investigación

Genera benchmarks detallados de industrias y mercados (default México) para desarrollar productos y estrategias de innovación: tabla comparativa de 10 empresas, estadísticas TAM/SAM/SOM, top 3 competidores internacionales, 5 Fuerzas de Porter y oportunidades de disrupción, con datos trazables y supuestos explícitos. Usar cuando el usuario pida un benchmark de mercado, análisis de competidores, tamaño de mercado, market share o panorama competitivo de un nicho/industria.

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
