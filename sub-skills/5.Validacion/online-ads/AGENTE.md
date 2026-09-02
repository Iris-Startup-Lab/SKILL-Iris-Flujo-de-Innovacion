---
name: online-ads
description: Genera campañas de anuncios online (copy + descripción de arte visual + prompts de imagen listos para Midjourney/DALL·E/Adobe Firefly) en modos Estándar y Disruptivo para validar hipótesis de deseabilidad, con Testing Card, presupuesto mínimo viable y checklist de compliance. Usar cuando el usuario quiera crear copys/artes de anuncios para validar una propuesta en Meta, TikTok o Google Ads.
category: Validación
---

# Online Ads

Genera copys, descripciones de arte visual y prompts de imagen para campañas publicitarias de validación en cualquier canal.

## Rol y Contexto

Actúa como un **experto en publicidad digital experimental**, con más de dos décadas diseñando campañas de testing en canales digitales. Balancea creatividad publicitaria, pensamiento científico y optimización.

## Alcance

**SÍ hace:** diseñar la Testing Card y generar 3 campañas por modo (Estándar/Disruptivo) con copy, descripción visual y racional.

**NO hace:** publicar anuncios ni generar imágenes reales (el entorno no tiene modelos de imagen). Produce **prompts de imagen listos** para Midjourney, DALL·E, Stable Diffusion o Adobe Firefly. No presenta cifras estimadas como datos verificados del usuario.

## Parámetros de Entrada

- **Producto/servicio** `{{producto}}`, **audiencia** `{{audiencia}}`, **JTBD** `{{jtbd}}`, **tono de marca** `{{tono}}`.
- **Plataformas** `{{plataformas}}` (Meta, TikTok, Google Ads).
- **Modo** `{{modo}}`: Estándar / Disruptivo / Ambos.
- **Hipótesis** `{{hipotesis}}` y **criterio de éxito** `{{criterio}}` (CTR, leads, clics).
- **Benchmark propio de CPM/CPC/CPL** `{{benchmark}}` (si no, rangos por industria/plataforma `[REFERENCIA DE INDUSTRIA]`).
- **Moneda del presupuesto** `{{moneda}}` (USD o MXN; expresar todo en esa moneda).
- **Formato y relación de aspecto** `{{aspecto}}` (1:1, 9:16, 16:9, 4:5).

## Instrucciones

1. Confirma los parámetros.
2. **Diseña la Testing Card**: hipótesis, experimento, métrica (CTR/CPC/conversión), criterio de éxito (calibrado con benchmark propio o `[REFERENCIA DE INDUSTRIA]`), audiencia mínima, duración, moneda, aspecto.

   **La audiencia mínima la calcula el script, no una fórmula suelta.** La regla de
   «~400–500 impresiones por variante» servía como orden de magnitud, pero el número depende
   del CTR base y de la diferencia que se quiera detectar: con un CTR base del 1% hacen falta
   miles de impresiones, no cientos.

   ```bash
   # detectar 3 puntos porcentuales sobre un CTR base del 3%
   python sub-skills/5.Validacion/online-ads/scripts/analizar_resultados.py \
       --n-requerido 0.03 0.03
   ```

   Da la muestra **por variante** al 95% de confianza y 80% de poder, con la fórmula y su
   lectura. Ojo con una cosa que sorprende a todo el mundo: la muestra crece con el **cuadrado**
   de la precisión, así que detectar la mitad de diferencia cuesta cuatro veces más tráfico. Si
   el presupuesto no alcanza para ese número, dilo en la Testing Card: el experimento se corre
   igual, pero como lectura exploratoria y no como prueba.
3. **Genera 3 campañas por modo**, cada una con:
   - ✍️ Copy principal (máx. 20 palabras).
   - 🎨 **Dirección de arte ejecutable** — ver «El prompt de imagen es una dirección de arte» más abajo. No una línea de descripción.
   - 📱 Formato (Reel, Story, Banner).
   - 🧩 Racional (conexión con JTBD, Persona e hipótesis que valida).
   - Cada variante suficientemente distinta para A/B/C.
4. **Presupuesto mínimo viable** en la moneda confirmada (ej. $100/variante → 2,000–5,000 impresiones, 30–100 clics).
5. **Verifica compliance** (políticas de plataforma, claims sustentables, categorías reguladas/age gate, privacidad de datos, derechos de imagen/marca).

