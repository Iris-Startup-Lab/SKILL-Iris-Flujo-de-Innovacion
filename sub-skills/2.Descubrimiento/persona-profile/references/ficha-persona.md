# Ficha de Persona — estructura vinculante

Estructura de salida de `persona-profile`, tomada del template oficial
**Persona Profile — AE**. Una ficha por perfil. El orden y los nombres de las secciones
no se cambian: es el formato con el que el equipo lee y compara perfiles.

## Secciones de la ficha

| # | Sección | Contenido | Quién la produce |
| --- | --- | --- | --- |
| 1 | **Nombre del perfil** | El segmento en mayúsculas (ej. `PRODUCTORES CASADOS`), no el nombre de la persona | persona-profile |
| 2 | **JTBD** | «Cuando (situación en un momento vital), quiero (tarea que debe cumplir), para (resultado esperado)» | persona-profile |
| 3 | **Con base en** | `N entrevistas` / `N encuestas` / `supuestos` — de dónde sale la ficha | persona-profile |
| 4 | **Fecha de ejecución** | `día/mes/año – día/mes/año` del trabajo de campo | persona-profile |
| 5 | **Identidad** | Nombre, Edad (rango), Rango de ingresos | persona-profile |
| 6 | **¿Qué quiere? (Metas)** | Qué quiere lograr, qué espera, qué debe garantizarle el producto | persona-profile |
| 7 | **¿Cuándo lo quiere? (Momentos vitales)** | Cuándo necesita el producto (o el de la competencia) | persona-profile |
| 8 | **¿Dónde está?** | Par **Canal físico** / **Canal digital**: espacios donde interactúa | persona-profile |
| 9 | **¿En quién confía? / Le recomienda** | Par **físico** / **digital**: de quién se inspira, quién lo impulsa a decidir | persona-profile |
| 10 | **Pains de productos/servicios actuales** | Numerados 1..N — los dolores que la persona relató | persona-profile |
| 11 | **¿Cómo lo soluciona?** | Numerado, **alineado 1:1 con los pains** | **problem-solution-fit** |
| 12 | **Costo de la solución actual** | Tiempo y dinero por pain: `1–2 horas, $3,000 – $10,000 MXN por jornada` | **problem-solution-fit** |
| 13 | **Importancia del problema × Satisfacción** | Matriz de cuadrantes: un punto numerado por pain | **problem-solution-fit** |
| 14 | **Accionables** | Hipótesis que surgieron, siguientes pasos, experimentos posibles | persona-profile |
| 15 | **Anexo** | Contexto extra que no cabe en las secciones anteriores | persona-profile |

## Frontera con problem-solution-fit (secciones 11–13)

El template oficial imprime la ficha completa porque en la versión de papel el análisis de
Problem-Solution Fit ya venía hecho. En el flujo IRIS **ese análisis es el paso siguiente**
(`html_5`, skill `problem-solution-fit`): es quien evalúa importancia y satisfacción en
escala, mide costos a partir de citas explícitas y valida el encaje de la solución.

Por lo tanto:

- **La sección 10 se queda.** Los pains son lo que la persona relató en campo — el
  apartado «Frustraciones o Dolores» del perfil. Van numerados, con `texto`.
- **Las secciones 11, 12 y 13 solo se rellenan si ya existe ese análisis** (porque
  `html_5` corrió antes y estás regenerando la ficha, o porque el usuario aportó la
  evaluación como insumo). Si no existe, **se omiten**: no se escriben `[no disponible]`
  ni valores estimados.
- **Nunca inventes `importancia`, `satisfaccion` o `costo`** para llenar la ficha. Puntuar
  un pain sin el análisis detrás es fabricar evidencia, y esas cifras alimentan después la
  priorización de todo el flujo.
- El HTML es adaptativo: la tabla de pains muestra solo las columnas con dato y la matriz
  de cuadrantes aparece únicamente cuando hay pares `importancia` + `satisfaccion`. Con la
  ficha sin evaluar, el reporte imprime una nota que remite a Problem-Solution Fit.

**Cuando las cuatro sí están, comparten número.** El pain 2 se resuelve con la solución 2,
cuesta lo que dice el costo 2 y es el punto 2 de la matriz. Por eso en `reporte.json` van
como **un solo array de objetos**, no como cuatro listas paralelas que se pueden
desalinear. O las trae la lista completa de pains, o ninguno: una tabla a medias no se
puede leer ni comparar.

## La matriz Importancia × Satisfacción

- **Eje X — Satisfacción de soluciones actuales** (0 a 5): qué tan bien resuelto está hoy.
- **Eje Y — Importancia del problema** (0 a 5): cuánto le pesa al usuario.
- **Arriba-izquierda = OPORTUNIDAD**: le importa mucho y hoy no está resuelto.
- **Arriba-derecha = COMPETENCIA**: le importa mucho y ya hay quien lo resuelve.

