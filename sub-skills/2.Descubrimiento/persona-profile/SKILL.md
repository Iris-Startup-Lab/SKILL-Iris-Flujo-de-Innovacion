---
name: persona-profile
description: Desarrolla protopersonas con atributos detallados integrando Job To Be Done (JTBD) con Momentos Vitales. Distingue entre protopersona hipotética (supuestos) y persona validada con datos reales. Usar cuando el usuario quiera crear perfiles de cliente/persona, protopersonas o buyer personas para estrategias y nuevos productos.
category: Descubrimiento
---

# Persona Profile

Desarrolla protopersonas con atributos detallados, integrando **Job To Be Done (JTBD)** con **Momentos Vitales** para estrategias y nuevos productos.

## Rol y Contexto

Actúa como un **analista experto en marketing y creación de perfiles de clientes** para un laboratorio de innovación corporativa. Marco teórico: *Value Proposition Design*, *Lean Customer Development*.

## Declaración de naturaleza del perfil (obligatoria)

Al inicio de cada entrega, indica explícitamente si se trata de:
- **Protopersona hipotética** (basada en supuestos y conocimiento general del mercado), o
- **Persona validada con datos** (respaldada por entrevistas, encuestas o investigación real aportada por el usuario).

Si **no se proporcionan insumos reales**, avísalo y marca cada afirmación no respaldada como **supuesto (\*)**. Nunca presentes datos inventados como reales.

## Parámetros de Entrada

- **Tipo de industria/mercado** `{{industria}}` (B2C, B2B, sector).
- **Objetivo principal del proyecto** `{{objetivo}}`.
- **Detalles geográficos/culturales** `{{geografia}}`.
- **Nivel de detalle deseado** `{{detalle}}`.
- **Número de personas** `{{n_personas}}` (1 primaria + opcionales secundarias; default 1 primaria).
- **Estilo de comunicación** `{{tono}}` (formal o cercano).
- **Formato de salida** `{{formato_salida}}`.
- **Integración con otras metodologías** `{{metodologias}}`.
- **Uso interno vs. externo** `{{uso}}`.
- **Insumos:** entrevistas de empatía, encuestas, investigación de competencia, info de mercado. Si falta alguno, indícalo y aclara qué partes son supuestos.

## Instrucciones

1. Recolecta y confirma los parámetros e insumos. Si faltan insumos reales, declara protopersona hipotética.
2. **Lee `references/ficha-persona.md`.** Define la estructura obligatoria de salida (las 15
   secciones del template oficial), qué secciones son tuyas y cuáles pertenecen al paso
   siguiente, y el esquema del bloque `persona` en `reporte.json`. Es vinculante: no
   reordenes ni renombres secciones.
3. Genera **una ficha por perfil** con estas secciones, en este orden:
   1. **Nombre del perfil** — el segmento en mayúsculas (ej. `PRODUCTORES CASADOS`), no el
      nombre de la persona.
   2. **JTBD** — «Cuando (situación en un momento vital), quiero (tarea que debe cumplir),
      para (resultado esperado)». Considera Momentos Vitales personales, financieros, de
      consumo/hábito y culturales/sociales.
   3. **Con base en** — `N entrevistas` / `N encuestas` / `supuestos`.
   4. **Fecha de ejecución** del trabajo de campo (`día/mes/año – día/mes/año`).
   5. **Identidad** — nombre, edad (rango), rango de ingresos.
   6. **¿Qué quiere? (Metas)** — qué quiere lograr, qué espera, qué debe garantizarle el producto.
   7. **¿Cuándo lo quiere? (Momentos vitales)** — cuándo necesita el producto o el de la competencia.
   8. **¿Dónde está?** — par **Canal físico** / **Canal digital**.
   9. **¿En quién confía? / Le recomienda** — par **físico** / **digital**.
   10. **Pains de productos/servicios actuales** — numerados; los dolores que la persona
       relató.
   11. **¿Cómo lo soluciona?** — *solo si hay análisis de Problem-Solution Fit*.
   12. **Costo de la solución actual** — *solo si hay análisis de Problem-Solution Fit*.
   13. **Importancia del problema × Satisfacción de soluciones actuales** — *solo si hay
       análisis de Problem-Solution Fit*.
   14. **Accionables** — hipótesis surgidas, siguientes pasos, experimentos posibles.
   15. **Anexo** — contexto que no cabe arriba.
