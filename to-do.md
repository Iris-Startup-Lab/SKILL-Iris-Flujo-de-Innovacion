# To-do — 24/08/2026

**La revisión del flujo general está escrita y probada.** El pendiente 0 se cerró el 24/08:
las 8 pruebas del script, el recorrido completo de los 11 pasos y la medición del render.
Salieron **5 bugs reales**, los 5 arreglados y vueltos a probar (detalle en «Hecho el
24/08/2026»). **La macro está lista para que la usen personas.**

**Decidido el 24/08:** el ZIP ya está empaquetado, y los proyectos de `output/` **se quedan como
material de revisión futura** — no se re-corren ni se borran, aunque `verificar` marque sus
decisiones antiguas como nodos que el flujo ya no reconoce (es lo esperado: son anteriores al
cambio).

**Las pruebas las harán colegas con casos reales de negocio**, no con recorridos sintéticos. Eso
cierra por la vía útil los pendientes 1 y 8: el nivel 2 de la medición de tokens y el estreno de
un simulador de punta a punta saldrán de ese uso real, que es la única fuente que dice si los
umbrales de los avisos ayudan o estorban.

Lo único que sigue siendo tuyo: regenerar `CLAUDE.md` con `.\actualizar_claude.ps1` cuando
`AGENTS.md` cambie, y decidir qué hacer con `skills_simuladoras_de_entrevistas/` (pendiente 5).

**Nuevo el 21/08** Script .ps1 y .sh para poder generar una copia de AGENTS.md  para convertirla a CLAUDE.md a demanda del usuario
Esto solo lo actualiza la persona no el agente

**Nuevo el 19/08:** las 5 skills simuladoras de entrevistas se integraron al flujo como
**sub-sub-skills** (`<skill>/simulador/SIMULADOR.md`), con estadística calculada por script y la
marca SIMULADO propagándose sola a todos los reportes. Detalle en «Hecho el 19/08/2026».

Los 5 pendientes del 13/08 están cerrados. El rechazo del ZIP por el gestor de habilidades
también: **subida confirmada el 14/08/2026** tras encontrar la causa raíz (barra invertida en las
entradas del ZIP) y tres problemas reales más por el camino.

Pendiente de aprender del uso real: si la skill se comporta bien ya instalada en el gestor.

Los otros dos sospechosos que quedaron **sin confirmar como problema** —el punto en las carpetas
de fase (`1.Investigacion`) y el guion bajo inicial (`_plantilla_html`)— se dejaron como están a
propósito: renombrarlos costaba decenas de referencias y resultó innecesario.

> **Antes de dar algo por hecho, compruébalo en el código.** La fuente de verdad es el repo,
> no este tracker.

Entorno para cualquier prueba (AGENTS.md y/o CLAUDE.md §2):

```powershell
& "E:\Users\1167486\AppData\Local\anaconda3\Scripts\conda.exe" shell.powershell hook | Out-String | Invoke-Expression
conda activate skills_env
```

Nada está commiteado: los commits los lleva el usuario.

---

### 0. Revisión del flujo general — cerrada el 24/08 (5 bugs encontrados y arreglados)

Objetivo cumplido: el agente macro **no puede** saltarse el flujo, no solo está escrito que no
debe. El flujo descrito por el usuario se comparó contra `pasos.json`, aparecieron 8 huecos, se
corrigieron con barreras en el script y se propagó a los 14 documentos que lo describen.

Lo escrito está en «Hecho el 21/08/2026» §8, §9 y §10. **Lo probado, en «Hecho el 24/08/2026».**

Solo quedan las cuatro cosas que dependen del usuario:

#### 0.4 Los dos proyectos ya recorridos — resuelto: se quedan

`output/ecopack-circular` y `output/huertos-urbanos-mx` **se conservan como material de revisión
futura.** No se re-corren ni se borran. Sus decisiones usan nombres de nodo que ya no existen
(«Simular o no», «Selección de agentes», «Elección de protopersona»), así que `verificar` las
marcará como decisiones que el flujo ignora: **es lo esperado**, no un fallo que haya que
arreglar. Tampoco se editan a mano.

#### 0.5 Empaquetado — hecho

El ZIP se empaquetó el 24/08. `CLAUDE.md` se regenera con `.\actualizar_claude.ps1` cada vez que
cambie `AGENTS.md`, y **eso lo hace la persona, no el agente**.

### 1. Terminar la medición de tokens — falta el nivel 2

El **nivel 1 está hecho** (17/08): `tiktoken` instalado en `skills_env`, `scripts/medir_tokens.py`
escrito (emite CSV) y los resultados exactos publicados en `PLAN_MEDICION_TOKENS.md` § Resultados.
E1 = 17,899 tok; E3 completa 124,968 vs mínima 52,721; herencia: declarados 14,875 vs cadena
35,754 (2.4×).

Falta el **nivel 2**: sesión instrumentada, 2× por ruta, con el mismo proyecto congelado. No se
automatiza — requiere una sesión real del usuario por ruta. Checklist en `PLAN_MEDICION_TOKENS.md` §8.

### 2. Decidir la estrategia de herencia — cerrado (hecho)

Decidido: **leer solo los predecesores declarados en `pasos.json`** (los que `mostrar` lista),
no toda la cadena. La cadena completa cuesta 2.4× más y no aporta bloques nuevos — los bloques
no son acumulativos (`persona` está en html_4, `psf` en html_5, html_7 necesita ambos). Escrito
en `SKILL.md` § «El ciclo de un paso», punto 5, y en `PLAN_MEDICION_TOKENS.md` § Resultados.

### 3. Partir el `AGENTE.md` de `senales-debiles` — cerrado (superado)

La modularización **ya está hecha**: orquestador `AGENTE.md` (26,409 car) + `SPEC.md` (18,033) +
`references/fase-0…4` y `design-system.md`. El orquestador sigue en **3.4×** la mediana de las 26
sub-skills, pero su contenido son las reglas globales y el contrato JSON entre fases, no detalle
que deba bajar a `references/`. Si se recortara más, sería cosmético y no urge.

### 4. Avisos de markdownlint que quedan (MD013) — cerrado (hecho)

Creado `.markdownlint.json` en la raíz con `"MD013": false`. La prosa del repo usa líneas largas
a propósito (hasta 747 car en los prompts base), así que desactivar la regla es lo correcto en
vez de reescribir 30 documentos. El editor que use markdownlint lo descubre solo.

### 5. Decidir qué se hace con `skills_simuladoras_de_entrevistas/` — decisión del usuario

Es la carpeta original con las 5 skills hechas en opencode. Su contenido ya está integrado en el
flujo (`<skill>/simulador/`), así que **queda duplicado y fuera del flujo**: quien la encuentre
suelta se llevará una versión sin estadística por script y sin la marca automática.

No la borré: es material del usuario y borrar no es reversible. Cuando confirme que la
integración le sirve, se elimina —o se deja como archivo histórico, pero entonces conviene un
`README.md` dentro que diga «superado por `sub-skills/2.Descubrimiento/*/simulador/`».

### 6. Ver un reporte simulado en el navegador — cerrado el 24/08 (hecho)

