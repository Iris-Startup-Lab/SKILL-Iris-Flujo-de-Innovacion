---
name: problem-solution-fit
description: Genera un análisis estructurado de Problem-Solution Fit a partir de entrevistas o encuestas: identifica problemas clave, evalúa importancia, satisfacción con la solución actual y costos, valida la solución propuesta y extrae insights JTBD y Blue Ocean, exportando a CSV. Usar cuando el usuario tenga entrevistas/encuestas y quiera evaluar si su solución encaja con los problemas del cliente.
category: Descubrimiento
---

# Problem-Solution Fit

Genera un análisis estructurado de Problem-Solution Fit a partir de entrevistas o encuestas, identificando problemas clave, evaluando la solución y extrayendo insights accionables (JTBD + Blue Ocean Strategy).

## Rol y Contexto

Actúa como un **experto en análisis de Problem-Solution Fit**, con conocimiento en Lean Startup, Design Thinking, Jobs To Be Done (JTBD) y Blue Ocean Strategy. Marco teórico: *Value Proposition Design*, *Lean Customer Development*.

## Alcance

**SÍ hace:** analizar respuestas reales de entrevistas/encuestas para identificar problemas, evaluar importancia y satisfacción, medir costos, validar la solución y exportar a CSV.

**NO hace:** inventar cifras. Los costos deben derivarse de citas explícitas del input. Sin datos reales, no ejecuta análisis como si fuera real.

**Este paso es el dueño de la evaluación de los problemas.** La ficha de persona (`html_4`,
`persona-profile`) entrega quién es el usuario y qué le duele; aquí se responde cuánto le
duele, cómo lo resuelve hoy, cuánto le cuesta y si la solución encaja. Las secciones 11–13
del template *Persona Profile* —«¿Cómo lo soluciona?», «Costo de la solución actual» y la
matriz «Importancia × Satisfacción»— **nacen en esta skill**, no en la ficha de persona.

## Vocabulario en el texto visible (obligatorio)

Este flujo lo usan personas expertas y no expertas. En **todo el texto que se ve en el
HTML y el CSV** (títulos, subtítulos, KPIs, labels, resúmenes y advertencias) usa palabras
claras:

| No escribas (jerga) | Escribe |
| --- | --- |
| `pains` | «problemas» o «dolores» |
| `JTBD` | «el trabajo que quiere hacer (Job To Be Done)» |
| `protopersona` | «ficha de persona» |
| `PSF` | «Problem-Solution Fit» (o «el encaje problema-solución») |
| `N/D` | «[no disponible]» |
| `html_N` | «paso N» |

Los **nombres de campo del JSON** (`psf`, `problemas`, `persona`, `importancia`,
`satisfaccion`) **no cambian**: son el contrato que leen la plantilla y el validador. Solo
cambia el texto visible, no las claves.

## Parámetros de Entrada

- **Respuestas de entrevistas/encuestas** (texto o tabla estructurada).
- **Número de entrevistas / tamaño de muestra** `{{n_muestra}}` para ponderar la columna de Frecuencia (Alta/Media/Baja o conteo). Si no se conoce, sugiere un tamaño según contexto, marcado `*`.
- **La ficha de persona y sus problemas** (del paso 4, si el flujo la produjo) y la **solución propuesta** que se pone a prueba.

## Instrucciones

1. Confirma `{{n_muestra}}` y la disponibilidad de datos reales.
2. **Lee `references/analisis-psf.md`.** Define la estructura obligatoria de salida y el
   esquema del bloque `psf` en `reporte.json`. Es vinculante: no reordenes ni renombres
   secciones.
3. Toma los problemas de la ficha de persona del paso 4 como punto de partida (si existe) y
   analiza las respuestas para:
   - **Identificar problemas clave** (más mencionados, contexto e impacto).
   - **Evaluar importancia** (1–5 según impacto en la actividad del usuario).
   - **Analizar satisfacción con la solución actual** (1–5).
   - **Medir costos:** tiempo (horas/semana) y dinero (USD/mes), **solo a partir de citas explícitas**.
   - **Validar la solución propuesta** (Sí/No/Parcialmente) y sugerir ajustes.
   - **Extraer patrones y tendencias** (similitudes/divergencias).
   - **El trabajo que quiere hacer (Job To Be Done):** ¿qué "trabajo" intenta resolver el
     usuario y cómo mejorarlo?
   - **Blue Ocean:** oportunidades de diferenciación y propuesta de valor única.
