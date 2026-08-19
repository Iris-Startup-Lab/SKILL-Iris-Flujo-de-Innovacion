---
name: simulador-day-in-the-life
description: Simula sesiones de observación etnográfica "A Day In The Life" con sujetos sintéticos y entrega un CSV codificable con la jornada por bloques horarios, fricciones y workarounds, muestreo reproducible por semilla y curva de saturación, todo etiquetado SIMULADO. Usar cuando el usuario no tenga acceso al campo para observar.
category: Descubrimiento
tipo: simulador
padre: 2.Descubrimiento/day-in-the-life
---

# Simulador de A Day In The Life (ADITL)

Fabrica las sesiones de observación que habría registrado un equipo siguiendo a una persona
durante su jornada, y las entrega en **un CSV** en formato largo listo para codificar. Todo
queda etiquetado **SIMULADO**.

## Alcance

**SÍ hace:** inventar los sujetos observados, repartir qué se observa en cada bloque horario
de cada sesión según la prevalencia declarada, y escribir el CSV con los conteos y la curva de
saturación calculados.

**NO hace:**

- **No analiza.** No consolida el esquema de codificación final ni concluye: eso es de
  `2.Descubrimiento/day-in-the-life`, que codifica el CSV como codificaría notas de campo
  reales.
- **No genera HTML** ni `reporte.json`, y no cierra pasos del flujo.
- **No sustituye la observación real.** Ver a alguien trabajar produce lo que nadie sabe
  contar de sí mismo; eso no se simula. Si hay acceso al campo, se va al campo.

## Cuándo se activa

Cuando el usuario decide simular en el **paso 2 del flujo** («Decisión — Entrevistas») con
A Day In The Life entre los agentes elegidos. Esa decisión enciende la marca de simulación en
todo el proyecto.

## El plan

Tú escribes el material cualitativo; **el script hace los números**:

```jsonc
{
  "proyecto": "Foro de producción audiovisual",
  "hipotesis": "La inconsistencia del staff técnico es la fricción principal de la jornada",
  "seed": 20260819,
  "ruido": 0.15,
  "sujetos": [               // 2-4 sesiones: los inventas tú, uno por uno
    { "nombre": "Laura (ficticio)", "rol": "Productora ejecutiva",
      "entorno": "Foro rentado, 3 cámaras", "actitud": "pragmática" },
    { "nombre": "Diego (ficticio)", "rol": "Director de fotografía",
      "entorno": "Foro propio pequeño", "actitud": "escéptico" }
  ],
  "bloques": [               // la jornada por tramos: el eje de la observación
    { "id": "B1", "hora": "07:00", "actividad": "Llegada y montaje" },
    { "id": "B2", "hora": "10:30", "actividad": "Primer bloque de rodaje" },
    { "id": "B4", "hora": "19:00", "actividad": "Desmontaje y cierre" }
  ],
  "codigos": [
    { "codigo": "STAFF-REEXPLICA",
      "tipo": "pain",                    // job | pain | gain | workaround
      "prevalencia": 0.8,                // DECLARADA: prob. de observarlo en una sesión
      "senal": "valida",                 // valida | refuta | neutral
      "bloque_id": "B1",                 // en qué tramo de la jornada ocurre
      "herramienta": "Hoja de setup impresa",
      "prevalencia_por_actitud": { "escéptico": 0.9 },
      "observaciones": ["Dedica 40 minutos a explicar el setup a un gaffer nuevo."] }
  ]
}
```

Reglas del plan:

1. **Los sujetos los escribes tú, uno por uno.** Son 2-4: nombre ficticio, rol, entorno y
   actitud. Que se distingan entre sí (antigüedad, contexto, temperamento), no tres versiones
   de la misma persona.
2. **Los bloques son el eje de la observación.** Una jornada sin tramos es una entrevista
   disfrazada: el valor de ADITL está en *cuándo* pasa cada cosa.
3. **Declara fricciones y workarounds.** El script avisa si el plan no trae ningún `pain` o
   ningún `workaround`: una jornada sin tropiezos no aporta nada, y la solución improvisada es
   el hallazgo más valioso de una observación —es la prueba de que el problema existe y de
   cuánto vale resolverlo.
4. **`prevalencia` es un supuesto declarado, no un dato.** El script sortea con ella e imprime
   lo declarado junto a lo observado.
5. **Al menos un código con `senal: refuta`.** El script avisa si no hay ninguno.
6. **`observaciones`** son las notas de campo literales que se citarán; el script las reparte.
7. **`herramienta`** es opcional pero vale la pena: qué usa la persona en ese momento es la
   mitad del hallazgo (la hoja impresa, el grupo de WhatsApp, la hoja de cálculo paralela).

## Ejecución

Desde la raíz del repositorio:

```bash
python sub-skills/2.Descubrimiento/day-in-the-life/simulador/scripts/simular_aditl.py \
    plan.json -o aditl_observaciones_SIMULADO.csv
```

Parámetros sobrescribibles: `--seed`, `--ruido`. El número de sesiones sale de la lista
`sujetos`.

## Qué produce

**Un CSV** (`aditl_observaciones_SIMULADO.csv`), una fila por sesión × bloque × código
observado. Los bloques sin ninguna observación **también dejan fila** (con `codigo` vacío):
así la jornada completa está en el archivo, huecos incluidos.

