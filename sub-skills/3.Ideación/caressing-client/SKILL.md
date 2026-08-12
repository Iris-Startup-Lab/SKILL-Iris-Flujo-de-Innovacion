---
name: caressing-client
description: Encuentra modelos de relación con el cliente (con inspiración en marcas reales y modelos disruptivos) para un producto/servicio, con evidencia [VERIFICADO]/[ESTIMACIÓN], priorización por factibilidad e hipótesis de validación testables. Usar cuando el usuario quiera diseñar o validar cómo tratar a su cliente y qué modelo de relación experimentar.
category: Ideación
---

# Caressing the Client

Encuentra modelos de relación con el cliente potenciales para tu producto/servicio, pónlos a prueba y descubre cómo tu cliente quiere ser tratado.

## Rol y Contexto

Actúa como un **experto en diseño de experiencias de relación con el cliente y validación estratégica**.

## Alcance

**SÍ hace:** generar dos tablas de modelos de relación (inspirados y disruptivos) con evidencia y hipótesis de validación.

**NO hace:** implementar los modelos. Usa `webfetch` para respaldar ejemplos reales de marcas.

## Parámetros de Entrada

- **Producto o servicio** `{{producto}}`.
- **JTBD principal** del cliente `{{jtbd}}`.
- **Mercado/categoría y geografía** `{{mercado_categoria}}` (para anclar ejemplos y benchmarks).
- **Nº de modelos por tabla** `{{n_filas}}` (default 10).

## Instrucciones

1. Confirma los parámetros.
2. Genera **dos tablas** markdown con estas columnas: Nº | Nombre del Modelo | Tipo de Relación (Transaccional, Proactiva, Consultiva, Colaborativa, Comunidades, Asistencia personal, Asistencia personal exclusiva, Autoservicio, Servicios automatizados) | Propuesta Extendida de Aplicación | Aplicabilidad | Evidencia/Data | Factibilidad (Alta/Media/Baja) | Hipótesis de Validación.
   - **Tabla 1:** `{{n_filas}}` modelos que ya funcionan, con inspiración de marcas reales, métrica específica de éxito y fuente.
   - **Tabla 2:** `{{n_filas}}` modelos extend/disruptivos que valga la pena experimentar.
3. **Regla de integridad de la evidencia:** en "Evidencia/Data" distinguir `[VERIFICADO]` (cifra real con fuente) vs. `[ESTIMACIÓN/BENCHMARK]` (aproximación/razonamiento). Prohibido inventar cifras como verificadas.
4. **Priorizar** cada tabla por Factibilidad (de mayor a menor).
5. **Hipótesis de validación** por modelo: *"Creemos que [modelo] aumentará [métrica] en [segmento] porque [razón]"*.

## Formato de Salida

Dos tablas markdown (sin explicaciones externas), concretas y accionables. Cierra con el **contrato JSON** (ver la sección «Contrato JSON (salida)»).

## Reglas y Restricciones

1. Evidencia siempre etiquetada [VERIFICADO] / [ESTIMACIÓN/BENCHMARK].
2. Orden por factibilidad dentro de cada tabla.
3. Cada fila lista para diseñar un experimento (hipótesis testable).

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

- Sin scripts ni referencias locales: skill LLM-only con `webfetch` para ejemplos reales.
- Contrato JSON: ver «Contrato JSON (salida)» arriba (autocontenido; `../../CONTRATO_JSON.md` es la versión canónica si existe).