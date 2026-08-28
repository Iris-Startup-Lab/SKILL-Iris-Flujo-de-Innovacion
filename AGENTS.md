# Reglas e Instrucciones del Proyecto

> Guía de referencia para cualquier agente que trabaje en este repositorio. Léela completa antes de tocar archivos.

## 1. Qué es este proyecto

Repositorio del **flujo de innovación IRIS** (Iris StartUp Lab). Contiene:

- Una **macro-skill orquestadora** (`SKILL.md` en la raíz, nombre `iris-flujo-de-innovacion`) que guía al usuario por el flujo completo de innovación con human-in-the-loop e histórico persistente.
- **26 sub-skills** en `sub-skills/`, organizadas por fase: Investigación, Descubrimiento, Ideación, Prototipado, Validación.
- La **infraestructura de salida HTML** (`_plantilla_html/`) con diseño corporativo IRIS.
- **Compatibilidad multiplataforma:** Para entornos como Claude Code o Claude Desktop que leen `CLAUDE.md`, las directrices de este archivo se sincronizan a demanda con `.\actualizar_claude.ps1` (o `./actualizar_claude.sh`), asegurando que ambos archivos compartan exactamente las mismas reglas.

## 2. Activación del Entorno de Python (Anaconda)

Cuando ejecutes comandos de Python o scripts dentro de este proyecto, activa siempre el entorno virtual `skills_env` de Anaconda utilizando el siguiente hook en PowerShell:

```powershell
& "E:\Users\1167486\AppData\Local\anaconda3\Scripts\conda.exe" shell.powershell hook | Out-String | Invoke-Expression
conda activate skills_env
```

Python del entorno: **3.12**. Paquetes disponibles: `pandas`, `numpy`, `scipy`, `bs4` (beautifulsoup4), `pytrends`, `python-pptx`, `openpyxl`, `tiktoken` (solo para la medición de tokens; `scripts/medir_tokens.py` cae a `÷4` si no está).

## 3. Estructura del repositorio

```text
SKILL.md                        # Macro-skill orquestadora (iris-flujo-de-innovacion)
pasos.json                      # FUENTE ÚNICA del flujo: 11 pasos, decisiones, rutas de
                                # sub-skills, predecesores y qué se puede omitir
scripts/estado_flujo.py         # Máquina de estados: crea/actualiza flujo_estado.json,
                                # construye el contexto que viaja a cada HTML y regenera STATE.md
scripts/generar_indice.py       # Genera index.html: tablero de navegación que enlaza
                                # los reportes del proyecto (se abre en el navegador)
flujo_estado.json               # Estado del proyecto en curso (lo escribe solo el script)
STATE.md                        # Vista humana GENERADA del estado — no editar a mano
README.md                       # Tutorial de uso y modelos recomendados por herramienta
flujo_agentes.md                # Descripción de cada agente del flujo (vista de pasos.json)
flujo_mermaid.md                # Grafo Mermaid de conexiones (vista de pasos.json)
sub-skills/
  CONTRATO_JSON.md              # Contrato JSON estándar entre skills (decision.siguiente_paso)
  SIMULACION.md                 # Convención de los simuladores (sub-sub-skills): plan.json,
                                # CSV, supuestos estadísticos y propagación de la marca SIMULADO
  1.Investigacion/ ...          # benchmark-mercado, foresight, senales-debiles,
                                # discussion-forums, search-trend-analysis
  2.Descubrimiento/ ...         # entrevistas-empatia, day-in-the-life, encuesta-kano,
                                # discovery-survey, expo-quest, persona-profile,
                                # problem-solution-fit, journey-builder
  3.Ideacion/ ...               # how-might-we, ideacion, caressing-client, referral-builder,
                                # dimensionador-estrategico, business-model-navigator
  4.Prototipado/ ...            # landing-page, landing-ux-analyzer
  5.Validacion/ ...             # email-campaign, explainer-video, feature-stub,
                                # online-ads, popup-store
_plantilla_html/                # Generador + plantilla HTML compartidos (ver §5)
Designs_files/                  # Design_iris_main_colors.md (sistema de diseño oficial)
imagenes_iconos_etc/            # Logos_GS_Iris_transparent.png (logo oficial)
sub-skills_sample_outputs/      # Muestras de salida HTML por skill (para revisar diseño)
Documentos_prompts_base_md/     # Los 24 prompts originales (fuente de cada skill)
PLAN_CONVERSION_SKILLS.md       # Plan de conversión prompts → skills
PLAN_MEDICION_TOKENS.md         # Plan de medición de tokens del flujo (alcance, niveles,
                                # línea base y comparación ruta completa vs mínima)
_template_generador_skill.py    # Genera esqueleto de AGENTE.md desde un prompt .md
actualizar_claude.ps1           # Sincroniza AGENTS.md -> CLAUDE.md a demanda del usuario
actualizar_claude.sh            # Versión bash para entornos Linux/macOS
CLAUDE.md                       # Clon de AGENTS.md (generado a demanda para Claude Code/Desktop)
```

