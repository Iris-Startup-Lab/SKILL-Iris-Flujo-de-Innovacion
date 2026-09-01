# To-do — 01/09/2026

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

**Nuevo el 28/08** los HTML ahora son **incrementales**: cada `html_N` embebe los reportes de los
pasos anteriores y el riel navega dentro del propio documento, no entre archivos.
Detalle en «Hecho el 28/08/2026».

**Nuevo el 01/09** el salto entre pasos **ya funciona dentro de Claude Desktop**. El ancla interna
(`#paso-N`) que resolvía el caso del 28/08 la interceptaba la pasarela y abría el diálogo «Estás
saliendo de Claude»; ahora el salto va con `<button>` + `data-salto`, sin `href`. Detalle en «Hecho
el 01/09/2026». **Te toca:** re-empaquetar el ZIP (el cambio está en la plantilla), regenerar
`CLAUDE.md` y confirmar el clic en Claude Desktop.

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

## Pendientes

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

### 9. Convertir `skill_de_investigacion.md` en sub-skill y revisar `real_examples/`

Dos cosas encadenadas, para otro día:

1. **Primero, robustecer Investigación sin fuentes de pago.** Cuando el usuario no tiene Statista
   (ni otro servicio pagado) hace falta una alternativa de datos abiertos. El texto ya está:
   `skill_de_investigacion.md` (en la raíz, nombre «Fuentes de Datos Abiertos sin API Key») es el
   catálogo de fuentes públicas/gratuitas sin registro ni token, con la distinción legal
   (oficiales vs. librerías de scraping). Falta **convertirla en sub-skill**: renombrarla a
   kebab-case, moverla a `sub-skills/1.Investigacion/`, escribirle su `AGENTE.md` + `README.md`
   (convención de sub-skill: contrato JSON y «Uso independiente»), adaptar/crear sus scripts y
   engancharla como opción cuando falte el acceso a fuentes de pago.

2. **Revisar los ejemplos reales — hecho el 01/09/2026.** Los dos proyectos de `real_examples/`
   se evaluaron contra `pasos.json` y las notas de los usuarios: veredicto en «Evaluación de los
   ejemplos reales — 01/09/2026». **El proceso resiste el uso real** (11 pasos, decisiones del
   usuario, marcas de supuestos, HTML con contexto); salieron **9 fricciones** (6 reportadas por
   los usuarios y 3 más detectadas en los HTML), ninguna es bug del script — son huecos de
   diseño en la orquestación y en cuatro sub-skills
   (`entrevistas-empatia`/`discovery-survey` ingesta de material, `problem-solution-fit` orden,
   `dimensionador-estrategico` justificación del score en el HTML, `online-ads` prompts de
   imagen) más el cierre del flujo (el resumen ejecutivo no es parte del cierre estándar) y el
   PSF/Journey de perfiles no elegidos que quedan huérfanos fuera del flujo. Cada fricción trae
   su idea de solución en la tabla de esa sección.

   El orden de trabajo queda igual: la sub-skill de datos abiertos va primero porque es la pieza
   que robustece; los arreglos de las fricciones 1–9 vienen después, ya con esa pieza puesta.

### 10. Evaluar los métodos estadísticos y construir los scripts que faltan

**Evaluación hecha el 01/09/2026** — ver «Evaluación de los métodos estadísticos — 01/09/2026»
más abajo. Veredicto: la estadística ya scripteada es correcta (muestras, Wilson, Kano, Berger,
saturación, EDA de señales débiles, SSoT); lo que falta es convertir a cálculo determinista
todo lo que hoy hace el LLM a mano:

1. **`calcular_tam_sam_som.py`** — TAM/SAM/SOM con reducciones top-down y proyección 1/3/5 + CAGR
   (`benchmark-mercado`, `dimensionador-estrategico`).
2. **`calcular_modelo.py`** — unidad económica del Dimensionador (CLV, CAC, CLV:CAC, payback,
   ROI, ARR) a partir de métricas unitarias. Hoy el `xlsx_generator.py` solo dibuja lo que ya
   calculó el LLM.
3. **`calcular_score.py`** — score /25 con justificación obligatoria por criterio y umbrales
   PROTOTIPAR/VALIDAR/DESCARTAR (atiende también la fricción 4 del pendiente 9).
4. **`analizar_resultados.py`** (o equivalente por skill) — k/n observados → IC de Wilson +
   comparación contra umbral o control, para que los pasos de validación sepan leer sus propios
   experimentos. Hoy solo `email-campaign` calcula el n requerido, y ninguno analiza el resultado.
5. **Baseline/grupo control explícito** en las Testing Cards de validación (responde la nota de
   `notas_humanas_…txt` de «no se tienen grupos control»).
