# dimensionador-estrategico

> Fase: 3.Ideación

Dimensiona el potencial de negocio de ideas de innovación con rigor tipo McKinsey/Bain/VC — TAM/SAM/SOM, panorama competitivo, CLV/CAC y cross-selling por buyer persona, score de atractivo /25, riesgos y veredicto (PROTOTIPAR / VALIDAR MÁS / DESCARTAR). Usa esta skill siempre que el usuario pida "dimensionar" ideas, priorizar ideas de negocio o de innovación, evaluar el potencial de una idea, calcular TAM/SAM/SOM, o mencione el "Dimensionador Estratégico" por nombre — incluso si no detalla el formato exacto. También aplica cuando el usuario comparte una lista de ideas filtradas por un equipo de innovación y pide ayuda para decidir cuáles llevar a prototipado.

## Salida principal — su propio dashboard HTML (+ PPTX)

El entregable principal de esta skill es el **dashboard HTML y los PPTX que generan sus
scripts**, no el reporte de la plantilla compartida. Lo definen «Generación de Entregables
Visuales» y «Como paso del flujo IRIS» en su `AGENTE.md`.

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

## Scripts de cálculo

Los números del análisis **los calcula un script**, no el modelo. Cada uno acepta
`--plantilla` (imprime el esqueleto de entrada), sale con código 2 y un mensaje concreto si la
entrada no permite calcular, y con `--seccion-reporte` escribe una sección de `REPORT_DATA`
lista para pegar en el `reporte.json` —con sus tablas y su gráfica ya armadas—.

| Script | Módulo | Qué calcula |
| --- | --- | --- |
| `scripts/calcular_tam_sam_som.py` | 1 | TAM/SAM/SOM con reducciones top-down, proyección 1/3/5, CAGR, penetración y **contraste contra el SAM bottom-up** |
| `scripts/calcular_modelo.py` | 3–8 | CLV, cross-selling, CAC por canal, CLV:CAC con su calificación, payback, ROI, ROAS, ARPU, clientes por cohortes, MRR/ARR 1–5, punto de equilibrio y EBITDA aproximado |
| `scripts/calcular_score.py` | 9 | Score /25, umbrales de veredicto, orden por score y la matriz criterio → puntaje → **justificación obligatoria** |

```bash
python sub-skills/3.Ideacion/dimensionador-estrategico/scripts/calcular_score.py --plantilla > ideas.json
python sub-skills/3.Ideacion/dimensionador-estrategico/scripts/calcular_score.py \
    --datos ideas.json -o score.json --seccion-reporte seccion_score.json
```

Los tres emiten `explicacion` (cada valor con su fórmula de libro, su fórmula en palabras y su
lectura) y `advertencias` con las contradicciones que detectan entre supuestos: una vida del
cliente que no cuadra con el churn, un payback mayor que la vida del cliente, un SAM bottom-up
que no se parece al top-down. Van al reporte tal cual, sin suavizar.

`scripts/xlsx_generator.py` **dibuja** el modelo financiero; no calcula nada. Aliméntalo con la
salida de `calcular_modelo.py`.

## Uso independiente

Esta skill es un paso del flujo IRIS, pero no depende de él para funcionar. Para usarla
sola basta con esta carpeta más `_plantilla_html/` al lado, y ejecutar el generador con
`--sin-flujo`: el contexto del flujo se omite y el logo sale de `assets/logo.png`.

Lo que aporta el repositorio completo —y que se pierde al extraerla— es el contexto del
flujo en el HTML (riel de progreso, decisiones previas, pasos omitidos) y el histórico de
`flujo_estado.json`. Nada de eso es necesario para producir el entregable.