## 4. Convención de sub-skills

Cada sub-skill vive en `sub-skills/<fase>/<skill>/` con:

```text
<skill>/
├── AGENTE.md       # frontmatter (name + description) + instrucciones del agente
├── README.md       # qué hace y cómo generar su HTML
├── assets/logo.png # copia del logo oficial
├── references/     # (opcional) taxonomías/catálogos/rúbricas vinculantes
├── scripts/        # (opcional) scripts Python de soporte
└── simulador/      # (opcional) sub-sub-skill que fabrica datos sintéticos — ver §4.1
```

Reglas:

- **El archivo de instrucciones se llama `AGENTE.md`, no `SKILL.md`.** El gestor rechaza el ZIP
  con `Zip must contain exactly one SKILL.md file` si hay más de uno, y ese nombre lo ocupa la
  macro en la raíz. Al empaquetar una sub-skill suelta (`-SubSkill`), el script la renombra a
  `SKILL.md` —archivo y referencias de texto— porque ahí sí es la skill del paquete.
- **Nombres en kebab-case.** El frontmatter DEBE llevar `name` y `description` (es lo que activa la skill).
- **Autonomía:** los scripts no importan módulos de otras skills; solo stdlib + paquetes PyPI declarados.
- **Extraíble:** cada sub-skill debe poder publicarse suelta con **su carpeta +
  `_plantilla_html/`** al lado, sin el resto del repositorio. En la práctica:
  - Su `AGENTE.md` es autocontenido: el contrato JSON va escrito completo y `pasos.json`,
    `flujo_estado.json` y `CONTRATO_JSON.md` se citan como opcionales («si tienes acceso a…»).
    Las referencias a otras sub-skills también van atenuadas: apuntan a contexto, nunca a un
    archivo sin el cual la skill no funcione.
  - Su `README.md` cierra con **«Uso independiente»**: qué hace falta para correrla sola y
    qué se pierde al sacarla del flujo (contexto en el HTML e histórico).
  - El generador cae en `assets/logo.png` cuando no encuentra el logo oficial, así que el
    comando con `--sin-flujo` funciona igual dentro y fuera del repositorio.
  - El foco sigue siendo el flujo: el comando del paso (`--estado` + `--paso`) va primero y
    el suelto después.
  - El ZIP de una sub-skill suelta lo produce
    `.\empaquetar_skill.ps1 -SubSkill "<fase>/<skill>"` (o `--sub-skill` en el `.sh`):
    su carpeta + `_plantilla_html/`, nada más.
- **Integridad de datos:** nunca inventar cifras. Los datos estimados se marcan `*` o `[REFERENCIA DE INDUSTRIA]`; si no hay dato, `[no disponible]`. Si un script puede calcularlo, el script lo calcula (el LLM redacta interpretación, no cifras).
- **Contrato JSON:** toda skill cierra con el contrato de `sub-skills/CONTRATO_JSON.md` (campos `skill`, `timestamp`, `parametros`, `output`, `decision` con `veredicto` + `siguiente_paso`, `advertencias`).