6. **Regla de explicación estadística accesible (obligatoria).** Cuando un script emita valores
   estadísticos —`p`, `alpha`, intervalo de confianza, margen de error, `n` requerido,
   coeficientes, etc.— el LLM debe **explicarlos con fórmulas fáciles de entender y en lenguaje
   de usuario**, siempre que apliquen. La audiencia son usuarios de todo tipo, expertos y no
   expertos: está prohibido soltar «p = 0.03» o «IC95 42–76%» sin decir en una frase qué
   significan («la probabilidad de que esta diferencia sea puro azar es del 3%»; «de cada 100
   repeticiones del estudio, en 95 el resultado caería en este rango»). La fórmula va en
   versión «de libro» y en versión «en palabras», como ya hace la regla de los `*` de
   `SKILL.md` § «Cómo nombrar las cosas ante el usuario».
7. **Honestidad sobre fallas metodológicas y de muestra (obligatoria).** El LLM debe declarar
   con total transparencia cuando encuentre fallas metodológicas o tamaños muestrales
   insuficientes —aunque el script no lo advierta—: sesgos del instrumento, ausencia de grupo
   control, `n` que no sostiene el porcentaje, comparaciones múltiples, muestras de conveniencia.
   No maquillar un resultado débil ni enterrarlo en `advertencias`: decirlo en el resumen y en
   la conversación, con el impacto que tiene sobre la decisión.
8. **Gráficos: generar los scripts requeridos.** Si la explicación de un método necesita gráficos
   (barras con IC, curvas de saturación, matriz Importancia × Satisfacción, distribuciones,
   trayectorias TAM/SAM/SOM), hay que **escribir los scripts que los generen** —Chart.js, Plotly,
   matplotlib— como parte del entregable, no dibujarlos a mano ni omitirlos. La regla de
   integridad se aplica igual: los gráficos salen de datos calculados por script, nunca de una
   aproximación visual del LLM.

Decisión pendiente de diseño: si enriquecer `catalogo-patrones.md` de `business-model-navigator`
con indicadores numéricos o al menos aplicar el orden de desempate por script.

---

## Hecho el 01/09/2026

### El salto entre pasos dentro de Claude Desktop — la pasarela intercepta cualquier `<a href>`

Lo que reportó el usuario: en Claude Desktop, al hacer clic en «Paso 1» desde `html_2`, salía el
diálogo **«Estás saliendo de Claude para visitar un enlace externo»** en lugar de saltar al paso.
Descargando los HTML sí funcionaba.

**Causa, leída en la URL del propio diálogo:** la pasarela sirve el reporte en un iframe suyo
(`claudeusercontent.com/?domain=claude.ai&parentOrigin=…`) e intercepta el clic de **cualquier**
`<a href>`. Resuelve el href contra la URL de ese iframe, así que `#paso-1` no se lee como «ancla
de este documento» sino como `https://www.claudeusercontent.com/?…#paso-1`: una salida del
producto. El arreglo del 28/08 (embeber los pasos y saltar con un ancla) era correcto en la parte
difícil —el contenido **sí estaba** dentro del html_2— y fallaba solo en el mecanismo del salto.

**Arreglo:** la navegación interna no usa anclas. Nada que interceptar, así que no depende de
adivinar cómo funciona el interceptor.

- **Riel** (`reporte_base.html`): un paso completado es un `<button data-salto="N">`, no un
  `<a href="#paso-N">`. Igual en «Lo que ya sabemos» (`<button class="salto">`). Un solo manejador
  delegado (`irAPaso`) abre el `<details>`, lo desplaza con `scrollIntoView` y lo realza 1.6 s.
- **No se pierde nada al quitar el `href`:** el riel lo dibuja ese mismo script desde
  `REPORT_DATA`, así que nunca existió un caso «sin JavaScript» al que el ancla sirviera.
- **Enlaces a archivo vecino** (riel en modo `--sin-historial`): se dibujan solo si el reporte
  **no** está embebido (`EMBEBIDO = window.self !== window.top`). Dentro de la pasarela no hay
  disco que abrir y el clic solo producía el diálogo; ahora el paso queda como texto con un
  `title` que explica por qué no se puede abrir desde ahí.
- **`EMBEBIDO` gobierna solo los enlaces a archivos.** El salto interno funciona en los dos
  contextos sin consultarlo: si la detección fallara, lo que se rompe es el extra, no el arreglo.
- **Nuevo extra al descargar:** cada paso del historial ofrece «Abrir el archivo» (su
  `html_N.html` vecino, para ver dos pasos lado a lado o imprimir uno solo). Con
  `stopPropagation`, porque si no el clic plegaba el paso además de abrir el archivo.
- **Dos arreglos de acabado** que también afectaban al HTML descargado: `scroll-margin-top`
  recalculado con la altura real de la barra sticky —que antes **tapaba el título** del paso al
  saltar (medido: 100 px)— y los estilos de hover, que colgaban de `a.flow-step` y se habrían
  quedado sin efecto al cambiar el elemento; ahora cuelgan de `.saltable`.

**Verificado con Chrome headless, las cuatro ramas:**

