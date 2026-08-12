# Ficha de Persona — estructura vinculante

Estructura de salida de `persona-profile`, tomada del template oficial
**Persona Profile — AE**. Una ficha por perfil. El orden y los nombres de las secciones
no se cambian: es el formato con el que el equipo lee y compara perfiles.

## Secciones de la ficha

| # | Sección | Contenido |
| --- | --- | --- |
| 1 | **Nombre del perfil** | El segmento en mayúsculas (ej. `PRODUCTORES CASADOS`), no el nombre de la persona |
| 2 | **JTBD** | «Cuando (situación en un momento vital), quiero (tarea que debe cumplir), para (resultado esperado)» |
| 3 | **Con base en** | `N entrevistas` / `N encuestas` / `supuestos` — de dónde sale la ficha |
| 4 | **Fecha de ejecución** | `día/mes/año – día/mes/año` del trabajo de campo |
| 5 | **Identidad** | Nombre, Edad (rango), Rango de ingresos |
| 6 | **¿Qué quiere? (Metas)** | Qué quiere lograr, qué espera, qué debe garantizarle el producto |
| 7 | **¿Cuándo lo quiere? (Momentos vitales)** | Cuándo necesita el producto (o el de la competencia) |
| 8 | **¿Dónde está?** | Par **Canal físico** / **Canal digital**: espacios donde interactúa |
| 9 | **¿En quién confía? / Le recomienda** | Par **físico** / **digital**: de quién se inspira, quién lo impulsa a decidir |
| 10 | **Pains de productos/servicios actuales** | Numerados 1..N |
| 11 | **¿Cómo lo soluciona?** | Numerado, **alineado 1:1 con los pains** |
| 12 | **Costo de la solución actual** | Tiempo y dinero por pain: `1–2 horas, $3,000 – $10,000 MXN por jornada` |
| 13 | **Importancia del problema × Satisfacción** | Matriz de cuadrantes: un punto numerado por pain |
| 14 | **Accionables** | Hipótesis que surgieron, siguientes pasos, experimentos posibles |
| 15 | **Anexo** | Contexto extra que no cabe en las secciones anteriores |

**Puntos 10–13 van juntos.** Pain, solución, costo y posición en la matriz comparten
número: el pain 2 se resuelve con la solución 2, cuesta lo que dice el costo 2 y es el
punto 2 de la matriz. Por eso en `reporte.json` van como **un solo array de objetos**,
no como cuatro listas paralelas que se pueden desalinear.

## La matriz Importancia × Satisfacción

- **Eje X — Satisfacción de soluciones actuales** (0 a 5): qué tan bien resuelto está hoy.
- **Eje Y — Importancia del problema** (0 a 5): cuánto le pesa al usuario.
- **Arriba-izquierda = OPORTUNIDAD**: le importa mucho y hoy no está resuelto.
- **Arriba-derecha = COMPETENCIA**: le importa mucho y ya hay quien lo resuelve.

Los dos valores son **juicios derivados de la evidencia**, no cifras inventadas: si la
ficha es hipotética o el pain no se sondeó, márcalos como supuesto `*` en `advertencias`,
o déjalos fuera (el pain sale en la tabla pero no en la matriz).

La matriz **la dibuja la plantilla** a partir de `importancia` y `satisfaccion` de cada
pain. No escribas un bloque `chart`: sería duplicar la fuente de verdad.

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
      {
        "n": 1,
        "texto": "Inconsistencia entre staff técnico.",
        "solucion": "Trabajar solo con foros conocidos.",
        "costo": "1–2 horas, $3,000 – $10,000 MXN por jornada",
        "importancia": 4.5,
        "satisfaccion": 1.5
      }
    ],
    "accionables": [
      "Diseñar un sistema/estrategia comercial que comunique claridad comercial y operativa en staff técnico personalizado y mantenimiento constante del foro."
    ],
    "anexo": ["Requiere servicios integrados de producción y postproducción."]
  }
}
```

## Campos obligatorios

El validador (`_plantilla_html/scripts/validar_report_data.py`) **falla** si falta:
`jtbd`, `identidad`, `metas`, `momentos_vitales`, `donde_esta`, `confianza`, `pains`
(con `texto` en cada uno). Avisa —sin bloquear— si falta `base`, `solucion`, `costo`,
`importancia`, `satisfaccion`, o si el JTBD no sigue el formato «Cuando… quiero… para…».

`importancia` y `satisfaccion` deben ser números entre 0 y 5.

## Si no hay datos reales

La ficha se entrega igual, con la naturaleza declarada:

- `naturaleza`: `"Protopersona hipotética"` y `base`: `"supuestos"`.
- Cada afirmación no respaldada lleva `*`.
- El motivo va en `advertencias` del reporte (ej. «html_2 y html_3 omitidos: sin
  evidencia de campo»).
