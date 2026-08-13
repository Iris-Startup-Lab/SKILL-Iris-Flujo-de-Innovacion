# Contrato JSON entre Skills — Flujo de Innovación IRIS

Estándar de comunicación entre la macro-skill orquestadora (`iris-flujo-de-innovacion`) y cada sub-skill, y entre sub-skills. Toda skill del flujo produce al cierre un JSON con esta estructura. El campo `decision.siguiente_paso` es el que la macro-skill interpreta para encadenar el flujo.

## Estructura base

```json
{
  "skill": "<nombre-skill>",
  "timestamp": "<ISO 8601>",
  "parametros": {
    "<var1>": "<valor1>",
    "<var2>": "<valor2>"
  },
  "output": {
    "formato": "<markdown|csv|json|html>",
    "contenido": "<resultado estructurado>",
    "archivos_generados": ["<path1>", "<path2>"]
  },
  "decision": {
    "veredicto": "<perseverar|pivotear|descartar>",
    "siguiente_paso": "<nombre-skill-siguiente | null>",
    "razon": "<por qué>",
    "contexto_usado": ["<html_N de los pasos cuyo output alimentó este resultado>"]
  },
  "advertencias": ["<lista de limitaciones>"]
}
```

## Semántica de campos

| Campo | Obligatorio | Descripción |
| --- | --- | --- |
| `skill` | Sí | Nombre de la skill (kebab-case). |
| `timestamp` | Sí | Momento real de generación, en orden cronológico. |
| `parametros` | Sí | Variables de entrada confirmadas con el usuario (con los supuestos/valores por defecto marcados `*`). |
| `output.formato` | Sí | Formato del entregable principal. |
| `output.contenido` | Sí | Resultado estructurado (puede ser el resumen del entregable si este es un archivo). |
| `output.archivos_generados` | No | Rutas de archivos escritos (CSV, MD, HTML, etc.). |
| `decision.veredicto` | Sí | `perseverar` / `pivotear` / `descartar`. En skills de diseño/planeación se usa `perseverar` cuando el experimento queda listo para ejecutarse. |
| `decision.siguiente_paso` | No | Nombre de la skill siguiente en el grafo, o `null` si es un punto de decisión del usuario. |
| `decision.razon` | Sí | Justificación breve del veredicto y del siguiente paso. |
| `decision.contexto_usado` | No | Pasos del flujo (`html_N`) cuyos resultados alimentaron este output. Lista vacía si la skill corrió suelta. Es la traza del encadenamiento: sin ella no se sabe qué evidencia previa sostiene el resultado. |
| `advertencias` | No | Limitaciones, datos estimados, supuestos, ausencias de información. |

## Reglas de integridad

1. **Nunca inventar cifras.** Si un dato es estimado, marcarlo con `*` y declarar el método/fuente en `advertencias`. Si es imposible de obtener, escribir `[no disponible]`.
2. **Datos reales por encima de síntesis.** Si un script (`scripts/`) o `webfetch` puede obtener el dato, se usa; el LLM solo redacta interpretación, no cifras crudas.
3. **Trazabilidad de archivos.** Todo archivo declarado en `archivos_generados` debe existir realmente en disco.
4. **Veredicto coherente con criterio de éxito.** El `decision.veredicto` se deriva de la Testing Card (criterio de éxito), no de una opinión libre.

## Encadenamiento: la salida de un paso es la entrada del siguiente

El contrato viaja hacia adelante por dos canales distintos, y no son intercambiables:

| Canal | Qué lleva | Dónde lo lee el paso siguiente |
| --- | --- | --- |
| **Resumen** | Una línea: qué se aprendió | `flujo.ruta[].resumen`, y el briefing de `estado_flujo.py mostrar` |
| **Datos** | El `reporte.json` completo del paso (bloques `persona`, `psf`, `secciones[].items[]`) | `flujo.ruta[].datos`; si falta, embebidos en el HTML (`window.REPORT_DATA`) |

Al cerrar un paso se registran los dos:

```bash
python scripts/estado_flujo.py completar --paso html_N \
    --resumen "<una línea>" --outputs html_N.html --datos reporte.json
```

**El resumen es el índice, no el contenido.** Una skill que necesita la estructura del paso
anterior abre su `datos` y la hereda; reconstruirla a partir del resumen pierde evidencia y
rompe la trazabilidad que declara `decision.contexto_usado`.

## Puntos de decisión (bifurcaciones)

Cuando el flujo llega a un nodo de decisión (ej. "¿Hay datos reales de entrevistas/encuestas?"), la skill saliente pone `decision.siguiente_paso = null` y describe las opciones en `output.contenido` para que la macro-skill se las presente al usuario.