| Contexto | Resultado |
| --- | --- |
| Iframe (reproduce la pasarela, servido por `http.server` para poder inspeccionarlo) | `EMBEBIDO` detectado; riel = 10 `<button>` + 1 `<span>` (el actual); **0 anclas internas**; 0 enlaces a archivo; clic en el paso 3 → `open=true`, realzado, `scroll-margin-top: 100px` |
| Descargado (`file://`) | 0 anclas internas; 20 botones de salto (riel + contexto); 10 enlaces «Abrir el archivo» a `html_1…10.html`; 10 pasos embebidos |
| `--sin-historial`, descargado | riel = 10 `<a>` a `html_N.html`, 0 `data-salto`, 0 pasos embebidos |
| `--sin-historial`, embebido | el enlace a archivo no se dibuja |

Además: `node --check` sobre el JS de la plantilla (941 líneas) y los 11 pasos regenerados sin
fallos. Regenerados también los HTML de `output/ecopack-circular` (11) y
`output/huertos-urbanos-mx` (6) más sus `index.html` — solo el render, desde los mismos
`reporte_*.json`, como el 28/08. `output/` está en `.gitignore`, así que no toca nada versionado.

**Cuidado con el chequeo estático:** buscar `<a href="#` en el HTML generado da **falsos
positivos**, porque los comentarios de CSS y de JS de la plantilla citan la regla. Hay que quitar
los bloques `<script>` y `<style>` antes de contar, o mirar el DOM renderizado.

**Documentado:** `_plantilla_html/README.md` § «Navegación interna sin `<a href>`» (con las tres
reglas para quien añada navegación a la plantilla) y `AGENTS.md` §5.

**Pendiente para el usuario:** re-empaquetar el ZIP (el cambio vive en la plantilla, así que el
paquete del 24/08 quedó atrás), regenerar `CLAUDE.md` con `.\actualizar_claude.ps1` y confirmar el
clic en Claude Desktop con un reporte recién generado.

`scripts/generar_indice.py` se dejó como está: su `index.html` enlaza archivos del disco, y esa
navegación solo tiene sentido con el proyecto descargado. Dentro de la pasarela no hay arreglo
posible, y para eso está el historial embebido.

---

## Evaluación de los ejemplos reales — 01/09/2026 (cierra el pendiente 9, punto 2)

Se revisaron los dos proyectos de `real_examples/` contra `pasos.json` y contra lo que cada
sub-skill declara que entrega, contrastando además con las notas de los usuarios que los
corrieron (Diana en Reclutalia, Jonathan en Divisas). Método: se extrajo `window.REPORT_DATA`
de cada HTML (los reportes viven como JSON embebido), se compararon las decisiones registradas
contra el catálogo de `pasos.json`, se contrastó cada fricción anotada contra el script y las
instrucciones de la sub-skill involucrada, y se cotejó con `verificar` (sin estado a mano en
`real_examples/`, la verificación se hizo leyendo los JSON).

### Veredicto general

**El proceso resiste el uso real.** Los dos proyectos recorrieron los 11 pasos completos, con
decisiones registradas por el usuario (no por el agente), con la marca de datos simulados
propagándose sola donde tocaba, con `*`/`[REFERENCIA DE INDUSTRIA]`/`[no disponible]` donde
faltaba fuente, y con los HTML generados con contexto del flujo. **No se encontró ningún caso
de decisión inventada, dato inventado o cierre de paso sin su decisión**: las cuatro invariantes
de `AGENTS.md` §6 se sostienen en la práctica.

**Pero las notas de usuario destapan 6 fricciones reales**, y al leer los HTML se ven además 2
más que nadie reportó. No son bugs del script (el script hizo lo que debía): son **huecos de
diseño** en la orquestación y en tres sub-skills. Detalle por fricción:

### Fricción 1 — Reclutalia paso 3: los zips de transcripciones entraron sin protocolo

Nota de Diana: «en el paso 3 cuando subí los transcripts de las entrevistas, sí me dejó subir en
un solo paso adjuntar en zips por perfiles todos los transcripts (no me preguntó nada, solo la
skill dice que con que sea formato csv texto etc)». El flujo acepta el material sin confirmar
**qué es lo que se sube**: cuántos archivos, de qué perfiles, si son entrevistas, encuestas o
notas, y sin declarar cómo se van a usar. Esto choca con el espíritu de human-in-the-loop: hay
un aporte de evidencia de campo y el agente no lo reconoce ni lo confirma.

Causa de diseño: `SKILL.md` § «Qué archivos puede adjuntar» lista formatos pero **no define un
protocolo de ingesta** (qué preguntar al recibir material, cómo confirmarlo, cómo declararlo en
el reporte). `entrevistas-empatia` y `discovery-survey` piden inputs pero no un momento de
"recibo tu material y esto es lo que entendí que es".

### Fricción 2 — Reclutalia paso 4: clic en los enlaces del HTML marcaba error

Nota de Diana: «en el html del paso 4 cuando le doy click a los links marca error». Es el
mismo síntoma del caso del 01/09 (la pasarela intercepta cualquier `<a href>`): los HTML de
`real_examples/` son anteriores al arreglo de navegación (`data-salto`), y en su riel los pasos
completados se dibujan como `<a href="output/CH_Reclutalia/html_1.html">`. Fuera del flujo ese
enlace además apunta a una ruta que no existe (`output/...`), así que el clic falla también en
local. **El arreglo del 01/09 ya lo cubre** para reportes recién generados; estos ejemplos
quedan como muestra del antes. Acción: no requiere cambio de código, pero conviene regenerar un
ejemplo con la plantilla nueva para la muestra.

