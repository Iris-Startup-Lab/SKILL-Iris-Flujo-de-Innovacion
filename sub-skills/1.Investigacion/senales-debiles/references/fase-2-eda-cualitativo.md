# Fase 2: EDA Cualitativo

## Propósito

Detectar señales débiles en los datos textuales buscando activamente rupturas de expectativas, contradicciones internas, metáforas inesperadas, silencios significativos y patrones en lo que no encaja.

## Input

`fase0_output.json` con:
- `transcripciones`: array de paths a archivos TXT
- `pregunta_investigacion`
- `advertencias`

## Output

`fase2_output.json`. Único archivo de salida.

Nota: `hipotesis_previas` no se repite en este archivo; se hereda de `fase0_output.json` (ver contrato en AGENTE.md). Los cambios de estado de una hipótesis se declaran en `advertencias`.

```json
{
  "fase": "fase-2-eda-cualitativo",
  "timestamp": "2026-01-01T00:00:00",
  "pregunta_investigacion": "texto exacto",
  "advertencias": [],
  "redundancia": [
    {
      "aplicada": true,
      "senal_id": "SD-CUAL-001",
      "resultado": "escala | absorbida",
      "absorbida_por": null,
      "razon": "mecanismo independiente"
    }
  ],
  "datos": {
    "bloques": [
      {
        "id": "B1",
        "nombre": "Paisaje emocional",
        "aplica": true,
        "expectativa_base": "Los temas centrales de la pregunta de investigación concentran la mayor carga emocional",
        "expectativa_inferida": true,
        "resultado": "CONTRADICCIÓN",
        "senales": [
          {
            "id": "SD-CUAL-001",
            "fuente_origen": ["entrevista1.txt", "entrevista3.txt"],
            "tipo": "De discurso",
            "dato": "El tema con mayor carga emocional no es 'falta de certificación' (foco de la pregunta) sino 'miedo a no ser suficiente' (28 intervenciones vs 12 en certificación)",
            "contexto": "5 entrevistas, 140 intervenciones analizadas",
            "poblacion": "entrevistas",
            "n": 4,
            "expectativa_rota": "Esperábamos que el dolor principal estuviera donde la pregunta de investigación lo ubica. El dolor emocional más intenso está en otra parte.",
            "severidad": "Alta",
            "justificacion_severidad": "Cuestiona si la pregunta de investigación está apuntando al problema correcto",
            "sorpresa": "Media",
            "justificacion_sorpresa": "El equipo asume que la falta de certificación es el motivador principal. El dato sugiere que la falta de confianza pesa más. La expectativa es inferida por el agente (bloque con `expectativa_inferida: true`), por lo que la sorpresa tope es Media.",
            "hipotesis_valor": "Si el programa prioriza acompañamiento y orientación individual (no solo más cursos), entonces la inscripción podría crecer, porque el dolor emocional más intenso del residente está donde nadie está mirando.",
            "validacion_pendiente": "Cuantificar en encuesta: ¿qué es lo que más te frena para inscribirte? (pregunta abierta)",
            "robustez": "4 de 5 entrevistas. Patrón consistente.",
            "escala_a_fase4": true,
            "clasificacion_hipotesis_previa": "señal débil",
            "hipotesis_previa_referenciada": null,
            "ancla": "expectativa_inferida",
            "exclusiones": ["Se excluye el párrafo duplicado entre Entrevista_1 y Entrevista_3 por posible error de captura"]
          }
        ],
        "grafica": {
          "tipo": "barras_frecuencia",
          "chartjs": {
            "type": "bar",
            "data": {
              "labels": ["Inscripción y papeles", "Miedo a no ser suficiente", "Vergüenza por falta de estudios", "Falta de tiempo", "Costo del traslado"],
              "datasets": [
                { "label": "Menciones del tema", "data": [12, 28, 8, 15, 6], "backgroundColor": "#3498db" }
              ]
            },
            "options": { "indexAxis": "y", "scales": { "x": { "title": { "text": "Número de intervenciones" } } } }
          },
          "descripcion": "Barras horizontales: frecuencia de menciones por tema en el corpus cualitativo"
        }
      },
      {
        "id": "B2",
        "nombre": "Contradicciones intra-entrevista",
        "aplica": true,
        "expectativa_base": "El discurso del entrevistado es internamente consistente",
        "expectativa_inferida": true,
        "resultado": "SEÑAL DÉBIL",
        "senales": [
          {
            "id": "SD-CUAL-002",
            "tipo": "De tensión",
            "dato": "E03: 'no tengo tiempo para el taller, trabajo todo el día' [min 8] vs 'los fines de semana me la paso viendo series, no sé ni qué hacer' [min 41]",
            "contexto": "Entrevista E03, 33 minutos de separación, temas distintos",
            "expectativa_rota": "Esperábamos falta de tiempo real. El tiempo existe pero se invierte en pantallas, no en capacitación. La barrera no es disponibilidad horaria: es el tipo de actividad que compite.",
            "severidad": "Media",
            "justificacion_severidad": "Redefine el problema: no es falta de tiempo, es competencia con entretenimiento pasivo",
            "sorpresa": "Media",
            "justificacion_sorpresa": "El equipo asumía que la barrera era objetiva (horas libres). La señal sugiere que es subjetiva (cómo se elige invertir el tiempo libre).",
            "hipotesis_valor": "Si los talleres se posicionan como 'formación flexible de fin de semana' (no como curso con horario fijo), entonces podrían competir mejor con el entretenimiento pasivo, porque la barrera no es la cantidad de tiempo sino el tipo de actividad que el participante elige.",
            "validacion_pendiente": "Encuesta: '¿En qué inviertes tu tiempo libre un fin de semana típico?' con opciones que incluyan pantallas, ejercicio, actividades de formación.",
            "robustez": "2 de 5 entrevistas muestran esta contradicción explícitamente. Otras 2 la insinúan.",
            "escala_a_fase4": true,
            "clasificacion_hipotesis_previa": "señal débil",
            "hipotesis_previa_referenciada": null,
            "ancla": "expectativa_inferida"
          }
        ],
        "grafica": null
      },
      {
        "id": "B3",
        "nombre": "Metáforas inesperadas",
        "aplica": true,
        "expectativa_base": "El lenguaje del entrevistado es literal y descriptivo",
        "expectativa_inferida": true,
        "resultado": "SEÑAL DÉBIL",
        "senales": [
          {
            "id": "SD-CUAL-003",
            "tipo": "De metáfora",
            "dato": "Metáforas de autoexclusión en 3 de 5 entrevistas: 'los puestos no son para gente como yo', 'siempre me toca la fila de la noche', 'aunque tenga el papel, no me van a dar entrada'",
            "contexto": "Entrevistas E01, E02, E05. Aparecen sin pregunta directa sobre discriminación o empleo.",
            "expectativa_rota": "Esperábamos que el participante hablara de barreras prácticas (tiempo, distancia, requisitos). En cambio, emergen metáforas de autoexclusión respecto del mundo laboral.",
            "severidad": "Crítica",
            "justificacion_severidad": "Revela una dimensión del problema completamente ausente en la pregunta de investigación y en la encuesta",
            "sorpresa": "Media",
            "justificacion_sorpresa": "Nadie en el equipo había planteado que el dolor del participante fuera de confianza (creer que el empleo no es para él), no de oferta. La expectativa es inferida por el agente (bloque con `expectativa_inferida: true`), por lo que la sorpresa tope es Media.",
            "hipotesis_valor": "Si el programa comunica 'mirá cómo gente como vos consiguió trabajo' en lugar de 'inscribite a un curso', entonces la conexión emocional con el participante podría ser más profunda, porque la señal indica que el dolor real no es la falta de cursos sino la pérdida de confianza en sí mismo.",
            "validacion_pendiente": "Entrevistas adicionales con pregunta explícita sobre confianza y experiencias previas de búsqueda de empleo",
            "robustez": "3 de 5 entrevistas. Las metáforas aparecen espontáneamente, sin inducción del entrevistador.",
            "escala_a_fase4": true,
            "clasificacion_hipotesis_previa": "señal débil",
            "hipotesis_previa_referenciada": null,
            "ancla": "expectativa_inferida"
          }
        ],
        "grafica": null
      },
      {
        "id": "B4",
        "nombre": "Silencios significativos",
        "aplica": true,
        "expectativa_base": "Los temas ausentes en el discurso son irrelevantes para el entrevistado",
        "expectativa_inferida": true,
        "resultado": "SEÑAL DÉBIL",
        "senales": [
          {
            "id": "SD-CUAL-004",
            "tipo": "De silencio",
            "dato": "Ningún participante menciona 'oficina de empleo' ni 'intermediación laboral' espontáneamente al hablar de los talleres. Solo aparecen cuando el entrevistador lo introduce.",
            "contexto": "5 entrevistas completas. Tema ausente en discurso espontáneo.",
            "expectativa_rota": "Esperábamos que los talleres remitieran a la bolsa de empleo como su atractivo natural. El silencio sugiere que el participante no percibe conexión entre el curso y el conseguir trabajo.",
            "severidad": "Media",
            "justificacion_severidad": "Afecta la propuesta de valor: si el participante no asocia taller con empleo, los mensajes de 'formación que consigue trabajo' no resuenan",
            "sorpresa": "Media",
            "justificacion_sorpresa": "El equipo asumía que la empleabilidad era el atractivo natural del taller. El dato obliga a repensar.",
            "hipotesis_valor": "Si el programa enlaza explícitamente cada taller con una práctica o vacante real, en lugar de presentarse como 'curso de formación', entonces la inscripción de nuevos participantes podría aumentar, porque el silencio sugiere que la empleabilidad no es un atractor inicial sino un posible beneficio secundario.",
            "validacion_pendiente": "Encuesta: '¿Qué esperas del taller: el certificado, la práctica o el contacto con empleadores?'",
            "robustez": "5 de 5 entrevistas. Patrón unánime.",
            "escala_a_fase4": true,
            "clasificacion_hipotesis_previa": "señal débil",
            "hipotesis_previa_referenciada": null,
            "ancla": "expectativa_inferida"
          }
        ],
        "grafica": null
      },
      {
        "id": "B5",
        "nombre": "Usos no esperados",
        "aplica": true,
        "expectativa_base": "El producto/servicio se usa para lo que fue diseñado, y el problema se resuelve por la vía oficial",
        "expectativa_inferida": true,
        "resultado": "SEÑAL DÉBIL",
        "senales": [
          {
            "id": "SD-CUAL-005",
            "tipo": "De uso no esperado",
            "dato": "'Uso el campo de comentarios del sistema como lista de pendientes, porque no hay dónde más anotarlas' [E02, min 18]",
            "contexto": "Entrevista E02. El usuario describe un uso del producto distinto al previsto.",
            "expectativa_rota": "Esperábamos que el sistema se usara para notas de cliente. El usuario lo usa como gestor de tareas personal.",
            "severidad": "Media",
            "justificacion_severidad": "Revela una necesidad latente (gestión de tareas) que el producto no cubre",
            "sorpresa": "Media",
            "justificacion_sorpresa": "El uso previsto se infiere del contexto (ancla `expectativa_inferida`), por lo que la sorpresa tope es Media.",
            "hipotesis_valor": "Si el producto incorpora una vista de tareas, entonces retendría a usuarios que hoy parchean esa necesidad con un campo de notas, porque el workaround revela una función ausente.",
            "validacion_pendiente": "Cuantificar cuántos usuarios usan campos de texto como listas de tareas",
            "robustez": "2 de 5 entrevistas muestran workarounds similares.",
            "escala_a_fase4": true,
            "clasificacion_hipotesis_previa": "señal débil",
            "hipotesis_previa_referenciada": null,
            "ancla": "expectativa_inferida"
          }
        ],
        "grafica": null
      },
      {
        "id": "B6",
        "nombre": "Categoría residual",
        "aplica": true,
        "expectativa_base": "Todo fragmento relevante encaja en las categorías identificadas",
        "expectativa_inferida": true,
        "resultado": "SEÑAL DÉBIL",
        "senales": [
          {
            "id": "SD-CUAL-006",
            "tipo": "De categoría residual",
            "dato": "Fragmentos que no encajan en categorías: 'mi mamá no terminó la primaria y yo tampoco' [E04, min 22], 'mi abuelo era albañil y no quiero ser como él, pero no sé qué más' [E01, min 45]",
            "contexto": "2 fragmentos en 2 entrevistas distintas. Ambos aparecen al cierre, en tono de nostalgia.",
            "expectativa_rota": "Esperábamos que lo no clasificable fuera ruido. Estos fragmentos revelan una memoria generacional de precariedad que se intenta cortar sin saber cómo.",
            "severidad": "Media",
            "justificacion_severidad": "Abre una categoría nueva ('memoria generacional de precariedad') que ninguna pregunta del instrumento captura",
            "sorpresa": "Media",
            "justificacion_sorpresa": "El tono nostálgico sugiere que el participante carga con una herencia que ni siquiera articula como necesidad. La expectativa es inferida por el agente (bloque con `expectativa_inferida: true`), por lo que la sorpresa tope es Media.",
            "hipotesis_valor": "Si el programa enmarca la formación como 'romper la herencia que te dejó tu casa' en lugar de 'mejorá tu currículum', entonces podría activar una memoria generacional latente que conecta emocionalmente con el participante.",
            "validacion_pendiente": "Entrevistas con pregunta: '¿Alguien en tu familia cercana pudo estudiar o logró un empleo formal?'",
            "robustez": "2 de 5 entrevistas. Baja frecuencia pero alta intensidad emocional.",
            "escala_a_fase4": true,
            "clasificacion_hipotesis_previa": "señal débil",
            "hipotesis_previa_referenciada": null,
            "ancla": "expectativa_inferida"
          }
        ],
        "grafica": null
      }
    ],
    "resumen": {
      "n_bloques_aplicables": 6,
      "n_bloques_ejecutados": 6,
      "n_bloques_no_aplica": 0,
      "n_senales_detectadas": 6,
      "n_expectativas_confirmadas": 0,
      "senales_que_escalan": ["SD-CUAL-001", "SD-CUAL-002", "SD-CUAL-003", "SD-CUAL-004", "SD-CUAL-005", "SD-CUAL-006"]
    }
  }
}
```

