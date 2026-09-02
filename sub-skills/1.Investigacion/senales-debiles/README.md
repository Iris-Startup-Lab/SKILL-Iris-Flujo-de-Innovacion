# senales-debiles

> Fase: 1.Investigación

Protocolo de 5 fases para detectar señales débiles en datos mixtos multi-formato (CSV, TXT, PDF, DOCX, XLSX, PPTX). El agente determina por contenido semántico si cada fuente aplica a análisis cuanti o cuali. Orden de filtrado unificado (exclusiones→novedad→redundancia), verificación de citas, rúbrica de calibración con modo fallback, blindaje de cruces transpoblacionales.

## El pipeline

```text
Fase 0 Viabilidad → Fase 1 Cuanti → Fase 2 Cuali → Fase 3 Cruce → Fase 4 Entrega → gate
```

Cada fase lee el JSON de la anterior y escribe el suyo (`faseN_output.json`), así que ninguna
depende de que el modelo «recuerde» lo que hizo antes. Las reglas globales viven en
[AGENTE.md](AGENTE.md); cada fase, en `references/fase-N-*.md`. El contenido y formato del
reporte los fija [SPEC.md](SPEC.md) y su aspecto visual
[references/design-system.md](references/design-system.md).

## Salida principal — su propio HTML detallado

El entregable principal es `reporte_ejecutivo.html`, y **no lo escribe el modelo a mano**:

```bash
# el LLM escribe el bloque `reporte` de fase4_output.json; el script aplica la plantilla
python sub-skills/1.Investigacion/senales-debiles/scripts/generar_reporte.py <proyecto> \
    -o reporte_ejecutivo.html
```

`scripts/plantilla_reporte.html` congela el design system (Sora/Inter, paleta morado→dorado,
radius 14px, Chart.js) y el generador incrusta el heatmap SVG y las gráficas. Ese reporte no
lleva el logo: es un documento de análisis, no una portada de catálogo. El logo corporativo
va en el HTML del paso (siguiente sección).

## Scripts

Ninguna cifra del reporte la escribe el modelo: la calculan estos scripts y el resultado
alimenta el JSON (regla de integridad de `AGENTS.md` §4).

| Script | Cuándo | Qué hace |
| --- | --- | --- |
| `scripts/preview_columnas.py` | antes de Fase 0 | Encabezados, tipo, cardinalidad y muestras por columna, para proponer el mapeo a roles en la consulta inicial única |
| `scripts/normalizar_transcripciones.py` | Fase 0 | Serializa a `transcripciones/*.txt` una fuente cualitativa que llegó en planilla (XLSX/DOCX con columna de diálogo y hablante) |
| `scripts/fase0_enriquecer.py` | Fase 0 | Enriquece el CSV y deja el dataset que es fuente única de verdad para los números |
| `scripts/fase1_analisis.py` | Fase 1 | Conteos, tasas, intervalos de Wilson y co-ocurrencias sobre el CSV enriquecido |
| `scripts/preparar_heatmap.py` + `scripts/generar_heatmap.py` | Fase 1/4 | `frecuencias.json` → `heatmap.svg` con márgenes dinámicos |
| `scripts/generar_reporte.py` + `scripts/plantilla_reporte.html` | Fase 4 | `fase4_output.json` → `reporte_ejecutivo.html` autocontenido |
| `scripts/logo_base64.py` | opcional | PNG → data URI, si algún día el reporte propio necesita el logo embebido |

### El gate

```bash
python sub-skills/1.Investigacion/senales-debiles/scripts/run_gate.py <proyecto> \
    -o gate_report.json --corpus <carpeta_txt> --dataset <dataset.csv>
```

`run_gate.py` es el **único** actor con autoridad para marcar `true` en el bloque
`validacion` de `fase4_output.json`; el modelo lo deja en `{}`. Corre en orden
`validar_esquema.py`, `verificar_trazabilidad.py`, `validar_reporte.py`,
`verificar_citas.py` y `verificar_numeros.py`, con timeout por verificador. Sin un
`gate_report.json` real el reporte se entrega marcado **NO VERIFICADO**.
`scripts/invariante_clasificacion.py` es la implementación compartida del Filtro 2, que
`validar_esquema.py` usa como gate intermedio al cerrar las Fases 1, 2 y 3.

## Resumen del paso — HTML interactivo de la plantilla

Dentro del flujo, el paso se resume además en un **reporte HTML autocontenido** con el diseño
corporativo IRIS (logo oficial + paleta morado/dorado, tipografías Sora/Inter).

### Generar el HTML

1. Estructura el resultado en `reporte.json` (esquema `REPORT_DATA` de `_plantilla_html/README.md`),
   con `meta.origen_datos` declarando si los datos son reales, simulados o mixtos.
2. Ejecuta **desde la raíz del repositorio**:

   ```bash
   # como paso del flujo: el contexto del flujo se inyecta solo
   python _plantilla_html/scripts/generar_html.py --data reporte.json \
       --estado flujo_estado.json --paso html_1 -o html_1.html

   # skill suelta
   python _plantilla_html/scripts/generar_html.py --data reporte.json --sin-flujo -o reporte.html
   ```

3. Entrega los dos HTML: el del paso y `reporte_ejecutivo.html` como anexo.

El logo se embebe en base64: el oficial del repositorio, o la copia `assets/logo.png` de
esta carpeta si la skill corre fuera del repo. Diseño de referencia:
`Designs_files/Design_iris_main_colors.md`.

## Uso independiente

Esta skill es un paso del flujo IRIS, pero no depende de él para funcionar. Para usarla
sola basta con esta carpeta más `_plantilla_html/` al lado, y ejecutar el generador con
`--sin-flujo`: el contexto del flujo se omite y el logo sale de `assets/logo.png`. Su
entregable propio (`reporte_ejecutivo.html`) y su gate no necesitan nada del repositorio.

Lo que aporta el repositorio completo —y que se pierde al extraerla— es el contexto del
flujo en el HTML (riel de progreso, decisiones previas, pasos omitidos) y el histórico de
`flujo_estado.json`. Nada de eso es necesario para producir el entregable.

Requiere Python con `pandas`, `numpy` y `beautifulsoup4`. Sin Python el pipeline puede
correr, pero el gate no: el reporte se entrega marcado **NO VERIFICADO** y ningún punto de
`validacion` se marca `true`.
