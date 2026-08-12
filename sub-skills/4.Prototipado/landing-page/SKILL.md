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

**SÍ hace:** diseñar la Testing Card, la estructura de la página, el checklist de copy/CTA y el plan de ejecución.

**NO hace:** construir ni lanzar la página. No inventa benchmarks propios.

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

1. Confirma los parámetros.
2. **Diseña la Testing Card** con: hipótesis, experimento (landing + CTA + canal), métricas clave (visitas, CTR, tiempo en página, conversión), métrica de éxito principal y umbral explícito calibrado con benchmark (ej. "≥ X% de conversión en N visitas únicas") y criterio de fracaso/iteración.
3. **Estructura la landing:** headline, subheadline, visual principal, beneficios (máx. 3), prueba social (opcional), CTA prominente, formulario/paso siguiente, age gate/disclaimers (si aplica).
4. **Verifica el checklist de copy y CTA** (headline < 5s y de beneficio, subheadline no repetitivo, beneficios escaneables, un solo CTA medible, mobile-first, cumplimiento legal).
5. **Plan de ejecución:** herramienta, duración, fuentes de tráfico, presupuesto + volumen esperado, analítica (GTM, Hotjar, GA4, Mixpanel), A/B testing.

## Formato de Salida

- **Testing Card** — con métrica de éxito principal y umbral calibrado + criterio de fracaso.
- **Estructura de la Landing Page** — por bloques.
- **Plan de ejecución** — herramienta, duración, tráfico, presupuesto, analítica.
- **Checklist de Copy y CTA** — marcado de verificación previo al lanzamiento.

Cierra con el **contrato JSON** (ver la sección «Contrato JSON (salida)»).

## Reglas y Restricciones

1. Umbrales calibrados con benchmark propio o estimación marcada, nunca arbitrarios sin justificación.
2. Age gate y disclaimers si la categoría es regulada.
3. Un solo CTA principal, medible y conectado a analítica.

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