---
name: simulador-entrevistas-empatia
description: Simula las respuestas de un panel de entrevistas de empatía 1:1 con entrevistados sintéticos aplicando The Mom Test, y entrega un CSV codificable con muestreo reproducible por semilla, conteos y curva de saturación, todo etiquetado SIMULADO. Usar cuando el usuario tenga la guía de entrevista pero no tenga a quién entrevistar.
category: Descubrimiento
tipo: simulador
padre: 2.Descubrimiento/entrevistas-empatia
---

# Simulador de Entrevistas de Empatía

Fabrica las respuestas que habría dado un panel de entrevistados a la guía de entrevista, y
las entrega en **un CSV** en formato largo listo para codificar. Todo queda etiquetado
**SIMULADO**.

## Alcance

**SÍ hace:** inventar el panel (personas con nombre ficticio, edad, ocupación y actitud),
repartir qué código menciona cada quien según la prevalencia declarada, y escribir el CSV con
la curva de saturación y los conteos calculados.

**NO hace:**

- **No analiza.** No consolida trabajos, dolores y ganancias (Jobs/Pains/Gains) en el entregable final ni concluye: eso es de
  `2.Descubrimiento/entrevistas-empatia`, que codifica el CSV como codificaría transcripciones
  reales.
- **No genera HTML** ni `reporte.json`, y no cierra pasos del flujo.
- **No sustituye una entrevista real** cuando el usuario sí tiene acceso a usuarios. Si los
  tiene, este simulador no interviene: la guía existe para usarla.

## Cuándo se activa

Cuando el usuario decide simular en el **paso 2 del flujo** («Decisión — Entrevistas»), nodo
«¿Ejecución de entrevistas?» → *No — simulación de respuestas e insights*, y luego
«Simular o no» → *Simular respuestas*. Esa decisión enciende la marca de simulación en todo el
proyecto.

Antes de simular, **la skill padre ya tiene que haber diseñado la guía**: el simulador
responde preguntas, no las inventa. Si no hay guía, primero se ejecuta
`entrevistas-empatia` y luego esto.

## El plan

Tú escribes el material cualitativo; **el script hace los números**:

```jsonc
{
  "proyecto": "Huertos urbanos MX",
  "hipotesis": "El costo de mantenimiento es la barrera principal de abandono",
  "seed": 20260819,          // semilla: misma semilla + mismo plan = CSV idéntico
  "ruido": 0.15,             // encoge la prevalencia hacia 0.5 (evita el laboratorio)
  "panel": [                 // 5-8 entrevistados: los inventas tú, uno por uno
    { "nombre": "María (ficticio)", "edad": 34,
      "ocupacion": "Dueña de cafetería", "actitud": "escéptica" },
    { "nombre": "Jorge (ficticio)", "edad": 41,
      "ocupacion": "Ingeniero en casa", "actitud": "entusiasta" }
  ],
  "guia": [                  // las preguntas de la guía que diseñó la skill padre
    { "id": "P1", "pregunta": "Cuéntame la última vez que…" },
    { "id": "P2", "pregunta": "¿Qué fue lo más difícil de sostenerlo?" }
  ],
  "codigos": [
    { "codigo": "COSTO-MANT",
      "tipo": "pain",                    // job | pain | gain
      "texto": "El mantenimiento sale más caro de lo previsto",
      "prevalencia": 0.6,                // DECLARADA: prob. de que un entrevistado lo diga
      "senal": "valida",                 // valida | refuta | neutral (frente a la hipótesis)
      "pregunta_id": "P2",               // en qué pregunta aparece
      "prevalencia_por_actitud": { "escéptica": 0.85, "entusiasta": 0.3 },
      "citas": ["Llevo tres meses y ya gasté el doble de lo que pensaba."] }
  ]
}
```

Reglas del plan:

1. **El panel lo escribes tú, persona por persona.** Son 5-8: no hay nada que sortear ahí, y
   una lista de personas creíbles es justo el material que hace útil la simulación. Diversidad
   real (edad, contexto, actitud), no arquetipos planos.
2. **`prevalencia` es un supuesto declarado, no un dato.** Es la probabilidad de que un
   entrevistado mencione ese código. El script sortea con ella e imprime lo declarado junto a
   lo obtenido, para que se pueda contrastar.
3. **`prevalencia_por_actitud`** es lo que hace que el panel no responda al unísono: la
   escéptica habla más del costo, el entusiasta menos.
4. **Al menos un código con `senal: refuta`.** El script avisa si no hay ninguno: una
   simulación que solo confirma la hipótesis no es una prueba, es un espejo.
5. **`citas` son frases literales**, cortas y con sustancia: es lo que se cita en el reporte.
   El script las reparte; no las invente el reporte después.
6. **5-8 entrevistados.** Con menos de 5 no hay saturación posible; con muchos más, el
   instrumento correcto es una encuesta (y entonces toca `discovery-survey`).

## Ejecución

Desde la raíz del repositorio:

```bash
python sub-skills/2.Descubrimiento/entrevistas-empatia/simulador/scripts/simular_entrevistas.py \
    plan.json -o entrevistas_SIMULADO.csv
```

Parámetros sobrescribibles: `--seed`, `--ruido`. El tamaño del panel no es un parámetro: sale
de la lista `panel`.

## Qué produce