### Fricción 3 — Reclutalia paso 5: lista de problemas en desorden en la conversación

Nota de Diana: «en la conversación del skill generó un listado pero lo hizo en desorden, en el
html sí vienen bien los números consecutivos, pero supongo que los ordenó así porque los
descarta como solución». El `psf.problemas` del HTML está numerado 1–5 pero **no ordenado por
importancia** (4.5, 3.5, 3.5, 4.0, 3.0) — el orden no es evidente y la conversación lo presentó
distinto. Causa: `problem-solution-fit` no declara un criterio de orden visible (por importancia,
por frecuencia, por `n` de evidencia). El lector no sabe por qué el 4 va antes que el 2.

### Fricción 4 — Reclutalia paso 9: el HTML menos claro que la conversación

Nota de Diana: «a mí me quedó más claro el resumen de la conversación que el html, tiene más
detalle y las tablas se me hicieron más fáciles de leer»; «no me quedó claro de dónde sacó los
datos que estoy marcando en el recuadro rojo (urgencia, diferenciación, escalabilidad, etc.)»;
«al dar click en metodología no lo menciona y dice que se generó una tabla de resumen pero no se
muestra en el html solo en la conversación».

Al comparar `html_9` de Reclutalia con el de Divisas se ve el hueco con nitidez: el de Divisas
**sí** trae el item «Score de atractivo y riesgos» con una fila de justificación por criterio
(urgencia/diferenciación/escalabilidad/velocidad/fit, cada una con su porqué). El de Reclutalia
solo muestra el `subtitulo` con el score y unos pocos bullets de valor/adopción/riesgo, **sin
la justificación criterio por criterio**. La tabla de resumen (score por idea) que la skill
genera en conversación no viaja al HTML. Causa: `dimensionador-estrategico` entrega el detalle
en el chat pero su `reporte.json` para el paso **no incluye obligatoriamente** la matriz de
justificación del score; el validador no la exige, así que depende de que el agente la ponga.

### Fricción 5 — Reclutalia paso 11: el reporte final de insights no se generó solo

Nota de Diana: «al final del flujo no generó el reporte final de los insights solo hasta que lo
pedí (Jonathan me comentó que a él sí se lo generó al terminar el paso 11)». El cierre de
`SKILL.md` («¿Qué hacer al final de todo el flujo?») pregunta por auditar + `index.html` + medir
tokens, pero **no menciona el resumen ejecutivo/insights**. Que Jonathan lo recibiera fue
iniciativa del agente, no del proceso. Acción: añadir al cierre del flujo la pregunta explícita
por el resumen ejecutivo (o hacerlo parte del cierre estándar).

### Fricción 6 — Reclutalia: el PSF/Journey de Reclutadores y Candidatos se hizo fuera del flujo

Nota de Diana: «le pregunté en dónde estaba cierta información y en uno de los casos tuvo que
actualizar el html (ya había terminado los 11 pasos)». En los archivos están `h5_reclutadores`,
`h5_candidatos`, `h6_reclutadores`, `h6_candidatos`: PSF y Journey de los otros dos perfiles,
generados **después** de cerrar el flujo y con `flujo: null` (sin contexto, sin riel, sin
decisión de ficha, sin marca). Son análisis válidos pero **huérfanos**: no heredan nada del
proyecto y no son accesibles desde el riel. Causa de diseño: `html_5` y `html_6` se corrieron
solo sobre la ficha elegida (Formadores) porque así está diseñado el paso; el usuario pidió los
demás perfiles y el agente los resolvió fuera del flujo.

### Fricción 7 (no reportada, detectada en los HTML) — la marca de simulación de Reclutalia

El proyecto Reclutalia eligió «Sí — respuestas e insights reales» en el paso 2, y en el paso 3
eligió Kano + Discovery Survey **simulados**. Desde el `html_3` todos los reportes posteriores
llevan la marca «Datos simulados» (correcto por diseño: la marca se propaga). Pero los pasos
4–11 se construyeron sobre las **42 entrevistas reales** de Reclutalia, y cada reporte tiene que
añadir a mano la nota aclaratoria «este paso está construido 100% con entrevistas reales». La
marca es global y binaria, y no hay forma de declarar «este paso sí es real aunque el proyecto
haya simulado algo antes». Es coherente con el diseño actual, pero es una fricción de
credibilidad que los usuarios tendrán que explicar a quien revise el proyecto.

### Fricción 8 (no reportada, detectada en los HTML) — el orden de ideas del `html_9` de Reclutalia

Las fichas de ideas del `html_9` de Reclutalia salen numeradas 1, 2, 3, 7, 4, 6, 11, 8, 9, 10,
5, 12: mezcla el número original de la idea del paso 8 con el orden por score de este paso. La
tabla resumen que sí trae orden por score no se ve como tabla (está en el `subtitulo` de cada
item). Confunde: parece un desorden, no una priorización.

### Fricción 9 — Divisas paso 11: los prompts de imagen de los ads no dan para el arte