## 4.1 Sub-sub-skills: los simuladores

Cinco sub-skills de Descubrimiento llevan dentro un **simulador**, la sub-sub-skill que
fabrica datos sintéticos cuando el usuario no tiene a quién entrevistar o encuestar
(`entrevistas-empatia`, `day-in-the-life`, `encuesta-kano`, `discovery-survey`, `expo-quest`).
La convención completa está en **`sub-skills/SIMULACION.md`**; lo esencial:

```text
<skill>/simulador/
├── SIMULADOR.md               # instrucciones (frontmatter name + description)
└── scripts/simular_*.py       # plan.json -> un CSV
```

- **El archivo se llama `SIMULADOR.md`.** No `SKILL.md` (el gestor exige exactamente uno por
  ZIP y lo ocupa la macro) ni `AGENTE.md` (lo ocupa la sub-skill padre). Al empaquetar la
  sub-skill suelta, `simulador/` viaja con ella y el único `SKILL.md` sigue siendo uno.
- **Un simulador entrega un CSV y nada más:** ni HTML, ni `reporte.json`, ni cierre de paso.
  La sub-skill padre analiza ese CSV con los mismos scripts que usaría con datos reales.
- **El LLM escribe el `plan.json` (contenido cualitativo y prevalencias declaradas); el script
  hace todos los números** —muestreo con semilla, conteos, IC de Wilson, saturación—, según la
  regla de integridad de §4: si un script puede calcularlo, lo calcula el script.
- **El archivo se llama `*_SIMULADO.csv`** y lleva una columna `simulado` en cada fila.
- **La marca se propaga sola.** La opción de `pasos.json` marcada `marca_simulacion: true`
  enciende `flujo.simulacion` en el contexto, y de ahí sale el distintivo «Datos simulados» en
  la cabecera de **todos** los HTML posteriores, la caja ámbar del contexto, una advertencia
  automática y la línea del pie. Ninguna skill tiene que acordarse de etiquetar.
- **Validez externa nula, escrito en cada salida.** Una simulación puede ser internamente
  válida (reproducible, con prevalencias declaradas e intervalos bien calculados) y no decir
  nada sobre usuarios reales. Sin esa frase, los intervalos serían decoración pseudo-científica.

## 5. Salidas HTML (diseño IRIS)

La salida principal de cada skill es un **reporte HTML interactivo** autocontenido. Se genera
**siempre desde la raíz del repositorio** (la carpeta que contiene `pasos.json` y `sub-skills/`):

```bash
# como paso del flujo: el contexto del flujo se inyecta solo
python _plantilla_html/scripts/generar_html.py --data reporte.json \
    --estado flujo_estado.json --paso html_N -o html_N.html

# skill suelta, fuera de un proyecto del flujo
python _plantilla_html/scripts/generar_html.py --data reporte.json --sin-flujo -o reporte.html
```

- `_plantilla_html/templates/reporte_base.html` — plantilla interactiva genérica (riel del flujo, bloque de contexto, header con logo, KPIs, buscador/filtros/orden, tarjetas expandibles, Chart.js, decisiones, modal).
- `_plantilla_html/scripts/generar_html.py` — inyecta el contexto del flujo, **valida el esquema** (falla si falta algo), **embebe el logo oficial en base64** y **embebe los reportes de los pasos previos** (`flujo.historial`) para que cada HTML sea navegable por sí mismo dentro de Claude/Codex (desactivable con `--sin-historial`).
- `_plantilla_html/scripts/validar_report_data.py` — validador del esquema `REPORT_DATA`, usable por separado.
- `_plantilla_html/scripts/logo_base64.py` — helper PNG → data URI (también copiado en `senales-debiles/scripts/`).
- Esquema `REPORT_DATA`, bloque `flujo` y guía de uso: `_plantilla_html/README.md`.

**Convención de rutas (obligatoria):** todos los comandos de este repo se ejecutan desde la
raíz. No uses rutas relativas tipo `../../../` dentro de las sub-skills.