Renderizado en Chrome headless: sin errores de JS, el distintivo dorado no se pisa con el de la
skill, y a 320/360/390/480 px el documento no desborda. De aquí salieron dos bugs de render, los
dos arreglados (ver «Hecho el 24/08/2026» §3).

### 7. Guardar una muestra de diseño del reporte simulado — cerrado el 24/08 (hecho)

En `sub-skills_sample_outputs/3.Ideacion/how-might-we/`: el HTML, el `STATE.md` del proyecto que
lo generó y un `LEEME.md` con la tabla de qué marca pone la plantilla y dónde mirarla. La carpeta
está en `.gitignore` —son muestras locales—, así que no viaja en el repositorio.

### 8. Estrenar un simulador en un proyecto real

Ningún proyecto ha corrido todavía la cadena completa **decisión → `plan.json` → CSV → skill
padre → HTML marcado → cierre con los dos archivos**. Es la misma prueba de fuego que quedó
pendiente para `--datos`, y ahora se pueden hacer las dos de una: un proyecto corto que simule
las entrevistas del paso 2, construya la ficha de persona del paso 4 con esa evidencia y
compruebe que la ficha sale marcada como simulada sin que nadie se lo pida.

Lo que hay que mirar con ojo crítico en ese estreno: **si los avisos de los scripts ayudan o
estorban**. Están calibrados a ojo (n<20, Q+R>10%, saturación en 2 sesiones sin novedad), y el
uso real es lo único que dice si el umbral es el correcto.

---

## Hecho el 24/08/2026

Sesión de pruebas del pendiente 0. Se ejecutó todo lo que estaba escrito sin probar, y
aparecieron **5 bugs reales**. Los 5 están arreglados y vueltos a probar.

### 1. Los tres bugs de las barreras del script

**a) Una decisión que dependía de otra se podía responder antes, aceptando cualquier texto.**
El nodo «Apalancamiento» saca sus opciones de la ambición elegida (`opciones_desde`). Si nadie
había registrado la ambición, no había catálogo contra el que comprobar nada y el script
aceptaba lo que le llegara —`--opcion "Cualquier cosa inventada"` entraba con exit 0—. Era
justo el agujero por el que se cuela una opción inventada.
**Arreglo:** `origen_sin_responder()`. Si el catálogo depende de otro nodo sin responder, se
bloquea y se dice cuál hay que preguntar primero. Un `opciones_desde` sin punto («las ideas
generadas en este paso») no depende de nadie: ahí el texto libre sigue siendo correcto.

**b) Las sub-decisiones condicionales se podían registrar antes de saber si aplicaban.**
«Entrega de la landing page» solo aplica si se eligió *Simple Landing Page*, pero `cmd_decision`
no miraba el `solo_si`: se podía registrar antes de elegir el agente, y quedaba en el histórico
una decisión de un nodo que el usuario quizá nunca debió ver.
**Arreglo:** se comprueba `nodo_aplica()` antes de escribir, distinguiendo los dos casos —el
nodo fuente aún sin responder, o respondido con un valor que no cumple la condición—.

**c) Una respuesta se quedaba obsoleta en silencio.** Si registrabas la palanca «Mayor ticket»
(de *Crecer Negocio Actual*) y **después** cambiabas la ambición a *Expandir Negocio*, la
palanca ya no pertenecía a la ambición vigente. En su momento fue válida, así que nada lo
detectaba.
**Arreglo:** `verificar` compara el orden de registro. Si la dependiente se registró antes que
su fuente, lo dice: «se registró ANTES que X, que cambió después». Cubre además los casos de
fuente sin responder y de fuente resuelta con una opción fuera de catálogo.

**Afinado, no bug:** una propuesta legítima (nodo con `permite_propuestas`) y una opción fuera
del catálogo ya no se anotan igual. `propuesta_agente` solo se marca cuando el nodo las admite;
`STATE.md`, el HTML y `verificar` usan la etiqueta que corresponde. Y si **todo** lo elegido
está fuera del catálogo, no se repite el nombre detrás de la opción.

### 2. Lo que las pruebas confirmaron que sí funcionaba

- **Recorrido completo:** 11 pasos, 13 decisiones, `verificar` con exit 0 y sin hallazgos. Las
  cuatro barreras bloquearon donde debían: cerrar sin decisiones, palanca antes de la ambición,
  sub-decisión antes de su condición, y opción de otra ambición.
- **Catálogo:** una opción inventada, un nodo inventado, dos opciones en un nodo de elección
  única y una palanca de otra ambición se rechazan con exit 2 y la lista de lo válido.
- **Tipografía tolerante:** «¿Como quieres iniciar?» sin tilde y «senales debiles…» en
  minúsculas se aceptan y se guardan con el texto canónico de `pasos.json`.
- **Ruta mínima:** omite 6 pasos de entrada y sus nodos no bloquean (un paso omitido no pasa
  por la barrera de decisiones).
- **Herencia del `auto_si`:** elegir simular en el paso 2 deja decidido el origen de las
  respuestas del paso 3, y `mostrar` lista solo los simuladores de los agentes elegidos.

### 3. Los dos bugs de render (y un diagnóstico mío que estaba mal)

**a) Tarjetas desbordando a 320 px.** `.grid` y `.dec-grid` usaban
`minmax(295px,1fr)`: en una pantalla de 320 px el track mínimo era más ancho que el espacio
disponible y las tarjetas sobresalían 14 px, dejando toda la página con scroll horizontal.
**Arreglo:** `minmax(min(295px,100%),1fr)`. Medido después: 0 desbordes a 320 y 360 px.

**b) La cabecera se recortaba en silencio.** `.header-top` es un flex sin `flex-wrap`, y el
`header` lleva `overflow:clip`. En pantalla estrecha, el logo + la etiqueta de la skill + el
distintivo de datos simulados + el botón no caben en una línea y los últimos **desaparecían**
recortados, sin dejar rastro. **Arreglo:** `flex-wrap:wrap`, y bajan a una segunda línea.

**El diagnóstico que estaba mal, y por qué importa:** las primeras capturas «de móvil» las hice
con `--window-size=390`, y de ahí concluí que la página desbordaba a 390 px. Era falso: Chrome
headless en Windows **no baja de ~485 px de viewport** y estaba recortando una imagen de 390 px
sobre un render de 485. La conclusión correcta salió al medir con una sonda que fuerza el ancho
por CSS y compara los rectángulos contra el objetivo: a 390 px `scrollWidth == 390`, sin
desborde. El `flex-wrap` sigue siendo un arreglo válido, pero por el recorte, no por el scroll.
**Una captura recortada no es una medición.**

### 4. Afinado del validador

`fuentes` y `advertencias` son listas de **texto plano**; la plantilla las pinta con `esc()`, así
que un objeto salía como `[object Object]` sin que nadie se enterase. El validador solo decía
«entrada vacía», que despista porque el problema es el tipo. Ahora es un ERROR que nombra el
tipo y dice qué se espera.

### 5. Herramientas de prueba (en el scratchpad, no en el repo)

- `recorrido.py` — recorre los 11 pasos comprobando que cada comando devuelve el exit esperado.
- `sonda_ancho.py` + `probar_anchos.ps1` — inyectan la sonda de desbordes y la corren a varios
  anchos. Es lo único que da una respuesta fiable sobre el render estrecho.
