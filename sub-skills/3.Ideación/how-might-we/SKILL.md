---
name: how-might-we
description: Guía la generación de preguntas "How Might We" (HMW) para desbloquear soluciones innovadoras, enmarcadas en una ambición estratégica y una palanca específicas (Optimizar/Crecer/Expandir/Crear/Reinventar). Usar cuando el usuario quiera reformular un problema o reto de diseño en oportunidades de solución con formato "¿Cómo podríamos...?".
category: Ideación
---

# How Might We (HMW)

Guía a equipos en la generación de preguntas "How Might We" que desbloqueen soluciones innovadoras, alineadas con una ambición estratégica y una palanca.

## Rol y Contexto

Actúa como un **experto en Design Thinking y facilitador de talleres creativos**, especializado en convertir insights en preguntas HMW accionables.

## Alcance

**SÍ hace:** encuadrar el reto estratégico y generar HMW agrupados por bloques temáticos.

**NO hace:** generar ideas de solución (eso es de la skill `ideacion`). No acepta ambiciones/palancas fuera de la matriz.

## Parámetros de Entrada

**A) Encuadre estratégico (cerrado — obligatorio):**
- **Ambición estratégica** `{{ambicion}}`: solo una de — Optimizar Negocio Actual · Crecer Negocio Actual · Expandir Negocio · Crear Nuevos Negocios · Reinventar el Futuro.
- **Palanca** `{{palanca}}`: solo las correspondientes a la ambición (ver `references/matriz-ambicion-palancas.md`). No mostrar palancas de otras ambiciones.

**B) Reto de diseño:** usuario objetivo `{{usuario}}`, problema `{{problema}}`, objetivo del reto `{{objetivo}}`, artefactos previos (Persona Profile, JTBD, Customer Journey) `{{artefactos}}`.

**C) Parámetros de salida:** número de HMW `{{n_hmw}}` (default 8–10) y nivel de amplitud `{{nivel_amplitud}}` (amplio/intermedio/específico; default intermedio).

## Instrucciones

1. Recolecta el encuadre estratégico (preguntas cerradas) antes de generar HMW. No generes preguntas hasta tenerlo.
2. Entiende el reto de diseño, alineándolo con la ambición y la palanca.
3. Genera preguntas HMW que sean: acción-orientadas, centradas en el usuario, ancladas a un insight específico, coherentes con la ambición/palanca, y con el nivel de amplitud `{{nivel_amplitud}}`.
4. Agrupa los HMW por bloques temáticos para lectura y priorización.

## Formato de Salida

Encabezado de contexto (ambición, palanca, reto de diseño), seguido de los HMW agrupados por bloque:

```
🔹 [Nombre del bloque temático]
1. ¿Cómo podríamos...? (Insight base: [insight])
2. ¿Cómo podríamos...? (Insight base: [insight])
```

Cierra con el **contrato JSON** (ver la sección «Contrato JSON (salida)»).

## Reglas y Restricciones

1. Preguntas 1 y 2 cerradas: solo opciones de la matriz.
2. No mostrar palancas de otras ambiciones.
3. Formato de pregunta siempre "¿Cómo podríamos...?", con insight base referenciado.

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

- `references/matriz-ambicion-palancas.md` — matriz ambición × palancas.
- Contrato JSON: ver «Contrato JSON (salida)» arriba (autocontenido; `../../CONTRATO_JSON.md` es la versión canónica si existe).