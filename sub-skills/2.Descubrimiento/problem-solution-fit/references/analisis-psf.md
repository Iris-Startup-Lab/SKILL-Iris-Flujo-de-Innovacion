# Análisis Problem-Solution Fit — estructura vinculante

Estructura de salida de `problem-solution-fit`. Un item por protopersona analizada (o uno
solo si el análisis es agregado). El orden y los nombres de las secciones no se cambian:
es el formato con el que el equipo compara problemas y decide qué atacar.

## Qué produce este análisis (y qué no)

Este paso es el dueño de la **evaluación de los pains**. La protopersona (`html_4`,
`persona-profile`) entrega quién es y qué le duele; aquí se responde cuánto le duele,
cómo lo resuelve hoy, cuánto le cuesta y si la solución propuesta encaja.

Por eso las secciones 11, 12 y 13 del template *Persona Profile* —«¿Cómo lo soluciona?»,
«Costo de la solución actual» y la matriz «Importancia × Satisfacción»— **nacen aquí**, no
en la ficha de persona. Si tienes acceso a `../persona-profile/references/ficha-persona.md`,
ahí está la ficha completa; si no, el mapeo de vuelta está resumido más abajo.

## Secciones del análisis

| # | Sección | Contenido |
| --- | --- | --- |
| 1 | **Solución evaluada** | Qué solución propuesta se está poniendo a prueba |
| 2 | **Con base en** | `N entrevistas` / `N encuestas` / `SIMULADO` + tamaño de muestra |
| 3 | **Problemas priorizados** | Una fila por problema: contexto, frecuencia, importancia, satisfacción, costo, encaje |
| 4 | **Matriz Importancia × Satisfacción** | Un punto numerado por problema |
| 5 | **Job To Be Done** | El «trabajo» que el usuario intenta resolver y cómo mejorarlo |
| 6 | **Patrones y tendencias** | Similitudes y divergencias entre respuestas |
| 7 | **Oportunidad Blue Ocean** | Diferenciación y propuesta de valor única |
| 8 | **Anexo** | Contexto extra (citas largas, notas de campo) |

**Los problemas comparten número** entre la tabla y la matriz: el problema 2 es el punto 2.
Por eso van como un solo array de objetos, no como listas paralelas.

## La matriz Importancia × Satisfacción

- **Eje X — Satisfacción de soluciones actuales** (0 a 5): qué tan bien resuelto está hoy.
- **Eje Y — Importancia del problema** (0 a 5): cuánto le pesa al usuario.
- **Arriba-izquierda = OPORTUNIDAD**: le importa mucho y hoy no está resuelto.
- **Arriba-derecha = COMPETENCIA**: le importa mucho y ya hay quien lo resuelve.

Puntúa en escala 1 a 5 según el prompt; la matriz se dibuja sobre un lienzo 0–5. La
plantilla la genera a partir de `importancia` y `satisfaccion` de cada problema: **no
escribas un bloque `chart`**, sería duplicar la fuente de verdad.

## Bloque `psf` en `reporte.json`

Un item por análisis dentro de `secciones[].items[]`. El frente de la tarjeta (`titulo`,
`subtitulo`, `tags`, `veredicto`) sigue el estándar de todos los reportes IRIS.

```jsonc
{
  "titulo": "PRODUCTORES CASADOS",
  "subtitulo": "4 problemas priorizados · 2 con encaje parcial",
  "tags": ["primaria", "12 entrevistas"],
  "veredicto": "pivotear",
  "psf": {
    "persona": "PRODUCTORES CASADOS",
    "solucion_propuesta": "Foro all-in-one con staff técnico fijo y postproducción incluida.",
    "base": "12 entrevistas",
    "n_muestra": 12,
    "problemas": [
      {
        "n": 1,
        "problema": "Inconsistencia entre staff técnico.",
        "contexto": "Cada jornada llega gente distinta y hay que reexplicar el setup.",
        "frecuencia": "Alta (9/12)",
        "importancia": 4.5,
        "satisfaccion": 1.5,
        "costo_tiempo": "1–2 h por jornada",
        "costo_dinero": "$3,000 – $10,000 MXN por jornada",
        "solucion_actual": "Trabajar solo con foros conocidos.",
        "cubre": "parcial",
        "ajustes": "Comprometer nominalmente al mismo equipo técnico por proyecto."
      }
    ],
    "patrones": ["Los productores senior aceptan pagar más por continuidad de equipo."],
    "jtbd": "Cuando ejecuto una producción de alta visibilidad, quiero un equipo técnico que ya conozca mi setup, para no gastar la primera jornada reexplicando.",
    "blue_ocean": ["Nadie vende continuidad de staff como garantía contractual."],
    "anexo": ["3 entrevistados mencionaron postproducción sin que se les preguntara."]
  }
}
```