- `comprobar_nodos.py` — extrae **todos** los comandos `decision` de los `.md` del repo y los
  valida con las funciones reales del script. 0 nodos u opciones inexistentes.

### 6. Regresión final

`py_compile` de los 6 scripts · `node --check` del JS de la plantilla · coherencia
`pasos.json` ↔ Mermaid (39 nodos declarados = 39 definidos, sin huérfanos ni aristas rotas) ·
11 pasos y 13 nodos de decisión · recorrido completo con `verificar` en 0 · los reportes
`html_4` y `html_5` del proyecto ecopack regenerados con la plantilla nueva y medidos sin
desborde a 320 y 390 px (el `html_4` incluye tablas de persona con `min-width:640px`, que siguen
conteniéndose en su propio contenedor con scroll).

## Hecho el 21/08/2026

### 1. Render del HTML — encabezado cortado y tarjetas expandibles

- **Encabezado cortado en los pasos finales (html_9 en adelante).** Causa raíz:
  `scrollIntoView({inline:'center'})` desplazaba también el `header` (que con
  `overflow:hidden` es contenedor de scroll), recortando logo y título. Arreglo en
  `reporte_base.html`: `overflow:clip` (con fallback `hidden`) y `scrollLeft` manual del riel
  (con clamp y re-centrado al cargar Sora/Inter).
- **Botón «Ver detalle» vacío.** Oculto cuando la tarjeta no tiene `body`/`persona`/`psf`/`chart`
  (`tieneDetalle()` + clase `.no-detail`).
- **Panel de detalle mal ubicado.** Antes iba al fondo de la grilla (abajo de todas las tarjetas);
  ahora `insertarDetalle()` lo coloca justo debajo de la fila de la tarjeta elegida.

### 2. Legibilidad para expertos y no expertos

- **Nada de abreviaturas en los pasos.** `pasos.json`: «HMW + Ambición estratégica» →
  «El reto creativo (How Might We) + Ambición estratégica»; «Elección de protopersona» →
  «Elección de la ficha de persona»; sin «protopersona/JTBD» en objetivo y `razon_no_omitible`.
  Referencias actualizadas en `SKILL.md`, `README.md`, `flujo_agentes.md`, `flujo_mermaid.md`,
  `PLAN_MEDICION_TOKENS.md` y `_plantilla_html/README.md`.
- **Plantilla:** «Score»→«Puntaje», «JTBD»→«El trabajo que quiere hacer (Job To Be Done)»,
  «Pains»→«Problemas…», «Protopersona»→«Persona hipotética», «N/D»→«[no disponible]», badges
  «Paso N» en vez de `html_N` en el contexto, y leyenda siempre visible «Cómo leer este reporte».
- **Skills de Descubrimiento:** sección «Vocabulario en el texto visible» en `persona-profile`,
  `problem-solution-fit`, `day-in-the-life` y `discovery-survey`; etiquetas de `ficha-persona.md`
  y `analisis-psf.md` en lenguaje claro (claves del JSON intactas: `pains`, `jtbd`, `psf`…).

### 3. Medición de tokens + costo en dinero

- **Bug:** `medir_tokens.py --proyecto` crasheaba con `UnicodeDecodeError` en Windows (leía stdout
  de `estado_flujo.py` como UTF-8 cuando salía en cp1252). Arreglo: `PYTHONIOENCODING=utf-8`.
- **`SKILL.md` § «¿Qué hacer al final de todo el flujo?»** ahora ejecuta `medir_tokens.py`.
- **Precios y costo:** `scripts/precios_modelos.json` (catálogo curado con fuente y fecha) +
  flags `--modelo` (costo por paso y total), `--precios` (catálogo) y `--precios --actualizar`
  (chequeo de accesibilidad). Caducidad `validez_dias: 90`: avisa y hace fetch de accesibilidad,
  **no** reescribe cifras (el refresco es manual, integridad de datos).

### 4. Entradas del usuario y arranque intermedio

- **`SKILL.md` § «Qué archivos puede adjuntar»:** solo texto e imágenes; audio/video requieren
  transcripción externa y se orienta al usuario a convertir (gratis/pago).
- **`SKILL.md` § «Empezar desde un paso intermedio»:** al saltar a un paso N se omiten los previos
  y **se piden sus materiales** antes de ejecutar (si el usuario los aporta, son evidencia; si no,
  supuestos `*`).

### 5. Navegación entre los 11 HTML

- **`scripts/generar_indice.py`** (nuevo): genera `index.html`, tablero con los 11 pasos, estado y
  «Abrir reporte» por completado. Los enlaces del riel son relativos y funcionan en el navegador
  con los HTML en la misma carpeta; en el preview embebido del gestor no (sin sistema de archivos).
  El riel abre en pestaña nueva (`target="_blank"`). Documentado en `SKILL.md`, `README.md` y `AGENTS.md`.

### 6. Bug `estado_flujo.py`

- Crascaba en Windows al imprimir `→` (U+2192, no está en cp1252) en `decision`/`completar`.
  Arreglo: `sys.stdout/stderr.reconfigure(encoding="utf-8")` al arrancar.

### 8. El flujo descrito por el usuario contra `pasos.json` — 8 huecos, corregidos

Se comparó el flujo de 11 pasos tal como lo describió el usuario contra la definición real. Lo
que faltaba o estaba mal colocado:

| Hueco | Qué pasaba | Corrección |
| --- | --- | --- |
| Selección de agentes de descubrimiento | Colgaba del paso 2, no del 3: el agente preguntaba «cuáles ejecuto» un paso antes de ejecutarlos | Movida al paso 3, con `minimo: 1` y `ofrecer_todos` |
| Selección de agentes de ideación | Igual: colgaba del paso 7 | Movida al paso 8, con `minimo: 1` |
| Dos nodos que se contradecían | El paso 2 preguntaba «¿entrevistas sí o no?» y después «¿simular o no?», y se podía elegir «No — simulación» y luego «No simular» | Un solo nodo con 3 opciones excluyentes: reales / simuladas / solo el guion |
| Paso 5 sin la tercera opción | Solo «problema más grande» y «tamaño de mercado» | Añadida «Por otro criterio que recomiende el agente» (`requiere_propuesta`) |
| «IA» como palanca | Abreviatura, contra la regla de no abreviar | «Inteligencia artificial», con las cuatro preguntas que hay que responder para que la palanca sea real y no una etiqueta de moda |
| «Ecosistema» sin explicar | El usuario pidió explícitamente explicarlo | `glosario` nuevo en el nodo de palancas: las 7 palancas que no se entienden solas, explicadas |
| Paso 11 sin sub-decisiones | No se preguntaba si la landing es demo o guion, ni de dónde sale la página a analizar | Dos nodos con `solo_si` estructurado, que aparecen solo si se eligió su agente |
| Ninguna selección múltiple tenía mínimo | Se podía «elegir» cero agentes y cerrar el paso igual | `minimo: 1` en los pasos 3, 8 y 11 |