| Columna | Contenido |
| --- | --- |
| `sesion_id` | `S01`, `S02`, … (el orden es el de `sujetos`) |
| `sujeto`, `rol`, `entorno`, `actitud` | La persona observada |
| `bloque_id`, `hora`, `actividad` | El tramo de la jornada |
| `herramienta` | Con qué lo hace |
| `codigo`, `tipo` | Código y Job/Pain/Gain/Workaround (vacíos si no hubo observación) |
| `senal` | `valida` / `refuta` / `neutral` |
| `observacion` | La nota de campo repartida por el script |
| `simulado` | `si` en todas las filas |
| `seed` | La semilla, para que el archivo sea auditable por sí solo |

Además **imprime en pantalla** (no genera archivo): conteos por código y por tipo, **curva de
saturación**, reparto de señales, ficha de sujetos y avisos —incluido el aviso por cada sujeto
cuya jornada salió sin fricciones ni workarounds. Ese bloque es lo que se cita en el reporte:
**no lo reescribas de memoria.**

## Supuestos estadísticos y sus límites

**Aquí no hay porcentajes, y es a propósito.** Con 3 sesiones no se estima nada de una
población. Una muestra etnográfica se justifica por **saturación de códigos** —se observa hasta
que las jornadas dejan de traer fricciones nuevas— y se reporta con conteos: «2 de 3», nunca
«66%».

Lo que el script garantiza:

- **Reproducibilidad:** semilla explícita; misma semilla + mismo plan = CSV idéntico.
- **Muestreo declarado:** cada observación es un ensayo Bernoulli con la prevalencia del plan
  (modulada por actitud), encogida hacia 0.5 según el `ruido`.
- **Conteos derivados:** el recuento real de las filas del CSV.
- **Curva de saturación:** códigos nuevos por sesión; saturación = 2 sesiones seguidas sin
  novedad.
- **Avisos** si hay una sola sesión, si faltan fricciones o workarounds en el plan, si un
  sujeto no registra ninguna fricción, si no hay saturación o si ningún código refuta.

El límite, que va escrito en toda salida:

> **Validez externa: nula.** Los sujetos, sus jornadas y sus frases son inventados. La
> saturación indica que las sesiones cubrieron los códigos que tú declaraste, no la realidad de
> un puesto de trabajo. Y hay algo que una observación simulada nunca puede dar: lo que la
> gente hace sin darse cuenta de que lo hace. Eso solo aparece mirando.

## La marca SIMULADO

La propaga el flujo solo (`flujo.simulacion` → distintivo en la cabecera del HTML, caja ámbar
en el contexto, advertencia automática y línea en el pie). Lo que te toca:

1. `base` empieza con `SIMULADO · 3 sesiones ADITL sintéticas (semilla 20260819)`.
2. Los `tags` del item llevan `SIMULADO`.
3. `advertencias` recoge los sujetos, la semilla, el ruido, el estado de la saturación y el
   límite de validez externa.
4. El CSV se declara en `output.archivos_generados` y en `--outputs` al cerrar el paso.
5. **Los tiempos y costos que aparezcan en las notas van marcados `*`:** son inventados para
   el relato, no medidos con cronómetro.

## Contrato JSON (salida)

```json
{
  "skill": "simulador-day-in-the-life",
  "timestamp": "<ISO 8601>",
  "parametros": { "sesiones": 3, "seed": 20260819, "ruido": 0.15, "codigos": 5 },
  "output": {
    "formato": "csv",
    "contenido": "<resumen del bloque que imprimió el script: conteos y saturación>",
    "archivos_generados": ["aditl_observaciones_SIMULADO.csv"]
  },
  "decision": {
    "veredicto": "perseverar",
    "siguiente_paso": "day-in-the-life",
    "razon": "Observaciones sintéticas listas para codificar.",
    "contexto_usado": ["html_1"]
  },
  "advertencias": [
    "DATOS SIMULADOS: 3 sesiones sintéticas, semilla 20260819, ruido 15%. No se observó a nadie.",
    "Sin porcentajes: con n=3 solo se reportan conteos. Validez externa nula.",
    "Los tiempos y costos de las notas son inventados para el relato (*)."
  ]
}
```

## Reglas y Restricciones

1. **Nunca redactes conteos ni porcentajes.** Los conteos los calcula el script; los
   porcentajes no existen en este instrumento.
2. **Un CSV, nada más.** Ni HTML ni `reporte.json` ni cierre de paso.
3. **El nombre del archivo termina en `_SIMULADO.csv`.**
4. **No inventes personas ni lugares reales** como observados. Todo nombre lleva «(ficticio)».
5. **Registra la semilla** en `parametros` y en el resumen del paso.
6. **Cada sujeto necesita al menos una fricción y un workaround** para que la sesión sirva de
   material. Si el script avisa de una jornada plana, ajusta el plan en vez de entregarla.

## Referencias

- Convención de simuladores y propagación de la marca: `sub-skills/SIMULACION.md` (canónica,
  si tienes acceso).
- Enfoque C.R.A.F.T. y esquema de codificación: `../AGENTE.md` de la skill padre.
- Contrato JSON: `sub-skills/CONTRATO_JSON.md` (canónico) o la estructura de arriba, que es
  equivalente y autocontenida.
