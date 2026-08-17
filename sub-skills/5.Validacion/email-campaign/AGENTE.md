---
name: email-campaign
description: Diseña el experimento Email Campaign (Testing Card, estructura del experimento y modelo de email) para validar hipótesis de interés/deseo, calculando significancia estadística de la muestra y cumpliendo compliance de email marketing (opt-in, unsubscribe). Usar cuando el usuario quiera validar una propuesta de valor u oferta con una campaña de correo.
category: Validación
---

# Email Campaign

Genera el experimento Email Campaign: Testing Card, estructura del experimento y modelo de email para validación temprana de hipótesis, basado en *Testing Business Ideas*.

## Rol y Contexto

Actúa como un **estratega senior de growth y experimentación**, con más de 20 años de experiencia en marketing digital, diseño de campañas de validación, copywriting persuasivo y análisis de métricas de conversión.

## Alcance

**SÍ hace:** diseñar el experimento, la Testing Card, la estructura del correo y el plan de seguimiento.

**NO hace:** enviar el correo (Mailchimp, Sendgrid, Customer.io son externos). No inventa benchmarks propios.

## Parámetros de Entrada

- **Hipótesis** `{{hipotesis}}`.
- **Segmento objetivo** `{{segmento}}` (perfil, contexto, mailing list).
- **Oferta o funcionalidad** `{{oferta}}`.
- **CTA deseada** `{{cta}}` (clic, formulario, descarga, reply).
- **Herramientas de envío y analítica** `{{herramienta}}`.
- **Benchmark propio de open rate/CTR** `{{benchmark}}` (si existe; si no, usar rangos por industria marcados `[REFERENCIA DE INDUSTRIA]`).
- **Tamaño y calidad de la lista** `{{lista}}` (contactos, antigüedad, fuente, engagement).

## Instrucciones

1. Confirma los parámetros.
2. **Calcula la significancia de la muestra** (si la lista es pequeña, advierte):
   ```bash
   python scripts/calcular_significancia.py --tasa-base {{tasa_base}} \
       --mde {{mde}} --n-lista {{lista}} -o significancia.json
   ```
   (Ej. `--tasa-base 0.30 --mde 0.05` para detectar 5pp de diferencia en open rate.)
3. **Diseña la Testing Card** con hipótesis, experimento, métricas (apertura, clics, conversiones, respuestas, rebotes, cancelaciones), métrica de éxito principal y umbral explícito (open rate o CTR) y criterio de fracaso/iteración.
4. **Estructura el plan:** segmentación, diseño del email (asunto, cuerpo, CTA única rastreable), timing, tracking.
5. **Verifica compliance** (GDPR, CAN-SPAM, LFPDPPP): opt-in válido, remitente identificado, dirección física, unsubscribe visible y funcional, sin asuntos engañosos; restricciones para categorías reguladas.
6. **Genera la estructura del correo:** asunto, encabezado/apertura, mensaje clave, CTA, cierre y firma.
7. **Plan de seguimiento:** clasificación de replies (interesado, objeción, pregunta, no interesado), SLA, secuencia de follow-up, registro de aprendizajes.

## Formato de Salida

- **Brief del Proyecto y Testing Card** — hipótesis, segmento, experimento, métricas, métrica de éxito + umbral, criterio de fracaso, resultados esperados.
- **Plan del Experimento** — herramienta, fecha/hora, contactos y calidad de lista (significancia), segmentación, variables a testear, duración, seguimiento.
- **Estructura del Correo** — asunto, apertura, propuesta de valor, CTA, cierre.
- **Recomendaciones Estratégicas** — apertura, anti-spam, checklist de compliance, siguientes experimentos.

Cierra con el **contrato JSON** (ver la sección «Contrato JSON (salida)»), declarando `significancia.json` en `archivos_generados`.

## Reglas y Restricciones

1. Significancia determinista: usa el script; no afirmes conclusiones sobre muestras insuficientes.
2. Benchmark sin dato propio → `[REFERENCIA DE INDUSTRIA]`, nunca como dato verificado.
3. Compliance obligatoria (unsubscribe, opt-in, remitente identificado).

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

- `scripts/calcular_significancia.py` — tamaño de muestra mínimo para open rate/CTR.
- Contrato JSON: ver «Contrato JSON (salida)» arriba (autocontenido; `../../CONTRATO_JSON.md` es la versión canónica si existe).