Además, `pasos.json` gana un bloque `convenciones_decisiones` que documenta qué significa cada
campo de un nodo (`minimo`, `ofrecer_todos`, `glosario`, `solo_si`, `permite_propuestas`,
`requiere_propuesta`, `efecto`, `agente`) y quién lo hace cumplir.

### 9. Barreras en `estado_flujo.py`: el flujo se hace cumplir, no solo se describe

La causa de que el agente macro se saltara el flujo era estructural: **nada comprobaba nada**.
`decision` aceptaba cualquier texto como nodo y como opción, y `completar` cerraba un paso sin
mirar si sus decisiones existían. La prosa de `SKILL.md` era la única defensa, y un documento no
puede impedir nada.

- **`decision` valida contra el catálogo.** Rechaza (exit 2) un nodo que no esté en el paso, una
  opción que no esté en su lista, dos opciones en un nodo `unica` y menos opciones que el
  `minimo`. Los mensajes listan lo válido, así que el error se corrige en el mismo turno.
- **La comparación es tolerante con la tipografía y estricta con el contenido:** sin acentos, sin
  mayúsculas y con cualquier guion largo reducido a `-`. «No - simulacion» entra como
  «No — simulación de respuestas e insights», y **se guarda el texto canónico de `pasos.json`**,
  no el que escribió el agente. Así el histórico no se llena de variantes del mismo valor.
- **Nodos `multiple` de verdad.** `--opcion` se repite (`--opcion A --opcion B`) y se guarda
  `opciones: [...]`. `opcion` sigue siendo el texto plano de antes, así que los proyectos ya
  empezados, `STATE.md` y el bloque `flujo` del HTML no se enteran del cambio.
- **`completar` se niega a cerrar un paso con decisiones sin registrar.** Es la barrera que
  ataca el fallo real: ejecutar las sub-skills eligiendo por el usuario y cerrar como si él
  hubiera decidido. `--forzar` cierra igual y lo anota en el histórico
  (`decisiones_sin_registrar`), que es lo que después detecta `verificar`.
- **`mostrar` ya no obliga a cruzar dos listas.** Cada nodo sale marcado `RESPONDIDA → «x»`,
  `PENDIENTE` o `no aplica por ahora`, con su `efecto`, su glosario, su mínimo y una línea
  `BARRERA` al final con lo que impide cerrar. Las sub-skills salen marcadas
  `[ELEGIDA por el usuario]` o `(no elegida: no la ejecutes)`, y con la simulación activa solo
  se listan los simuladores de los agentes elegidos.
- **`solo_si` y `opciones_desde` se evalúan.** `solo_si` estructurado (`{nodo, opcion}` o
  `{nodo, incluye}`) decide si el nodo aplica; en texto libre no se puede evaluar, así que se da
  por aplicable y **no** bloquea —una condición que el script no entiende no puede detener el
  flujo—. `opciones_desde` resuelve las palancas de la ambición elegida.
- **`verificar` (comando nuevo).** Audita el proyecto contra `pasos.json` y responde una sola
  pregunta: qué se cerró sin preguntar lo que había que preguntar. Detecta pasos cerrados sin
  decisión, sin resumen, sin `--datos` o sin entrega; omisiones sin motivo; predecesores saltados
  con `--forzar`; y decisiones cuyo nodo no existe en el flujo. Exit 2 si encuentra algo.

**Verificado:** `py_compile` limpio; `pasos.json` válido con los 11 pasos y 14 nodos; los 5 casos
de bloqueo (decisión sin registrar, opción inventada, nodo inventado, dos opciones en un `unica`,
mínimo incumplido) devuelven exit 2 con el mensaje correcto; una opción escrita sin acentos ni
mayúsculas se acepta y se guarda canónica; un nodo `multiple` con dos opciones se registra y
recuerda lo que queda pendiente; la marca de simulación del paso 2 se hereda al 3 y filtra los
simuladores a los 2 agentes elegidos de 4.

**No verificado todavía:** lo que queda en el pendiente 0 (palancas del paso 7, sub-decisiones del
paso 11, propuestas con `--forzar`, `verificar` sobre un proyecto completo).

**Archivos tocados:** `pasos.json` (11 pasos + bloque `convenciones_decisiones`) ·
`scripts/estado_flujo.py` (`_norm`, `_elegidas`, `decision_registrada`, `buscar_nodo`,
`opciones_declaradas`, `nodo_aplica`, `decisiones_sin_resolver`, `_revisar_decisiones`,
`cmd_verificar`, `cmd_decision` reescrito, `cmd_mostrar` ampliado, `detectar_simulacion` y
`render_state_md` retocados, CLI con `--opcion` repetible y `--forzar` en `decision`).

### 10. Propagación a la documentación y a las sub-skills

Cerrado el estado intermedio: el flujo nuevo está ahora en los 14 documentos que lo describen o
lo ejecutan, no solo en el script.

**`SKILL.md`** — cuatro cosas nuevas y una contradicción resuelta:

- **Las «tres reglas» son cuatro:** se añadió *cada decisión del paso la registra el usuario, o
  el paso no cierra*, con la nota de que las reglas 1 y 3 las comprueba el script y que
  `--forzar` deja rastro.
- **Paso 8 del ciclo, «Preguntar si sigue»:** cerrar un paso no autoriza el siguiente. Y el
  punto 3 pasó de tres opciones a cuatro, con **«Parar aquí por ahora»** — que no es omitir.
  Nueva sección **«Pausar el proyecto»**: parar deja el paso pendiente y no declara ningún hueco;
  omitir sí. Con la excepción escrita: si el usuario pide encadenar pasos sin preguntar, se
  encadena, pero las **decisiones** de cada paso se siguen preguntando.
- **Punto 4 reescrito:** `mostrar` marca cada nodo PENDIENTE / RESPONDIDA / no aplica y esa es la
  agenda del paso. Documentados `minimo`, `ofrecer_todos`, `glosario`, `solo_si`,
  `opciones_desde`, `auto_si` y el `--opcion` repetido. Y la regla explícita: **preguntar antes
  de ejecutar** en los pasos 3, 8 y 11.
- **«Cuándo puedes proponer una opción nueva»** (sección nueva). Human-in-the-loop decía «sin
  añadir opciones nuevas» y el usuario pidió lo contrario para el paso 7. La regla ya no se
  contradice: **prohibido quitar, renombrar, fusionar o reordenar** las declaradas; **permitido
  añadir** donde el nodo trae `permite_propuestas`, marcado como propuesta, con justificación y
  registrado con `--forzar`. Aparte, `requiere_propuesta` (paso 5): la opción es oficial y lo que
  se propone es su contenido.
- `verificar` al cerrar el flujo, y en la tabla de referencias.

**`AGENTS.md`** — §6 con los cuatro invariantes y el porqué de que el tercero viva en el script;
la lista de «Además» con pausar ≠ omitir, preguntar antes de ejecutar y la regla de propuestas;
fila de `verificar` y de `convenciones_decisiones` en §8. **`CLAUDE.md` no se tocó**: es copia
de `AGENTS.md` y la regenera el usuario (pendiente 0.5).

**Las vistas de `pasos.json`, que decían el flujo viejo:**