---

## Procedimiento

### Principio: lectura por ventanas, no por corpus

Leer 5 entrevistas de corrido produce atención diluida. En su lugar, cada entrevista se parte en ventanas manejables (~5 minutos de transcripción o ~1,500 palabras por ventana). Cada ventana se procesa de forma independiente y completa —los 6 bloques B1–B6— antes de avanzar a la siguiente. Esto garantiza que cada segmento recibe atención plena y que las señales detectadas en ventanas tempranas no se "contaminan" con lo que aparece después (ni se olvidan).

Al final, una fase de consolidación cruza todas las ventanas de todas las entrevistas para detectar patrones transversales y evolución temporal.

### Mecánica de lectura eficiente (1-2 accesos por transcripción)

**Restricción de presupuesto**: cada transcripción se lee en el menor número de accesos posible.
- Si la transcripción cabe en la ventana de la herramienta (p. ej. ≤2000 líneas), se lee **una sola vez** completa.
- Si excede la ventana, se leen **2-3 rangos de líneas** contiguos que cubran el archivo entero (p. ej. `offset=1 limit=2000`, `offset=2001 limit=2000`, etc.).
- **Prohibido** leer el mismo archivo más veces de las estrictamente necesarias o releer porciones ya leídas.
- La bitácora de ventanas (Paso 1–5) se **computa internamente** sobre el texto ya leído; no se re-lee el corpus para generar la bitácora.
- Para obtener el índice de rangos/líneas se puede usar `scripts/normalizar_transcripciones.py` (que ya serializa y reporta líneas/palabras) en lugar de leer a mano.
- Estimación de presupuesto de turno: si las lecturas pendientes superan el límite de herramientas del turno (~20), cortar al cierre de Fase 2 y continuar en el siguiente turno reanudando desde el último JSON emitido (handoff).