4. **Numera los problemas.** El problema 2 de la tabla es el punto 2 de la matriz: van como
   un solo array de objetos (`psf.problemas`), no como listas paralelas.
5. **Puntúa solo lo que la evidencia sostiene.** Si `importancia` o `satisfaccion` no se
   pudieron derivar, déjalas fuera: el problema sale en la tabla pero no en la matriz, y se
   declara en `advertencias`. No escribas un bloque `chart`: la matriz la dibuja la
   plantilla desde los problemas.
6. Estructura el resultado y **exporta a CSV desde el mismo `reporte.json`** —los datos se
   escriben una sola vez, el script aplica el mapeo:

   ```bash
   python sub-skills/2.Descubrimiento/problem-solution-fit/scripts/exportar_csv.py \
       reporte.json -o problem_solution_fit.csv
   ```

   (Una fila por problema, con la `persona` de cada bloque `psf`; el mapeo bloque `psf` →
   columnas está en `references/analisis-psf.md`. El script sigue aceptando un
   `analisis.json` con filas ya nombradas, por compatibilidad.)

## Formato de Salida

- **Reporte HTML** con el bloque `psf`: problemas priorizados, matriz Importancia ×
  Satisfacción, el trabajo que quiere hacer (Job To Be Done), patrones y Blue Ocean
  (ver «Salida HTML» abajo).
- **CSV** (`problem_solution_fit.csv`) con columnas: problema, contexto, impacto (1-5), satisfacción solución actual (1-5), costo tiempo (hrs/sem), costo dinero (USD/mes), solución cubre (Sí/No/Parcial), ajustes, patrones, el trabajo que quiere hacer (Job To Be Done), oportunidad Blue Ocean.

Lectura de la matriz de cuadrantes:

- **Eje X — Satisfacción de soluciones actuales** (0–5): qué tan resuelto está hoy.
- **Eje Y — Importancia del problema** (0–5): cuánto le pesa al usuario.
- **Arriba-izquierda = OPORTUNIDAD** (le importa y no está resuelto) · **arriba-derecha =
  COMPETENCIA** (le importa y ya hay quien lo resuelve).

Cierra con el **contrato JSON** (ver la sección «Contrato JSON (salida)»), declarando el HTML y el CSV en `archivos_generados`.

## Reglas y Restricciones

1. **Integridad de datos (obligatoria):** costo en tiempo/dinero solo de citas explícitas; si se infiere, marcar `[ESTIMACIÓN]`; si no hay mención, `[no disponible]`. Prohibido inventar cifras.
2. Si no se proporcionan datos reales: solicitar los datos, o etiquetar toda la salida como **"DATOS SIMULADOS"** si el usuario pide un ejemplo.
3. Priorizar problemas más recurrentes y de mayor impacto; señalar inconsistencias entre impacto y costos.

## Contexto del flujo (entrada)

Esta skill puede ejecutarse suelta o como paso del **flujo de innovación IRIS**. Si la
invoca la macro-skill, recibes un bloque `flujo` con el histórico del proyecto (también
disponible en `flujo_estado.json`, o con
`python scripts/estado_flujo.py mostrar --paso <html_N>` desde la raíz del repositorio).

Cuando ese contexto existe:

1. **No vuelvas a preguntar lo ya decidido.** Las decisiones registradas y los datos del
   proyecto (objetivo, audiencia) ya están ahí.
2. **Parte de los resúmenes previos** en lugar de reconstruir el contexto desde cero.
3. **Lee los datos del predecesor, no solo su resumen.** Cada paso cerrado deja en
   `flujo.ruta[]` un campo `datos` (la ruta de su `reporte.json`) y la lista `archivos`.
   Abre ese `reporte.json` y toma de ahí los bloques que necesites —`secciones[].items[]`
   y los especializados como `persona` o `psf`— en vez de reescribirlos a partir del
   resumen: **el resumen es el índice, los datos están en el archivo.** Si un paso no
   registró `datos`, su HTML (`archivo`) lleva lo mismo embebido en `window.REPORT_DATA`.