- **`flujo_mermaid.md`:** fuera `N34` («Simular o no»); `N31` renombrado a «Selección de agentes
  de descubrimiento» y movido al subgrafo del paso 3; nuevos `N37` (origen de las respuestas),
  `N38` (entrega de la landing) y `N39` (origen de la página); tres ramas en `N35`; arista
  punteada para la propuesta del agente; «IA» → «Inteligencia artificial». Los `nodo_mermaid` de
  `pasos.json` se reajustaron en 5 pasos. **Comprobado:** 39 declarados = 39 definidos, sin
  huérfanos y sin aristas que citen un nodo inexistente.
- **`flujo_agentes.md`:** puntos de decisión de los pasos 2, 3, 7, 8 y 11 reescritos; tabla final
  con **los 13 nodos** del flujo, su tipo y sus opciones; nota de por qué se unificaron los dos
  nodos del paso 2; y las cuatro preguntas que exige la palanca de Inteligencia artificial.
- **`README.md`:** sección «Comprobar que se respetó el flujo» con las dos barreras y
  `verificar`; `mostrar` documentado con sus marcas nuevas.
- **`PLAN_MEDICION_TOKENS.md`:** las decisiones del plan de medición movidas a su paso correcto.

**Las sub-skills afectadas:**

- **`how-might-we/references/matriz-ambicion-palancas.md`** reescrita: «Inteligencia artificial»
  en vez de «IA», las 7 palancas que no se entienden solas con su explicación, la regla de
  propuestas (añadir sí, quitar no) y las cuatro preguntas obligatorias de la palanca de IA.
- **`landing-page/AGENTE.md`:** sección **«Modo de entrega»** — demo construida (`landing_demo.html`,
  autocontenido) o solo el guion para una herramienta externa, sin generar código. El alcance ya
  no dice «no construye la página»: dice que no la **publica**.
- **`landing-ux-analyzer/AGENTE.md`:** las cuatro formas de recibir la página con **qué se puede
  auditar y qué queda fuera en cada una** (un archivo HTML no da render; una captura no da
  estados interactivos). Paso 0: sin material no se arranca.
- **`SIMULACION.md`** y el **`SIMULADOR.md`** de entrevistas: fuera la referencia al nodo
  «Simular o no»; añadido que en el paso 3 la decisión viene por `auto_si` y que los simuladores
  a usar son los de los agentes elegidos.
- **`_plantilla_html/templates/reporte_base.html`:** una decisión con `fuera_de_catalogo` se
  pinta «(propuesta del agente)» en el contexto — era el pendiente 9 del ciclo anterior.
  Documentado en `_plantilla_html/README.md`, junto al campo `opciones` de las decisiones
  múltiples.
- **`ejemplos_para_testear.md`:** los 9 comandos con nodos viejos corregidos, los `multiple` con
  `--opcion` repetido, y añadidas las decisiones del paso 3 y la sub-decisión de la landing.
- **`mindmanager_converter.py`:** **no** se cambió su mapeo, a propósito — sus claves son los
  nombres del mapa mental original y cambiarlas rompería el conversor contra su propia entrada.
  Lleva un aviso en la cabecera explicándolo.

**Verificado en esta ronda:** `py_compile` de los 4 scripts tocados; `pasos.json` válido (11
pasos, 13 nodos); coherencia `pasos.json` ↔ Mermaid en los tres sentidos; `node --check` del JS
de la plantilla; y un comprobador que extrae **todos** los comandos `decision` de los `.md` del
repo y los valida con las funciones reales del script: **0 nodos u opciones inexistentes** (el
único aviso es un `html_N` de plantilla en el `STATE.md` generado).

**No verificado:** todo lo del pendiente 0. Nada de esto se ha ejecutado como flujo.

### 7. Simulación completa de prueba — «EcoPack Circular»

Recorrido de punta a punta en `output/ecopack-circular/` con supuestos (sin investigación real):
11 pasos ejecutados, 8 decisiones registradas, 11 HTML + `index.html` + `STATE.md` + 11
`reporte_html_N.json`. Verificado con Chrome headless: los 11 renderizan sin errores de JS, con el
riel de 11 pasos, la marca **Datos simulados** propagada desde el paso 2 y el encabezado sin cortar.

## Hecho el 19/08/2026

### Simuladores de entrevistas y encuestas, integrados como sub-sub-skills

Las 5 skills que el usuario había creado en opencode (`skills_simuladoras_de_entrevistas/`)
quedaron dentro del flujo, con tres cambios de fondo respecto al original.

**1. Ubicación y convención.** Cada simulador vive dentro de la sub-skill que analizaría esos
datos, con el archivo de instrucciones llamado **`SIMULADOR.md`** —ni `SKILL.md` (uno por ZIP, y
lo ocupa la macro) ni `AGENTE.md` (lo ocupa la sub-skill padre):

```text
sub-skills/2.Descubrimiento/<skill>/simulador/
├── SIMULADOR.md
└── scripts/simular_<x>.py
```

Convención escrita en **`sub-skills/SIMULACION.md`** (nueva, canónica) y en AGENTS.md §4.1.

**2. Un CSV y nada más.** El simulador fabrica el dato; no analiza, no genera HTML y no cierra
pasos. La skill padre analiza ese CSV con los mismos scripts que usaría con datos reales — por
eso `clasificar_kano.py` se come el CSV simulado sin cambios. Los CSV se llaman `*_SIMULADO.csv`
y llevan columna `simulado` y `seed` en cada fila, para que el archivo se declare solo si se
separa de su contexto.

**3. La estadística la hace el script, no el LLM.** El LLM escribe un `plan.json` con el
contenido cualitativo (panel de personas, códigos, citas) y las **prevalencias declaradas**; el
script sortea, cuenta y calcula. Lo que aporta cada uno:

| Simulador | Instrumento | Estadística |
| --- | --- | --- |
| `simular_kano.py` | Kano funcional × disfuncional | Matriz oficial (idéntica al clasificador, 25 celdas verificadas), moda por feature, IC de Wilson, coeficientes de Berger CS/DS —suprimidos si la base A+O+M+I no llega a la mitad—, tasa de descartables, margen de error |
| `simular_discovery.py` | Encuesta de descubrimiento | Proporciones con IC de Wilson, `n` requerido con las fórmulas de `calcular_muestra.py` (+ población finita y envíos), prueba z de dos proporciones entre segmentos |
| `simular_entrevistas.py` | Entrevistas 1:1 | Conteos y **curva de saturación** de códigos. Sin porcentajes: con n=6 el margen sería de ±40 pp |
| `simular_aditl.py` | Observación etnográfica | Conteos por tipo (incl. workarounds) y saturación por sesión; avisa de jornadas sin fricciones |
| `simular_expo.py` | Interacciones en feria | Conteos, saturación, asistentes vs. expositores, `solo_tipo` para que los hallazgos de competencia solo salgan de expositores |

Los cinco: semilla obligatoria (reproducible byte a byte), `ruido` que encoge la prevalencia
hacia 0.5 para que el resultado no salga de laboratorio, aviso si ningún código refuta la
hipótesis, y el límite **«validez externa: nula»** impreso en cada ejecución. Sin esa frase los
intervalos serían decoración pseudo-científica: describen al generador, no a una población.

