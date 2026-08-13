# problem-solution-fit

> Fase: 2.Descubrimiento

Genera un análisis estructurado de Problem-Solution Fit a partir de entrevistas o encuestas: identifica problemas clave, evalúa importancia, satisfacción con la solución actual y costos, valida la solución propuesta y extrae insights JTBD y Blue Ocean, exportando a CSV. Usar cuando el usuario tenga entrevistas/encuestas y quiera evaluar si su solución encaja con los problemas del cliente.

## Salida principal — HTML interactivo

Esta skill entrega su resultado como un **reporte HTML autocontenido** con el diseño corporativo IRIS (logo oficial + paleta morado/dorado, tipografías Sora/Inter).

### Generar el HTML

1. Estructura el resultado en `reporte.json` (esquema `REPORT_DATA` de
   `_plantilla_html/README.md`), con un item por análisis y su bloque `psf`
   (`references/analisis-psf.md`).
2. Ejecuta **desde la raíz del repositorio**:

   ```bash
   # como paso del flujo
   python _plantilla_html/scripts/generar_html.py --data reporte.json \
       --estado flujo_estado.json --paso html_5 -o html_5.html

   # skill suelta
   python _plantilla_html/scripts/generar_html.py --data reporte.json --sin-flujo -o reporte.html
   ```

3. Exporta el CSV **desde el mismo `reporte.json`** (el script lee los bloques `psf`):

   ```bash
   python scripts/exportar_csv.py reporte.json -o problem_solution_fit.csv
   ```

4. Entrega el HTML y el CSV (`problem_solution_fit.csv`).

> Esta skill es la dueña de la evaluación de los pains: la ficha de `persona-profile`
> entrega los dolores y aquí se les pone importancia, satisfacción, costo y veredicto de
> encaje. La matriz Importancia × Satisfacción la dibuja la plantilla desde
> `psf.problemas`.

El logo se embebe en base64: el oficial del repositorio, o la copia `assets/logo.png` de
esta carpeta si la skill corre fuera del repo. Diseño de referencia:
`Designs_files/Design_iris_main_colors.md`.

## Uso independiente

Esta skill es un paso del flujo IRIS, pero no depende de él para funcionar. Para usarla
sola basta con esta carpeta más `_plantilla_html/` al lado, y ejecutar el generador con
`--sin-flujo`: el contexto del flujo se omite y el logo sale de `assets/logo.png`.
El análisis se puede hacer sobre los pains de una protopersona previa o directamente sobre
las entrevistas, sin que exista una ficha de `persona-profile`.

Lo que aporta el repositorio completo —y que se pierde al extraerla— es el contexto del
flujo en el HTML (riel de progreso, decisiones previas, pasos omitidos) y el histórico de
`flujo_estado.json`. Nada de eso es necesario para producir el entregable.
