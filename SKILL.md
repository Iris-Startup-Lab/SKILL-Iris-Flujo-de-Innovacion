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

## Primer contacto (saludo, presentación o invocación sin tarea)

Cuando el usuario solo saluda, se presenta o invoca la skill sin pedir nada concreto,
**preséntate y dibuja el recorrido antes de pedir datos.** No arranques preguntando el
nombre del proyecto a secas: quien llega no sabe todavía en qué se está metiendo.

Primero comprueba si hay un proyecto a medias:

```bash
python scripts/estado_flujo.py mostrar
```

- **Devuelve un paso** → hay un proyecto en curso. Di cuál es, resume en dos líneas dónde
  quedó y pregunta si quiere continuarlo o empezar otro. No lo sobreescribas.
- **Falla porque no existe `flujo_estado.json`** → es un proyecto nuevo: da la bienvenida.

La bienvenida lleva cuatro cosas, en este orden y sin alargarse:

1. **Qué es esto**, en dos líneas: IRIS lleva una intuición hasta un experimento listo para
   ponerse frente a usuarios reales, en 11 pasos, y cada paso entrega un reporte HTML
   interactivo.
2. **Cómo se trabaja:** paso a paso, y en cada uno decide el usuario — ejecutar, omitir o
   preguntar por qué importa. Nada avanza sin su confirmación, y lo que se omite queda
   declarado en los reportes siguientes.
3. **El recorrido por etapas**, para que vea el mapa completo:

   | Etapa | Pasos | Qué sale |
   | --- | --- | --- |
   | Investigación | 1 | El terreno: mercado, futuros, señales débiles o conversaciones reales |
   | Descubrimiento | 2–6 | A quién le hablas, qué le duele y cómo lo vive hoy |
   | Ideación | 7–10 | El reto creativo, las ideas y su potencial de negocio |
   | Prototipado y Validación | 11 | El experimento que pone la idea frente a usuarios |

   Si pide el detalle de los 11 pasos, dáselo con `python scripts/estado_flujo.py rutas`
   (nómbralos, no los llames `html_N`).
4. **Qué hace falta para empezar:** nombre del proyecto, objetivo y audiencia. Nada más;
   el resto se pregunta cuando toca.

Cierra con **una sola** pregunta, no con cuatro seguidas. Y sigue en «Arranque de un
proyecto».

---

## Arranque de un proyecto

Pide al usuario: **nombre**, **objetivo** y **audiencia**. Todo lo demás se pregunta
paso a paso, cuando toca.

Luego ofrece el recorrido. **Nombra los pasos, no los `html_N`:** al usuario «5 pasos»
o «html_7» no le dicen nada. Pide la lista al script y preséntala:

```bash
python scripts/estado_flujo.py rutas
```

Devuelve los dos recorridos con el título y la etapa de cada paso, y **qué se salta la
ruta mínima con su impacto**. Muestra al usuario:

- **Ruta completa** (11 pasos) — el proceso íntegro.
- **Ruta mínima** (5 pasos) — Investigación → Persona → Reto (HMW) → Ideación →
  Validación. Enumera los 5 por su nombre y di qué se pierde: sin entrevistas ni
  descubrimiento de campo, sin priorización de problemas, sin journey, sin
  dimensionamiento ni modelo de negocio.

No resumas la lista de memoria: sale de `pasos.json` y ahí está al día.

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

Abre nombrando el paso, nunca con su `html_N`: «**Paso 4 de 11 — Persona Profile**». Ver
«Cómo nombrar las cosas ante el usuario».

### 3. Ofrecer ejecutar u omitir

Presenta siempre tres opciones:

- **Ejecutar** — sigue al paso 4.
- **Omitir** — ve a «Omitir un paso».
- **¿Por qué importa?** — lee el `objetivo` del paso y su `si_omitido`, y vuelve a preguntar.

Al describir qué pasa si se omite, traduce el `si_omitido`: sin nombres de carpeta y con el
efecto explicado en una frase, no con un `*` suelto entre paréntesis.

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

Para cada ruta que devolvió `mostrar`, **lee** `sub-skills/<ruta>/AGENTE.md` y ejecuta
sus instrucciones al pie de la letra. (El archivo se llama `AGENTE.md`, no `SKILL.md`: los
gestores admiten un solo `SKILL.md` por paquete y ese es el de esta macro.)

