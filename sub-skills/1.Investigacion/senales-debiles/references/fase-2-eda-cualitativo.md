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
            "dato": "El tema con mayor carga emocional no es 'alimentación saludable' (foco de la pregunta) sino 'desconexión con la naturaleza' (28 intervenciones vs 12 de alimentación saludable)",
            "contexto": "5 entrevistas, 140 intervenciones analizadas",
            "expectativa_rota": "Esperábamos que el dolor principal estuviera donde la pregunta de investigación lo ubica. El dolor emocional más intenso está en otra parte.",
            "severidad": "Alta",
            "justificacion_severidad": "Cuestiona si la pregunta de investigación está apuntando al problema correcto",
            "sorpresa": "Alta",
            "justificacion_sorpresa": "El equipo asume que la alimentación es el motivador principal. El dato sugiere que la necesidad de reconexión con la tierra es más profunda.",
            "hipotesis_valor": "Si el municipio comunica el huerto como 'espacio de reconexión con la naturaleza' en lugar de 'programa de alimentación saludable', entonces la participación podría aumentar, porque el dolor emocional más intenso del residente está donde nadie está mirando.",
            "validacion_pendiente": "Cuantificar en encuesta: ¿qué es lo que más te atrae de un huerto urbano? (pregunta abierta)",
            "robustez": "4 de 5 entrevistas. Patrón consistente.",
            "escala_a_fase4": true,
            "clasificacion_hipotesis_previa": "confirmacion | señal débil | tension",
            "hipotesis_previa_referenciada": "texto de la hipótesis previa o null",
            "exclusiones": ["Se excluye el párrafo duplicado entre Entrevista_1 y Entrevista_3 por posible error de captura"]
          }
        ],
        "grafica": {
          "tipo": "barras_frecuencia",
          "chartjs": {
            "type": "bar",
            "data": {
              "labels": ["Alimentación saludable", "Desconexión naturaleza", "Falta de comunidad", "Estrés urbano", "Costo de vida"],
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
            "dato": "E03: 'no tengo tiempo para el huerto, trabajo todo el día' [min 8] vs 'los fines de semana me la paso viendo series, no sé ni qué hacer' [min 41]",
            "contexto": "Entrevista E03, 33 minutos de separación, temas distintos",
            "expectativa_rota": "Esperábamos falta de tiempo real. El tiempo existe pero se invierte en pantallas, no en tierra. La barrera no es disponibilidad horaria: es el tipo de actividad que compite.",
            "severidad": "Media",
            "justificacion_severidad": "Redefine el problema: no es falta de tiempo, es competencia con entretenimiento pasivo",
            "sorpresa": "Media",
            "justificacion_sorpresa": "El equipo asumía que la barrera era objetiva (horas libres). La señal sugiere que es subjetiva (cómo se elige invertir el tiempo libre).",
            "hipotesis_valor": "Si el huerto se posiciona como 'actividad recreativa de fin de semana' (no como 'programa de alimentación'), entonces podría competir mejor con el entretenimiento pasivo, porque la barrera no es la cantidad de tiempo sino el tipo de actividad que el residente elige.",
            "validacion_pendiente": "Encuesta: '¿En qué inviertes tu tiempo libre un fin de semana típico?' con opciones que incluyan pantallas, ejercicio, actividades al aire libre.",
            "robustez": "2 de 5 entrevistas muestran esta contradicción explícitamente. Otras 2 la insinúan.",
            "escala_a_fase4": true
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
            "dato": "Metáforas de desconexión en 3 de 5 entrevistas: 'vivo en una caja de cemento', 'no sé ni cómo huele la tierra ya', 'aquí todo es gris, hasta el cielo'",
            "contexto": "Entrevistas E01, E02, E05. Aparecen sin pregunta directa sobre naturaleza o espacios verdes.",
            "expectativa_rota": "Esperábamos que el residente hablara de barreras prácticas (tiempo, distancia). En cambio, emergen metáforas existenciales de desconexión con la naturaleza y el entorno vivo.",
            "severidad": "Crítica",
            "justificacion_severidad": "Revela una dimensión del problema completamente ausente en la pregunta de investigación y en la encuesta",
            "sorpresa": "Alta",
            "justificacion_sorpresa": "Nadie en el equipo había planteado que el dolor del residente urbano fuera existencial (desconexión con la tierra), no práctico",
            "hipotesis_valor": "Si el municipio comunica 'recordá lo que es ensuciarte las manos' en lugar de 'mejorá tu alimentación', entonces la conexión emocional con el residente podría ser más profunda, porque la señal indica que el dolor real no es la dieta sino la pérdida de contacto con lo vivo.",
            "validacion_pendiente": "Entrevistas adicionales con pregunta explícita sobre relación con la naturaleza en la ciudad",
            "robustez": "3 de 5 entrevistas. Las metáforas aparecen espontáneamente, sin inducción del entrevistador.",
            "escala_a_fase4": true
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
            "dato": "Ningún entrevistado menciona 'comunidad' o 'vecinos' espontáneamente al hablar del huerto. Solo aparece cuando el entrevistador lo introduce.",
            "contexto": "5 entrevistas completas. Tema ausente en discurso espontáneo.",
            "expectativa_rota": "Esperábamos que el huerto evocara comunidad y convivencia. El silencio sugiere que el residente lo percibe como una actividad individual, no social.",
            "severidad": "Media",
            "justificacion_severidad": "Afecta la propuesta de valor: si el residente no asocia huerto con comunidad, los mensajes de 'ven a convivir' no resuenan",
            "sorpresa": "Media",
            "justificacion_sorpresa": "El equipo asumía que el componente comunitario era un atractivo natural del huerto. El dato obliga a repensar.",
            "hipotesis_valor": "Si el municipio enfoca el huerto como 'tu espacio personal de siembra' en lugar de 'huerto comunitario', entonces la adopción en residentes nuevos podría aumentar, porque el silencio sugiere que la comunidad no es un atractor inicial sino un posible beneficio secundario.",
            "validacion_pendiente": "Encuesta: '¿Prefieres un espacio de siembra individual o compartido?'",
            "robustez": "5 de 5 entrevistas. Patrón unánime.",
            "escala_a_fase4": true
          }
        ],
        "grafica": null
      },
      {
        "id": "B5",
        "nombre": "Categoría residual",
        "aplica": true,
        "expectativa_base": "Todo fragmento relevante encaja en las categorías identificadas",
        "expectativa_inferida": true,
        "resultado": "SEÑAL DÉBIL",
        "senales": [
          {
            "id": "SD-CUAL-005",
            "tipo": "De categoría residual",
            "dato": "Fragmentos que no encajan en categorías: 'mi abuelo tenía milpa, yo ya ni sé qué es eso' [E04, min 22], 'a veces sueño con irme al campo pero aquí me tocó' [E01, min 45]",
            "contexto": "2 fragmentos en 2 entrevistas distintas. Ambos aparecen al cierre, en tono de nostalgia.",
            "expectativa_rota": "Esperábamos que lo no clasificable fuera ruido. Estos fragmentos revelan una memoria generacional de conexión con la tierra que se está perdiendo.",
            "severidad": "Media",
            "justificacion_severidad": "Abre una categoría nueva ('memoria generacional') que ninguna pregunta del instrumento captura",
            "sorpresa": "Alta",
            "justificacion_sorpresa": "El tono nostálgico sugiere que el residente urbano carga con una pérdida que ni siquiera articula como necesidad",
            "hipotesis_valor": "Si el municipio enmarca el huerto como 'lo que tu abuelo sabía y vos podés recuperar', entonces podría activar una memoria generacional latente que conecta emocionalmente con el residente.",
            "validacion_pendiente": "Entrevistas con pregunta: '¿Alguien en tu familia sembraba o trabajaba la tierra?'",
            "robustez": "2 de 5 entrevistas. Baja frecuencia pero alta intensidad emocional.",
            "escala_a_fase4": true
          }
        ],
        "grafica": null
      }
    ],
    "resumen": {
      "n_bloques_aplicables": 5,
      "n_bloques_ejecutados": 5,
      "n_bloques_no_aplica": 0,
      "n_senales_detectadas": 5,
      "n_expectativas_confirmadas": 0,
      "senales_que_escalan": ["SD-CUAL-001", "SD-CUAL-002", "SD-CUAL-003", "SD-CUAL-004", "SD-CUAL-005"]
    }
  }
}
```

---

## Procedimiento

### Principio: lectura por ventanas, no por corpus

Leer 5 entrevistas de corrido produce atención diluida. En su lugar, cada entrevista se parte en ventanas manejables (~5 minutos de transcripción o ~1,500 palabras por ventana). Cada ventana se procesa de forma independiente y completa —los 5 bloques B1–B5— antes de avanzar a la siguiente. Esto garantiza que cada segmento recibe atención plena y que las señales detectadas en ventanas tempranas no se "contaminan" con lo que aparece después (ni se olvidan).

Al final, una fase de consolidación cruza todas las ventanas de todas las entrevistas para detectar patrones transversales y evolución temporal.

### Paso 1: Particionar

Para cada archivo de transcripción en `fase0_output.json.transcripciones`:

1. Leer el archivo completo.
2. Reportar: N total de líneas, N total de palabras, duración estimada (si el archivo declara timestamp o minuto).
3. Dividir en ventanas de ~1,500 palabras o ~5 minutos de conversación (lo que resulte en segmentos más naturales). Si la transcripción tiene marcas de tiempo, usarlas como límite natural. Si no, dividir por párrafos o bloques de líneas equivalentes.
4. Cada ventana recibe un ID: `{archivo}_W{numero}` (ej. `entrevista1_W1`, `entrevista1_W2`).
5. Si una entrevista tiene ≤1,500 palabras, se procesa como una sola ventana.

### Paso 2: Procesar cada ventana

Para cada ventana, ejecutar los 5 bloques generadores. Cada bloque produce un mini-output que se acumula en una bitácora por ventana.

**Por cada ventana, responder:**

| Bloque | Pregunta guía | Output mínimo |
|---|---|---|
| **B1** | ¿El dolor emocional está donde la pregunta de investigación lo ubica? | Temas con carga emocional detectados en esta ventana, con citas y ubicación. |
| **B2** | ¿Hay contradicciones internas en esta ventana? | Declaraciones inconsistentes detectadas (o "sin contradicciones en esta ventana"). |
| **B3** | ¿El lenguaje figurativo revela algo que el discurso literal no dice? | Metáforas, analogías, imágenes detectadas (o "sin metáforas en esta ventana"). |
| **B4** | ¿Qué temas esperables están ausentes en esta ventana? | Temas que el contexto de la entrevista haría esperar y no aparecen. |
| **B5** | ¿Hay fragmentos que no encajan en B1–B4? | Fragmentos residuales con posible patrón (o "sin residuales en esta ventana"). |

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

1. **Intra-bloque:** para cada bloque (B1–B5), cruzar los hallazgos de todas las ventanas de todas las entrevistas. ¿El mismo patrón aparece en múltiples entrevistas? ¿En las mismas ventanas (mismo momento de la conversación)?
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
      "bloques_procesados": ["B1","B2","B3","B4","B5"],
      "hallazgos": {
        "B1": "Tema dominante: desconfianza en apps financieras (3 intervenciones). Citas: L24, L67, L112.",
        "B2": "Sin contradicciones en esta ventana.",
        "B3": "Metáfora detectada: 'es como si te hablara un robot' (L89).",
        "B4": "No menciona BAZ Negocio espontáneamente. Solo aparece cuando el entrevistador lo nombra (L130).",
        "B5": "Sin residuales."
      }
    }
  ]
}
```