### Campos

| Campo | Obligatorio | Nota |
| --- | --- | --- |
| `problemas[].problema` | sí | El dolor, en una línea |
| `problemas[].n` | no | Si falta, se numera por posición |
| `problemas[].contexto` | no | Se imprime bajo el problema, en letra pequeña |
| `problemas[].frecuencia` | no | `Alta/Media/Baja` o conteo (`9/12`) |
| `problemas[].importancia` | avisa si falta | 1 a 5 · sin ella el problema no entra en la matriz |
| `problemas[].satisfaccion` | avisa si falta | 1 a 5 · sin ella el problema no entra en la matriz |
| `problemas[].costo_tiempo` | avisa si falta | Solo de citas explícitas · `[ESTIMACIÓN]` o `N/D` |
| `problemas[].costo_dinero` | avisa si falta | Ídem |
| `problemas[].solucion_actual` | avisa si falta | Cómo lo resuelve hoy |
| `problemas[].cubre` | avisa si falta | `si` / `parcial` / `no` — otro valor es error |
| `problemas[].ajustes` | no | Qué cambiarle a la solución |
| `solucion_propuesta`, `base` | avisan si faltan | Sin solución declarada, `cubre` no tiene referente |
| `patrones`, `blue_ocean` | avisan si faltan | Listas de textos |
| `jtbd` | avisa si falta | Formato «Cuando… quiero… para…» |

El validador (`_plantilla_html/scripts/validar_report_data.py`) **falla** si falta
`problemas` o el `problema` de una fila, si `cubre` trae un valor fuera de
`si` / `parcial` / `no`, o si `importancia` / `satisfaccion` no son números entre 0 y 5.

## Integridad de datos

- **Costos solo de citas explícitas.** Si se infiere, `[ESTIMACIÓN]`; si no se mencionó,
  `N/D`. Nunca una cifra inventada.
- **Sin datos reales no hay análisis real.** Pide los datos o etiqueta todo el reporte como
  `SIMULADO` (en `base`, en `advertencias` y en los `tags` del item).
- Si `importancia` y `satisfaccion` no se pudieron derivar de la evidencia, déjalas fuera:
  el problema sale en la tabla pero no en la matriz, y se declara en `advertencias`.

## Devolver las secciones 11–13 a la ficha de persona

El análisis es también lo que completa la ficha de `persona-profile`. Si se regenera esa
ficha después de este paso, cada pain puede llevar la evaluación mapeada así:

| Este análisis | Ficha de persona (`persona.pains[]`) |
| --- | --- |
| `solucion_actual` | `solucion` |
| `costo_tiempo` + `costo_dinero` | `costo` (una sola línea) |
| `importancia` | `importancia` |
| `satisfaccion` | `satisfaccion` |

## Exportación a CSV

El CSV es un derivado del mismo contenido, con nombres de columna propios. **No se
reescriben los datos:** el script lee el `reporte.json` y aplica este mapeo.

```bash
python scripts/exportar_csv.py reporte.json -o problem_solution_fit.csv
```

Una **fila por problema**, en el orden en que aparecen; los campos del análisis se repiten
en cada fila del mismo bloque. Las listas se unen con ` · `.

| Bloque `psf` | Columna CSV |
| --- | --- |
| `persona` (o el `titulo` del item, si falta) | `persona` |
| `problemas[].n` (o su posición) | `n` |
| `problemas[].problema` | `problema` |
| `problemas[].contexto` | `contexto` |
| `problemas[].frecuencia` | `frecuencia` |
| `problemas[].importancia` | `impacto` |
| `problemas[].satisfaccion` | `satisfaccion_solucion_actual` |
| `problemas[].costo_tiempo` | `costo_tiempo_horas_semana` |
| `problemas[].costo_dinero` | `costo_dinero_usd_mes` |
| `problemas[].solucion_actual` | `solucion_actual` |
| `problemas[].cubre` | `solucion_cubre` |
| `problemas[].ajustes` | `ajustes_sugeridos` |
| `patrones` | `patrones_tendencias` |
| `jtbd` | `jtbd` |
| `blue_ocean` | `oportunidad_blue_ocean` |

Si el reporte trae varios items con bloque `psf`, salen todos en el mismo CSV y la columna
`persona` es la que los separa. El script también acepta un JSON de filas ya nombradas
(`[{...}]` o `{"filas": [...]}`) por compatibilidad con la entrada anterior.
