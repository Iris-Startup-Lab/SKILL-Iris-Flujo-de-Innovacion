---
name: landing-page
description: Diseña el experimento "Simple Landing Page" para validar una propuesta de valor: Testing Card con umbral calibrado por benchmark, estructura de la página, checklist de copy/CTA, plan de ejecución y compliance (age gate para categorías reguladas). Usar cuando el usuario quiera diseñar una landing page de validación temprana de producto o funcionalidad.
category: Prototipado
---

# Landing Page (Simple Landing Page)

Diseña el experimento "Simple Landing Page" para un responsable con experiencia construyendo landings de validación, conservando la rigurosidad de *Testing Business Ideas*.

## Rol y Contexto

Actúa como un *product experiment strategist* con experiencia avanzada en validación ágil, diseño de landing pages orientadas a conversión, growth hacking y análisis de comportamiento digital.

## Alcance

**SÍ hace:** diseñar la Testing Card, la estructura de la página, el checklist de copy/CTA y el plan de ejecución. Y, si el usuario lo pide, **construir la página como demo** (ver «Modo de entrega»).

**NO hace:** publicar ni lanzar la página —el dominio, el hosting y la pauta son del usuario—, ni inventar benchmarks propios.

## Modo de entrega (pregúntalo antes de empezar)

El paso 11 del flujo trae esta decisión en el nodo «Entrega de la landing page». Si trabajas la
skill suelta, pregúntala igual: cambia lo que produces, no solo cómo lo presentas.

- **«La landing page como demo, construida con el contexto del flujo»** — entregas además un
  **archivo HTML autocontenido**, listo para abrir en el navegador y publicar tal cual, con los
  textos ya escritos a partir de la persona, el problema y la propuesta de valor que traen los
  pasos anteriores. **No lo escribes a mano:** lo arma `scripts/generar_landing.py` desde un
  `landing.json` (ver «Construir la demo»). Es una demo para enseñar y medir, no un sitio de
  producción: dilo así.
- **«Solo los pasos para construirla en una herramienta externa»** — entregas el guion completo
  (titular, subtítulo, beneficios, llamada a la acción, estructura por bloques, qué medir y con
  qué umbral) para que el usuario lo arme donde ya trabaje: Webflow, Framer, WordPress,
  Unbounce, Carrd. **No generas código.**

En los dos casos la Testing Card, el checklist y el plan de ejecución van igual: lo que cambia es
si el entregable incluye la página construida.

## Construir la demo (solo en modo demo)

La landing se viste con la marca **del producto que se prueba**, no con la de IRIS. El diseño lo
pone la plantilla (`templates/landing_base.html`); tú decides el contenido en un `landing.json`.
Esquema, catálogo de bloques y de maquetas, y reglas: **`references/landing.md`**.

1. **Marca** — el paso 11 trae la decisión «Marca de la landing» (si trabajas la skill suelta,
   pregúntala igual): la marca real (pide nombre, logo y colores; si no los tiene, búscalos en el
   sitio oficial o la guía de marca y **confírmalos antes de usarlos**), una marca nueva que
   propones y el usuario aprueba, o una marca neutra de prueba.
2. **Estilo** — elige uno de `references/estilos.json` por la categoría del producto
   (`--listar-estilos`) y ajústalo con los colores de la marca.
3. **Imágenes** — la decisión «Imágenes de la landing» dice de dónde salen: las aporta el
   usuario, se generan con inteligencia artificial (escribes el prompt; las generas si tu
   herramienta puede, o las genera el usuario), fotos de bancos libres con licencia comercial y
   crédito, o las maquetas de la plantilla. Incluye siempre alguna maqueta como respaldo.
4. **Contenido** — 5 a 7 bloques escritos con lo que heredaste del flujo: la persona, el problema
   de mayor importancia, el journey, la idea elegida y su modelo. Un solo CTA.
5. **Genera** desde la raíz del repositorio:

   ```bash
   python sub-skills/4.Prototipado/landing-page/scripts/generar_landing.py \
       --data landing.json -o landing_demo.html
   ```

   Falla a propósito si el texto sale ilegible, si falta el aviso de privacidad o el aviso
   transparente de una puerta falsa, o si hay prueba social inventada. Corrige el JSON.
6. **Enséñala en el reporte del paso**: añade al item de la landing
   `"vista_previa": {"archivo": "landing_demo.html", "titulo": "Landing de validación"}`; el
   reporte muestra el botón «Ver la landing» y la abre en su ventana.

## Parámetros de Entrada

- **Hipótesis** `{{hipotesis}}` y **propuesta de valor principal** `{{propuesta}}`.
- **Segmento objetivo** `{{segmento}}`.
- **CTA esperada** `{{cta}}` (registro, clic, descarga, compra, reply).
- **Canales de tráfico** `{{canales}}` (orgánico, pago, social, email).
- **Tiempo de prueba y volumen objetivo** `{{volumen}}`.
- **Benchmark histórico de conversión** `{{benchmark}}` (si existe; si no, proponer rango por industria/canal marcado como estimación).
- **Presupuesto de pauta/ads** `{{presupuesto}}` (dimensionar volumen de tráfico realista según CPC/CPM).
- **¿Categoría regulada?** `{{regulada}}` (age gate/verificación de edad + disclaimers legales).

