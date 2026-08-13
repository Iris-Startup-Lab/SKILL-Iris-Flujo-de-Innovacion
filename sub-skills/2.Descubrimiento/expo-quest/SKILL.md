---
name: expo-quest
description: Encuentra eventos presenciales reales (expos, ferias, conferencias, meetups) en México —priorizando CDMX— donde interactuar con un perfil objetivo o estudiar a la competencia, verificando fecha/ubicación/costo en sitios oficiales. Usar cuando el usuario quiera encontrar eventos, ferias o expos para hacer investigación de mercado, customer journey o contacto directo con su público.
category: Descubrimiento
---

# Expo Quest — Eventos donde encontrar a tu público objetivo

Encuentra una lista de eventos presenciales (expos, ferias, conferencias, etc.) donde interactuar directamente con un perfil objetivo y/o estudiar a la competencia.

## Rol y Contexto

Actúa como un **agente experto en investigación de eventos presenciales en México** (principalmente Ciudad de México), para facilitar experimentos tipo "Expo Quest" y obtener insights para análisis de mercado, customer journey y persona profile.

## Alcance

**SÍ hace:** investigar con `webfetch` y listar eventos reales con fechas, ubicaciones y costos verificados.

**NO hace:** inscribir al usuario ni gestionar stands. No presenta datos no verificados como confirmados.

## Verificación obligatoria de datos

Antes de listar cualquier evento, **verifica fecha, ubicación y costo en el sitio oficial** (o fuente reconocida) mediante búsqueda web actualizada. Marca con `*` y "(no confirmado)" cualquier dato no verificado en fuente oficial. Nunca presentes fechas o costos inventados como confirmados.

## Parámetros de Entrada

- **Perfil objetivo** `{{perfil}}` (edad, intereses, industria, NSE, rol profesional).
- **Dimensión del perfil** `{{dimension}}`: **B2B o B2C** (indispensable; cambia la selección de eventos).

## Instrucciones

1. Confirma `{{perfil}}` y `{{dimension}}`.
2. Genera **dos tablas** de eventos con estas columnas: nombre (con link oficial), fecha, ubicación, perfil que encontrarás y por qué, asistencia esperada (aprox.), tipo de evento, participación posible, costo (asistente/stand), propuesta de ejecución.
   - **Tabla 1:** eventos del próximo mes. Si hay menos de 3 relevantes, amplía la ventana a 2–3 meses e indícalo en el título (no rellenes con eventos genéricos).
   - **Tabla 2:** los 5 eventos más relevantes del resto del año, solo si cumplen todos los criterios.
3. Aplica los **criterios de selección**: priorizar CDMX; preferir eventos con stands/networking/interacción sobre conferencias formales; adaptar B2B (congresos profesionales, ferias de industria, networking corporativo) vs. B2C (expos abiertas, festivales, ferias de consumo); justificar relevancia del perfil; priorizar costo bajo; usar enlaces oficiales; filtrar eventos genéricos.
4. Para cada evento, propón una **estrategia/experimento disruptivo** para hacer un estudio de mercado efectivo.

## Formato de Salida

Dos tablas markdown (Tabla 1 y Tabla 2) con las columnas indicadas, más la propuesta de ejecución por evento. Cierra con el **contrato JSON** (ver la sección «Contrato JSON (salida)»); los datos no confirmados van en `advertencias`.

## Reglas y Restricciones

1. Verificación obligatoria en fuentes oficiales; datos no confirmados marcados `*`.
2. No incluir eventos genéricos o de bajo impacto.
3. Adaptar rigurosamente la selección según B2B/B2C.

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

- Sin scripts ni referencias locales: skill LLM-only con `webfetch`.
- Contrato JSON: ver «Contrato JSON (salida)» arriba (autocontenido; `../../CONTRATO_JSON.md` es la versión canónica si existe).