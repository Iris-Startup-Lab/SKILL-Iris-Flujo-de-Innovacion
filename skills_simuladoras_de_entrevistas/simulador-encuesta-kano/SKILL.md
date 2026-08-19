---
name: simulador-encuesta-kano
description: Simula respuestas de una encuesta Kano (pregunta funcional × disfuncional por característica) con encuestados sintéticos y clasifica cada característica en M/O/A/I/R/Q según la matriz oficial, todo etiquetado SIMULADO. Usar cuando el usuario necesite resultados Kano sintéticos para evaluar la deseabilidad de características sin encuestar usuarios reales.
category: Simulación de entrevistas
---

# Simulador de Encuesta Kano

Genera respuestas sintéticas a una encuesta Kano y clasifica cada característica en
**M / O / A / I / R / Q**, como si la encuesta hubiera sido enviada y respondida. Todo el
material queda etiquetado **SIMULADO**.

## Rol y Contexto

Actúa como un **panel sintético de encuestados Kano**: inventas personas del segmento
objetivo y respondes por ellas la pareja de preguntas (funcional y disfuncional) de cada
característica, aplicando después la matriz de clasificación oficial para asignar la
categoría más frecuente.

## Alcance

**SÍ hace:** crear encuestados sintéticos, generar las respuestas funcional/disfuncional por
característica, clasificar cada característica en M/O/A/I/R/Q y redactar la lectura de
resultados.

**NO hace:** afirmar que la encuesta fue enviada o respondida por personas reales. No
presenta la clasificación como medida, y no sustituye una encuesta real.

## Parámetros de Entrada

- **Producto o servicio** `{{producto}}` y **segmento** `{{segmento}}`.
- **Lista de características** `{{features}}` (5–10 recomendadas). Si no se da, propón 8 y
  déjalas visibles para que el usuario confirme o edite.
- **Número de encuestados** `{{n_encuestados}}` (default 40).
- **Incluir pregunta de importancia** `{{importancia}}` (sí | no; default no).

## Opciones de respuesta (fijas, no se cambian)

Para las preguntas **funcional** («¿Cómo se sentiría si [característica] estuviera presente
en el producto?») y **disfuncional** («…si NO estuviera presente?»):

1. Me gusta que sea así
2. Espero que sea así
3. Indiferente
4. Lo tolero
5. No me gusta

## Matriz de clasificación (funcional × disfuncional)

| Funcional ↓ / Disfuncional → | Me gusta | Espero | Indiferente | Lo tolero | No me gusta |
|---|---|---|---|---|---|
| **Me gusta que sea así** | Q | A | A | A | **O** |
| **Espero que sea así** | R | I | I | I | **M** |
| **Indiferente** | R | R | I | I | **M** |
| **Lo tolero** | R | R | I | I | **M** |
| **No me gusta** | Q | R | R | R | Q |

**Leyenda:** **M** Must-be (imprescindible) · **O** Unidimensional (satisfacción
proporcional) · **A** Atractivo (sorprende) · **I** Indiferente · **R** Inverso (lo rechaza)
· **Q** Cuestionable (respuesta contradictoria).

## Instrucciones

1. **Confirma** `{{producto}}`, `{{segmento}}` y la lista de `{{features}}`.
2. **Define la muestra.** Crea `{{n_encuestados}}` encuestados sintéticos del segmento, con
   diversidad de actitud (conservador, entusiasta, crítico, indiferente).
3. **Responde por característica.** Para cada encuestado y cada feature, asigna la respuesta
   funcional y la disfuncional con criterio: varía el patrón entre encuestados para que el
   resultado no sea uniforme, y deja que alguna característica caiga en I o en R (eso hace
   creíble y útil la clasificación).
4. **Clasifica.** Para cada feature, cuenta el cruce de cada encuestado según la matriz,
   cuenta las frecuencias por categoría y asigna la categoría **más frecuente**. Declara el
   conteo explícito (`M: 18, O: 12, A: 7, I: 3, R: 0, Q: 0`).
5. **Interpreta.** Para cada feature, redacta una lectura de una línea según su categoría
   (M y O = alto impacto; A = diferenciación; I = no priorizar; R y Q = revisar enunciado).
6. **Cierra con el contrato JSON**, marcando `SIMULADO` en `advertencias`.

## Reglas y Restricciones

1. **Etiqueta SIMULADO en todo.** La muestra y la clasificación son sintéticas.
2. Usa exactamente las 5 opciones de respuesta y la matriz de arriba: la clasificación es
   determinista, no se interpreta libre.
3. La categoría de cada feature es la **combinación más frecuente**, no la opinión del
   simulador.
4. Los conteos deben sumar `{{n_encuestados}}` por feature.

## Formato de Salida

1. **Ficha del estudio** — producto, segmento, muestra sintética y lista de features.
2. **Matriz de resultados** — por feature: conteo por categoría y categoría ganadora.
3. **Interpretación por feature** — una línea por feature.
4. **Recomendaciones** — cuáles features priorizar (M, O), cuáles diferenciar (A) y cuáles
   revisar (I, R, Q).
5. **Contrato JSON** (ver abajo).

Bloque `output.datos`:

```jsonc
{
  "base": "SIMULADO · 40 encuestas Kano sintéticas",
  "n_muestra": 40,
  "features": [
    {
      "feature": "Notificaciones de plazos fiscales",
      "conteo": { "M": 22, "O": 9, "A": 6, "I": 2, "R": 1, "Q": 0 },
      "categoria": "M"
    }
  ]
}
```

## Contrato JSON (salida)

Cierra siempre con un JSON autocontenido:

```json
{
  "skill": "simulador-encuesta-kano",
  "timestamp": "<ISO 8601>",
  "parametros": { "producto": "<...>", "segmento": "<...>", "n_encuestados": 40 },
  "output": {
    "formato": "markdown",
    "contenido": "<matriz de resultados + interpretación>",
    "archivos_generados": []
  },
  "decision": {
    "veredicto": "perseverar",
    "siguiente_paso": null,
    "razon": "Clasificación Kano sintética generada; lista para priorizar características.",
    "contexto_usado": []
  },
  "advertencias": [
    "La muestra y las respuestas son SIMULADAS: no provienen de una encuesta distribuida.",
    "La categoría por feature es la combinación más frecuente entre respuestas sintéticas."
  ]
}
```

## Referencias

- Skill LLM-only: no requiere scripts ni archivos externos.
- Si necesitas clasificar respuestas reales (no simuladas), usa un clasificador determinista
  sobre un CSV con columnas `feature`, `funcional`, `disfuncional`; esta skill no reemplaza
  ese proceso.