Los dos valores son **juicios derivados de la evidencia**, no cifras inventadas, y su
fuente es `problem-solution-fit`. La matriz **la dibuja la plantilla** a partir de
`importancia` y `satisfaccion` de cada pain. No escribas un bloque `chart`: sería duplicar
la fuente de verdad.

## Bloque `persona` en `reporte.json`

Un item por perfil dentro de `secciones[].items[]`. El frente de la tarjeta (`titulo`,
`subtitulo`, `tags`, `veredicto`) sigue el estándar de todos los reportes IRIS, para que
buscador, filtros y orden funcionen igual que en el resto del flujo.

```jsonc
{
  "titulo": "PRODUCTORES CASADOS",
  "subtitulo": "Alan Martínez · 40 a 55 años · $90,000–$150,000 MXN",
  "tags": ["primaria", "2 entrevistas"],
  "veredicto": "perseverar",
  "persona": {
    "jtbd": "Cuando estoy por ejecutar una producción de alta visibilidad y múltiples dependencias, quiero trabajar con foros y staff conocidos que me hayan demostrado buenos resultados, para proteger el ritmo y mi reputación profesional.",
    "base": "2 entrevistas",
    "fecha_ejecucion": "03/03/2026 – 13/04/2026",
    "naturaleza": "Persona validada con datos",
    "identidad": {
      "nombre": "Alan Martínez",
      "edad": "40 a 55 años",
      "ingresos": "$90,000 – $150,000 MXN"
    },
    "metas": [
      "Eliminar incertidumbre técnica antes del día 0.",
      "Conservar reputación y liderazgo."
    ],
    "momentos_vitales": [
      "Cuando la naturaleza del proyecto requiere alta exigencia (talento, dinero, tiempo).",
      "Cuando requiere servicios específicos e integrados para producción o postproducción (all in one)."
    ],
    "donde_esta": {
      "fisico": ["Foros de TV, estudios grandes, juntas técnicas.", "Stage, scoutings, eventos y ferias del giro."],
      "digital": ["Email profesional.", "LinkedIn.", "Llamadas telefónicas."]
    },
    "confianza": {
      "fisico": ["Ingenieros líderes, productores senior, coordinadores técnicos."],
      "digital": ["Recomendaciones humanas, no publicidad."]
    },
    "pains": [
      { "n": 1, "texto": "Inconsistencia entre staff técnico." },
      { "n": 2, "texto": "Cotizaciones que no incluyen postproducción." }
    ],
    "accionables": [
      "Diseñar un sistema/estrategia comercial que comunique claridad comercial y operativa en staff técnico personalizado y mantenimiento constante del foro."
    ],
    "anexo": ["Requiere servicios integrados de producción y postproducción."]
  }
}
```

### Ficha enriquecida (solo con el análisis de html_5 disponible)

Cuando `problem-solution-fit` ya corrió, cada pain puede llevar su evaluación y la ficha
imprime las secciones 11–13 completas:

```jsonc
"pains": [
  {
    "n": 1,
    "texto": "Inconsistencia entre staff técnico.",
    "solucion": "Trabajar solo con foros conocidos.",
    "costo": "1–2 horas, $3,000 – $10,000 MXN por jornada",
    "importancia": 4.5,
    "satisfaccion": 1.5
  }
]
```

Declara en `advertencias` de dónde viene esa evaluación (ej. «secciones 11–13 tomadas del
análisis de html_5»).

## Campos obligatorios

El validador (`_plantilla_html/scripts/validar_report_data.py`) **falla** si falta:
`jtbd`, `identidad`, `metas`, `momentos_vitales`, `donde_esta`, `confianza`, `pains`
(con `texto` en cada uno). Avisa —sin bloquear— si falta `base`, si el JTBD no sigue el
formato «Cuando… quiero… para…», si un pain trae `importancia` sin `satisfaccion` (o al
revés) o si unos pains traen evaluación y otros no.

`solucion`, `costo`, `importancia` y `satisfaccion` son **opcionales**: su ausencia no
genera aviso, porque salen de `problem-solution-fit`. Cuando vienen, `importancia` y
`satisfaccion` deben ser números entre 0 y 5.

## Si no hay datos reales

La ficha se entrega igual, con la naturaleza declarada:

- `naturaleza`: `"Protopersona hipotética"` y `base`: `"supuestos"`.
- Cada afirmación no respaldada lleva `*`.
- El motivo va en `advertencias` del reporte (ej. «html_2 y html_3 omitidos: sin
  evidencia de campo»).
