---
name: simulador-discovery-survey
description: Simula las respuestas de una encuesta de descubrimiento con encuestados sintéticos y entrega un CSV en formato largo listo para Affinity Sorting, con muestreo reproducible por semilla, proporciones con intervalo de Wilson, tamaño de muestra requerido y prueba z entre segmentos, todo etiquetado SIMULADO. Usar cuando el usuario tenga el cuestionario pero no pueda distribuirlo.
category: Descubrimiento
tipo: simulador
padre: 2.Descubrimiento/discovery-survey
---

# Simulador de Discovery Survey

Fabrica las respuestas que habría dado una muestra de encuestados al cuestionario de
descubrimiento, y las entrega en **un CSV** en formato largo listo para agrupar por afinidad.
Todo queda etiquetado **SIMULADO**.

## Alcance

**SÍ hace:** definir la muestra sintética por segmentos, repartir qué tema menciona cada
encuestado según la prevalencia declarada, y escribir el CSV con las proporciones, los
intervalos y el contraste entre segmentos ya calculados.

**NO hace:**

- **No analiza.** No hace el Affinity Sorting final ni concluye: eso es de
  `2.Descubrimiento/discovery-survey`, que trata el CSV como trataría un export de Google Forms.
- **No genera HTML** ni `reporte.json`, y no cierra pasos del flujo.
- **No sustituye distribuir la encuesta.** Si el usuario puede enviarla, se envía: este
  simulador es para cuando no hay lista de distribución.

## Cuándo se activa

Cuando el usuario decide simular en el **paso 2 del flujo** («Decisión — Entrevistas») con la
Discovery Survey entre los agentes elegidos. Esa decisión enciende la marca de simulación en
todo el proyecto.

## El plan

Tú escribes el material cualitativo; **el script hace los números**:

```jsonc
{
  "proyecto": "Huertos urbanos MX",
  "hipotesis": "El costo de mantenimiento es la barrera principal de abandono",
  "n": 30,                    // encuestados sintéticos
  "seed": 20260819,           // semilla: misma semilla + mismo plan = CSV idéntico
  "ruido": 0.15,              // encoge la prevalencia hacia 0.5
  "rango_edad": [28, 45],
  "muestra": {                // contra qué se compara la n elegida
    "confianza": 0.95,
    "error": 0.10,            // margen de error que se querría poder afirmar
    "poblacion": 120000,      // opcional: ajuste por población finita
    "tasa_respuesta": 0.20    // opcional: cuántas invitaciones haría falta enviar
  },
  "segmentos": [
    { "nombre": "Primerizos", "peso": 0.6 },
    { "nombre": "Con experiencia", "peso": 0.4 }
  ],
  "preguntas": [
    { "id": "P1", "pregunta": "Cuéntame la última vez que…" },
    { "id": "P2", "pregunta": "¿Qué fue lo más difícil de sostenerlo?" }
  ],
  "temas": [
    { "tema": "Costo de mantenimiento mayor al previsto",
      "tipo": "pain",                    // job | pain | gain
      "prevalencia": 0.6,                // DECLARADA: prob. de que un encuestado lo mencione
      "senal": "valida",                 // valida | refuta | neutral
      "pregunta_id": "P2",
      "prevalencia_por_segmento": { "Primerizos": 0.75, "Con experiencia": 0.4 },
      "citas": ["Llevo tres meses y ya gasté el doble de lo que pensaba."] }
  ]
}
```

Reglas del plan:

1. **`prevalencia` es un supuesto declarado, no un dato medido.** El script sortea con ella e
   imprime lo declarado junto a lo observado con su intervalo, para que se pueda contrastar.
2. **`prevalencia_por_segmento` es lo que hace útil la simulación:** si dos segmentos
   responden distinto, el script lo detecta con una prueba z y lo reporta. Sin diferencias
   declaradas, el resultado es una muestra plana.
3. **Al menos un tema con `senal: refuta`.** El script avisa si no hay ninguno.
4. **`citas`** son las frases que se citarán en el reporte; el script las reparte entre los
   encuestados que mencionan el tema.
5. **`muestra.error` es honesto, no aspiracional.** Declara el margen que querrías poder
   afirmar; si `n` no llega, el script lo dice con el número exacto que haría falta.
6. **20-40 encuestados** hacen legible la simulación. Con menos de 20 los porcentajes se
   mueven demasiado; el script avisa cuando un tema tiene menos de 5 menciones.

## Ejecución

Desde la raíz del repositorio:

```bash
python sub-skills/2.Descubrimiento/discovery-survey/simulador/scripts/simular_discovery.py \
    plan.json -o discovery_respuestas_SIMULADO.csv
```

Parámetros sobrescribibles: `--n`, `--seed`, `--ruido`.

Para calcular el tamaño de muestra de un estudio **real** (no simulado), la skill padre tiene
`scripts/calcular_muestra.py`: este simulador usa las mismas fórmulas para decirte si tu `n`
sintética sostiene el margen que declaras.

## Qué produce

**Un CSV** (`discovery_respuestas_SIMULADO.csv`), una fila por encuestado × pregunta × tema
mencionado. Los pares encuestado-pregunta sin ningún tema **también dejan fila** (con `tema`
vacío): así el denominador de cada proporción está en el archivo.

