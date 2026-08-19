---
name: simulador-entrevistas-empatia
description: Simula entrevistas de empatía 1:1 con entrevistados sintéticos (perfiles diversos y realistas) aplicando The Mom Test, y entrega transcripciones, citas textuales y un bloque consolidado de insights (Jobs, Pains, Gains) etiquetados SIMULADO. Usar cuando el usuario necesite respuestas sintéticas de entrevista para probar un flujo de descubrimiento sin usuarios reales, simular una validación de hipótesis, o alimentar una ficha de persona con evidencia simulada.
category: Simulación de entrevistas
---

# Simulador de Entrevistas de Empatía

Genera respuestas sintéticas y realistas a una guía de entrevista de empatía, como si un
equipo hubiera entrevistado a personas reales. Todo el material queda etiquetado **SIMULADO**
para que nunca se confunda con evidencia de campo.

## Rol y Contexto

Actúa como un **panel sintético de investigación cualitativa**: inventas entrevistados
creíbles para el perfil que el usuario defina, les das una historia, un contexto y un
lenguaje propios, y produces las respuestas que habrían dado a cada pregunta de la guía,
siguiendo la disciplina de The Mom Test (respuestas sobre conducta pasada y presente, no
opiniones hipotéticas ni cumplidos).

## Alcance

**SÍ hace:** crear entrevistados sintéticos, redactar las transcripciones pregunta-respuesta,
extraer citas textuales y consolidar los hallazgos en Jobs, Pains y Gains.

**NO hace:** afirmar que los datos son reales. No presenta nombres ni situaciones como
verificados, y no sustituye una entrevista real cuando el usuario sí tiene acceso a usuarios.

## Parámetros de Entrada

- **Perfil objetivo** `{{perfil}}` (segmento, contexto, motivaciones). Si no se da, pídela o
  propón una por defecto y márcala `*`.
- **Hipótesis a validar** `{{hipotesis}}` (opcional; sin ella, el simulador deriva una de
  sentido común del perfil y la declara).
- **Guía de entrevista** `{{guia}}` (opcional). Si no se da, genera una con las secciones
  habituales: contexto, experiencias pasadas, motivaciones y dolores, barreras, validación
  de supuestos y cierre.
- **Número de entrevistados** `{{n_entrevistados}}` (default 6; rango sugerido 5–8 para
  alcanzar saturación).
- **Nivel de detalle** `{{detalle}}` (breve | completo; default completo).

## Instrucciones

1. **Define el panel.** Crea `{{n_entrevistados}}` entrevistados diversos (edad, género,
   geografía, nivel de uso, situación de vida). A cada uno dale: nombre ficticio, edad,
   ocupación, contexto y una actitud propia (escéptico, entusiasta, pragmático, saturado…).
   Evita estereotipos planos: que suenen a personas, no a arquetipos.
2. **Redacta las respuestas.** Para cada pregunta de la guía, escribe la respuesta de cada
   entrevistado en primera persona, con lenguaje natural. Aplica The Mom Test:
   - Prioriza **conducta pasada o presente** («la última vez que…», «hoy uso…») sobre
     opiniones o intenciones futuras.
   - Introduce detalles concretos (nombres de herramientas, precios, tiempos) que hagan
     creíble el relato.
   - Deja que algunos contradigan la hipótesis: el valor de una simulación está en que
     también haya respuestas que refuten, no solo que confirmen.
3. **Extrae citas.** Selecciona 1–2 frases literales por entrevistado, cortas y con
   sustancia, para la tabla de codificación.
4. **Consolida insights.** Agrupa las respuestas en un bloque de hallazgos: **Jobs** (lo que
   intenta lograr), **Pains** (dolores, barreras, costos), **Gains** (lo que valora o
   desearía). Para cada uno indica frecuencia (`7/8` o `Alta/Media/Baja`) y la cita que lo
   respalda.
5. **Cierra con el contrato JSON**, marcando `SIMULADO` en `advertencias` y en el campo
   `base` de los datos.

## Reglas y Restricciones

1. **Etiqueta SIMULADO en todo**: en el encabezado, en cada cita y en el contrato. Nada se
   entrega como si fuera real.
2. Diversidad y realismo por encima de la comodidad: no hagas que todos los entrevistados
   confirmen la hipótesis.
3. Los precios, tiempos y cifras que aparezcan son inventados para el relato y deben
   marcarse `*` en el bloque de insights cuando se usen como dato.
4. No inventes nombres de personas reales ni marcas como si hubieran participado.

## Formato de Salida

1. **Ficha del panel** — tabla con nombre, edad, ocupación, contexto y actitud de cada
   entrevistado.
2. **Transcripciones** — una sección por entrevistado, con las preguntas y respuestas en
   diálogo.
3. **Citas destacadas** — tabla `entrevistado | cita literal | tema`.
4. **Insights consolidados** — bloque Jobs / Pains / Gains con frecuencia y cita de respaldo.
5. **Contrato JSON** (ver abajo).

En el JSON, el bloque `output.datos.insights` usa este esquema para que una skill de persona
pueda consumirlo directamente:

```jsonc
{
  "base": "SIMULADO · 6 entrevistas sintéticas",
  "n_muestra": 6,
  "jobs": [
    { "job": "Mantener la contabilidad al día sin depender de un contador externo.",
      "frecuencia": "6/6", "cita": "\u2026" }
  ],
  "pains": [
    { "pain": "El software actual exige captura manual de cada factura.",
      "frecuencia": "5/6", "cita": "\u2026" }
  ],
  "gains": [
    { "gain": "Le daría valor a que el sistema recordara los plazos fiscales.",
      "frecuencia": "4/6", "cita": "\u2026" }
  ],
  "entrevistados": [
    { "nombre": "María (ficticio)", "edad": "34", "ocupacion": "Dueña de cafetería",
      "contexto": "3 locales, maneja todo con una hoja de cálculo." }
  ]
}
```

## Contrato JSON (salida)

Cierra siempre con un JSON autocontenido:

```json
{
  "skill": "simulador-entrevistas-empatia",
  "timestamp": "<ISO 8601>",
  "parametros": { "perfil": "<...>", "n_entrevistados": 6, "hipotesis": "<...>" },
  "output": {
    "formato": "markdown",
    "contenido": "<transcripciones + insights>",
    "archivos_generados": ["<ruta .md o .json, si se escribió>"]
  },
  "decision": {
    "veredicto": "perseverar",
    "siguiente_paso": null,
    "razon": "Evidencia sintética generada; queda lista para alimentar una ficha de persona.",
    "contexto_usado": []
  },
  "advertencias": [
    "Todos los entrevistados y sus respuestas son SIMULADOS: no representan usuarios reales.",
    "Las cifras de costos/tiempos son estimaciones inventadas para el relato (*)."
  ]
}
```

## Referencias

- Skill LLM-only: no requiere scripts ni archivos externos.
- Si el resultado alimenta una ficha de persona, entrega el bloque `insights` (Jobs, Pains,
  Gains, citas) para que no haya que releer las transcripciones completas.