Nota de Jonathan: «siento que las descripciones de las imágenes para generar los ads no son tan
específicas como para generar los artes necesarios o estos también son muy simples». Al leer el
`html_11` de Divisas, los prompts de imagen de las 3 campañas son genéricos («ilustración plana
minimalista de un teléfono móvil mostrando una notificación de banco con un ícono de check
verde, paleta verde y dorado, sin texto, estilo flat design»). Sirven como concepto, pero no
como dirección de arte ejecutable: no hay composición detallada, iluminación, referencias,
tipografía ni variantes. Causa: `online-ads` genera el prompt en una sola línea, sin el nivel
de detalle que una herramienta de imagen necesita para producir algo publicable.

### Tabla resumen de fricciones y soluciones

| # | Fricción | Solución propuesta |
| --- | --- | --- |
| 1 | Zips de transcripciones sin protocolo | Añadir en `SKILL.md` (y en `entrevistas-empatia`/`discovery-survey`) un **protocolo de ingesta de material**: al recibir adjuntos, el agente responde «recibí N archivos: X entrevistas, Y encuestas, de perfiles A/B/C — ¿es correcto?» antes de analizar. Confirmar perfiles y decidir si son datos reales o a simular. Registrarlo en `advertencias`/`contexto_usado`. |
| 2 | Links rotos en HTML viejos | Ya cubierto por el `data-salto` del 01/09. Regenerar una muestra de `real_examples/` con la plantilla nueva para que sirva de referencia. |
| 3 | Orden de problemas no evidente | En `problem-solution-fit`, ordenar el `psf.problemas` por un criterio declarado (importancia desc) y mostrarlo igual en conversación y HTML; o documentar el criterio en el `subtitulo`. |
| 4 | `html_9` sin justificación del score | Hacer **obligatorio** en `dimensionador-estrategico` que el `reporte.json` del paso lleve, por idea, la matriz criterio→puntaje→justificación (como ya lo hace Divisas). Reflejar en `validar_report_data.py` una advertencia si el paso 9 no la incluye. Y que la tabla resumen de scores viaje al HTML como sección. |
| 5 | Resumen final no se generó solo | Añadir al cierre del flujo la pregunta explícita: «¿Genero el resumen ejecutivo del proyecto?» (una página, legible sin abrir los HTML). Hacerlo parte de la pregunta (a) del cierre. |
| 6 | PSF/Journey de otros perfiles fuera del flujo | Documentar en `SKILL.md`/pasos que el PSF/Journey corre sobre la ficha elegida, y ofrecer al usuario, al elegir ficha, «analizar también los otros perfiles como anexo» — ejecutado como paso del flujo (con contexto y marca) o al menos con `--estado` para que herede. Si es post-cierre, generarlo con `--estado` para que no quede huérfano. |
| 7 | Marca de simulación global | Considerar un campo opcional por reporte (`meta.simulado` a nivel de sección/item) para que un paso con datos reales dentro de un proyecto simulado pueda declararlo sin apagar la marca global. Decisión de diseño para el usuario: ¿la marca es del proyecto o del paso? |
| 8 | Orden de ideas del `html_9` | El `dimensionador` debe presentar las ideas **por score descendente** en el HTML (con el número original solo como tag), y la tabla resumen como tabla visible, no solo en `subtitulo`. |
| 9 | Prompts de imagen genéricos | Ampliar `online-ads` para que el prompt de imagen sea una dirección de arte ejecutable: composición, iluminación, encuadre, estilo visual de referencia, paleta exacta, y qué evitar (texto, marcas de terceros). Incluir una variante de prompt por campaña y una nota de cuándo usar cada herramienta (Midjourney/DALL·E/Firefly). |

---

## Evaluación de los métodos estadísticos — 01/09/2026

Evaluación de la base estadística del flujo: qué métodos se proponen, cuáles están ya
implementados por script (y son correctos), y cuáles se dejan al LLM cuando deberían ser
cálculo determinista. Parte del pendiente que quedó anotado en `notas_humanas_…txt`
(«evaluar los métodos estadísticos y proponer otra arquitectura… por ejemplo no se tienen
grupos control»).

### 1. Lo que ya está bien resuelto (script existente y fórmula correcta)

