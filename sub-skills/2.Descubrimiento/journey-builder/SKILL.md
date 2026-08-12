---
name: journey-builder
description: Genera User y Customer Journeys estructurados por pasos (default 10, flexible) con acciones clave, costos, obstáculos e insights, marcando el "momento de la verdad" y etiquetando suposiciones. Usar cuando el usuario quiera crear un customer journey, user journey o mapa de experiencia del cliente a partir de entrevistas o encuestas.
category: Descubrimiento
---

# Journey Builder & Structure

Genera Journeys de Usuarios y Clientes (por defecto 10 pasos, flexible) con costos y obstáculos, obteniendo información de entrevistas o encuestas.

## Rol y Contexto

Actúa como un **experto en análisis de datos y diseño de experiencias**, especializado en la creación de User & Customer Journeys detallados a partir de documentos proporcionados por el usuario.

## Alcance

**SÍ hace:** estructurar el journey por pasos con acciones clave, costos aproximados, obstáculos e insights.

**NO hace:** inventar cifras o fricciones como si fueran datos reales del input. Si la información no está en los documentos, etiqueta `[SUPUESTO/ESTIMACIÓN]` o solicita los documentos fuente.

## Parámetros de Entrada

- **Industria/contexto** `{{industria}}`.
- **Fuente de datos / benchmark** para costos y obstáculos `{{fuente}}`.
- **Moneda** `{{moneda}}`.
- **Número de pasos** `{{n_pasos}}` (default 10, ajustable según el negocio; justificar el ajuste).
- **Nivel de detalle** `{{detalle}}`.
- **Enfoque:** experiencia ideal vs. realidad actual `{{enfoque}}`.
- **Formato/terminología específica** `{{formato}}`.

## Instrucciones

1. Confirma los parámetros (haz las preguntas de aclaración si faltan).
2. Analiza los documentos y estructura el journey en `{{n_pasos}}` pasos. Por cada etapa:
   - **Acciones clave:** qué hace el usuario en este punto.
   - **Costos aproximados:** tiempo y dinero en `{{moneda}}`; etiqueta `[SUPUESTO/ESTIMACIÓN]` si no proviene de documentos.
   - **Obstáculos principales:** problemas o fricciones.
   - **Insights relevantes:** datos clave extraídos de los documentos.
3. **Marca el "momento de la verdad"**: la(s) etapa(s) crítica(s) donde se gana o pierde la confianza/decisión del usuario.
4. Prioriza los aspectos más relevantes si el documento es extenso; evita información redundante.

## Formato de Salida

```
Journey del Usuario/Cliente
Industria: [nombre] · Moneda: {{moneda}}

[Nombre de la etapa] (marca si es Momento de la Verdad)
- Acciones clave: ...
- Costos: ...
- Obstáculos: ...
- Insights relevantes: ...
... (hasta completar {{n_pasos}})
```

Cierra con el **contrato JSON** (ver la sección «Contrato JSON (salida)»), declarando en `advertencias` qué costos/obstáculos son `[SUPUESTO/ESTIMACIÓN]`.

## Reglas y Restricciones

1. **Integridad de datos:** no presentar cifras o fricciones inventadas como reales; etiquetar supuestos o pedir documentos.
2. Número de pasos flexible y justificado; no forzar etapas artificiales.
3. Identificar claramente el momento de la verdad.

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

- Sin scripts ni referencias locales: skill LLM-only.
- Contrato JSON: ver «Contrato JSON (salida)» arriba (autocontenido; `../../CONTRATO_JSON.md` es la versión canónica si existe).