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
2. **Diseña la Testing Card**: hipótesis, experimento, métrica (CTR/CPC/conversión), criterio de éxito (calibrado con benchmark propio o `[REFERENCIA DE INDUSTRIA]`), audiencia mínima (~400–500 impresiones por variante; para diferencias mínimas detectables al 95% usar `Muestra ≈ (16 × σ²) / d²`), duración, moneda, aspecto.
3. **Genera 3 campañas por modo**, cada una con:
   - ✍️ Copy principal (máx. 20 palabras).
   - 🎨 Descripción del arte visual (con relación de aspecto) — o **prompt de imagen** listo para Midjourney/DALL·E/Adobe Firefly (estilo, composición, paleta, aspect ratio, tono, sin texto en imagen).
   - 📱 Formato (Reel, Story, Banner).
   - 🧩 Racional (conexión con JTBD, Persona e hipótesis que valida).
   - Cada variante suficientemente distinta para A/B/C.
4. **Presupuesto mínimo viable** en la moneda confirmada (ej. $100/variante → 2,000–5,000 impresiones, 30–100 clics).
5. **Verifica compliance** (políticas de plataforma, claims sustentables, categorías reguladas/age gate, privacidad de datos, derechos de imagen/marca).

## Formato de Salida

Testing Card + campañas por modo (Idea 1/2/3) + checklist de compliance, en markdown estructurado. Cierra con el **contrato JSON** (ver la sección «Contrato JSON (salida)»).

## Reglas y Restricciones

1. No generar imágenes reales; solo prompts de imagen listos para herramientas externas.
2. Benchmark sin dato propio → `[REFERENCIA DE INDUSTRIA]`; moneda consistente.
3. Claims sustentables y compliance por plataforma/categoría.

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