**4. La marca SIMULADO se propaga sola.** La opción de `pasos.json` marcada
`marca_simulacion: true` (dos opciones de `html_2`) enciende `flujo.simulacion` en el contexto
del flujo, y de ahí sale, en **todos** los HTML posteriores: distintivo dorado «Datos simulados»
en la cabecera, caja ámbar «esto no es evidencia de campo» como primer bloque del contexto,
`DATOS SIMULADOS` en el pie, prefijo `SIMULADO ·` en el título de la pestaña y una advertencia
automática si ninguna de las declaradas menciona la simulación. Ninguna skill tiene que
acordarse de etiquetar. Para skills sueltas hay `meta.simulado: true`.

**Archivos tocados:** `sub-skills/SIMULACION.md` (nuevo) · 5 × `simulador/SIMULADOR.md` (nuevos)
· 5 × `simulador/scripts/simular_*.py` (nuevos) · `pasos.json` (`marca_simulacion` + campo
`simuladores` en html_2/html_3) · `scripts/estado_flujo.py` (`detectar_simulacion`, bloque
`flujo.simulacion`, aviso en `mostrar`, banner en `STATE.md`) ·
`_plantilla_html/templates/reporte_base.html` (distintivo, caja, pie, título, advertencia
automática) · `_plantilla_html/scripts/validar_report_data.py` (`_validar_simulacion`: 2 WARN) ·
`_plantilla_html/README.md` · `AGENTS.md` (§3, §4, §4.1, §8) · `SKILL.md` (§5.1) ·
`sub-skills/CONTRATO_JSON.md` (regla 5) · 5 × `AGENTE.md` y 5 × `README.md` de las skills padre ·
`flujo_agentes.md` · `README.md`.

**Verificado:** `py_compile` de los 5 scripts + los 2 modificados; los 5 simuladores ejecutados
con planes reales; reproducibilidad por semilla (mismo hash con la misma, distinto con otra);
matriz Kano del simulador **idéntica** a la del clasificador y conteos coincidentes (200 filas);
`clasificar_kano.py` consume el CSV simulado sin cambios; validaciones de plan inválido devuelven
exit 2 con mensaje útil; detección de la simulación en `mostrar` (antes/después de registrar la
decisión), en los 4 simuladores de html_3 y en `STATE.md`; HTML generado con
`flujo.simulacion.activo` y las cuatro marcas presentes; los 2 WARN del validador cuando la skill
olvida la marca; script inline de la plantilla pasa `node --check`; ZIP de sub-skill suelta con el
simulador dentro, un solo `SKILL.md`, 0 barras invertidas y la referencia `../AGENTE.md` reescrita
a `../SKILL.md`; ZIP completo de la macro con los 5 simuladores (177 entradas, un `SKILL.md`);
comprobación de rutas seguras sin hallazgos.

**No verificado:** el render en un navegador (ver pendiente 6).

## Hecho el 17/08/2026

### 1. Medición de tokens — nivel 1 ejecutado

- **`tiktoken` instalado** en `skills_env` (0.14.0) y `scripts/medir_tokens.py` escrito: mide
  E1 (arranque fijo), E3 (sub-skills por ruta) y, con `--proyecto`, E2 (briefing de `mostrar`),
  E4 (herencia en tres estrategias) y S1 (salida). Emite CSV.
- **Resultados publicados** en `PLAN_MEDICION_TOKENS.md` § Resultados. Confirmó que el estimador
  `÷4` subestimaba un 18% (E1 real 17,899 vs ~15,145).
- **Pendiente nivel 2** (sesión instrumentada, 2× por ruta): requiere sesión real del usuario.

### 2. Estrategia de herencia decidida

**Predecesores declarados** (los que `pasos.json` lista), no la cadena completa. La cadena cuesta
2.4× más (35,754 vs 14,875 tokens en el recorrido de 6 pasos) y no aporta bloques: `persona` y
`psf` viven en reportes distintos. Escrito en `SKILL.md` § «El ciclo de un paso», punto 5.

### 3. Avisos de markdownlint (MD013) cerrados

`.markdownlint.json` en la raíz con `"MD013": false`. La prosa larga es la convención del repo
(hasta 747 car en los prompts base), no un defecto.

---

## Hecho el 14/08/2026

### Cuarta ronda: la CAUSA RAÍZ — barra invertida en las entradas del ZIP — **hecho**