| Método | Script | Revisión |
| --- | --- | --- |
| Tamaño de muestra de encuesta (n, n_aj, envíos) | `discovery-survey/scripts/calcular_muestra.py` | Fórmulas correctas (Z²pq/e², ajuste finito, envíos). Tabla Z por proximidad: OK para 95/99. |
| Significancia de tasas (una muestra y A/B) | `email-campaign/scripts/calcular_significancia.py` | `NormalDist` correcto; las dos fórmulas (una/dos muestras) son las estándar. |
| Intervalo de Wilson, prueba z de dos proporciones, margen de error | simuladores (`simular_discovery`, `simular_kano`) | Implementaciones correctas y con avisos de n pequeña. |
| Matriz Kano M/O/A/I/R/Q (25 celdas) | `encuesta-kano/scripts/clasificar_kano.py` + `simular_kano.py` | Matriz verificada; idéntica en los dos scripts. |
| Coeficientes de Berger CS/DS, tasa Q+R | `simular_kano.py` | Fórmulas correctas; suprimidos cuando la base A/O/M/I es minoritaria. |
| Curva de saturación cualitativa | `simular_entrevistas/aditl/expo` | Heurística correcta (2 sesiones sin novedad); criterio documentado. |
| Score ponderado y ranking de ideas | `ideacion/scripts/evaluar_ideas.py` | Promedio ponderado correcto; los inputs (N/U/F) son juicio del agente y así se declaran. |
| EDA de señales débiles (chi², Cramér's V, Cohen's d, Gini, Spearman, IQR, tasa base) | `senales-debiles/scripts/fase1_analisis.py` | Estadística correcta; p de chi² vía scipy (disponible). |
| Verificación SSoT de cifras (fracciones a/b, sumas, tasa base) | `senales-debiles/scripts/verificar_numeros.py` | Invariante bien planteado: ninguna cifra del LLM sobrevive al gate. |
| Pendiente de regresión lineal de Google Trends | `search-trend-analysis/scripts/google_trends.py` | Regresión simple correcta para la tendencia. |

### 2. Métodos propuestos que hoy calcula el LLM y deberían ser script

Estos violan la regla «si un script puede calcularlo, el script lo calcula»: son aritmética
determinista sobre supuestos, y el LLM los hace a mano. Es la misma causa de la fricción 4
(«de dónde sacó urgencia/diferenciación…») y de que el usuario de Divisas dudara de los
números («todos los datos fueron supuestos»).

| Método | Dónde | Qué falta |
| --- | --- | --- |
| **TAM/SAM/SOM con reducciones top-down y proyección 1/3/5 años + CAGR** | `benchmark-mercado` y `dimensionador-estrategico` | Un `calcular_tam_sam_som.py`: base de mercado + % de reducción (geografía/vertical/canal) + tasa de crecimiento → TAM/SAM/SOM a 1/3/5 y CAGR. El LLM solo escribe fuentes y narrativa. |
| **Modelo financiero del Dimensionador** (CLV, CLV ajustado con cross-sell, CAC, CLV:CAC, payback, ROI, EBITDA, MRR/ARR, churn/NRR, punto de equilibrio) | `dimensionador-estrategico` (módulos 3–8 del AGENTE.md) | Un `calcular_modelo.py` que reciba métricas unitarias (ticket, frecuencia, vida, margen, CAC, cross-sell) y derive el resto. Hoy el `xlsx_generator.py` solo **dibuja** valores que ya calculó el LLM: no calcula nada. |
| **Score de atractivo /25 y sus umbrales** (20-25 PROTOTIPAR · 13-19 VALIDAR · ≤12 DESCARTAR) | `dimensionador-estrategico` (módulo 9) | Un `calcular_score.py` que tome los 5 criterios (urgencia/diferenciación/escalabilidad/velocidad/fit) y agregue + aplique umbrales, **exigiendo justificación por criterio** (lo que reclama la fricción 4). El LLM propone los 5 puntajes con su porqué; el script suma, decide y verifica que ninguna justificación falte. |
| **Muestra mínima de anuncios** (`Muestra ≈ (16·σ²)/d²`, ~400–500 impresiones/variante) | `online-ads` | Reusar `calcular_significancia.py` (o un script propio en la skill): que el n por variante salga del script, no de una fórmula suelta en el AGENTE.md. |
| **Umbrales de conversión de los experimentos** (landing, feature-stub, popup, explainer) | `4.Prototipado/landing-page`, `5.Validacion/*` | Las Testing Cards fijan «≥ X% de conversión en N visitas» sin derivar N. Un script de **n requerido y de análisis posterior** (k/n observado + IC Wilson + comparación vs. umbral/control) serviría a las cinco skills de validación. Hoy solo `email-campaign` tiene el de n requerido, y ninguno analiza resultados después. |
| **Indicadores del catálogo de Business Model Navigator** (Costo/Configuración/Ejecución/Fuerza de Evidencia 1-5) | `business-model-navigator` | El catálogo no trae esos números, así que el agente los estima (en los ejemplos reales se declara «estimación del analista»). Decidir: (a) enriquecer `catalogo-patrones.md` con indicadores, o (b) al menos que el script de ranking aplique el orden de desempate (evidencia > costo > configuración > ejecución) de forma determinista sobre los valores que se declaren. |

### 3. Decisiones de diseño estadístico que proponer

1. **Grupo control / baseline en los experimentos de validación.** Los pasos 11 comparan contra
   un umbral de industria (`[REFERENCIA DE INDUSTRIA]`) o contra un objetivo declarado, pero no
   contra un **control medido en el mismo experimento** (p. ej. la versión actual sin el cambio).
   `calcular_significancia.py` ya tiene el modo dos muestras (A/B): la propuesta es que las
   Testing Cards de landing/ads/feature-stub/email/explainer **incluyan siempre un baseline o
   grupo control explícito**, o declaren por qué no es posible y que la lectura es exploratoria.
   Esto responde la nota «no se tienen grupos control».
