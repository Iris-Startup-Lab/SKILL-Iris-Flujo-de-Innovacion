# senales-debiles

> Fase: 1.Investigación

Protocolo de 5 fases para detectar señales débiles en datos mixtos multi-formato (CSV, TXT, PDF, DOCX, XLSX, PPTX). El agente determina por contenido semántico si cada fuente aplica a análisis cuanti o cuali. Orden de filtrado unificado (exclusiones→novedad→redundancia), verificación de citas, rúbrica de calibración con modo fallback, blindaje de cruces transpoblacionales.

## Salida principal — su propio HTML detallado

El entregable principal de esta skill es el **HTML detallado que generan sus scripts**, no el
de la plantilla compartida. Lo define su `AGENTE.md`: ver «Como paso del flujo IRIS».

## Resumen del paso — HTML interactivo de la plantilla

Dentro del flujo, el paso se resume además en un **reporte HTML autocontenido** con el diseño
corporativo IRIS (logo oficial + paleta morado/dorado, tipografías Sora/Inter).

### Generar el HTML

1. Estructura el resultado en `reporte.json` (esquema `REPORT_DATA` de `_plantilla_html/README.md`).
2. Ejecuta **desde la raíz del repositorio**:

   ```bash
   # como paso del flujo: el contexto del flujo se inyecta solo
   python _plantilla_html/scripts/generar_html.py --data reporte.json \
       --estado flujo_estado.json --paso html_N -o html_N.html

   # skill suelta
   python _plantilla_html/scripts/generar_html.py --data reporte.json --sin-flujo -o reporte.html
   ```

3. Entrega el HTML.

El logo se embebe en base64: el oficial del repositorio, o la copia `assets/logo.png` de
esta carpeta si la skill corre fuera del repo. Diseño de referencia:
`Designs_files/Design_iris_main_colors.md`.

## Uso independiente

Esta skill es un paso del flujo IRIS, pero no depende de él para funcionar. Para usarla
sola basta con esta carpeta más `_plantilla_html/` al lado, y ejecutar el generador con
`--sin-flujo`: el contexto del flujo se omite y el logo sale de `assets/logo.png`.

Lo que aporta el repositorio completo —y que se pierde al extraerla— es el contexto del
flujo en el HTML (riel de progreso, decisiones previas, pasos omitidos) y el histórico de
`flujo_estado.json`. Nada de eso es necesario para producir el entregable.