**Rutas seguras (obligatorio).** Todo nombre de archivo y de carpeta usa **solo
`[A-Za-z0-9._-]`**: sin acentos, sin espacios, sin `&`. Los gestores de habilidades rechazan el
ZIP con `Zip file contains path with invalid characters` y no documentan qué aceptan, así que se
usa el juego conservador que sí funciona. Por eso las fases son `1.Investigacion`, `3.Ideacion`
y `5.Validacion` sin tilde, y los prompts base van en kebab-case (`how-might-we.md`, no
`How Might We.md`). **El acento se conserva en la prosa y en los nombres de agente**
(«Entrevistas de Empatía», «Dimensionador Estratégico de Ideas de Negocio»): la regla es solo
para rutas. Comprobación:

```powershell
Get-ChildItem -Recurse -File | Where-Object {
  $_.FullName -notmatch 'output|\.git' -and $_.Name -notmatch '^[A-Za-z0-9._-]+$'
}
```

**Estructura del ZIP (obligatorio).** El gestor exige **una sola carpeta de primer nivel,
llamada igual que el `name` del frontmatter** — para la macro, `iris-flujo-de-innovacion/`. Los
archivos sueltos en la raíz del ZIP se rechazan. Lo arma `empaquetar_skill.ps1`/`.sh`, que lee el
`name` del `SKILL.md` y avisa si no es `[a-z0-9-]`. Dentro de esa carpeta la estructura del repo
se conserva intacta, así que la regla «ejecuta desde la raíz» sigue valiendo: la raíz pasa a ser
la carpeta de la skill.

**Exactamente un `SKILL.md` por ZIP (obligatorio).** El gestor responde
`Zip must contain exactly one SKILL.md file. Currently there are N` en cuanto hay más de uno. Por
eso las 26 sub-skills guardan sus instrucciones en **`AGENTE.md`** y el único `SKILL.md` del
repositorio es el de la macro, en la raíz. Al empaquetar una sub-skill suelta, el script renombra
su `AGENTE.md` a `SKILL.md` (y reescribe las referencias de texto), porque en ese paquete la
sub-skill sí es la skill.

