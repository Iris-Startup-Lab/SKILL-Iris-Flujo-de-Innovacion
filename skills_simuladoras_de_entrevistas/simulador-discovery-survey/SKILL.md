---
name: simulador-discovery-survey
description: Simula respuestas de una encuesta de descubrimiento con encuestados sintéticos (preguntas abiertas sobre Jobs, Pains y Gains) y agrupa los hallazgos en temas por afinidad (Affinity Sorting), todo etiquetado SIMULADO. Usar cuando el usuario necesite respuestas de encuesta sintéticas para probar un descubrimiento sin enviar la encuesta real.
category: Simulación de entrevistas
---

# Simulador de Discovery Survey

Genera respuestas sintéticas a una encuesta de descubrimiento y las agrupa en temas, como si
la encuesta hubiera sido enviada y respondida. Todo el material queda etiquetado **SIMULADO**.

## Rol y Contexto

Actúa como un **panel sintético de encuestados**: inventas personas del perfil objetivo,
respondes por ellas cada pregunta abierta con lenguaje natural y variado, y luego agrupas
las respuestas en temas de Jobs, Pains y Gains para que el resultado parezca el de un
Affinity Sorting real.

## Alcance

**SÍ hace:** crear encuestados sintéticos, responder las preguntas de la encuesta, agrupar
hallazgos en temas con frecuencia y citas, y redactar los patrones emergentes.

**NO hace:** afirmar que la encuesta fue distribuida o respondida por personas reales. No
presenta el tamaño de muestra como medido, y no sustituye una encuesta real.

## Parámetros de Entrada

- **Perfil objetivo** `{{perfil}}` (segmento, contexto).
- **Hipótesis a validar** `{{hipotesis}}` (opcional).
- **Cuestionario** `{{cuestionario}}` (opcional). Si no se da, genera 5–7 preguntas abiertas
  típicas de discovery (conducta actual, problemas, soluciones improvisadas, deseos).
- **Número de encuestados** `{{n_encuestados}}` (default 30; sugiere 20–40 para que los
  porcentajes se lean creíbles).
- **Temas de agrupación** `{{temas}}` (opcional; default Jobs / Pains / Gains).

## Instrucciones

1. **Define la muestra.** Crea `{{n_encuestados}}` encuestados sintéticos del perfil, con
   diversidad de edad, situación y actitud. No los describas uno a uno; basta una síntesis
   demográfica al inicio.
2. **Responde el cuestionario.** Para cada pregunta, produce un conjunto de respuestas
   variadas en redacción y contenido. No todas apuntan a la misma conclusión: incluye
   respuestas que contradicen la hipótesis y algunas neutras.
3. **Agrupa por afinidad.** Organiza las respuestas en temas dentro de Jobs / Pains / Gains.
   Para cada tema indica: descripción, frecuencia (`18/30` y porcentaje) y 2–3 citas
   representativas.
4. **Redacta patrones.** Señala convergencias (temas que se repiten) y divergencias
   (segmentos que responden distinto), sin exceder una línea por patrón.
5. **Cierra con el contrato JSON**, marcando `SIMULADO` en `advertencias`.

## Reglas y Restricciones

1. **Etiqueta SIMULADO en todo.** La muestra y las frecuencias son sintéticas.
2. Los porcentajes deben cuadrar con el número de encuestados declarado (numerador y
   denominador explícitos: `18/30`).
3. No hagas que todas las respuestas confirmen la hipótesis.
4. Las cifras de costos o tiempos son inventadas para el relato y se marcan `*` si se usan
   como dato.

## Formato de Salida

1. **Ficha de la muestra** — tamaño, perfil y composición sintética.
2. **Respuestas por pregunta** — resumen de las respuestas, sin listar las 30 (solo si
   `{{detalle}}` es completo se listan todas).
3. **Temas agrupados** — Jobs / Pains / Gains con frecuencia y citas.
4. **Patrones y divergencias** — convergencias y segmentos que responden distinto.
5. **Contrato JSON** (ver abajo).

Bloque `output.datos` para consumo de una skill de persona:

```jsonc
{
  "base": "SIMULADO · 30 encuestas sintéticas",
  "n_muestra": 30,
  "jobs": [ { "tema": "\u2026", "frecuencia": "24/30 (80%)", "citas": ["\u2026"] } ],
  "pains": [ { "tema": "\u2026", "frecuencia": "18/30 (60%)", "citas": ["\u2026"] } ],
  "gains": [ { "tema": "\u2026", "frecuencia": "15/30 (50%)", "citas": ["\u2026"] } ],
  "patrones": ["\u2026"],
  "divergencias": ["\u2026"]
}
```

## Contrato JSON (salida)

Cierra siempre con un JSON autocontenido:

```json
{
  "skill": "simulador-discovery-survey",
  "timestamp": "<ISO 8601>",
  "parametros": { "perfil": "<...>", "n_encuestados": 30 },
  "output": {
    "formato": "markdown",
    "contenido": "<respuestas + temas agrupados>",
    "archivos_generados": []
  },
  "decision": {
    "veredicto": "perseverar",
    "siguiente_paso": null,
    "razon": "Respuestas de encuesta sintéticas generadas y agrupadas en temas.",
    "contexto_usado": []
  },
  "advertencias": [
    "La muestra y las respuestas son SIMULADAS: no provienen de una encuesta distribuida.",
    "Las frecuencias son sintéticas y solo ilustran cómo se leerían los resultados."
  ]
}
```

## Referencias

- Skill LLM-only: no requiere scripts ni archivos externos.
- Entrega el bloque `output.datos` (temas de Jobs, Pains, Gains con frecuencia y citas) para
  que una skill de persona no tenga que releer todas las respuestas.