`Compress-Archive` escribía las 171 entradas con la barra invertida de Windows
(`iris-flujo-de-innovacion\SKILL.md`). El formato ZIP exige `/`, y el validador del gestor —que
corre en Linux— lee el `\` como **parte del nombre del archivo**: de ahí
`Zip file contains path with invalid characters`. Las tres rondas anteriores arreglaron problemas
reales, pero ninguno era este.

**Aviso lo dio Gemini**, y mi verificación previa lo había ocultado: `zipfile` de Python
**normaliza** `\` a `/` en Windows dentro de `ZipInfo.__init__`, así que `namelist()` devolvía 0
backslashes. Falso negativo. La comprobación válida es `orig_filename` o los bytes del directorio
central:

```text
namelist()      -> 0 entradas con backslash   (MIENTE en Windows)
orig_filename   -> 171 de 171
bytes del ZIP   -> 171 con 0x5C, 0 con 0x2F
```

**Arreglo:** `empaquetar_skill.ps1` ya no usa `Compress-Archive`. Construye el ZIP con
`System.IO.Compression.ZipArchive` y escribe el nombre de cada entrada a mano, normalizando a `/`.
De paso desaparecen las 6 entradas de directorio (171 → 165 entradas, solo archivos).

**Guardia nuevo:** los dos scripts **releen el directorio central del ZIP escrito** y avisan si
alguna entrada lleva `0x5C`. Es la única comprobación que no se puede falsear con herramientas que
normalizan rutas.

**Verificado:** el ZIP final tiene 165 entradas, **0 con `0x5C` y 165 con `0x2F`**; el guardia se
validó en los dos sentidos (avisa en un ZIP con backslashes hecho a propósito, calla en el bueno);
extraído en limpio el flujo corre y las 26 rutas resuelven. La sub-skill suelta también sale con
barras normales.

**No reproducible a demanda:** en pruebas posteriores con estructuras equivalentes,
`Compress-Archive` (módulo 1.2.5, PowerShell 7.6.3) sí escribió `/`. No documento un mecanismo que
no pude aislar; lo que consta es que el paquete real salió con `\` 171 de 171 veces, que ya no
dependemos de ese cmdlet y que el guardia detectaría cualquier regresión.

### Tercera ronda: `Zip must contain exactly one SKILL.md file` — **hecho**

Con los caracteres y la estructura ya arreglados, el gestor pasó al siguiente validador:
**exactamente un `SKILL.md` por ZIP**, y el paquete llevaba 27 (el de la macro más los 26 de las
sub-skills).

**Solución:** el archivo de instrucciones de cada sub-skill se llama ahora **`AGENTE.md`** —el
repo ya llamaba «agente» a cada sub-skill (`flujo_agentes.md`, «Agente HMW»…)—. Los 26 se
renombraron con `git mv`; el único `SKILL.md` del repositorio es el de la macro, en la raíz.

**El truco que evita dos verdades:** al empaquetar una sub-skill suelta (`-SubSkill`), el script
le devuelve el nombre `SKILL.md` —el archivo **y** las referencias de texto dentro del paquete—,
porque en ese ZIP la sub-skill sí es la skill. Así cada paquete es coherente consigo mismo y el
repo tiene una sola convención.

Referencias actualizadas: `pasos.json` (`nota_rutas`), `SKILL.md` de la macro (paso 5 del ciclo),
`AGENTS.md` (§3, §4 y §5), `scripts/estado_flujo.py` (lo que imprime `mostrar`),
`_template_generador_skill.py`, `README.md` y las 13 auto-referencias dentro de `sub-skills/`
(casi todas de `senales-debiles`).

**Guardia nuevo:** los dos scripts cuentan los `SKILL.md` del stage y avisan si no hay exactamente
uno, nombrando los culpables.

**Verificado:** el ZIP tiene 1 `SKILL.md` y 26 `AGENTE.md`; extraído en limpio, `init` y `mostrar`
funcionan y las 26 rutas de `pasos.json` resuelven a un `AGENTE.md` real; el ZIP de
`senales-debiles` suelta trae 1 `SKILL.md`, 0 `AGENTE.md` y su texto ya dice `SKILL.md`; el
guardia se probó duplicando un `SKILL.md` y avisa con la lista.

### Segunda ronda: eran DOS problemas — **hecho**

Quitar los acentos no bastó: el gestor seguía respondiendo `Zip file contains path with invalid
characters`. La auditoría carácter por carácter del ZIP encontró **dos causas más**, una de
caracteres y otra de estructura.

**a) Caracteres.** Además de los acentos sobraban:

- **40 espacios** en 22 rutas (`How Might We.md`, `Landing Page.md`…), incluida
  `Referral builder .md` con un espacio antes de la extensión.
- **un `&`** en `Journey Builder & Structure.md`.

Las 22 estaban todas en `Documentos_prompts_base_md/` y `_docx/`. Los 48 archivos de las dos
carpetas se renombraron a kebab-case con `git mv` (`journey-builder-structure.md`,
`referral-builder.md`, `how-might-we.md`…). Referencias actualizadas en la tabla de
`PLAN_CONVERSION_SKILLS.md`. **Regla nueva, más estricta que «solo ASCII»:** los nombres usan
solo `[A-Za-z0-9._-]`.

**b) Estructura.** La documentación oficial exige **una sola carpeta de primer nivel llamada
igual que el `name` del frontmatter**; el ZIP ponía los archivos sueltos en la raíz. Los dos
scripts ahora leen el `name` del `SKILL.md`, envuelven todo en `iris-flujo-de-innovacion/` y
avisan si ese `name` no es `[a-z0-9-]`. En el modo `-SubSkill`, `_plantilla_html/` pasó a ir
**dentro** de la carpeta de la sub-skill, porque todo el ZIP tiene que colgar de una sola raíz.

**Verificado:** el ZIP tiene una única carpeta raíz que coincide con el frontmatter, 0
caracteres fuera de `[A-Za-z0-9._-]`, 0 espacios, 0 `&`, 27 `SKILL.md` (1 de la skill + 26 de
sub-skills como recurso). Extraído en limpio, el flujo corre entero desde dentro: `init`,
`mostrar` con rutas ASCII y generación de HTML con el logo oficial.

**Pendiente de confirmar contigo:** si 27 `SKILL.md` en un mismo ZIP molestan al gestor. La
documentación no lo prohíbe —los recursos empaquetados son explícitamente compatibles— y el error
que da es de caracteres, no de estructura, pero no está documentado. En
`output/diagnostico-zip/` quedaron 3 ZIP para aislarlo subiéndolos en orden: `1-minimo.zip`
(1 `SKILL.md`), `2-con-subskills.zip` (27) y `3-completo.zip`.

### Rutas solo ASCII: primer intento — **hecho, pero insuficiente por sí solo**

El gestor rechazaba el ZIP con `Zip file contains path with invalid characters`. **Causa:** las
rutas con acento. El ZIP estaba bien formado (separador `/`, bandera UTF-8 correcta, sin
backslashes); lo que sobraba eran 103 rutas no-ASCII —88 en `sub-skills/` y 15 en
`Documentos_prompts_base_md/`— por tres caracteres: `ó`, `í` y `é`. Los espacios en los nombres
no eran el problema.

Renombrado en el repo con `git mv` (historial preservado, git lo registra como *rename*):

| Antes | Ahora |
| --- | --- |
| `1.Investigación/` | `1.Investigacion/` |
| `3.Ideación/` | `3.Ideacion/` |
| `5.Validación/` | `5.Validacion/` |
| `Entrevistas de Empatía.md` / `.docx` | `Entrevistas de Empatia.…` |
| `Dimensionador Estratégico de Ideas.md` / `.docx` | `Dimensionador Estrategico de Ideas.…` |
| `Ideación.md` / `.docx` | `Ideacion.…` |

Las 9 carpetas se renombraron en `sub-skills/`, `Documentos_prompts_base_md/` y
`Documentos_prompts_base_docx/`, más `sub-skills_sample_outputs/Investigación`.

Referencias de ruta actualizadas: `pasos.json` (32), `flujo_agentes.md` (5), `AGENTS.md` (3),
`scripts/estado_flujo.py` (1), `PLAN_MEDICION_TOKENS.md` (1) y los 3 nombres de prompt en
`PLAN_CONVERSION_SKILLS.md`. **La prosa conserva el acento** a propósito: «Entrevistas de
Empatía», «Dimensionador Estratégico de Ideas de Negocio» y los `> Fase: 1.Investigación` de los
README no son rutas. La `nota_rutas` de `pasos.json` ya no dice «acentos incluidos»: dice por qué
van sin tilde.

**Prevención:** los dos scripts de empaquetado escanean el stage antes de comprimir y avisan con
la lista de rutas culpables y el mensaje exacto del gestor. La regla quedó escrita en `AGENTS.md`
§5 («Rutas solo ASCII») con el comando para comprobarlo, y en `README.md`.

**Verificado:** las 26 rutas de `pasos.json` resuelven en disco y son ASCII; el ZIP tiene 170
entradas, **0 no-ASCII**, 0 backslashes, `SKILL.md` en la raíz y las 26 sub-skills; un `init`
nuevo y el `mostrar` de un paso devuelven rutas ASCII; la cadena `--datos` del proyecto real
sigue pasando entera; el guardia se probó plantando un archivo acentuado y avisa en `.ps1` y
en `.sh`.

## Hecho el 13/08/2026 (tarde)

### 1. Empaquetar una sub-skill sola — **hecho**

`empaquetar_skill.ps1` y `empaquetar_skill.sh` producen el ZIP de una sub-skill suelta:

```powershell
.\empaquetar_skill.ps1 -SubSkill "2.Descubrimiento/persona-profile"
.\empaquetar_skill.ps1 -ListSubSkills          # las 26 rutas válidas
```

```bash
./empaquetar_skill.sh --sub-skill "2.Descubrimiento/persona-profile"
./empaquetar_skill.sh --list-sub-skills
```

Contenido: `<sub-skill>/` + `_plantilla_html/`, nada más. El ZIP sale como `<sub-skill>.zip`
(0.13 MB) salvo que se pase `-Output`/`-o`. `-IncludeSamples`/`--samples` añade las muestras de
esa sub-skill en `sample_outputs/`; `--flujo`, `--docx` y `--temp` no aplican y avisan. Ruta
inexistente → error con la lista de sub-skills válidas. Documentado en `README.md` § «Empaquetar
una sub-skill sola» y en la regla «Extraíble» de `AGENTS.md` §4.

**Verificado:** descomprimido en carpeta limpia y generado el HTML con `--sin-flujo` sin
`--logo` → `logo embebido: 122 KB (base64) · copia local de la sub-skill`. Los dos scripts
producen **exactamente los mismos 9 archivos** (comparado ZIP contra tar.gz). El modo macro
sigue en 3 MB.

De paso se arreglaron dos fallos del `.sh`, uno de ellos heredado: el `find -exec sh -c` trataba
el directorio destino como un archivo más (`cp: -r not specified`), y el respaldo `tar` no podía
escribir en rutas con `:` (ahora va a stdout redirigido).

### 2. Estrenar `--datos` en un proyecto real — **hecho**

Proyecto **«Huertos urbanos MX»** recorrido de punta a punta en `output/huertos-urbanos-mx/`
(carpeta ya ignorada por `.gitignore`): 11 pasos resueltos, 6 ejecutados
(`html_1 → html_4 → html_5 → html_7 → html_8 → html_11`) y 5 omitidos, 8 decisiones registradas,
17 artefactos.

Lo que confirma el recorrido:

- **`problem-solution-fit` hereda de verdad.** Los 4 problemas de `html_5` son los 4
  `persona.pains[]` de `html_4` con **texto idéntico y el mismo número** — el `reporte.json` del
  predecesor se abre y se lee, no se reteclea del resumen. Comprobado campo por campo.
- **La frontera persona ↔ PSF se sostiene.** `html_4` entrega los pains sin `importancia`,
  `satisfaccion`, `solucion` ni `costo`; `html_5` es quien los puntúa. La matriz sale derivada,
  sin ningún `chart` escrito a mano.
- **El canal llega hasta el final.** `flujo.ruta[]` de `html_11` propaga los `datos` de los 5
  pasos previos; el `mostrar` de cada paso imprime `datos estructurados: reporte_html_N.json`.
- **`exportar_csv.py` cierra el círculo:** el CSV sale del mismo `reporte.json`, 4 filas, con el
  texto del pain 1 intacto.
- **El script de `ideacion` manda en los scores:** `evaluar_ideas.py` calculó promedios y
  ranking, y el reporte los leyó sin recalcularlos.

**Sobre los avisos de la barrera de predecesores:** en un recorrido bien ordenado —cerrar o
omitir cada paso a su turno— **no salió ni un solo aviso**. No estorban. Los que sí salen son
los de `completar` sin `--resumen` o sin `--datos`, y ahí ayudan.

**Contenido SIMULADO a propósito.** Sin acceso a usuarios reales, el recorrido entra por la
rama de supuestos (el `auto_si` de `pasos.json` la fuerza al estar `html_2` y `html_3` omitidos)
y los 6 reportes lo declaran en `meta.metodologia` y en `advertencias`. Sirve como prueba de la
máquina, **no** como investigación de mercado.

### 3. Verificar la línea nueva de `STATE.md` — **hecho**

Comprobada a ojo: cerrar `html_7` con `--forzar` saltando `html_4` imprime en el Historial

```text
  - **predecesores saltados con `--forzar`:** html_4