### Paso 1: Particionar

Para cada archivo de transcripción en `fase0_output.json.transcripciones`:

1. Leer el archivo completo.
2. Reportar: N total de líneas, N total de palabras, duración estimada (si el archivo declara timestamp o minuto).
3. Dividir en ventanas de ~1,500 palabras o ~5 minutos de conversación (lo que resulte en segmentos más naturales). Si la transcripción tiene marcas de tiempo, usarlas como límite natural. Si no, dividir por párrafos o bloques de líneas equivalentes.
4. Cada ventana recibe un ID: `{archivo}_W{numero}` (ej. `entrevista1_W1`, `entrevista1_W2`).
5. Si una entrevista tiene ≤1,500 palabras, se procesa como una sola ventana.

### Paso 2: Procesar cada ventana

Para cada ventana, ejecutar los 6 bloques generadores. Cada bloque produce un mini-output que se acumula en una bitácora por ventana.

**Por cada ventana, responder:**

| Bloque | Pregunta guía | Output mínimo |
|---|---|---|
| **B1** | ¿El dolor emocional está donde la pregunta de investigación lo ubica? | Temas con carga emocional detectados en esta ventana, con citas y ubicación. |
| **B2** | ¿Hay contradicciones internas en esta ventana? | Declaraciones inconsistentes detectadas (o "sin contradicciones en esta ventana"). |
| **B3** | ¿El lenguaje figurativo revela algo que el discurso literal no dice? | Metáforas, analogías, imágenes detectadas (o "sin metáforas en esta ventana"). |
| **B4** | ¿Qué temas esperables están ausentes en esta ventana? | Temas que el contexto de la entrevista haría esperar y no aparecen. |
| **B5** | ¿El usuario usa el producto/servicio —o resuelve el problema— de una forma distinta a la prevista? | Usos no esperados o workarounds detectados, con cita y la necesidad latente que revelan (o "sin usos no esperados en esta ventana"). |
| **B6** | ¿Hay fragmentos que no encajan en B1–B5? | Fragmentos residuales con posible patrón (o "sin residuales en esta ventana"). |

