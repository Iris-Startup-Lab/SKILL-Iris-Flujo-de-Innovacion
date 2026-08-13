# persona-profile

> Fase: 2.Descubrimiento

Desarrolla protopersonas con atributos detallados integrando Job To Be Done (JTBD) con Momentos Vitales. Distingue entre protopersona hipotética (supuestos) y persona validada con datos reales. Usar cuando el usuario quiera crear perfiles de cliente/persona, protopersonas o buyer personas para estrategias y nuevos productos.

## Salida principal — HTML interactivo

Esta skill entrega su resultado como un **reporte HTML autocontenido** con el diseño corporativo IRIS (logo oficial + paleta morado/dorado, tipografías Sora/Inter).

### Generar el HTML

1. Estructura el resultado en `reporte.json` (esquema `REPORT_DATA` de
   `_plantilla_html/README.md`), con un item por perfil y su bloque `persona`
   (`references/ficha-persona.md`).
2. Ejecuta **desde la raíz del repositorio**:

   ```bash
   # como paso del flujo
   python _plantilla_html/scripts/generar_html.py --data reporte.json \
       --estado flujo_estado.json --paso html_4 -o html_4.html

   # skill suelta
   python _plantilla_html/scripts/generar_html.py --data reporte.json --sin-flujo -o reporte.html
   ```

3. Entrega el HTML.

> Las secciones 11–13 de la ficha («¿Cómo lo soluciona?», «Costo de la solución actual» y
> la matriz Importancia × Satisfacción) las produce `problem-solution-fit` en el paso
> siguiente. Sin ese análisis se omiten: el HTML imprime la tabla de pains sin esas
> columnas y una nota que remite a Problem-Solution Fit.

El logo se embebe en base64: el oficial del repositorio, o la copia `assets/logo.png` de
esta carpeta si la skill corre fuera del repo. Diseño de referencia:
`Designs_files/Design_iris_main_colors.md`.

## Uso independiente

Esta skill es un paso del flujo IRIS, pero no depende de él para funcionar. Para usarla
sola basta con esta carpeta más `_plantilla_html/` al lado, y ejecutar el generador con
`--sin-flujo`: el contexto del flujo se omite y el logo sale de `assets/logo.png`.

Lo que aporta el repositorio completo —y que se pierde al extraerla— es el contexto del
flujo en el HTML (riel de progreso, decisiones previas, pasos omitidos), el histórico de
`flujo_estado.json` y la evaluación de los pains que produce `problem-solution-fit`. Nada
de eso es necesario para producir el entregable.