### Bloques generadores B1–B5

| Bloque | Nombre | Pregunta guía |
|---|---|---|
| **B1** | Paisaje emocional | ¿El dolor emocional está donde la pregunta de investigación lo ubica? |
| **B2** | Contradicciones | ¿El discurso es internamente consistente? ¿Hay escisiones reveladoras? |
| **B3** | Metáforas inesperadas | ¿El lenguaje figurativo revela algo que el discurso literal no dice? |
| **B4** | Silencios significativos | ¿Qué temas están ausentes? ¿Esa ausencia es información? |
| **B5** | Categoría residual | ¿Lo que no encaja en ninguna categoría tiene patrón? |

La clasificación contra hipótesis previas es obligatoria en cada ventana y en la consolidación final:
- "confirmacion": la señal refuerza algo que el equipo ya sospechaba.
- "señal débil": la señal revela algo que ninguna hipótesis previa anticipaba.
- "tension": la señal contradice directamente una hipótesis previa del equipo.

### Formato de señal débil cualitativa

```json
{
  "id": "SD-CUAL-001",
  "fuente_origen": ["entrevista1.txt", "entrevista3.txt"],
  "tipo": "De discurso | De tensión | De metáfora | De silencio | De categoría residual",
  "dato": "cita exacta o descripción del hallazgo",
  "contexto": "entrevista ID, momento, pregunta",
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
  "ancla": "hipotesis_usuario | expectativa_inferida"
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
- **Calibración:** `severidad` y `sorpresa` se puntúan contra la rúbrica de SPEC.md § 5, con el campo `ancla` declarado (`hipotesis_usuario` o `expectativa_inferida`). Si el ancla es `expectativa_inferida`, la sorpresa tope es Media.
- **Verificación de citas:** tras consolidar las señales finales, las citas deben verificarse contra el corpus con `scripts/verificar_citas.py` (referenciado en SPEC.md § 13). Cualquier cita `NO_ENCONTRADA` bloquea la escala hasta corregirse; `APROXIMADA` requiere justificación del analista.
- **Contradicción de ausencia (claim vs corpus):** toda señal de silencio ("nadie menciona X", "ningún entrevistado habla de Y") se verifica contra el corpus con `scripts/verificar_citas.py` (chequeo de ausencia). Si el término declarado ausente SÍ aparece en el corpus, la señal se corrige o descarta; no escala con un claim de ausencia falso.
- **Trazabilidad de IDs:** cada señal usa un ID secuencial nuevo (`SD-CUAL-NNN`). Ninguna fase posterior referencia IDs que esta fase no emitió; esta fase tampoco referencia IDs de Fase 1 que no existan.
