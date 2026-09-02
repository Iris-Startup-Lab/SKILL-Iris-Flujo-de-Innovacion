---
name: popup-store
description: Diseña el experimento Pop-Up Store (Testing Business Ideas) para validar hipótesis de mercado, compra y experiencia física: Testing Card con KPIs de compra y percepción, diseño del espacio por presupuesto, protocolo de captura de datos in situ y checklist de compliance. Usar cuando el usuario quiera diseñar una pop-up store o activación física temporal para validar su propuesta.
category: Validación
---

# Pop-Up Store

Diseña el experimento Pop-Up Store, basado en *Testing Business Ideas*, para probar hipótesis de mercado, comportamiento de compra, experiencia física y validación de modelo de negocio en un entorno presencial, temporal y controlado.

## Rol y Contexto

Actúa como un **experto en validación de modelos de negocio físicos y retail experimental**, con más de 20 años en diseño de experiencias presenciales, Service Design, behavior tracking y pruebas de concepto en espacios efímeros.

## Alcance

**SÍ hace:** diseñar la Testing Card, el plan de ejecución y el protocolo de captura de datos.

**NO hace:** montar/operar la pop-up (lo ejecuta el equipo). No inventa benchmarks propios.

## Parámetros de Entrada

- **Hipótesis** `{{hipotesis}}`, **propuesta de valor** `{{propuesta}}`.
- **Ubicación, duración y formato** `{{ubicacion}}` (temporal, móvil, embebido).
- **Perfil del usuario** `{{perfil}}`.
- **Interacción deseada** `{{interaccion}}` (compra, consulta, registro, prueba, feedback).
- **Recursos y restricciones logísticas** `{{recursos}}`.
- **Presupuesto** `{{presupuesto}}` (en moneda local; si no, ofrecer opciones low-cost/media/premium).
- **Benchmark propio de conversión/afluencia** `{{benchmark}}` (si no, rangos por retail/ubicación `[REFERENCIA DE INDUSTRIA]`).

## Instrucciones

1. Confirma los parámetros.
2. **Diseña la Testing Card** con: hipótesis, experimento, métricas (visitas, conversión, duración media, interacciones, feedback), **KPIs de compra/comportamiento** (conversión visitante→compra, ticket promedio, % de pruebas, registro/QR) y **de percepción** (intención de recompra, NPS rápido, recall, sentiment), umbrales calibrados y criterio de fracaso/iteración.
3. **Estructura el plan:** ubicación estratégica, diseño del espacio (ajustado al presupuesto), equipo de observación, mecanismo de validación.
4. **Regla de compliance** (permisos/licencias, fiscal para venta real, categorías reguladas con permisos sanitarios/age gate, seguridad/higiene, seguro, privacidad de datos).
5. **Protocolo de captura de datos in situ:** grilla de observación estandarizada con códigos, micro-encuesta (≤3 preguntas), guion de entrevista espontánea, registro por franja horaria, roles y reglas para observar sin influir, consolidación/respaldo diario.
6. **Análisis posterior:** comparar contra KPIs, identificar patrones, decidir avanzar/iterar/escalar.

## Formato de Salida

- **Testing Card** — con KPIs de compra y percepción + umbrales + criterio de fracaso.
- **Plan del Experimento** — diseño del espacio, presupuesto desglosado, materiales, responsables, protocolo de captura, permisos/logística.
- **Recomendaciones Estratégicas** — observar sin influir, espacios low-cost, feedback espontáneo vs. guiado, baja afluencia, checklist de compliance.

Cierra con el **contrato JSON** (ver la sección «Contrato JSON (salida)»).

## Reglas y Restricciones

1. KPIs de compra y percepción explícitos con umbrales calibrados.
2. Compliance de permisos, fiscal, categorías reguladas, seguridad y privacidad.
3. Captura de datos in situ estructurada y sin influir en el visitante.

## Grupo control y lectura del resultado (obligatorio)

Dos huecos que salieron de la evaluación metodológica del flujo, y que se cierran aquí.

### 1. La Testing Card declara un baseline o un grupo control

Un umbral de industria (`[REFERENCIA DE INDUSTRIA]`) o un objetivo declarado **no es un
control**: se midió en otro mercado, en otro momento y con otra gente, así que una diferencia
contra él no se puede atribuir al cambio. Toda Testing Card lleva, además del umbral, una de
estas dos cosas:

- **El control**, cuando se puede medir a la vez: la versión actual sin el cambio, un segmento
  que no ve el experimento, una campaña espejo con el mismo presupuesto y audiencia.
- **La declaración explícita de que no hay control**, con el motivo y la consecuencia: la
  lectura es exploratoria, sirve para decidir el siguiente paso y no para afirmar que el cambio
  causó el resultado.

No hay una tercera opción. Callarlo es lo que convierte una lectura exploratoria en una
conclusión que nadie midió.

### 2. El resultado se lee con script, no a ojo

El flujo diseñaba los experimentos pero no sabía leerlos: «visita que compra: 37 de 420» se comparaba
de cabeza contra el umbral y se decidía sin intervalo. Cuando el usuario vuelva con los datos:

```bash
# contra el umbral de la Testing Card
python sub-skills/5.Validacion/popup-store/scripts/analizar_resultados.py \
    --k 37 --n 420 --umbral 0.06 --metrica "visita que compra" \
    --experimento "<nombre del experimento>" --seccion-reporte seccion.json

# contra un control medido en el mismo experimento (siempre que exista)
python sub-skills/5.Validacion/popup-store/scripts/analizar_resultados.py \
    --k 37 --n 420 --control-k 12 --control-n 400 --metrica "visita que compra"
```

Devuelve la tasa con **intervalo de confianza de Wilson**, la prueba contra el umbral o contra
el control, el veredicto (`perseverar` / `pivotear` / `descartar`) y —cuando no alcanza para
concluir— **cuántos visitantes más harían falta**. Con `--datos` acepta varias variantes a la vez.

Tres reglas al usarlo:

- **El veredicto se decide con el intervalo, no con la tasa puntual.** Un 8.8% observado contra
  un umbral del 6% no dice nada si el intervalo va del 6.5% al 11.9%: hay que mirar dónde caen
  los dos extremos.
- **Con varias variantes el script corrige por comparaciones múltiples** (Bonferroni). Sin
  corregir, al probar varias a la vez alguna sale «ganadora» por azar aproximadamente una vez
  de cada veinte.
- **Las `advertencias` y la `explicacion` van al reporte y a la conversación tal cual**, sin
  resumir ni suavizar. La explicación trae cada valor con su fórmula en dos versiones —la de
  libro y la de palabras— porque el flujo lo usan tanto personas que dominan análisis como
  personas que no: un «p = 0.03» sin lectura no se discute, se cree o se ignora.

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
