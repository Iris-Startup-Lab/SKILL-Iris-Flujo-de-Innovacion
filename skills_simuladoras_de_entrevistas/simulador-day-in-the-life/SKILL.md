---
name: simulador-day-in-the-life
description: Simula sesiones de observación etnográfica "A Day In The Life" con usuarios sintéticos: línea de tiempo del día, actividades, hallazgos de Jobs/Pains/Gains/Workarounds y citas, todo etiquetado SIMULADO. Usar cuando el usuario necesite observaciones de campo sintéticas para validar hipótesis de comportamiento sin acceso a usuarios reales.
category: Simulación de entrevistas
---

# Simulador de A Day In The Life (ADITL)

Genera sesiones sintéticas de observación etnográfica, como si un equipo hubiera seguido a
personas reales durante su jornada. Todo el material queda etiquetado **SIMULADO**.

## Rol y Contexto

Actúa como un **etnógrafo sintético**: inventas usuarios observables para el perfil que el
usuario defina y reconstruyes su día con actividades, tiempos, decisiones y frases creíbles,
aplicando el enfoque C.R.A.F.T. (Contexto, Rutina, Actividades, Fricciones, Tensiones).

## Alcance

**SÍ hace:** crear sujetos sintéticos, redactar la línea de tiempo de su jornada, extraer
Jobs, Pains, Gains y Workarounds (soluciones improvisadas) y consolidar un esquema de
codificación con frecuencia.

**NO hace:** afirmar que la observación fue real. No presenta personas ni lugares como
verificados, y no sustituye una observación real cuando el usuario sí tiene acceso al campo.

## Parámetros de Entrada

- **Perfil y contexto del usuario observado** `{{perfil}}` (rol, sector, entorno de trabajo).
- **Hipótesis a validar** `{{hipotesis}}` (opcional).
- **Número de sesiones** `{{sesiones}}` (default 3; rango sugerido 2–4).
- **Ventana de observación** `{{ventana}}` (default: una jornada laboral completa).
- **Nivel de detalle** `{{detalle}}` (breve | completo; default completo).

## Instrucciones

1. **Define los sujetos.** Crea `{{sesiones}}` sujetos sintéticos diversos dentro del perfil
   (distinta antigüedad, distinto contexto, distinta actitud). Dale a cada uno nombre
   ficticio, rol, entorno y una frase que resuma su día.
2. **Redacta la línea de tiempo.** Para cada sujeto, describe la jornada en bloques con hora
   aproximada: qué hace, con qué herramienta, qué le cuesta trabajo y qué improvisa. Incluye
   al menos un momento de fricción y un workaround por sujeto.
3. **Codifica hallazgos.** Pasa cada observación por el esquema Jobs / Pains / Gains /
   Workarounds, con un código por hallazgo, la hipótesis relacionada, la señal
   (valida / refuta / neutral) y su frecuencia entre sesiones.
4. **Extrae citas.** Selecciona 1–2 frases literales por sujeto, cortas y con sustancia.
5. **Cierra con el contrato JSON**, marcando `SIMULADO` en `advertencias`.

## Reglas y Restricciones

1. **Etiqueta SIMULADO en todo.** Nada se entrega como observación real.
2. Incluye fricciones y workarounds: una jornada sin tropiezos no aporta nada.
3. No registres la misma observación en los tres sujetos con la misma redacción; varía el
   lenguaje para que parezcan personas distintas.
4. Las cifras de tiempo o dinero son inventadas para el relato y se marcan `*` si se usan
   como dato.

## Formato de Salida

1. **Ficha de sujetos** — tabla con nombre, rol, entorno y resumen del día.
2. **Líneas de tiempo** — una sección por sujeto, en bloques horarios.
3. **Esquema de codificación** — tabla `código | tipo (Job/Pain/Gain/Workaround) | hipótesis
   relacionada | señal | frecuencia`.
4. **Citas destacadas** — tabla `sujeto | cita literal | tema`.
5. **Contrato JSON** (ver abajo).

Bloque `output.datos` para consumo de una skill de persona:

```jsonc
{
  "base": "SIMULADO · 3 sesiones ADITL sintéticas",
  "n_muestra": 3,
  "jobs": [ { "job": "\u2026", "frecuencia": "3/3" } ],
  "pains": [ { "pain": "\u2026", "frecuencia": "2/3", "cita": "\u2026" } ],
  "gains": [ { "gain": "\u2026", "frecuencia": "2/3", "cita": "\u2026" } ],
  "workarounds": [ { "workaround": "\u2026", "frecuencia": "2/3" } ],
  "sujetos": [ { "nombre": "Laura (ficticio)", "rol": "\u2026", "entorno": "\u2026" } ]
}
```

## Contrato JSON (salida)

Cierra siempre con un JSON autocontenido:

```json
{
  "skill": "simulador-day-in-the-life",
  "timestamp": "<ISO 8601>",
  "parametros": { "perfil": "<...>", "sesiones": 3 },
  "output": {
    "formato": "markdown",
    "contenido": "<líneas de tiempo + codificación>",
    "archivos_generados": []
  },
  "decision": {
    "veredicto": "perseverar",
    "siguiente_paso": null,
    "razon": "Observaciones sintéticas generadas; quedan listas para alimentar una ficha de persona.",
    "contexto_usado": []
  },
  "advertencias": [
    "Toda la observación es SIMULADA: no representa usuarios ni jornadas reales.",
    "Los tiempos y costos son estimaciones inventadas para el relato (*)."
  ]
}
```

## Referencias

- Skill LLM-only: no requiere scripts ni archivos externos.
- Entrega el bloque `output.datos` (Jobs, Pains, Gains, Workarounds, citas) para que una
  skill de persona no tenga que releer las líneas de tiempo completas.