2. **Análisis posterior compartido.** Un script común (p. ej. `scripts/analizar_resultados.py`
   en `_plantilla_html` o por skill) que tome `k/n` observados + baseline y emita tasa con IC de
   Wilson, prueba vs. umbral y, si hay dos brazos, prueba z de dos proporciones. Así el flujo no
   solo **diseña** el experimento, sino que sabe **leerlo** cuando el usuario vuelve con datos.
3. **Múltiples comparaciones.** Los simuladores prueban muchas proporciones a la vez y no
   corrigen por comparaciones múltiples (el aviso del IC de Wilson es por-tema). Documentar que
   con decenas de temas un ~5% de IC caerá por azar fuera — el propio `simular_discovery` ya
   avisa que «pasa por azar de vez en cuando»; convertir ese comentario en advertencia estándar.
4. **`calcular_muestra.py` menor:** el Z se aproxima por el nivel de confianza más cercano en
   vez de interpolar. Irrelevante para 95/99; si se quiere exactitud para otros valores, usar
   `NormalDist().inv_cdf` como ya hace `calcular_significancia.py`.

### 4. Lo que se propone construir (resumen accionable)

| Prioridad | Script / cambio | Skill(s) |
| --- | --- | --- |
| Alta | `calcular_tam_sam_som.py` (reducciones top-down + proyección 1/3/5 + CAGR) | `benchmark-mercado`, `dimensionador-estrategico` |
| Alta | `calcular_modelo.py` (CLV/CAC/CLV:CAC/payback/ROI/ARR — unidad económica determinista) | `dimensionador-estrategico` |
| Alta | `calcular_score.py` (/25 con justificación obligatoria por criterio y umbrales) | `dimensionador-estrategico` |
| Media | n requerido + `analizar_resultados.py` (k/n → IC Wilson + prueba vs. baseline/control) | `landing-page`, `online-ads`, `feature-stub`, `popup-store`, `explainer-video`, `email-campaign` |
| Media | Muestra mínima de anuncios vía script (sustituir la fórmula del AGENTE.md) | `online-ads` |
| Media | Baseline/control explícito en las Testing Cards de validación | `5.Validacion/*`, `landing-page` |
| Baja | Advertencia de comparaciones múltiples en simuladores; Z interpolado en `calcular_muestra.py` | simuladores, `discovery-survey` |
| Decisión | Enriquecer `catalogo-patrones.md` con indicadores, o ranking determinista de BMN | `business-model-navigator` |

**Nota de alcance:** ninguna de estas piezas existe todavía; esta sección es el diagnóstico y la
propuesta. Implementarlas toca `AGENTE.md` + scripts de cada skill y, si se hace el
`analizar_resultados.py` compartido, la regla de extraibilidad de `AGENTS.md` §4 (cada skill
con su copia o script autocontenido, sin importar de otras skills).

### 5. Regla transversal: explicar la estadística para cualquier lector, con honestidad y gráficos

Vale para **todos** los métodos de arriba, nuevos y existentes, y se implementa junto con cada
script (también está como punto 6–8 del pendiente 10):

1. **Explicar, no soltar números.** Cada valor estadístico que emita un script (`p`, `alpha`,
   IC, margen de error, `n` requerido, coeficientes) se presenta con su fórmula **en dos
   versiones**: la de libro y la «en palabras», en lenguaje de usuario. Un «p = 0.03» nunca va
   solo: va con «la probabilidad de que esta diferencia se deba al azar es del 3%». Un
   «IC95 42–76%» va con «si repitiéramos el estudio 100 veces, en 95 el resultado caería en
   este rango». La audiencia son usuarios de todo tipo: quien domina matemáticas y quien no.
2. **Total honestidad metodológica.** Si el resultado tiene una falla metodológica o un tamaño
   de muestra insuficiente —aunque el script no la advierta—, se declara sin maquillar: sesgos
   del instrumento, ausencia de grupo control, `n` que no sostiene un porcentaje, muestras de
   conveniencia, comparaciones múltiples. Se dice en el resumen y en la conversación, con su
   impacto en la decisión, no solo enterrado en `advertencias`.
3. **Gráficos cuando el método lo pida, generados por script.** Si la explicación necesita
   gráfico (barras con IC, curva de saturación, matriz Importancia × Satisfacción, trayectoria
   TAM/SAM/SOM, histograma), el script correspondiente lo genera —Chart.js, Plotly o
   matplotlib— desde los datos calculados; el LLM nunca lo dibuja a mano ni lo omite.

---

## Hecho el 28/08/2026

### HTML incremental — cada reporte navegable por sí mismo (dentro de Claude/Codex)

Problema real: dentro de la pasarela (vista previa embebida de Claude/Codex) no hay sistema de
archivos, así que un `html_N` no puede abrir a su vecino (`html_2.html` desde `html_3`). La
navegación hacia atrás quedaba rota.

**Solución:** cada `html_N` **embebe los reportes de los pasos anteriores** dentro del propio
documento (`flujo.historial`), y el riel salta a ellos con un ancla interna (`#paso-N`) en vez de
abrir un archivo. `html_2` contiene a `html_1`; `html_11` contiene del `html_1` al `html_10`.