**Un CSV** (`entrevistas_SIMULADO.csv`), una fila por entrevistado × pregunta × código
mencionado. Los pares entrevistado-pregunta sin ningún código **también dejan fila** (con
`codigo` vacío): así el denominador está en el archivo y no hay que suponerlo.

| Columna | Contenido |
| --- | --- |
| `entrevistado_id` | `E01`, `E02`, … (el orden es el del panel) |
| `nombre`, `edad`, `ocupacion`, `actitud` | La persona sintética |
| `pregunta_id`, `pregunta` | La pregunta de la guía |
| `respuesta` | La cita repartida por el script |
| `codigo`, `tipo` | Código y Job/Pain/Gain (vacíos si no hubo mención) |
| `senal` | `valida` / `refuta` / `neutral` |
| `simulado` | `si` en todas las filas |
| `seed` | La semilla, para que el archivo sea auditable por sí solo |

Además **imprime en pantalla** (no genera archivo): conteos por código, **curva de
saturación**, reparto de señales, ficha del panel y avisos. Ese bloque es lo que se cita en el
reporte de la skill padre: **no lo reescribas de memoria.**

## Supuestos estadísticos y sus límites

**Aquí no hay porcentajes, y es a propósito.** Con 6 entrevistas el margen de error de una
proporción es de ±40 puntos: cualquier «67% de los usuarios» sería teatro. Una muestra
cualitativa se justifica por **saturación de códigos** —se entrevista hasta que dejan de
aparecer códigos nuevos— y se reporta con conteos: «4 de 6», nunca «66%».

Lo que el script garantiza:

- **Reproducibilidad:** semilla explícita; misma semilla + mismo plan = CSV idéntico.
- **Muestreo declarado:** cada mención es un ensayo Bernoulli con la prevalencia del plan
  (modulada por actitud), encogida hacia 0.5 según el `ruido`.
- **Conteos derivados:** el recuento real de las filas del CSV, nunca una cifra redactada.
- **Curva de saturación:** códigos nuevos por entrevista y en cuál dejó de aparecer nada
  nuevo. Saturación = 2 entrevistas seguidas sin novedad.
- **Avisos** si el panel es corto, si no hay saturación, si un código no apareció o si ningún
  código refuta.

El límite, que va escrito en toda salida:

> **Validez externa: nula.** Las personas, sus respuestas y sus citas son inventadas. La
> saturación indica que el panel cubrió los códigos que tú declaraste, no que haya cubierto la
> realidad. No hay hallazgo aquí: hay un ensayo del instrumento y de cómo se leerían los
> resultados.

## La marca SIMULADO

La propaga el flujo solo (`flujo.simulacion` → distintivo en la cabecera del HTML, caja ámbar
en el contexto, advertencia automática y línea en el pie). Lo que te toca:

1. `base` empieza con `SIMULADO · 6 entrevistas sintéticas (semilla 20260819)`.
2. Los `tags` del item llevan `SIMULADO`.
3. `advertencias` recoge el panel, la semilla, el ruido, el estado de la saturación y el límite
   de validez externa.
4. El CSV se declara en `output.archivos_generados` y en `--outputs` al cerrar el paso.
5. **Si esta evidencia alimenta la ficha de persona** (paso 4), esa ficha nace simulada: sus
   problemas llevan la marca y el reporte lo dice, no se disimula por venir de un paso anterior.

## Contrato JSON (salida)

```json
{
  "skill": "simulador-entrevistas-empatia",
  "timestamp": "<ISO 8601>",
  "parametros": { "panel": 6, "seed": 20260819, "ruido": 0.15, "codigos": 5 },
  "output": {
    "formato": "csv",
    "contenido": "<resumen del bloque que imprimió el script: conteos y saturación>",
    "archivos_generados": ["entrevistas_SIMULADO.csv"]
  },
  "decision": {
    "veredicto": "perseverar",
    "siguiente_paso": "entrevistas-empatia",
    "razon": "Respuestas sintéticas listas para codificar; saturación alcanzada en la 2.ª entrevista.",
    "contexto_usado": ["html_1"]
  },
  "advertencias": [
    "DATOS SIMULADOS: 6 entrevistados sintéticos, semilla 20260819, ruido 15%. Ninguna persona real fue entrevistada.",
    "Sin porcentajes: con n=6 solo se reportan conteos. Validez externa nula."
  ]
}
```

## Reglas y Restricciones

1. **Nunca redactes conteos ni porcentajes.** Los conteos los calcula el script; los
   porcentajes no existen en este instrumento.
2. **Un CSV, nada más.** Ni HTML ni `reporte.json` ni cierre de paso.
3. **El nombre del archivo termina en `_SIMULADO.csv`.**
4. **No inventes personas reales ni marcas como participantes.** Todo nombre lleva
   «(ficticio)».
5. **Registra la semilla** en `parametros` y en el resumen del paso.
6. **The Mom Test también aplica a las citas:** que hablen de conducta pasada («la última vez
   que…», «hoy uso…»), no de intenciones futuras ni de cumplidos. Una cita simulada que dice
   «me encantaría» no vale nada, igual que en una entrevista real.

## Referencias

- Convención de simuladores y propagación de la marca: `sub-skills/SIMULACION.md` (canónica,
  si tienes acceso).
- Guía de entrevista y plantilla de codificación: `../AGENTE.md` de la skill padre.
- Contrato JSON: `sub-skills/CONTRATO_JSON.md` (canónico) o la estructura de arriba, que es
  equivalente y autocontenida.