Cada output de ventana debe incluir:
- ID de ventana
- Rango de líneas o timestamps procesados
- Citas textuales con ubicación exacta (archivo + línea o minuto)
- Clasificación preliminar contra hipótesis previas

### Paso 3: Análisis temporal intra-entrevista

Al terminar todas las ventanas de una misma entrevista, antes de pasar a la siguiente:

1. Ordenar las ventanas cronológicamente (W1 → W2 → ... → Wn).
2. Detectar evolución: ¿un tema aparece solo al inicio, solo al final, o se sostiene? ¿Hay un punto de quiebre donde el discurso cambia? ¿El entrevistado se contradice entre ventanas tempranas y tardías?
3. Registrar hallazgos temporales como señales potenciales. Ejemplo: "El tema X domina W1–W3 pero desaparece en W4–W5, reemplazado por Y" → posible señal de que el entrevistador indujo el cambio o que el tema real emergió tarde.

### Paso 4: Consolidación transversal

Al terminar todas las entrevistas:

1. **Intra-bloque:** para cada bloque (B1–B6), cruzar los hallazgos de todas las ventanas de todas las entrevistas. ¿El mismo patrón aparece en múltiples entrevistas? ¿En las mismas ventanas (mismo momento de la conversación)?
2. **Inter-bloque:** ¿hallazgos de B1 se refuerzan o contradicen con hallazgos de B3? ¿Un silencio en B4 explica una contradicción en B2?
3. **Frecuencia y robustez:** contar en cuántas entrevistas y cuántas ventanas aparece cada patrón. Un patrón en 1 ventana de 1 entrevista no escala. Un patrón en múltiples ventanas de múltiples entrevistas sí.
4. **Evolución temporal como señal:** si un patrón aparece consistentemente en ventanas tardías (últimos ~10 min de cada entrevista) pero no en las tempranas, eso es en sí mismo una señal: el tema requiere confianza para emerger.