**Separador `/` dentro del ZIP (obligatorio).** El formato ZIP exige la barra normal. Si las
entradas llevan la barra invertida de Windows (`iris-flujo-de-innovacion\SKILL.md`), un validador
en Linux lee el `\` como **parte del nombre** y responde
`Zip file contains path with invalid characters`. Es lo que rechazó el paquete durante tres
rondas de diagnóstico.

- **No uses `Compress-Archive`** para el paquete final: en este repo produjo las 171 entradas con
  `\`. `empaquetar_skill.ps1` construye el ZIP con `System.IO.Compression.ZipArchive` y escribe
  el nombre de cada entrada a mano, con `/`.
- **Cuidado al verificarlo:** `zipfile` de Python **normaliza** `\` a `/` en Windows dentro de
  `ZipInfo.__init__`, así que `namelist()` da un **falso negativo**. Hay que mirar
  `orig_filename` o los bytes del directorio central:

```powershell
python -c "import zipfile,sys; z=zipfile.ZipFile(sys.argv[1]); print(sum(1 for i in z.infolist() if chr(92) in i.orig_filename), 'entradas con barra invertida')" iris-flujo-de-innovacion.zip
```

Los dos scripts avisan antes de comprimir si detectan un nombre fuera del juego seguro o más de
un `SKILL.md`, y releen el ZIP escrito para comprobar que ninguna entrada lleva `\`.

**Diseño oficial:** `Designs_files/Design_iris_main_colors.md` (tipografías Sora/Inter, paleta morado `--purple-*` + dorado `--gold-*`). **Logo oficial:** `imagenes_iconos_etc/Logos_GS_Iris_transparent.png`.

## 6. Flujo de la macro-skill (orquestación)

Cuatro invariantes, detallados en `SKILL.md`:

1. **`pasos.json` manda.** Nunca deduzcas qué sub-skill toca ni el nombre de su carpeta:
   está escrito ahí, acentos incluidos. Ningún otro documento define el flujo — `flujo_agentes.md`
   y `flujo_mermaid.md` son vistas suyas.
2. **El estado se cambia con `scripts/estado_flujo.py`,** nunca editando `flujo_estado.json`
   ni `STATE.md` a mano. `mostrar` da el briefing del paso (histórico, decisiones ya tomadas,
   omisiones y su impacto); `completar` / `omitir` / `decision` lo actualizan.
3. **Cada decisión del paso la registra el usuario, o el paso no cierra.** No es una regla de
   estilo: la comprueba el script. `decision` rechaza un nodo o una opción que no estén en
   `pasos.json` y exige el `minimo` de los nodos `multiple`; `completar` se niega a cerrar un
   paso con nodos de decisión sin responder. `--forzar` es el único escape y deja rastro.
4. **Todo HTML lleva el contexto del flujo,** inyectado por el generador con `--estado` y
   `--paso`. Si falta, el generador falla a propósito.

**Por qué la regla 3 está en el script y no solo aquí:** el fallo más común de la orquestación
era ejecutar las sub-skills eligiendo por el usuario y cerrar el paso como si él hubiera
decidido. Un documento no puede impedirlo; una barrera sí. `verificar` audita después lo que
las barreras dejaron pasar con `--forzar`.

**Herencia entre pasos:** al cerrar un paso se registran su `--resumen` (una línea) y sus
`--datos` (el `reporte.json`). Los dos viajan en `flujo.ruta[]` al paso siguiente: el
resumen es el índice y `datos` son los bloques estructurados (`persona`, `psf`, `items`)
que la skill siguiente hereda en lugar de reconstruirlos. Detalle en
`sub-skills/CONTRATO_JSON.md` § «Encadenamiento».

Además:

- La macro invoca sub-skills **leyendo** `sub-skills/<fase>/<skill>/AGENTE.md` por ruta (no depende de registro global).
- **Human-in-the-loop:** se detiene en cada nodo de decisión y espera confirmación. Y también
  entre pasos: cerrar un paso no autoriza el siguiente (`SKILL.md` § «Preguntar si sigue»).
- **Pausar ≠ omitir.** Parar deja el paso pendiente y el proyecto se retoma tal cual; omitir
  declara un hueco que se hereda a todos los reportes siguientes.
- **Preguntar antes de ejecutar.** Los pasos 3, 8 y 11 tienen varios agentes y su primer nodo es
  cuáles se ejecutan (`minimo: 1`). Ejecutarlos todos sin preguntar es el error clásico.
- **Propuestas del agente:** prohibido quitar, renombrar, fusionar o reordenar las opciones
  declaradas; permitido **añadir** solo donde el nodo trae `permite_propuestas` (hoy, la Ambición
  estratégica del paso 7), marcadas como propuesta y registradas con `--forzar`. Qué significa
  cada campo de un nodo está en `pasos.json` → `convenciones_decisiones`.
- **Omisión:** el usuario puede omitir pasos. Los marcados `omitible: false` en `pasos.json`
  requieren `--forzar` y quedan registrados como omisión forzada. El `si_omitido` del paso
  ausente se hereda a los siguientes: lo que falte se sustituye por supuestos marcados `*`
  y se declara en `advertencias`.
- **Ruta mínima:** `html_1 → html_4 → html_7 → html_8 → html_11` (`init --ruta minima`).

## 7. Estilo de Redacción y Tono (Reglas Estilísticas)

**Regla:** Todos los textos generados por la IA para uso con usuarios o clientes (manuales, guías, respuestas, resúmenes) deben seguir estas pautas de estilo y tono.

### 7.1. Propósito y Audiencia

- **Propósito:** Guiar, educar e inspirar a los usuarios del sistema.
- **Audiencia:** Equipos de innovación, gestores de producto y usuarios finales de soluciones tecnológicas.

### 7.2. Tono y Personalidad

El tono de los textos debe ser:

- **Claro:** Lenguaje directo, evitando jerga innecesaria.
- **Conciso:** Máxima información con mínimo texto.
- **Positivo:** Enfocado en soluciones y posibilidades.
- **Profesional pero Cercano:** Técnico cuando sea necesario, pero siempre accesible.

### 7.3. Directrices de Redacción

- **Evitar el "AI Speak":** No usar frases como "Como modelo de IA...", "Estoy aquí para ayudarte...", "Es importante señalar que...".
- **Traducir la notación interna.** El usuario no conoce los identificadores del flujo:
  di «Paso 4 de 11 — Persona Profile», no «html_4» (que es el nombre del archivo de entrega);
  di «la ficha de persona», no «persona-profile». Y explica con palabras qué significan `*`,
  `[REFERENCIA DE INDUSTRIA]` y `[no disponible]` la primera vez que aparezcan: un símbolo
  suelto entre paréntesis solo confunde. Detalle en `SKILL.md` § «Cómo nombrar las cosas ante
  el usuario».
- **Verbos de Acción:** Usar verbos fuertes para inspirar e instruir.
- **Estructura:**
  - **Inicio:** Captar la atención con el beneficio clave.
  - **Cuerpo:** Instrucciones claras y paso a paso.
  - **Cierre:** Resumen del impacto o siguiente paso.

## 8. Referencias rápidas para agentes

| Pregunta | Dónde mirar |
| --- | --- |
| ¿Qué sub-skill invoca el paso N y qué decisiones tiene? | `pasos.json` (fuente única) |
| ¿Cuáles son los dos recorridos y qué pasos lleva cada uno? | `python scripts/estado_flujo.py rutas` |
| ¿En qué paso va el proyecto y qué se decidió? | `python scripts/estado_flujo.py mostrar` |
| ¿Se respetó el flujo? ¿Qué se cerró sin preguntar? | `python scripts/estado_flujo.py verificar` |
| ¿Qué significa cada campo de un nodo de decisión? | `pasos.json` → `convenciones_decisiones` |
| ¿Qué comandos hay para mover el estado? | `python scripts/estado_flujo.py --help` |
| ¿Qué hace cada agente del flujo? | `flujo_agentes.md` |
| ¿Cómo se conectan los agentes? | `flujo_mermaid.md` |
| ¿Cómo se comunican las skills? | `sub-skills/CONTRATO_JSON.md` |
| ¿Cómo se simulan entrevistas/encuestas y cómo se marca? | `sub-skills/SIMULACION.md` |
| ¿Cómo genero un HTML de salida? | `_plantilla_html/README.md` |
| ¿Qué se renderiza del contexto del flujo? | `_plantilla_html/README.md` § bloque `flujo` |
| ¿Cuál es el diseño/logo oficial? | `Designs_files/Design_iris_main_colors.md` + `imagenes_iconos_etc/Logos_GS_Iris_transparent.png` |
| ¿Dónde veo ejemplos de diseño? | `sub-skills_sample_outputs/` |
| ¿Cuál es el prompt original de una skill? | `Documentos_prompts_base_md/<fase>/<archivo>.md` |
| ¿Cómo valido scripts? | Activar `skills_env` y `python -m py_compile <script>` |
| ¿Cuánto cuesta el recorrido en tokens y en dinero? | `python scripts/medir_tokens.py [--proyecto <dir>] [--modelo "<modelo>"]`; precios en `scripts/precios_modelos.json` y `--precios` |
| ¿Cómo navegar entre los reportes de un proyecto? | `python scripts/generar_indice.py --estado <dir>/flujo_estado.json` → `index.html` (abrir en navegador) |
| ¿Cómo sincronizar reglas con Claude Code/Desktop? | `.\actualizar_claude.ps1` (o `./actualizar_claude.sh`) genera `CLAUDE.md` a demanda |

---

**[Regla generada por el sistema para futura incorporación en las directrices de la macro skill].**
