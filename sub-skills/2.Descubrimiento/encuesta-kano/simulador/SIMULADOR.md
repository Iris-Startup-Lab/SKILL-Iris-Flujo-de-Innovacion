---
name: simulador-encuesta-kano
description: Simula las respuestas de una encuesta Kano (pregunta funcional × disfuncional por característica) con encuestados sintéticos y entrega un CSV listo para clasificar, con muestreo reproducible por semilla, intervalos de Wilson, coeficientes de Berger y todo etiquetado SIMULADO. Usar cuando el usuario quiera resultados Kano pero no tenga a quién encuestar.
category: Descubrimiento
tipo: simulador
padre: 2.Descubrimiento/encuesta-kano
---

# Simulador de Encuesta Kano

Fabrica las respuestas que habría dado un panel de encuestados a la pareja de preguntas Kano
de cada característica, y las entrega en **un CSV** con la forma exacta que consume el
clasificador de la skill padre. Todo queda etiquetado **SIMULADO**.

## Alcance

**SÍ hace:** definir un panel sintético, sortear la respuesta funcional y disfuncional de cada
encuestado para cada característica, y escribir el CSV con los supuestos estadísticos del
muestreo declarados.

**NO hace:**

- **No analiza.** No clasifica en la salida final, no prioriza y no concluye: eso es trabajo de
  `2.Descubrimiento/encuesta-kano` con `scripts/clasificar_kano.py`, el mismo script que usaría
  con respuestas reales.
- **No genera HTML** ni `reporte.json`, y no cierra pasos del flujo.
- **No afirma que los datos sean reales.** No sustituye una encuesta cuando el usuario sí tiene
  a quién preguntar.

## Cuándo se activa

Solo cuando el usuario decide simular en el **paso 2 del flujo** («Decisión — Entrevistas»),
en el nodo «¿Ejecución de entrevistas?» → *No — simulación de respuestas e insights*, con la
Encuesta Kano entre los agentes elegidos. Esa decisión enciende la marca de simulación en todo
el proyecto (ver «La marca SIMULADO», abajo).

Si el usuario tiene respuestas reales, este simulador no interviene.

## El plan

El contenido cualitativo lo escribes tú; **los números los hace el script**. Escribe un
`plan.json`:

```jsonc
{
  "proyecto": "Huertos urbanos MX",
  "perfil": "Familias urbanas 28-45, CDMX",
  "hipotesis": "El recordatorio de riego es lo que decide la compra",
  "n": 40,                    // encuestados sintéticos (Kano pide 20-30 por segmento)
  "seed": 20260819,           // semilla: misma semilla + mismo plan = CSV idéntico
  "ruido": 0.15,              // prob. de responder fuera del patrón declarado
  "importancia": true,        // añade la columna de importancia (1-5)
  "segmentos": [
    { "nombre": "Primerizos", "peso": 0.6 },
    { "nombre": "Con experiencia", "peso": 0.4 }
  ],
  "features": [
    { "feature": "Recordatorio de riego por app",
      "categoria_objetivo": "O",       // M | O | A | I | R  (Q nunca se declara)
      "importancia_media": 4.2 },
    { "feature": "Suscripción mensual obligatoria",
      "categoria_objetivo": "R" }
  ]
}
```

Reglas del plan:

1. **`categoria_objetivo` es la categoría latente**, la que el equipo cree que tiene esa
   característica: el script sortea las respuestas desde la distribución típica de esa
   categoría. Admite `M`, `O`, `A`, `I` y `R`. **`Q` no se declara**: una respuesta
   contradictoria es un accidente del instrumento, no un objetivo de diseño.
2. **Declara las cinco categorías, no solo las buenas.** Un plan donde todo es `M` u `O`
   produce una encuesta que solo confirma. Mete al menos una `I` y, si el producto tiene una
   característica que parte de opiniones, una `R`.
3. **`ruido` (0.15 por defecto)** es lo que hace creíble el resultado: con esa probabilidad el
   encuestado responde uniforme sobre las 5 opciones, así que aparecen categorías minoritarias
   y algún `Q`. Con `ruido: 0` el resultado sale de laboratorio y no sirve de ensayo.
4. **`segmentos` con peso** reparte el panel. Si vas a comparar segmentos entre sí, cada uno
   necesita sus propios 20-30 encuestados: el script avisa cuando no llegan.
5. Puedes forzar las distribuciones de una característica con
   `"distribuciones": {"funcional": {...}, "disfuncional": {...}}` (pesos sobre `like`,
   `expect`, `neutral`, `tolerate`, `dislike`). Úsalo solo si sabes qué estás haciendo: el
   patrón por categoría ya está calibrado.

## Ejecución

Desde la raíz del repositorio:

```bash
# 1. simular las respuestas -> CSV
python sub-skills/2.Descubrimiento/encuesta-kano/simulador/scripts/simular_kano.py \
    plan.json -o kano_respuestas_SIMULADO.csv

# 2. clasificar con el script de la skill padre (el mismo que con datos reales)
python sub-skills/2.Descubrimiento/encuesta-kano/scripts/clasificar_kano.py \
    kano_respuestas_SIMULADO.csv -o clasificacion_kano_SIMULADO.csv
```

Parámetros sobrescribibles: `--n`, `--seed`, `--ruido`.

## Qué produce