### Paso 5: Redactar señales finales

Solo después de completar los pasos 1–4 para todas las entrevistas, redactar las señales que escalan a Fase 4. Cada señal debe referenciar:
- En qué ventanas y entrevistas se detectó
- Si mostró evolución temporal
- Citas representativas con ubicación exacta

### Formato de bitácora por ventana (obligatorio)

Cada ventana procesada debe dejar registro en el JSON de salida. Esto permite auditar que todas las ventanas fueron efectivamente procesadas:

```json
{
  "bitacora_ventanas": [
    {
      "ventana_id": "entrevista1_W1",
      "archivo": "entrevista1.txt",
      "rango": "L1–L142 (min 0:00–5:12)",
      "n_palabras": 1480,
      "bloques_procesados": ["B1","B2","B3","B4","B5","B6"],
      "hallazgos": {
        "B1": "Tema dominante: falta de tiempo para asistir a los talleres (3 intervenciones). Citas: L24, L67, L112.",
        "B2": "Sin contradicciones en esta ventana.",
        "B3": "Metáfora detectada: 'los puestos no son para gente como yo' (L89).",
        "B4": "No menciona 'bolsa de empleo' ni 'intermediación' espontáneamente. Solo aparecen cuando el entrevistador los nombra (L130).",
        "B5": "Sin usos no esperados.",
        "B6": "Sin residuales."
      }
    }
  ]
}
```