4. **Los pasos con estado `omitido` no aportan datos.** Su campo `impacto` dice qué falta:
   sustitúyelo por un supuesto marcado `*` y decláralo en `advertencias`.
5. **Declara qué usaste** en `decision.contexto_usado` del contrato JSON.
6. **No escribas el bloque `flujo` a mano** en `reporte.json`: lo inyecta el generador con
   `--estado` y `--paso`.

## Salida HTML (interactiva)

La salida principal es un **reporte HTML interactivo** con el diseño corporativo IRIS
(logo + paleta morado/dorado). Para generarlo:

1. Estructura el resultado en `reporte.json` según el esquema `REPORT_DATA`
   (ver `_plantilla_html/README.md`), con **un item por análisis** que lleve el bloque
   `psf` descrito en `references/analisis-psf.md`. El frente de la tarjeta (`titulo`,
   `subtitulo`, `tags`, `veredicto`) sigue el estándar de todos los reportes IRIS, para
   que buscador, filtros y orden funcionen igual que en el resto del flujo.
2. Ejecuta **desde la raíz del repositorio** — la carpeta que contiene `pasos.json` y
   `sub-skills/`:

   ```bash
   # como paso del flujo: el contexto del flujo se inyecta solo
   python _plantilla_html/scripts/generar_html.py --data reporte.json \
       --estado flujo_estado.json --paso html_N -o html_N.html

   # skill suelta, fuera de un proyecto del flujo
   python _plantilla_html/scripts/generar_html.py --data reporte.json \
       --sin-flujo -o reporte.html
   ```

3. El generador **valida el esquema y falla si falta algo**. Si reporta errores, corrige
   `reporte.json`; no uses `--no-strict` para saltártelos.
4. Entrega el HTML (autocontenido: el logo oficial va embebido en base64).

En el contrato JSON, `output.formato` es `html` y el archivo se declara en
`archivos_generados`.

## Contrato JSON (salida)

Toda skill cierra con un JSON de salida con esta estructura (autocontenida; no requiere archivos externos):

```json
{
  "skill": "<nombre-skill>",
  "timestamp": "<ISO 8601>",
  "parametros": { "<var>": "<valor>" },
  "output": {
    "formato": "<markdown|csv|json|html>",
    "contenido": "<resultado estructurado>",
    "archivos_generados": ["<ruta>"]
  },
  "decision": {
    "veredicto": "<perseverar|pivotear|descartar>",
    "siguiente_paso": "<skill-siguiente | null>",
    "razon": "<por qué>",
    "contexto_usado": ["<html_N de los pasos cuyo output usaste>"]
  },
  "advertencias": ["<limitaciones>"]
}
```

- `veredicto`: `perseverar` / `pivotear` / `descartar` (skills de diseño: `perseverar` = experimento listo para ejecutarse).
- `siguiente_paso`: nombre de la skill siguiente, o `null` en un punto de decisión.
- `contexto_usado`: pasos del flujo (`html_N`) cuyos resultados alimentaron este
  output; lista vacía si la skill corrió suelta.
- Integridad: no inventar cifras (estimadas con `*` o `[no disponible]`); si un script puede calcularlo, el script lo calcula.

> Si tienes acceso a `../../CONTRATO_JSON.md`, ese archivo es la versión canónica del contrato; si no, usa la estructura descrita aquí (son equivalentes).

## Referencias

- `references/analisis-psf.md` — **estructura vinculante** del análisis, esquema del bloque
  `psf`, lectura de la matriz de cuadrantes y mapeo hacia la ficha de persona y hacia el CSV.
- `scripts/exportar_csv.py` — exporta el análisis a CSV estructurado.
- `../persona-profile/references/ficha-persona.md` — la ficha que este análisis completa
  (secciones 11–13). **Opcional:** el mapeo hacia esa ficha está resumido en
  `references/analisis-psf.md`, así que esta skill funciona sin ese archivo.
- Contrato JSON: ver «Contrato JSON (salida)» arriba (autocontenido; `../../CONTRATO_JSON.md` es la versión canónica si existe).
