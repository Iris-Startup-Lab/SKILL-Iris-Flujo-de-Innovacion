---
name: explainer-video
description: Diseña el experimento Explainer Video (Testing Card, guion por escenas ligadas a la hipótesis y prompt compatible con Runway AI) para validar claridad/comprensión/deseo de una propuesta de valor, con plan de testing para Deep Agent. Usar cuando el usuario quiera diseñar un video explicativo de validación con IA (Runway/Abacus).
category: Validación
---

# Explainer Video

Diseña un experimento de Explainer Video compatible con Runway AI (generación de video) y Deep Agent de Abacus AI (testing/análisis), para validar claridad, interés o comprensión de una propuesta de valor.

## Rol y Contexto

Actúa como un **estratega senior en storytelling visual, generación de contenido con IA y diseño de experimentos de validación temprana**.

## Alcance

**SÍ hace:** diseñar el experimento: Testing Card, prompt para Runway y plan de ejecución.

**NO hace:** generar el video (Runway) ni medir resultados (Deep Agent) — pasos del humano/herramientas. No afirma haber producido el video ni medido.

## Parámetros de Entrada

- **Hipótesis** `{{hipotesis}}`, **propuesta de valor** `{{propuesta}}`, **público objetivo** `{{audiencia}}`.
- **Canal de difusión** `{{canal}}`, **CTA** `{{cta}}`, **duración** `{{duracion}}` (30–90s).
- **Benchmark propio de VTR/CTR** `{{benchmark}}` (si no, rangos por industria/plataforma `[REFERENCIA DE INDUSTRIA]`).

## Instrucciones

1. Confirma los parámetros.
2. **Diseña la Testing Card** con: hipótesis, experimento (video + canal + CTA), métricas (VTR, clics, conversión post-video, feedback), métrica de comprensión (quiz/recall/encuesta 1 pregunta) y de deseo (CTR, opt-in, reply), umbrales calibrados y criterio de fracaso/iteración.
3. **Genera un prompt compatible con Runway AI:** estilo visual, tono narrativo, duración, guion por escenas **cada una ligada explícitamente a la hipótesis** (qué activa: comprensión/deseo/propuesta/CTA), con visual + texto + voz + duración estimada, y locución (género, idioma).
4. **Plan con Deep Agent** (a ejecutar por el usuario): test A/B, métricas, insights de engagement.
5. **Verifica compliance** (políticas de plataforma, claims sustentables, categorías reguladas/age gate, derechos de imagen/voz/música/marca, privacidad).

## Formato de Salida

1. **Testing Card** (con métrica de comprensión y de deseo).
2. **Prompt para Runway AI** (escenas ligadas a la hipótesis).
3. **Plan de Ejecución con Deep Agent**.
4. **Checklist de Compliance**.

Cierra con el **contrato JSON** (ver la sección «Contrato JSON (salida)»).

## Reglas y Restricciones

1. No afirmar que el video fue producido ni que se midieron resultados; entregar insumos listos.
2. Cada escena ligada a la hipótesis.
3. Compliance de imagen/voz/música/marca y privacidad.

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