> **Corregido el 01/09:** la parte del embebido quedó bien y sigue igual, pero el ancla `#paso-N`
> no servía dentro de Claude Desktop —la pasarela la trataba como enlace externo—. El salto se
> hace ahora con `<button data-salto="N">`. Ver «Hecho el 01/09/2026».

- **Generador** (`_plantilla_html/scripts/generar_html.py`): `anexar_historial()` lee los
  `reporte.json` de los predecesores (desde `flujo_estado.json` → `ruta[].datos`, resueltos
  relativos a la carpeta del estado) y los mete en `flujo.historial`. Solo los pasos
  **anteriores** al actual (el `ruta` viene en orden; se corta al llegar al paso en curso). Si un
  predecesor no tiene `datos` o su archivo no se lee, se omite sin romper. Flag `--sin-historial`
  para no embeder.
- **Plantilla** (`reporte_base.html`): sección «Pasos anteriores del flujo» —un `<details>`
  plegable por paso con su contenido completo (KPIs, tarjetas expandibles, gráficas, decisiones,
  notas)—; el riel enlaza a `#paso-N` y abre el detalle al clic; el bloque «Lo que ya sabemos»
  del contexto también enlaza a `#paso-N`, y ya **no lista pasos futuros** (antes, en un proyecto
  con los 11 cerrados, «Lo que ya sabemos» de `html_1` listaba `html_2…11`).
- **Costo en tokens: cero.** El HTML lo escribe el script, no el modelo; el embebido lo hace
  `generar_html.py` leyendo `reporte.json` ya existentes. El archivo crece de forma incremental
  pero es despreciable: cada `reporte.json` pesa ~3–5 KB frente a ~122 KB del logo embebido
  (html_1: 210 KB → html_11: 268 KB).
- Lo que aún no existe (pasos **futuros**) sigue como enlace relativo, navegable con
  `index.html` en el navegador.

**Verificado** con Chrome headless: html_N embebe N−1 pasos (0 en html_1, 10 en html_11), el riel
y «Lo que ya sabemos» enlazan a `#paso-N`, el clic abre el detalle, la gráfica scatter del PSF se
renderiza dentro del historial y 0 errores de JS. Regenerados los 11 HTML de
`output/ecopack-circular/`.

**Documentado:** `README.md` § «Navegar entre los reportes», `SKILL.md` § final del flujo,
`AGENTS.md` §5 y `_plantilla_html/README.md` (bloque `flujo.historial` + flag `--sin-historial`).

### Medición de tokens al cierre + gráfica de barras (Plotly)

El cierre del flujo no estaba ocurriendo: al terminar el paso 11, el agente **no preguntaba** por
la medición ni daba el resumen de tokens/costo. Se arregló por los dos lados:

- **Orquestación (`SKILL.md`):** el cierre ahora es explícito. «Preguntar si sigue» (paso 8 del
  ciclo) apunta a «¿Qué hacer al final de todo el flujo?» cuando se cierra el último paso, y esa
  sección arranca **preguntando al usuario** (auditar + `index.html` + medir con gráfica) en vez
  de asumirlo. La medición se corre solo si la pide; el resumen en 2–3 líneas se da siempre, y si
  hay gráfica se dice dónde está y qué destaca.
- **`scripts/medir_tokens.py`:** nuevo flag `--grafica [ruta]` (default `tokens_por_paso.html`)
  que escribe una **gráfica de barras Plotly** con los tokens por paso (entrada + salida),
  ordenada de mayor a menor —el paso que más consume es la primera barra, en dorado; el resto en
  morado IRIS—. `--grafica` funciona con o sin `--modelo` y con o sin `--proyecto` (sin proyecto
  solo hay E3).
- **Bug corregido (caracteres vs tokens):** el script sumaba el índice equivocado de E3 (`chars`
  en vez de `tok`) en el total, en el CSV y en el costo: E3 salía ~4× inflado. Corregido a
  `por_id[...][4]`. E1, E2, E4 y S1 nunca estuvieron afectados. Esto invalida la cifra de E3 de
  `PLAN_MEDICION_TOKENS.md` § Resultados (completa 124,968 era chars; correcta ≈ 39,231 con el
  contenido actual) — se dejó una nota de corrección ahí.
- **`plotly` instalado** en `skills_env` (7.0.0) y declarado en `AGENTS.md` §2; el script avisa
  y sigue sin gráfica si no está.

**Verificado:** `medir_tokens.py --proyecto output/ecopack-circular --grafica ... --modelo
"DeepSeek V4 Flash"` genera `tokens_por_paso.html` (~9 KB) con 11 barras ordenadas (Paso 4 —
Persona Profile es la primera, 25,862 tok; la última, Paso 1, 10,603). Render comprobado en
Chrome headless: 11 barras, 11 etiquetas de valor, 0 errores de JS.

**Documentado:** `README.md` § «Medir el consumo de tokens», `AGENTS.md` (§2 y §8) y `SKILL.md`
§ «¿Qué hacer al final de todo el flujo?».

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