## Instrucciones

1. Confirma los parámetros **y el modo de entrega** (demo construida o solo el guion).
2. **Diseña la Testing Card** con: hipótesis, experimento (landing + CTA + canal), métricas clave (visitas, CTR, tiempo en página, conversión), métrica de éxito principal y umbral explícito calibrado con benchmark (ej. "≥ X% de conversión en N visitas únicas") y criterio de fracaso/iteración.
3. **Estructura la landing:** headline, subheadline, visual principal, beneficios (máx. 3), prueba social (opcional), CTA prominente, formulario/paso siguiente, age gate/disclaimers (si aplica).
4. **Verifica el checklist de copy y CTA** (headline < 5s y de beneficio, subheadline no repetitivo, beneficios escaneables, un solo CTA medible, mobile-first, cumplimiento legal).
5. **Plan de ejecución:** herramienta, duración, fuentes de tráfico, presupuesto + volumen esperado, analítica (GTM, Hotjar, GA4, Mixpanel), A/B testing.

## Formato de Salida

- **Testing Card** — con métrica de éxito principal y umbral calibrado + criterio de fracaso.
- **Estructura de la Landing Page** — por bloques.
- **Plan de ejecución** — herramienta, duración, tráfico, presupuesto, analítica.
- **Checklist de Copy y CTA** — marcado de verificación previo al lanzamiento.
- **La página construida** (`landing_demo.html`) — solo en el modo demo. Archivo autocontenido (las imágenes van incrustadas; solo las fuentes y, si se configuran, GA4/GTM se cargan de la red), generado con `scripts/generar_landing.py` desde `landing.json`. Los dos se declaran en los `outputs` del paso junto al reporte.

Cierra con el **contrato JSON** (ver la sección «Contrato JSON (salida)»).

## Reglas y Restricciones

1. Umbrales calibrados con benchmark propio o estimación marcada, nunca arbitrarios sin justificación.
2. Age gate y disclaimers si la categoría es regulada.
3. Un solo CTA principal, medible y conectado a analítica.
4. **Nada de prueba social inventada** en la landing: ni cifras de clientes, ni estrellas, ni
   testimonios, ni logos de clientes. Un producto en validación todavía no los tiene. Una cifra
   real de la empresa va en `evidencia` con su fuente.
5. **La puerta falsa se confiesa:** si el producto aún no existe, el clic lo dice
   (`aviso_transparente`) y explica qué pasa con los datos.
6. **Una foto de banco o generada nunca se presenta como un cliente real.**

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

El flujo diseñaba los experimentos pero no sabía leerlos: «conversión: 37 de 420» se comparaba
de cabeza contra el umbral y se decidía sin intervalo. Cuando el usuario vuelva con los datos:

```bash
# contra el umbral de la Testing Card
python sub-skills/4.Prototipado/landing-page/scripts/analizar_resultados.py \
    --k 37 --n 420 --umbral 0.06 --metrica "conversión" \
    --experimento "<nombre del experimento>" --seccion-reporte seccion.json

# contra un control medido en el mismo experimento (siempre que exista)
python sub-skills/4.Prototipado/landing-page/scripts/analizar_resultados.py \
    --k 37 --n 420 --control-k 12 --control-n 400 --metrica "conversión"
```

Devuelve la tasa con **intervalo de confianza de Wilson**, la prueba contra el umbral o contra
el control, el veredicto (`perseverar` / `pivotear` / `descartar`) y —cuando no alcanza para
concluir— **cuántos visitas únicas más harían falta**. Con `--datos` acepta varias variantes a la vez.

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
  **En el reporte van en capas:** a la vista, la etiqueta `significancia` (Significativo /
  No significativo / Aún no se puede saber) con su frase sin cifras, el veredicto y las
  `advertencias` completas; la `explicacion`, las cifras exactas y la tabla con p e
  intervalos, en la ventana «Cómo se calculó» (`estadistica` y `tabla.calculo`). No
  reacomodes a mano: `--seccion-reporte` ya entrega el item repartido así. Ver
  `_plantilla_html/README.md` § «La estadística en tres capas».

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

- `references/landing.md` — esquema de `landing.json`, bloques, maquetas, marca, imágenes, medición e integridad.
- `references/estilos.json` — los estilos visuales (`--listar-estilos`).
- `templates/landing_base.html` — plantilla de la landing (no se edita por proyecto).
- `scripts/generar_landing.py` — arma la landing, comprueba contraste e integridad, incrusta imágenes.
- `scripts/analizar_resultados.py` — lectura del resultado del experimento (ver «Grupo control»).
- Contrato JSON: ver «Contrato JSON (salida)» arriba (autocontenido; `../../CONTRATO_JSON.md` es la versión canónica si existe).