- Antes de invocarla, traslada al usuario sus **Parámetros de Entrada** y confirma los valores.
- Pásale el contexto del flujo (paso 1) para que no repita preguntas ni reinvente supuestos.
- **Pásale también los datos de sus predecesores, no solo el resumen.** `mostrar` imprime,
  por cada predecesor **declarado en `pasos.json`**, la ruta de su `reporte.json`
  (`datos estructurados: …`) o el HTML que los lleva embebidos. Abre **solo esos** —los que
  `mostrar` lista, no toda la cadena de pasos— y toma los bloques que la sub-skill hereda:
  `persona`, `psf`, `secciones[].items[]`. Los bloques no son acumulativos entre reportes
  (`persona` vive en el reporte de Persona Profile, `psf` en el de Problem-Solution Fit), así
  que un paso puede necesitar más de un predecesor declarado; releer toda la cadena cuesta
  **2.4× más** y no aporta nada que no esté en esos predecesores (ver
  `PLAN_MEDICION_TOKENS.md` § Resultados).
- Respeta `cadenas` (ejecución secuencial obligatoria) y `paralelo` (se ejecutan a la
  vez y se consolidan en un solo HTML).

### 5.1 Simular las entrevistas o encuestas

En el paso 2 el usuario decide si ejecuta las entrevistas con usuarios reales o las **simula**.
Si elige simular (opciones «No — simulación de respuestas e insights» y «Simular respuestas»),
entra en juego un **simulador**: una sub-sub-skill que vive dentro de la sub-skill que
normalmente analizaría esos datos.

El orden no cambia el resto del flujo, porque el simulador **solo fabrica el dato de entrada**:

1. **Registra la decisión primero.** Es lo que enciende la marca de simulación en todo el
   proyecto:

   ```bash
   python scripts/estado_flujo.py decision --paso html_2 \
       --nodo "¿Ejecución de entrevistas?" --opcion "No — simulación de respuestas e insights"
   ```

2. **Lee el simulador que `mostrar` indique** (`sub-skills/<ruta>/simulador/SIMULADOR.md`; las
   rutas están en el campo `simuladores` del paso, no se deducen) y escribe con el usuario el
   `plan.json`: el panel de personas, los códigos o características y su **prevalencia
   declarada**. Ese plan es la conversación importante — son los supuestos del equipo puestos
   por escrito para que se puedan discutir.
3. **Ejecuta el script del simulador.** Produce **un CSV** (`*_SIMULADO.csv`) y **no** un HTML.
   Todos los conteos, intervalos y avisos los calcula él: cítalos, no los reescribas.
4. **Invoca la sub-skill padre con ese CSV**, con las mismas instrucciones que usaría con datos
   reales, y sigue en el punto 6 (generar el HTML) como siempre.
5. **Cierra el paso declarando los dos archivos:** `--outputs html_2.html entrevistas_SIMULADO.csv`.

Lo que **no** tienes que hacer: acordarte de etiquetar el reporte. La marca la propaga el flujo
—distintivo «Datos simulados» en la cabecera, caja ámbar en el contexto, advertencia automática
y línea en el pie— en **todos** los HTML posteriores, no solo en el del paso 2. Lo que sí te
toca es que la advertencia sea específica (qué se simuló, con qué `n`, con qué semilla) y que
los items lleven el tag `SIMULADO`: el validador avisa si faltan.

Ante el usuario, dilo sin rodeos: la simulación sirve para **ensayar el instrumento y ver cómo
se leerían los resultados**, y para hacer explícitos los supuestos del equipo. No es evidencia,
y ninguna decisión de inversión debería apoyarse solo en ella. Detalle de la convención y de
los supuestos estadísticos: `sub-skills/SIMULACION.md`.

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

Entrega el HTML al usuario, di cuál es el siguiente paso y vuelve al punto 1. Anuncia el
cierre por el nombre del paso y su posición, no por el nombre del archivo:

- **Mal:** «Paso html_1 completado.»
- **Bien:** «Paso 1 de 11 completado — Inicio + Investigación. Tu reporte está en
  `html_1.html`. Siguiente: paso 2 de 11, Decisión — Entrevistas.»

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

---

## Cómo nombrar las cosas ante el usuario

El usuario no conoce la notación interna del flujo. Tradúcela siempre.

| No digas | Di |
| --- | --- |
| «Paso html_1 completado» | «Paso 1 de 11 completado — Inicio + Investigación» |
| «Ahora vamos a html_5» | «Ahora vamos al paso 5 de 11: Problem-Solution Fit» |
| «persona-profile quedará con supuestos» | «la ficha de persona quedará con supuestos» |
| «2.Descubrimiento/journey-builder» | «el agente Journey Builder» |

**`html_N` es el nombre del archivo que se entrega** (`html_5.html`), no el nombre del paso.
Úsalo solo cuando hables del archivo: «tu reporte está en `html_5.html`». Los títulos de los
pasos salen de `mostrar` y de `estado_flujo.py rutas`; los nombres de carpeta de las
sub-skills (`2.Descubrimiento/persona-profile`) son rutas de disco y **nunca** se le
muestran al usuario.

### El asterisco hay que explicarlo

`*` marca un dato **estimado, no verificado**. Es convención interna: el usuario no la
conoce y un `*` suelto solo confunde. La primera vez que aparezca en la conversación,
dilo con palabras:

