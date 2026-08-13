---
name: iris-flujo-de-innovacion
description: "Orquesta el flujo completo de innovación IRIS (Investigación → Descubrimiento → Ideación → Prototipado → Validación). Guía paso por paso con human-in-the-loop, invoca las sub-skills especializadas por ruta y consolida sus resultados en 11 reportes HTML interactivos con el diseño corporativo IRIS. Cada reporte lleva el contexto completo del flujo y el usuario puede omitir los pasos que no necesite. Usar cuando el usuario quiera iniciar un proyecto de innovación, investigación de mercado, validación de una idea o producto, o ejecutar el proceso IRIS completo o una de sus fases."
version: 2.0
author: "Skill Integradora: Fernando Dorantes Nieto  SubSkills: Integrantes de Iris Startup Lab"
creacion_date: "2026-08-12"
---

# IRIS — Flujo de Innovación (Skill Integradora)

Orquesta 11 pasos y 26 sub-skills, de la investigación a la validación, deteniéndose
en cada decisión para que la dirija el usuario.

## Las tres reglas que no se rompen

1. **`pasos.json` manda.** Nunca deduzcas qué sub-skill toca ni cómo se llama su carpeta: está escrito ahí. Ningún otro documento define el flujo.
2. **El estado se cambia con el script, no a mano.** `scripts/estado_flujo.py` es el único que edita `flujo_estado.json` y regenera `STATE.md`.
3. **Todo HTML lleva el contexto del flujo.** Se genera con `--estado` y `--paso`, que inyectan el contexto solos. Si falta, el generador falla a propósito.

## Regla dependiendo de la herramienta

1. Si estás en Claude, Antigravity o Codex, realiza las preguntas al usuario como un agente de IA, no como un humano. Es decir, no utilices fórmulas coloquiales, refranes, muletillas, ni expresiones que denoten una conciencia de sí mismo o una capacidad de "sentir" o "creer", además siempre que sea en opciones, para que el usuario de click.  

## Los cuatro archivos del flujo

| Archivo | Qué es | Quién lo edita |
| --- | --- | --- |
| `pasos.json` | Definición del flujo: pasos, decisiones, rutas de sub-skills, qué se puede omitir | Nadie durante un proyecto (es la plantilla) |
| `flujo_estado.json` | Avance del proyecto en curso: estados, decisiones, resúmenes | Solo `scripts/estado_flujo.py` |
| `STATE.md` | Vista humana del estado, **generada** | Nadie: se reescribe en cada paso |
| `html_1 … html_11` | Los entregables | El generador HTML |

---

## Arranque de un proyecto

Pide al usuario: **nombre**, **objetivo** y **audiencia**. Todo lo demás se pregunta
paso a paso, cuando toca.

Luego ofrece el recorrido:

- **Ruta completa** (11 pasos) — el proceso íntegro.
- **Ruta mínima** (5 pasos: `html_1 → html_4 → html_7 → html_8 → html_11`) — de la
  investigación al experimento sin las etapas intermedias.

```bash
python scripts/estado_flujo.py init --proyecto "<nombre>" \
    --objetivo "<objetivo>" --audiencia "<audiencia>" [--ruta minima]
```

Si `flujo_estado.json` ya existe, el script se detiene y muestra el proyecto en curso:
**pregunta al usuario si quiere continuarlo** antes de tocar nada.

---

## El ciclo de un paso

Repite estos 7 pasos hasta que el flujo esté completo. No improvises el orden.

### 1. Leer el paso

```bash
python scripts/estado_flujo.py mostrar          # el paso_actual
python scripts/estado_flujo.py mostrar --paso html_5
```

Devuelve todo lo necesario: histórico de los predecesores, decisiones ya tomadas,
pasos omitidos con su impacto, decisiones a presentar, sub-skills invocables y si el
paso se puede omitir.

### 2. Resumir el histórico al usuario

En 2–3 líneas: dónde está, qué se decidió antes y qué va a pasar ahora.
**No preguntes nada que ya aparezca en «Decisiones ya tomadas».**

### 3. Ofrecer ejecutar u omitir

Presenta siempre tres opciones:

- **Ejecutar** — sigue al paso 4.
- **Omitir** — ve a «Omitir un paso».
- **¿Por qué importa?** — lee el `objetivo` del paso y su `si_omitido`, y vuelve a preguntar.

### 4. Resolver las decisiones del paso

Para cada nodo de decisión que devolvió `mostrar`:

1. Presenta las opciones **exactas** de `pasos.json`, con opciones clickeables si la
   herramienta las tiene; si no, lista numerada.
2. Respeta `solo_si` (decisiones condicionales), `opciones_desde` (ej. las palancas
   dependen de la ambición elegida: muestra solo las suyas) y `auto_si` (si se cumple
   la condición, informa al usuario de la opción forzada en vez de preguntar).
3. Registra cada elección:

```bash
python scripts/estado_flujo.py decision --paso html_5 \
    --nodo "Elección de protopersona" --opcion "Por problema más grande"
```

### 5. Invocar las sub-skills

Para cada ruta que devolvió `mostrar`, **lee** `sub-skills/<ruta>/SKILL.md` y ejecuta
sus instrucciones al pie de la letra.