| Columna | Contenido |
| --- | --- |
| `respondent_id` | `E001`, `E002`, … |
| `segmento`, `edad` | Asignados por peso y rango declarados |
| `pregunta_id`, `pregunta` | La pregunta del cuestionario |
| `respuesta` | La cita repartida por el script |
| `tema`, `tipo` | Tema y Job/Pain/Gain (vacíos si no hubo mención) |
| `senal` | `valida` / `refuta` / `neutral` |
| `simulado` | `si` en todas las filas |
| `seed` | La semilla, para que el archivo sea auditable por sí solo |

Además **imprime en pantalla** (no genera archivo): margen de error de la muestra, `n`
requerido para el error declarado, proporción de cada tema con su intervalo de Wilson,
contraste declarado vs. observado, reparto de señales, prueba z entre segmentos y avisos.
Ese bloque es lo que se cita en el reporte: **no lo reescribas de memoria ni redondees a ojo.**

## Supuestos estadísticos y sus límites

Lo que el script garantiza:

- **Reproducibilidad:** semilla explícita; misma semilla + mismo plan = CSV idéntico.
- **Muestreo declarado:** cada mención es un ensayo Bernoulli con la prevalencia del segmento,
  encogida hacia 0.5 según el `ruido` (`p_ef = (1 − ruido)·p + ruido·0.5`).
- **Conteos derivados:** el recuento real de las filas, nunca una cifra redactada.
- **Intervalo de Wilson al 95%** por tema (no la aproximación normal, que con `n` pequeña y
  proporciones cercanas a 0 o 1 se sale del rango).
- **Tamaño de muestra:** `n = (Z²·p·(1−p))/e²` con ajuste por población finita y envíos
  requeridos, las mismas fórmulas que `calcular_muestra.py`.
- **Prueba z de dos proporciones** al 95% entre los dos segmentos declarados.
- **Avisos** si `n` no alcanza el margen declarado, si un tema tiene menos de 5 menciones, si
  un tema declarado no aparece, si la prevalencia efectiva cae fuera del intervalo observado o
  si el segmento más pequeño no llega a 20.

El límite, que va escrito en toda salida:

> **Validez externa: nula.** El intervalo y la prueba z describen la variabilidad del generador
> sintético: contrastan lo observado con las prevalencias que tú declaraste. Estos números
> dicen cómo se leerían los resultados si el mundo se pareciera al plan; no dicen que se le
> parezca. Ninguna decisión de inversión debe apoyarse solo en esto.

Cuidado con un malentendido fácil: que la prueba z encuentre una «diferencia significativa
entre segmentos» **no** significa que esos segmentos difieran en la realidad. Significa que la
diferencia que tú declaraste en el plan es lo bastante grande para detectarse con esta `n`.
Eso sí es información útil —dice si tu encuesta real podría detectarla—, pero es una propiedad
del instrumento, no del mercado.

## La marca SIMULADO

La propaga el flujo solo (`flujo.simulacion` → distintivo en la cabecera del HTML, caja ámbar
en el contexto, advertencia automática y línea en el pie). Lo que te toca:

1. `base` empieza con `SIMULADO · 30 encuestas sintéticas (semilla 20260819)`.
2. Los `tags` del item llevan `SIMULADO`.
3. `advertencias` recoge `n`, la semilla, el ruido, el margen de error real y el límite de
   validez externa.
4. El CSV se declara en `output.archivos_generados` y en `--outputs` al cerrar el paso.
5. **Los porcentajes se escriben con su denominador y su intervalo:** «18 de 30 (60%, IC95
   42-76%)», nunca «60% de los usuarios».

## Contrato JSON (salida)

```json
{
  "skill": "simulador-discovery-survey",
  "timestamp": "<ISO 8601>",
  "parametros": { "n": 30, "seed": 20260819, "ruido": 0.15, "temas": 5, "segmentos": 2 },
  "output": {
    "formato": "csv",
    "contenido": "<resumen del bloque que imprimió el script: proporciones e intervalos>",
    "archivos_generados": ["discovery_respuestas_SIMULADO.csv"]
  },
  "decision": {
    "veredicto": "perseverar",
    "siguiente_paso": "discovery-survey",
    "razon": "Respuestas sintéticas listas para agrupar por afinidad.",
    "contexto_usado": ["html_1"]
  },
  "advertencias": [
    "DATOS SIMULADOS: 30 encuestados sintéticos, semilla 20260819, ruido 15%. La encuesta no se distribuyó.",
    "n=30 da un margen de ±18 pp: sirve para ordenar temas por magnitud, no para afirmar porcentajes.",
    "Validez externa nula: los intervalos describen al generador sintético, no a una población."
  ]
}
```

## Reglas y Restricciones

1. **Nunca redactes conteos, porcentajes ni intervalos.** Los calcula el script; tú los citas.
2. **Un CSV, nada más.** Ni HTML ni `reporte.json` ni cierre de paso.
3. **El nombre del archivo termina en `_SIMULADO.csv`.**
4. **Todo porcentaje va con denominador e intervalo.** Un porcentaje suelto de una muestra
   simulada es la forma más rápida de que alguien lo cite como si fuera real.
5. **Registra la semilla** en `parametros` y en el resumen del paso.
6. **No presentes la prueba z como evidencia de mercado** (ver el malentendido de arriba).

## Referencias

- Convención de simuladores y propagación de la marca: `sub-skills/SIMULACION.md` (canónica,
  si tienes acceso).
- Fórmulas de muestra y cuestionario: `../references/formulas-muestra.md` y `../AGENTE.md` de
  la skill padre.
- Contrato JSON: `sub-skills/CONTRATO_JSON.md` (canónico) o la estructura de arriba, que es
  equivalente y autocontenida.