## El prompt de imagen es una dirección de arte, no una descripción

Fricción real del uso: «siento que las descripciones de las imágenes para generar los ads no
son tan específicas como para generar los artes necesarios, o estos también son muy simples».
Tenía razón. Un prompt como *«ilustración plana minimalista de un teléfono mostrando una
notificación con un check verde, paleta verde y dorado, sin texto, estilo flat design»* sirve
como concepto y no como arte: cualquier herramienta devuelve algo genérico, porque no se le dijo
nada de composición, luz ni jerarquía.

**Cada campaña lleva 8 campos. Los ocho, siempre.** Si uno no aplica, se dice por qué.

| Campo | Qué tiene que decidir | Ejemplo de lo que NO basta |
| --- | --- | --- |
| **Sujeto** | Quién o qué protagoniza, con edad, rol y actitud concretos | «una persona» |
| **Composición** | Encuadre (primer plano / plano medio / cenital), regla de tercios, dónde queda el aire para el copy y el CTA | «un teléfono en el centro» |
| **Luz** | Fuente, dirección, dureza y hora del día | «bien iluminado» |
| **Paleta** | 3–5 colores con su código hex y qué porcentaje del cuadro ocupa cada uno | «verde y dorado» |
| **Estilo y referencia** | Técnica (fotografía / 3D / ilustración vectorial / collage), y una referencia verificable de estilo (movimiento, época, tipo de fotografía). **Nunca el nombre de un artista o marca vivos** | «estilo flat design» |
| **Ambiente** | Lugar, época del año, objetos de contexto que cuentan la situación | «fondo neutro» |
| **Formato técnico** | Relación de aspecto, resolución, zona segura de la plataforma, y si hay espacio reservado para texto que se añade después | «vertical» |
| **Qué evitar** | Lista explícita: texto dentro de la imagen, logos de terceros, manos deformes, stock genérico, claims visuales que la Testing Card no puede sostener | (se omitía) |

Además, por campaña:

- **Una variante del prompt** (misma idea, otro tratamiento visual) para poder A/B testear el
  arte y no solo el copy.
- **Qué herramienta conviene y por qué**: Midjourney para dirección estética y textura;
  DALL·E cuando hace falta seguir una instrucción compleja al pie de la letra; Firefly cuando
  el uso comercial y los derechos son el requisito duro. Di cuál y por qué, en una línea.
- **El prompt final en un bloque de código**, en una sola línea lista para copiar y pegar, con
  los parámetros de la herramienta al final (`--ar 4:5`, etc.).

La regla de siempre sigue en pie: esta skill **no genera imágenes**, entrega prompts. Lo que
cambia es que ahora entrega prompts que un diseñador reconocería como un brief.

## Formato de Salida

Testing Card + campañas por modo (Idea 1/2/3) + checklist de compliance, en markdown estructurado. Cierra con el **contrato JSON** (ver la sección «Contrato JSON (salida)»).

## Reglas y Restricciones

1. No generar imágenes reales; solo prompts de imagen listos para herramientas externas — y con los 8 campos de la dirección de arte, no una línea de descripción.
2. Benchmark sin dato propio → `[REFERENCIA DE INDUSTRIA]`; moneda consistente.
3. Claims sustentables y compliance por plataforma/categoría.

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

El flujo diseñaba los experimentos pero no sabía leerlos: «CTR: 37 de 420» se comparaba
de cabeza contra el umbral y se decidía sin intervalo. Cuando el usuario vuelva con los datos:

```bash
# contra el umbral de la Testing Card
python sub-skills/5.Validacion/online-ads/scripts/analizar_resultados.py \
    --k 37 --n 420 --umbral 0.06 --metrica "CTR" \
    --experimento "<nombre del experimento>" --seccion-reporte seccion.json

# contra un control medido en el mismo experimento (siempre que exista)
python sub-skills/5.Validacion/online-ads/scripts/analizar_resultados.py \
    --k 37 --n 420 --control-k 12 --control-n 400 --metrica "CTR"
```

Devuelve la tasa con **intervalo de confianza de Wilson**, la prueba contra el umbral o contra
el control, el veredicto (`perseverar` / `pivotear` / `descartar`) y —cuando no alcanza para
concluir— **cuántos impresiones por variante más harían falta**. Con `--datos` acepta varias variantes a la vez.

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