```

junto con los tres avisos correspondientes (predecesor duro saltado, predecesores blandos
abiertos y falta de `--datos`).

### 4. Cosmético — **hecho**

- **Los 3 README atípicos** (`foresight`, `senales-debiles`, `dimensionador-estrategico`) ya no
  se contradicen: el encabezado principal es «Salida principal — su propio HTML detallado» (o
  «su propio dashboard HTML (+ PPTX)») y el reporte de la plantilla compartida pasó a un segundo
  encabezado, «Resumen del paso». Se fue la nota aclaratoria que corregía al título.
- **`AGENTS.md`** quedó sin los avisos que listaba el to-do: listas de §7 con `-` en vez de `*`
  (MD004), los dos bloques de código sin lenguaje ahora son ```text (MD040) y la tabla de §8 usa
  `| --- | --- |` como el resto del repo (MD060). Se arregló también el `### Autor` de `README.md`
  que saltaba de H1 a H3 (MD001).
- **`render_state_md`** genera la tabla de `STATE.md` con el mismo estilo `| --- |`.

### 5. Plan de medición de tokens — **hecho** (escrito, no ejecutado)

`PLAN_MEDICION_TOKENS.md`. El alcance, que era lo que faltaba definir, queda fijado: entran el
arranque fijo, el briefing de `mostrar`, las sub-skills del paso, la herencia y el `reporte.json`
generado; quedan fuera los turnos del human-in-the-loop, el razonamiento, el system prompt del
gestor y los insumos del usuario.

**El HTML también queda fuera, y es el hallazgo que justifica la decisión:** lo escribe
`generar_html.py`, no el modelo. Los 6 HTML del recorrido pesan **20.8×** sus `reporte.json`
(~295,700 contra ~14,200 tokens\*), así que contarlos como salida inflaría la cifra 21 veces.

El plan incluye una línea base real: arranque fijo ~12,450 tokens\*, las 7 sub-skills del
recorrido ~19,575\* (23% de lo que costaría cargar las 26 y sus `references`), `mostrar` plano
entre 609 y 873\* por paso, y la herencia como único coste que crece.

## Hecho el 13/08/2026 (mañana — contexto)

1. **`exportar_csv.py` lee el bloque `psf`.** Deriva las filas de `secciones[].items[].psf`
   aplicando el mapeo de `references/analisis-psf.md`. Sigue aceptando la entrada anterior
   (`[{...}]`, `{"filas": [...]}`) y un `{"psf": {...}}` suelto.
2. **Barrera de predecesores en la máquina de estados.** `iniciar` y `completar` avisan si un
   predecesor sigue abierto y **bloquean** (exit 2) si no es omitible, con `--forzar` como
   escape. Los `predecesores` de `pasos.json` son alternativos entre sí, así que un paso cuenta
   como resuelto si está completado, omitido o fallido.
3. **Muestras de diseño de los bloques nuevos** en `sub-skills_sample_outputs/2.Descubrimiento/`.

## Hecho el 12/08/2026 (contexto)

1. **Frontera persona ↔ PSF.** Las secciones 11–13 del template *Persona Profile* pertenecen a
   `problem-solution-fit` (`html_5`) y ya no se rellenan en `html_4`.
2. **Autonomía de las 26 sub-skills.** El logo cae en `assets/logo.png`; 24 rutas `../../../`
   corregidas y «Uso independiente» añadido a las 26. Regla «Extraíble» en AGENTS.md §4.
3. **Herencia de datos entre pasos.** `completar --datos reporte.json` viaja como
   `flujo.ruta[].datos`; `CONTRATO_JSON.md` ganó `decision.contexto_usado` y «Encadenamiento».