> Las cifras marcadas con `*` son estimaciones nuestras, no datos de una fuente citable:
> sirven para dimensionar el orden de magnitud, no para presentarlas como evidencia.

Y al ofrecer una opción, escribe el efecto completo en vez del símbolo a secas:

- **Mal:** «Omitir (persona-profile quedará con supuestos marcados con `*`)»
- **Bien:** «Omitir — la ficha de persona se construirá con supuestos en vez de evidencia
  de campo. Cada dato supuesto se marcará con `*` en el reporte, para que se distinga de un
  dato respaldado.»

Lo mismo con las otras dos marcas, que también hay que explicar la primera vez:

| Marca | Qué significa | Cómo decirlo |
| --- | --- | --- |
| `*` | Estimación propia, sin fuente | «estimado por nosotros, no es un dato citable» |
| `[REFERENCIA DE INDUSTRIA]` | Cifra típica del sector, no medida en este proyecto | «referencia del sector, no un dato de tu caso» |
| `[no disponible]` | No hay dato y no se inventa | «no tenemos ese dato y preferimos dejarlo en blanco antes que inventarlo» |

Cuando preguntes por el acceso a una fuente de pago (Euromonitor, Statista, IWSR…), di qué
pasa si no la hay **en una frase completa**, no con un símbolo entre paréntesis:

> ¿Tienes acceso a Euromonitor, Statista o IWSR? Si no, trabajo con estimaciones de orden de
> magnitud y las marco con `*` en el reporte, para que quede claro que no son cifras de una
> fuente y no se puedan citar como tales.

## Integridad de datos

Nunca inventes cifras. Estimado → `*` o `[REFERENCIA DE INDUSTRIA]`; sin dato →
`[no disponible]`. Si un script puede calcularlo, lo calcula el script: tú redactas
la interpretación, no las cifras. **Y explícale al usuario qué quiere decir cada marca**
(ver «Cómo nombrar las cosas ante el usuario»).

---

## Referencias

| Para | Mira |
| --- | --- |
| Definición del flujo (fuente única) | `pasos.json` |
| Los dos recorridos con el nombre de cada paso | `scripts/estado_flujo.py rutas` |
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

## ¿Qué hacer al final de todo el flujo?

Tras cerrar el último paso (Prototipado y Validación), mide el coste del recorrido y
preséntaselo al usuario. El medidor es `scripts/medir_tokens.py` y se ejecuta desde la
raíz del repositorio:

```bash
python scripts/medir_tokens.py                              # E1 + E3, ruta completa y mínima
python scripts/medir_tokens.py --proyecto <dir>             # añade E2/E4/S1 del proyecto real
```

`<dir>` es la carpeta que guarda `flujo_estado.json` y los `reporte_*.json` del
proyecto (por ejemplo `output/<proyecto>`; si el estado vive en la raíz del repo, usa
`.`). La primera variante funciona siempre, con o sin proyecto.

### Estimar el costo en dinero

Con el modelo que se usó en la sesión (pregúntaselo al usuario si no lo sabes), añade
`--modelo` para obtener el costo por paso y el total:

```bash
python scripts/medir_tokens.py --proyecto <dir> --modelo "Claude Sonnet"
```

Los precios viven en `scripts/precios_modelos.json` (fuente oficial + fecha). Para
verlos o refrescarlos:

```bash
python scripts/medir_tokens.py --precios                  # catálogo completo
python scripts/medir_tokens.py --precios --actualizar     # comprobar fuentes online
```

Si los precios superan su umbral de caducidad (`validez_dias`, 90 por defecto), el
script lo avisa y comprueba solo la accesibilidad de las fuentes; **no** reescribe
las cifras automáticamente. El refresco de precios es manual: relee la fuente oficial
y edita `precios_modelos.json`, nunca estimes de memoria.

Si el modelo **no está** en el catálogo, dilo tal cual: «no tengo precios oficiales
para este modelo todavía; se irán añadiendo conforme avance la skill». No inventes el
precio ni lo estimes de memoria: se añade a `precios_modelos.json` cuando se tenga la
fuente. Si está pero sin precio verificado (ej. `Gemini 3.1 Pro`), avisa de que falta
confirmar el precio en su fuente y no des una cifra.

No vuelques la tabla cruda. Resume en dos o tres líneas lo que importa: cuánto costó de
entrada y de salida el recorrido, el costo estimado en dinero (si hay precio) y la
diferencia entre ruta completa y mínima. Traduce la notación interna (di «tokens de
entrada» y «tokens de salida», no «E1» o «S1»).

Si además estás en Claude Code (Cowork), ejecuta la skill nativa `/explain-usage` para
el uso real de la sesión; en un chat simple esa funcionalidad no existe y se omite.
Finalmente, agradece al usuario por el trabajo realizado.
