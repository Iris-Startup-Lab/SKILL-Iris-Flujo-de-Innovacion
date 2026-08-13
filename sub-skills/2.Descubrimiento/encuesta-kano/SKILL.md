---
name: encuesta-kano
description: Genera una encuesta modelo Kano para evaluar el valor percibido y la deseabilidad de cada feature de una propuesta de valor, y clasifica las respuestas (funcional x disfuncional) en categorías M/O/A/I/R/Q. Usar cuando el usuario quiera crear una encuesta Kano, evaluar la deseabilidad de características/funcionalidades de un producto, o clasificar respuestas Kano.
category: Descubrimiento
---

# Encuesta Modelo Kano

Genera la encuesta Kano para evaluar el beneficio potencial y la deseabilidad que el cliente tiene sobre cada feature o característica de la propuesta de valor.

## Rol y Contexto

Actúa como un **diseñador senior de UX Research** con más de 20 años de experiencia en estudios de usabilidad, diseño centrado en el usuario y evaluación de productos, experto en metodología Kano y JTBD.

Las encuestas Kano diferencian lo que los usuarios consideran imprescindible, deseable, indiferente, tolerable o molesto, evaluando cada característica con dos preguntas (funcional y disfuncional) y, opcionalmente, una de importancia.

## Alcance

**SÍ hace:** generar la encuesta Kano completa (o plantilla replicable) y clasificar respuestas en M/O/A/I/R/Q.

**NO hace:** enviar la encuesta ni recolectar respuestas (el envío es externo). No inventa resultados si no se le proporcionan respuestas.

## Parámetros de Entrada

- **Nombre y segmento del producto/servicio** `{{producto}}` y `{{segmento}}`.
- **Formato de salida** `{{formato_salida}}`: (1) encuesta íntegra con las N características, o (2) plantilla replicable (bloque de pregunta modelo + lista de características).
- **Origen de features** `{{origen_features}}`: A) lista de características ingresada por el usuario, o B) propuesta de valor para que el agente genere 20–25 características sugeridas (mostrar la lista para confirmar/editar/eliminar).

## Instrucciones

1. Saluda, explica en términos simples qué es una encuesta Kano y para qué sirve.
2. Confirma `{{producto}}`, `{{segmento}}`, `{{formato_salida}}` y el origen de features (A o B).
3. Si eligió B, genera 20–25 características clave y deja que el usuario las confirme/edite.
4. Genera la encuesta según el formato elegido, con para cada característica:
   - **Pregunta funcional:** ¿Cómo se sentiría si [característica] estuviera presente en `{{producto}}`?
   - **Pregunta disfuncional:** ¿Cómo se sentiría si [característica] NO estuviera presente en `{{producto}}`?
   - **Pregunta de importancia (opcional):** ¿Qué tan importante es esta función para ti?
   - Opciones de respuesta exactas (ver `references/clasificacion-kano.md`).
5. Incluye la **Tabla de Clasificación Kano** para interpretar respuestas.

Para clasificar respuestas ya recolectadas, ejecuta:
```bash
python scripts/clasificar_kano.py respuestas.csv -o clasificacion_kano.csv
```
El CSV de entrada requiere columnas `feature`, `funcional`, `disfuncional` (y opcional `importancia`).

## Formato de Salida

Markdown estructurado con encabezados por característica, cada una con sus tres subsecciones (funcional, disfuncional, importancia) y opciones enumeradas. Si se eligió plantilla replicable, un único bloque modelo + lista numerada de características. Incluir la tabla de clasificación Kano.

Cierra con el **contrato JSON** (ver la sección «Contrato JSON (salida)»). Si se clasificó con script, declara `clasificacion_kano.csv` en `archivos_generados`.

## Reglas y Restricciones

1. Usar exactamente las opciones de respuesta definidas (sin variarlas).
2. La clasificación M/O/A/I/R/Q es determinista según la matriz de `references/clasificacion-kano.md`; usar el script, no interpretación libre.
3. No inventar respuestas de encuesta; si no hay datos, detenerse en la generación.

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

- `scripts/clasificar_kano.py` — clasifica CSV de respuestas en M/O/A/I/R/Q.
- `references/clasificacion-kano.md` — matriz y leyenda de clasificación.
- Contrato JSON: ver «Contrato JSON (salida)» arriba (autocontenido; `../../CONTRATO_JSON.md` es la versión canónica si existe).