- Antes de invocarla, traslada al usuario sus **Parámetros de Entrada** y confirma los valores.
- Pásale el contexto del flujo (paso 1) para que no repita preguntas ni reinvente supuestos.
- **Pásale también los datos de sus predecesores, no solo el resumen.** `mostrar` imprime,
  por cada predecesor, la ruta de su `reporte.json` (`datos estructurados: …`) o el HTML que
  los lleva embebidos. Ahí están los bloques que la sub-skill hereda —`persona`, `psf`,
  `secciones[].items[]`— y reteclearlos desde el resumen es perder evidencia.
- Respeta `cadenas` (ejecución secuencial obligatoria) y `paralelo` (se ejecutan a la
  vez y se consolidan en un solo HTML).

### 6. Generar el HTML

Consolida los outputs en un `reporte.json` con el esquema `REPORT_DATA`
(ver `_plantilla_html/README.md`) — una sección por sub-skill si el paso tiene varias — y:

```bash
python _plantilla_html/scripts/generar_html.py --data reporte.json \
    --estado flujo_estado.json --paso html_5 -o html_5.html
```

El generador **valida el esquema y falla si algo falta**: un reporte incompleto no se
entrega, se corrige. No uses `--no-strict` para saltarte un error; arregla el JSON.
No escribas el bloque `flujo` a mano: `--paso` lo inyecta.

### 7. Cerrar el paso

```bash
python scripts/estado_flujo.py completar --paso html_5 \
    --skills "2.Descubrimiento/problem-solution-fit" \
    --resumen "<una línea: qué se aprendió>" \
    --veredicto perseverar --outputs html_5.html --datos reporte.json
```

`--resumen` y `--datos` son las dos mitades de lo que hereda el paso siguiente: el resumen
es el índice y `--datos` (el `reporte.json` del paso) son los datos estructurados que se
podrán leer en vez de reteclearlos. Si omites cualquiera de los dos, el script avisa.

Entrega el HTML al usuario, di cuál es el siguiente paso y vuelve al punto 1.

> Si el paso ya tiene su HTML en disco (por ejemplo al retomar un proyecto), pregunta
> antes: **regenerar** o **continuar al siguiente**. Nunca sobreescribas en silencio.

---

## Omitir un paso

El usuario decide cuánto recorrido quiere. Omitir es normal, no un error — pero el hueco queda declarado en todos los reportes posteriores.

```bash
python scripts/estado_flujo.py omitir --paso html_2 \
    --motivo "<lo que dijo el usuario>"
```

Reglas:

1. **`omitible: false`** — el script se niega y explica por qué (`razon_no_omitible`).
   Trasládale el motivo al usuario. Si insiste, repite con `--forzar`: queda marcado
   como **omisión forzada** en el HTML.
2. **El impacto se hereda.** Cada paso posterior recibe el `si_omitido` del paso
   ausente. Cuando falte un input por una omisión: usa un supuesto, márcalo con `*` y
   decláralo en `advertencias` del reporte.
3. **Nunca omitas por tu cuenta.** Solo cuando el usuario lo pida.

---

## Human-in-the-loop

- **Detente en cada diamante.** No auto-avances por un nodo de decisión.
- **Opciones textuales de `pasos.json`**, sin reescribirlas ni añadir opciones nuevas.
- **Confirma los parámetros** de cada sub-skill antes de invocarla.
- **Registra todo** con `estado_flujo.py`: lo que no queda en el estado, no llega al
  siguiente paso ni al HTML.

## Integridad de datos

Nunca inventes cifras. Estimado → `*` o `[REFERENCIA DE INDUSTRIA]`; sin dato →
`[no disponible]`. Si un script puede calcularlo, lo calcula el script: tú redactas
la interpretación, no las cifras.

---

## Referencias

| Para | Mira |
| --- | --- |
| Definición del flujo (fuente única) | `pasos.json` |
| Máquina de estados y comandos | `scripts/estado_flujo.py` (`--help`) |
| Grafo visual | `flujo_mermaid.md` |
| Descripción de cada agente | `flujo_agentes.md` |
| Contrato JSON entre skills | `sub-skills/CONTRATO_JSON.md` |
| Esquema `REPORT_DATA` y contexto del flujo | `_plantilla_html/README.md` |
| Entorno Python y reglas de estilo | `AGENTS.md` |

## Notas de ejecución

- **Python:** activa `skills_env` antes de cualquier script (ver `AGENTS.md`).
- **Rutas:** ejecuta siempre desde la raíz del repositorio — la carpeta que contiene
  `SKILL.md`, `pasos.json` y `sub-skills/`.
- **Idioma:** responde siempre en español, tono claro, conciso y positivo
  (reglas en `AGENTS.md` §7).
- **Modelo recomendado por herramienta:** ver `README.md`.

## ¿Que hacer al final de todo el flujo?

Si estás en la herramienta Claude o usando el modelo del mismo nombre
ejecuta la skill nativa /explain-usage para que el usuario entienda
cuanto ha usado, eso solo si se está usando Claude Cowork, si es un chat simple, no es necesario un resumen de la sesión porque no existe esta funcionalidad.
Finalmente, agradece al usuario por el trabajo realizado.