**Un CSV** (`kano_respuestas_SIMULADO.csv`), una fila por encuestado × característica:

| Columna | Contenido |
| --- | --- |
| `respondent_id` | `R001`, `R002`, … |
| `segmento` | Segmento asignado por peso |
| `feature` | Nombre de la característica |
| `funcional` | «Me gusta que sea así» / «Espero que sea así» / «Indiferente» / «Lo tolero» / «No me gusta» |
| `disfuncional` | Las mismas cinco opciones, para la pregunta en negativo |
| `importancia` | 1-5, solo si el plan lo pide |
| `simulado` | `si` en todas las filas |
| `seed` | La semilla, para que el archivo sea auditable por sí solo |

Además **imprime en pantalla** (no genera archivo) el bloque de supuestos: margen de error de
la muestra, conteo M/O/A/I/R/Q y categoría ganadora por característica, intervalo de Wilson al
95%, coeficientes de Berger CS/DS, tasa de respuestas descartables y avisos. Ese bloque es lo
que copias al reporte de la skill padre: **no lo reescribas de memoria ni redondees a ojo.**

## Supuestos estadísticos y sus límites

Lo que el script garantiza:

- **Reproducibilidad:** semilla explícita; misma semilla + mismo plan = CSV idéntico byte a byte.
- **Muestreo declarado:** cada pareja de respuestas sale de la distribución de la categoría
  latente del plan, con `ruido` de respuesta uniforme. Los conteos son el recuento real de las
  filas, nunca una cifra redactada.
- **Clasificación determinista:** la matriz Kano oficial, idéntica celda por celda a la de
  `clasificar_kano.py`.
- **Incertidumbre:** intervalo de Wilson al 95% (no la aproximación normal, que con `n` pequeña
  y proporciones cercanas a 0 o 1 se sale del rango).
- **Berger CS/DS** sobre la base A+O+M+I; si esa base no llega a la mitad de las respuestas, el
  script **no los reporta** y explica por qué: describirían a una minoría.
- **Avisos** cuando `n` < 20, cuando un segmento no llega a 20, cuando hay empate en la moda y
  cuando las respuestas descartables pasan del 10%.

El límite, que va escrito en toda salida:

> **Validez externa: nula.** El intervalo describe la variabilidad del generador sintético, no
> la de una población. Estos números dicen cómo se leerían los resultados si el mundo se
> pareciera a las categorías declaradas en el plan; no dicen que se le parezca. Ninguna
> decisión de inversión debe apoyarse solo en esto.

El criterio de calidad de la simulación no es la significancia, sino **si el plan es
discutible**: prevalencias y categorías que alguien del equipo pueda mirar y corregir. Ahí está
el valor — la simulación hace explícitos los supuestos que, sin ella, se quedan implícitos.

## La marca SIMULADO

La marca la propaga el flujo solo (`flujo.simulacion` → distintivo en la cabecera del HTML,
caja ámbar en el contexto, advertencia automática y línea en el pie). Lo que te toca a ti:

1. `base` del análisis empieza con `SIMULADO · 40 encuestas Kano sintéticas (semilla 20260819)`.
2. Los `tags` del item del reporte llevan `SIMULADO`.
3. `advertencias` recoge el `n`, la semilla, el ruido y el límite de validez externa.
4. El CSV se declara en `output.archivos_generados` y en `--outputs` al cerrar el paso.

## Contrato JSON (salida)

```json
{
  "skill": "simulador-encuesta-kano",
  "timestamp": "<ISO 8601>",
  "parametros": { "n": 40, "seed": 20260819, "ruido": 0.15, "features": 5 },
  "output": {
    "formato": "csv",
    "contenido": "<resumen del bloque de supuestos que imprimió el script>",
    "archivos_generados": ["kano_respuestas_SIMULADO.csv"]
  },
  "decision": {
    "veredicto": "perseverar",
    "siguiente_paso": "encuesta-kano",
    "razon": "Respuestas sintéticas listas para clasificar con clasificar_kano.py.",
    "contexto_usado": ["html_1"]
  },
  "advertencias": [
    "DATOS SIMULADOS: 40 encuestados sintéticos, semilla 20260819, ruido 15%. No provienen de una encuesta distribuida.",
    "Validez externa nula: los intervalos describen al generador sintético, no a una población."
  ]
}
```

## Reglas y Restricciones

1. **Nunca redactes conteos, porcentajes ni intervalos.** Los calcula el script; tú los citas.
2. **Un CSV, nada más.** Ni HTML ni `reporte.json` ni cierre de paso: eso es de la skill padre.
3. **El nombre del archivo termina en `_SIMULADO.csv`.** El script avisa si no.
4. **Registra la semilla** en `parametros` y en el resumen del paso. Sin ella la simulación no
   es auditable.
5. **No presentes la simulación como evidencia** ni omitas el límite de validez externa, ni
   siquiera «para abreviar».

## Referencias

- Convención de simuladores, esquema del plan y propagación de la marca:
  `sub-skills/SIMULACION.md` (canónica, si tienes acceso).
- Matriz Kano y lectura de categorías: `../references/clasificacion-kano.md` de la skill padre.
- Contrato JSON: `sub-skills/CONTRATO_JSON.md` (canónico) o la estructura de arriba, que es
  equivalente y autocontenida.