### Bloques generadores B1–B6

| Bloque | Nombre | Pregunta guía |
|---|---|---|
| **B1** | Paisaje emocional | ¿El dolor emocional está donde la pregunta de investigación lo ubica? |
| **B2** | Contradicciones | ¿El discurso es internamente consistente? ¿Hay escisiones reveladoras? |
| **B3** | Metáforas inesperadas | ¿El lenguaje figurativo revela algo que el discurso literal no dice? |
| **B4** | Silencios significativos | ¿Qué temas están ausentes? ¿Esa ausencia es información? |
| **B5** | Usos no esperados | ¿El usuario usa el producto/servicio —o resuelve el problema— de una forma distinta a la prevista? ¿Qué necesidad real está cubriendo ese desvío? |
| **B6** | Categoría residual | ¿Lo que no encaja en ninguna categoría tiene patrón? |

La clasificación contra hipótesis previas es obligatoria en cada ventana y en la consolidación final:
- "confirmacion": la señal refuerza algo que el equipo ya sospechaba.
- "señal débil": la señal revela algo que ninguna hipótesis previa anticipaba.
- "tension": la señal contradice directamente una hipótesis previa del equipo.

### Formato de señal débil cualitativa

```json
{
  "id": "SD-CUAL-001",
  "fuente_origen": ["entrevista1.txt", "entrevista3.txt"],
  "tipo": "De discurso | De tensión | De metáfora | De silencio | De uso no esperado | De categoría residual",
  "dato": "cita exacta o descripción del hallazgo",
  "contexto": "entrevista ID, momento, pregunta",
  "poblacion": "entrevistas",
  "n": "N de entrevistas que sostienen el patrón (int > 0, tomado de robustez)",
  "expectativa_rota": "Esperábamos X, observamos Y",
  "severidad": "Baja | Media | Alta | Crítica",
  "justificacion_severidad": "por qué, según implicación estratégica",
  "sorpresa": "Baja | Media | Alta",
  "justificacion_sorpresa": "por qué, según distancia a premisas del equipo",
  "hipotesis_valor": "Si [cambio], entonces [resultado], porque [mecanismo].",
  "validacion_pendiente": "qué medir para confirmar o descartar",
  "robustez": "N de entrevistas que la sostienen. ¿Patrón o caso único?",
  "exclusiones": ["Se excluye el párrafo duplicado entre Entrevista_1 y Entrevista_3 por posible error de captura"],
  "escala_a_fase4": true,
  "clasificacion_hipotesis_previa": "confirmacion | señal débil | tension",
  "hipotesis_previa_referenciada": "texto de la hipótesis previa o null",
  "ancla": "hipotesis_usuario | expectativa_inferida",
  "mecanismo_nuevo": null
}
```

---

## Reglas

