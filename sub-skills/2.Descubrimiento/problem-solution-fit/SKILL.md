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

## Parámetros de Entrada

- **Respuestas de entrevistas/encuestas** (texto o tabla estructurada).
- **Número de entrevistas / tamaño de muestra** `{{n_muestra}}` para ponderar la columna de Frecuencia (Alta/Media/Baja o conteo). Si no se conoce, sugiere un tamaño según contexto, marcado `*`.

## Instrucciones

1. Confirma `{{n_muestra}}` y la disponibilidad de datos reales.
2. Analiza las respuestas para:
   - **Identificar problemas clave** (más mencionados, contexto e impacto).
   - **Evaluar importancia** (1–5 según impacto en la actividad del usuario).
   - **Analizar satisfacción con la solución actual** (1–5).
   - **Medir costos:** tiempo (horas/semana) y dinero (USD/mes), **solo a partir de citas explícitas**.
   - **Validar la solución propuesta** (Sí/No/Parcialmente) y sugerir ajustes.
   - **Extraer patrones y tendencias** (similitudes/divergencias).
   - **JTBD:** ¿qué "trabajo" intenta resolver el usuario y cómo mejorarlo?
   - **Blue Ocean:** oportunidades de diferenciación y propuesta de valor única.
3. Estructura el resultado y **exporta a CSV:**
   ```bash
   python scripts/exportar_csv.py analisis.json -o problem_solution_fit.csv
   ```
   (Escribe primero el `analisis.json` con la lista de problemas y sus campos; ver `scripts/exportar_csv.py` para el esquema de columnas.)

## Formato de Salida

- **Análisis en markdown** (problemas priorizados, evaluación de solución, JTBD, Blue Ocean, recomendaciones).
- **CSV** (`problem_solution_fit.csv`) con columnas: problema, contexto, impacto (1-5), satisfacción solución actual (1-5), costo tiempo (hrs/sem), costo dinero (USD/mes), solución cubre (Sí/No/Parcial), ajustes, patrones, JTBD, oportunidad Blue Ocean.

Cierra con el **contrato JSON** (ver la sección «Contrato JSON (salida)»), declarando el CSV en `archivos_generados`.

## Reglas y Restricciones

1. **Integridad de datos (obligatoria):** costo en tiempo/dinero solo de citas explícitas; si se infiere, marcar `[ESTIMACIÓN]`; si no hay mención, `N/D`. Prohibido inventar cifras.
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
3. **Los pasos con estado `omitido` no aportan datos.** Su campo `impacto` dice qué falta:
   sustitúyelo por un supuesto marcado `*` y decláralo en `advertencias`.
4. **Declara qué usaste** en `decision.contexto_usado` del contrato JSON.
5. **No escribas el bloque `flujo` a mano** en `reporte.json`: lo inyecta el generador con
   `--estado` y `--paso`.

## Salida HTML (interactiva)

La salida principal es un **reporte HTML interactivo** con el diseño corporativo IRIS
(logo + paleta morado/dorado). Para generarlo:

1. Estructura el resultado en `reporte.json` según el esquema `REPORT_DATA`
   (ver `_plantilla_html/README.md`).
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

- `scripts/exportar_csv.py` — exporta el análisis a CSV estructurado.
- Contrato JSON: ver «Contrato JSON (salida)» arriba (autocontenido; `../../CONTRATO_JSON.md` es la versión canónica si existe).