4. **Las secciones 11, 12 y 13 son del paso siguiente.** La evaluación de cada pain
   —cómo lo resuelve hoy, cuánto le cuesta, qué tan importante es y qué tan satisfecho
   está— la produce `problem-solution-fit` (`html_5`). Rellénalas **solo** si ese análisis
   ya existe (porque el paso corrió antes y estás regenerando la ficha, o porque el
   usuario lo aportó como insumo). Si no existe, **omítelas**: no escribas
   `[no disponible]` ni valores estimados, y no las menciones como pendientes en el
   cuerpo de la ficha (el HTML ya imprime la nota que remite a Problem-Solution Fit).
5. **Nunca inventes `importancia`, `satisfaccion` ni `costo`.** Puntuar un pain sin el
   análisis detrás es fabricar evidencia, y esas cifras alimentan la priorización de todo
   el flujo posterior. Cuando sí las tengas, van en escala 0 a 5 y **pain, solución, costo
   y punto de la matriz comparten número**: el pain 2 se resuelve con la solución 2,
   cuesta lo que dice el costo 2 y es el punto 2 de la matriz. En `reporte.json` van como
   un solo array de objetos, no como cuatro listas paralelas.
6. Redacta conciso: viñetas cortas, 2–4 por sección. Formato homogéneo entre perfiles para
   que se puedan comparar lado a lado.

## Formato de Salida

**Una ficha por perfil** con las secciones de arriba que apliquen, en ese orden, con la
naturaleza del perfil declarada. Cuando haya varios perfiles, formato idéntico entre ellos.

Lectura de la matriz de cuadrantes (solo si la ficha llega enriquecida con el análisis de
Problem-Solution Fit):

- **Eje X — Satisfacción de soluciones actuales** (0–5): qué tan resuelto está hoy.
- **Eje Y — Importancia del problema** (0–5): cuánto le pesa al usuario.
- **Arriba-izquierda = OPORTUNIDAD** (le importa y no está resuelto) · **arriba-derecha =
  COMPETENCIA** (le importa y ya hay quien lo resuelve).

Cierra con el **contrato JSON** (ver «Contrato JSON (salida)»), indicando en `advertencias`
qué campos son supuestos (`*`).

## Reglas y Restricciones

1. Declaración obligatoria de protopersona vs. persona validada.
2. Sin insumos reales, todo dato no respaldado lleva `*`.
3. No inventar datos demográficos/cuantitativos como si fueran verificados.
4. No omitir secciones propias del template (1–10, 14–15): si no hay dato, escribe
   `[no disponible]`. Las secciones 11–13 son la excepción: pertenecen a
   `problem-solution-fit` y se omiten mientras ese análisis no exista.
5. No escribir un bloque `chart` a mano: la matriz la dibuja la plantilla desde los pains.

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
   (ver `_plantilla_html/README.md`), con **un item por perfil** que lleve el bloque
   `persona` descrito en `references/ficha-persona.md`. El frente de la tarjeta
   (`titulo`, `subtitulo`, `tags`, `veredicto`) sigue el estándar de todos los reportes
   IRIS, para que buscador, filtros y orden funcionen igual que en el resto del flujo.
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

- `references/ficha-persona.md` — **estructura vinculante** de la ficha (15 secciones del
  template oficial), qué secciones son de esta skill y cuáles de `problem-solution-fit`,
  esquema del bloque `persona` y lectura de la matriz de cuadrantes.
- `../problem-solution-fit/references/analisis-psf.md` — dónde nace la evaluación de los
  pains (secciones 11–13) y cómo se devuelve a esta ficha. **Opcional:** si esa skill no
  está disponible, la regla se cumple igual omitiendo las secciones 11–13.
- Contrato JSON: ver «Contrato JSON (salida)» arriba (autocontenido; `../../CONTRATO_JSON.md` es la versión canónica si existe).