- No toques el CSV. Esta fase es cualitativa pura.
- No reportes problemas del instrumento (mala pregunta, entrevistador sesgado, transcripción defectuosa) como señales débiles.
- Nunca inventes una cita. Si no tienes texto literal: `[cita no disponible]`.
- Toda cita debe incluir ubicación verificable (archivo + minuto/línea) o `[no localizable]`.
- No uses NLP para análisis de sentimientos. Este no es un output de NLP. Las emociones se infieren del contenido del discurso, no de scores numéricos.
- Los IDs usan prefijo `SD-CUAL-`. En el reporte final se simplificarán a "Señal Débil N".
- **Calibración:** `severidad` y `sorpresa` se puntúan contra la rúbrica de SPEC.md sección 5, con el campo `ancla` declarado (`hipotesis_usuario` o `expectativa_inferida`). Si el ancla es `expectativa_inferida`, la sorpresa tope es Media.
- **Regla de cierre (reclasificación auditable):** si la señal se clasifica "señal débil" con ancla `hipotesis_usuario` (toca hipótesis previas del usuario), declara `mecanismo_nuevo` (string no vacío) con el mecanismo causal nuevo e independiente que la separa de `confirmacion`/`tension`. Sin él, la señal queda `confirmacion`/`tension` y no escala; `scripts/validar_esquema.py` lo exige (AGENTE.md regla 13).
- **Pre-registro (sin carta blanca para `expectativa_inferida`):** la expectativa contra la que se puntúa la señal debe estar declarada en el pre-registro de Fase 0 (`pre_registro.expectativas_*`) o derivarse de `expectativa_base` del bloque. `expectativa_rota` formula "esperábamos X, observamos Y" contra esa expectativa. Si la expectativa no está en el pre-registro ni en `expectativa_base`, se declara el motivo de la inferencia en `expectativa_rota` y la sorpresa queda tope Media. Se prohíbe inventar la expectativa a posteriori para justificar una sorpresa Alta (SPEC sección 5).
- **Verificación de citas:** tras consolidar las señales finales, las citas deben verificarse contra el corpus con `scripts/verificar_citas.py` (referenciado en SPEC.md sección 13). Cualquier cita `NO_ENCONTRADA` bloquea la escala hasta corregirse; `APROXIMADA` requiere justificación del analista. Las citas truncadas con `...` se toleran como `ENCONTRADA_TRUNCADA` (no bloquea); con `--exacto` se desactiva la tolerancia.
- **Paráfrasis fiel (verificación anclada):** si la cita no es verbatim, `verificar_citas.py` intenta validarla como paráfrasis contra la **ventana declarada** (archivo + líneas ±2). Cobertura léxica ≥ 0.6 con números presentes → `PARAFRASIS_VALIDADA` (auto, pasa). Banda 0.35–0.6 → `PARAFRASIS_APROXIMADA` (ADV). Cobertura < 0.35 o número faltante → `PARAFRASIS_NO_SOPORTADA` (bloquea). **La cobertura no prueba fidelidad semántica** (una paráfrasis fiel puede tener cobertura baja y una vaga alta): por eso las bandas media/baja nunca se auto-aprueban.
  **El juez por defecto es el propio agente (LLM):** en el cierre de Fase 3, el agente ejecuta `verificar_citas`, lee las ventanas que el script imprime, y resuelve cada cita `APROXIMADA`/`NO_SOPORTADA` como juez: si la ventana la respalda → registra el veredicto en `juicio.json` (para pasarlo al gate con `--juicio`); si no → corrige la cita a verbatim o ajusta la ubicación antes de Fase 4. La confirmación humana queda opcional, para equipos que quieran revisión.
- **Formato de citas inline (contrato con `verificar_citas.py`):** las citas en prosa de `dato`, `contexto`, `sintesis` y `bitacora_ventanas` deben usar uno de estos formatos exactos para que el script las audite (regex estricto, no parseo difuso de lenguaje natural):
  - **Ubicación antes de la cita (canónico):** `E<ID>/L<ini>[-L<fin>]: '<texto>'` — ej. `E4/L256-292: 'al rato me asaltan'`. La comilla simple recta (`'`) solo se admite como delimitador cuando va inmediatamente precedida por el ancla de ubicación.
  - **Ubicación después de la cita:** `'<texto>' (E<ID>/L<ini>[-L<fin>])`, `'<texto>' [L<ini>[-L<fin>]]` o `'<texto>' [min <n>]`.
  - Las comillas pueden ser dobles rectas (`"`), dobles tipográficas (`“ ”`) o simples tipográficas (`‘ ’`). Se prohíbe citar sin ancla de ubicación; si no hay ubicación verificable se escribe `[no localizable]` y el script la reporta como `NO_ENCONTRADA`.
- **Contradicción de ausencia (claim vs corpus):** toda señal de silencio ("nadie menciona X", "ningún entrevistado habla de Y") se verifica contra el corpus con `scripts/verificar_citas.py` (chequeo de ausencia). Si el término declarado ausente SÍ aparece en el corpus, la señal se corrige o descarta; no escala con un claim de ausencia falso.
- **Trazabilidad de IDs:** cada señal usa un ID secuencial nuevo (`SD-CUAL-NNN`). Ninguna fase posterior referencia IDs que esta fase no emitió; esta fase tampoco referencia IDs de Fase 1 que no existan.
- **`poblacion` y `n` por señal (obligatorios):** declara `poblacion: "entrevistas"` y `n` = número de entrevistas que sostienen el patrón (el mismo de `robustez`, p. ej. `"4 de 5 entrevistas"` → `n: 4`). Para una convergencia transpoblacional el piso cuali es `n >= 2` entrevistas — NO un N de registros: una muestra cualitativa es pequeña por diseño y exigirle 30 registros prohibiría toda convergencia sostenida en entrevistas (SPEC.md sección 5).
