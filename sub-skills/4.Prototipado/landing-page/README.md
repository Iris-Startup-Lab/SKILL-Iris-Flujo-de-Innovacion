# landing-page

> Fase: 4.Prototipado

Diseña el experimento "Simple Landing Page" para validar una propuesta de valor: Testing Card con umbral calibrado por benchmark, estructura de la página, checklist de copy/CTA, plan de ejecución y compliance (age gate para categorías reguladas). Usar cuando el usuario quiera diseñar una landing page de validación temprana de producto o funcionalidad.

## Salida principal — HTML interactivo

Esta skill entrega su resultado como un **reporte HTML autocontenido** con el diseño corporativo IRIS (logo oficial + paleta morado/dorado, tipografías Sora/Inter).

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

`scripts/analizar_resultados.py` lee el experimento cuando el usuario vuelve con los datos:
tasa con **intervalo de confianza de Wilson**, prueba contra el umbral de la Testing Card o
contra el grupo control, veredicto (`perseverar` / `pivotear` / `descartar`) y —si no alcanza
para concluir— cuántos intentos más harían falta. Con varias variantes corrige por comparaciones
múltiples (Bonferroni).

```bash
# después del experimento
python sub-skills/4.Prototipado/landing-page/scripts/analizar_resultados.py \
    --k 37 --n 420 --umbral 0.06 --seccion-reporte seccion.json
# antes: muestra por brazo para detectar 3 puntos sobre una base del 3%
python sub-skills/4.Prototipado/landing-page/scripts/analizar_resultados.py --n-requerido 0.03 0.03
```

Solo stdlib, así que funciona con la skill suelta. El mismo archivo está copiado en las seis
skills que diseñan experimentos (las cinco de Validación y `landing-page`), según la regla de
autonomía de `AGENTS.md` §4: ninguna skill importa scripts de otra.

## Uso independiente

Esta skill es un paso del flujo IRIS, pero no depende de él para funcionar. Para usarla
sola basta con esta carpeta más `_plantilla_html/` al lado, y ejecutar el generador con
`--sin-flujo`: el contexto del flujo se omite y el logo sale de `assets/logo.png`.

Lo que aporta el repositorio completo —y que se pierde al extraerla— es el contexto del
flujo en el HTML (riel de progreso, decisiones previas, pasos omitidos) y el histórico de
`flujo_estado.json`. Nada de eso es necesario para producir el entregable.
