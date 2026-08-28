# IRIS — Innovation Research & Intelligence System

## Autor

- Fernando Dorantes Nieto

Repositorio del **flujo de innovación IRIS** (Iris StartUp Lab). Contiene una **macro-skill orquestadora** (`iris-flujo-de-innovacion`) que guía al usuario por el flujo completo de innovación —de la investigación a la validación— invocando **26 sub-skills** especializadas y consolidando sus resultados en **reportes HTML interactivos** con el diseño corporativo IRIS.

## ¿Dónde ejecutar esta skill?

Esta skill tiene como objetivo que sea totalmente agnóstica, entonces está diseñada para
ejecutarse en cualquier gestor de skills (Kimi Code, Antigravity, Claude Desktop/Claude Code, OpenCode, ChatGPT/Codex).

## Qué contiene

| Elemento | Descripción |
| --- | --- |
| `SKILL.md` | Macro-skill orquestadora (nombre `iris-flujo-de-innovacion`). |
| `pasos.json` | **Fuente única del flujo**: los 11 pasos, sus decisiones, las rutas exactas de las sub-skills y qué se puede omitir. |
| `scripts/estado_flujo.py` | Máquina de estados del flujo: avance, decisiones, omisiones y el contexto que viaja a cada HTML. |
| `flujo_estado.json` / `STATE.md` | Estado del proyecto en curso (JSON) y su vista humana generada. |
| `flujo_agentes.md` / `flujo_mermaid.md` | Vistas del flujo: descripción de cada agente y grafo Mermaid. |
| `sub-skills/` | Las 26 sub-skills, organizadas por fase. Cinco de Descubrimiento llevan dentro un `simulador/` para fabricar datos sintéticos cuando no hay a quién entrevistar (ver `sub-skills/SIMULACION.md`). |
| `_plantilla_html/` | Generador + plantilla + validador HTML compartidos (salida interactiva con diseño IRIS). |
| `sub-skills_sample_outputs/` | Muestras de salida HTML por skill (para revisar el diseño). |
| `Documentos_prompts_base_md/` | Los 24 prompts originales (fuente de cada skill). |
| `PLAN_MEDICION_TOKENS.md` | Plan para medir el consumo de tokens por paso y sub-skill, y comparar la ruta completa contra la mínima. |
| `actualizar_claude.ps1` / `CLAUDE.md` | Script de sincronización a demanda y clon de `AGENTS.md` para entornos Claude Code / Claude Desktop. |

## Fases del flujo

1. **Investigación** — benchmark-mercado, foresight, senales-debiles, discussion-forums, search-trend-analysis.
2. **Descubrimiento** — entrevistas-empatia, day-in-the-life, encuesta-kano, discovery-survey, expo-quest, persona-profile, problem-solution-fit, journey-builder.
3. **Ideación** — how-might-we, ideacion, caressing-client, referral-builder, dimensionador-estrategico, business-model-navigator.
4. **Prototipado** — landing-page, landing-ux-analyzer.
5. **Validación** — email-campaign, explainer-video, feature-stub, online-ads, popup-store.

## Tutorial de uso

### Cómo iniciar un proyecto

Solo hacen falta tres datos: **nombre**, **objetivo** y **audiencia**. Todo lo demás se
pregunta paso a paso, cuando toca.

```bash
python scripts/estado_flujo.py init --proyecto "Huertos urbanos MX" \
    --objetivo "Validar demanda de kits de huerto" \
    --audiencia "Familias urbanas 28-45, CDMX"
```

Luego la macro-skill arranca con el nodo de decisión **«¿Cómo quieres iniciar?»**
(Estado actual → Benchmark · Futuros → Foresight · Señales débiles → Señales débiles ·
Opiniones → Discussion Forums) y avanza paso por paso con **human-in-the-loop**,
deteniéndose en cada decisión y registrando todo en el estado del flujo.

### Dos recorridos

| Recorrido | Pasos | Para qué |
| --- | --- | --- |
| **Completa** | 11 | El proceso íntegro, de la investigación al experimento. |
| **Mínima** (`--ruta minima`) | 5 | Investigación → Persona Profile → El reto creativo (How Might We) + Ambición estratégica → Ideación → Prototipado y Validación, sin las etapas intermedias. |

Los 5 pasos de la ruta mínima son **Inicio + Investigación**, **Persona Profile**,
**El reto creativo (How Might We) + Ambición estratégica**, **Ideación** y
**Prototipado y Validación**. Se salta los 6
restantes: entrevistas, descubrimiento de campo, Problem-Solution Fit, Journey Builder,
Dimensionador estratégico y Business Model Navigator — cada uno con su impacto declarado en los
reportes posteriores.

Para ver los dos recorridos con el nombre de cada paso y qué pierde el corto:

```bash
python scripts/estado_flujo.py rutas
```

### Omitir pasos

En cada paso el usuario elige **Ejecutar**, **Omitir** o **¿Por qué importa?**. Al omitir,
el hueco queda declarado: el reporte de cada paso posterior muestra qué falta y por qué,
y los datos que dependían de ese input se marcan como supuestos con `*`.

Los pasos que sostienen el resto del flujo (`html_4` Persona Profile, `html_7`
El reto creativo (How Might We), `html_8`
Ideación, `html_11` Prototipado y Validación) piden confirmación extra antes de omitirse.

### Contexto en cada reporte

Los 11 HTML llevan **el contexto completo del flujo**: un riel de progreso con los 11
pasos (completados, omitidos, el actual), las decisiones tomadas hasta ese punto, el
resumen de cada paso previo con enlace a su contenido —embebido en el propio HTML—, y
los pasos omitidos con su impacto. Ningún reporte se lee fuera de contexto.

### Navegar entre los reportes

Cada reporte es **incremental y navegable por sí mismo**: `html_N` embebe dentro del mismo
archivo los reportes de los pasos `1…N−1`, y el riel del flujo salta a ellos con un ancla
interna (`#paso-N`). Así se navega hacia atrás también desde la **vista previa embebida** de
un gestor (Claude/Codex), que no tiene sistema de archivos para abrir a un HTML vecino.

Lo que aún no existe —los pasos **futuros**— queda como **enlace relativo** a
`html_4.html`, `html_11.html`, …, y funciona cuando los 11 HTML están en la **misma
carpeta** y se abren con el **navegador**. El embebido se desactiva con `--sin-historial`
(archivos más pequeños, sin navegación interna).

Para una puerta de entrada única, genera el tablero de navegación:

```bash
python scripts/generar_indice.py --estado <carpeta>/flujo_estado.json
```

Escribe `index.html` en esa carpeta, con los 11 pasos, su estado y un botón «Abrir
reporte» por cada paso completado. Se abre una vez y desde ahí se navega a cualquier
reporte.

### Retomar un proyecto

El estado es persistente. Para saber dónde quedó:

```bash
python scripts/estado_flujo.py mostrar
```

Devuelve el paso actual, el histórico de sus predecesores, las decisiones ya tomadas
(que no se vuelven a preguntar) y las sub-skills que toca invocar. Cada nodo de decisión
sale marcado como **PENDIENTE**, **RESPONDIDA** o **no aplica**, y las sub-skills como
`[ELEGIDA por el usuario]` o `(no elegida)`.

### Comprobar que se respetó el flujo

El flujo no se cumple por buena voluntad del agente: está comprobado por el script.

- `decision` **rechaza** un nodo o una opción que no estén en `pasos.json`, y exige el mínimo
  de opciones de los nodos de elección múltiple.
- `completar` **se niega** a cerrar un paso con decisiones del usuario sin registrar.
- `--forzar` es el único escape en los dos casos, y deja rastro en el histórico.

Para auditar un proyecto entero —al terminar o cuando algo no cuadre:

```bash
python scripts/estado_flujo.py verificar --estado <carpeta>/flujo_estado.json
```

Responde qué se cerró sin preguntar lo que había que preguntar: pasos cerrados sin su
decisión, sin resumen, sin datos o sin entrega; omisiones sin motivo; predecesores saltados
con `--forzar`; y decisiones que no corresponden a ningún nodo del flujo. Devuelve 0 si no
hay nada y 2 con la lista si lo hay, así que sirve como comprobación automática.

### Modelo recomendado por herramienta

| Herramienta | Recomendado | Alternativa |
| --- | --- | --- |
| **Claude Desktop** | Claude Sonnet | Claude Opus (más gasto) |
| **Antigravity** | Gemini 3.1 Pro | — |
| **OpenCode** | DeepSeek V4 Flash | — |
| **ChatGPT Desktop** | GPT Terra | — |

### Medir el consumo de tokens

Al terminar el flujo, puedes medir cuántos tokens costó cada paso y el recorrido completo, y
verlo en una **gráfica de barras** (Plotly) ordenada de mayor a menor —el paso que más consume
es la primera barra, en dorado—:

```bash
python scripts/medir_tokens.py --proyecto <carpeta> --grafica <carpeta>/tokens_por_paso.html
```

- Con `--proyecto` se miden los tokens reales del proyecto (briefing, herencia y salida de cada
  paso), no solo los archivos de las sub-skills.
- Con `--modelo "Claude Sonnet"` se añade el costo estimado en dinero por paso y el total
  (precios en `scripts/precios_modelos.json`).
- `--grafica` escribe una gráfica Plotly autocontenida que se abre en el navegador (requiere
  conexión). Sin `plotly` instalado, el script lo avisa y sigue sin la gráfica.

El detalle del plan y de los niveles de medición está en `PLAN_MEDICION_TOKENS.md`.

### Sincronización para Claude Code / Claude Desktop (CLAUDE.md)

Para utilizar este repositorio en entornos como **Claude Code** o **Claude Desktop** que leen `CLAUDE.md`, las directrices del proyecto residen en `AGENTS.md` y se clonan a demanda para mantener la compatibilidad sin inconsistencias.

Para actualizar `CLAUDE.md` a partir de `AGENTS.md`:

```powershell
.\actualizar_claude.ps1
```

O en Linux / macOS:

```bash
./actualizar_claude.sh
```

## Salidas HTML (diseño IRIS)

Cada skill entrega su resultado como un **reporte HTML interactivo** autocontenido (logo embebido en base64, tipografías Sora/Inter, paleta morado/dorado). Se genera **desde la raíz del repositorio**:

```bash
# como paso del flujo: el contexto del flujo se inyecta solo
python _plantilla_html/scripts/generar_html.py --data reporte.json \
    --estado flujo_estado.json --paso html_4 -o html_4.html

# skill suelta, fuera de un proyecto del flujo
python _plantilla_html/scripts/generar_html.py --data reporte.json --sin-flujo -o reporte.html
```

El generador **valida el esquema y falla si falta algo**, para que un reporte incompleto no se entregue como HTML en blanco.

- Esquema del JSON (`REPORT_DATA`), bloque `flujo` y guía: `_plantilla_html/README.md`.
- Diseño oficial: `Designs_files/Design_iris_main_colors.md`.
- Logo oficial: `imagenes_iconos_etc/Logos_GS_Iris_transparent.png`.
- Ejemplos visuales: `sub-skills_sample_outputs/`.

## Empaquetado de la skill (ZIP)

Los gestores de agentes suelen tener un límite de **30 MB** por skill. El paquete con los documentos necesarios pesa ~3 MB (muy por debajo del límite). Para generarlo:

Cuatro requisitos del gestor que el script ya cumple por ti:

> **Separador `/` en las entradas del ZIP.** Con la barra invertida de Windows, un validador en
> Linux lee `iris-flujo-de-innovacion\SKILL.md` como un nombre con un carácter inválido dentro.
> Por eso el script **no usa `Compress-Archive`**: construye el ZIP con `ZipArchive` escribiendo
> cada nombre con `/`, y relee el resultado para confirmarlo.
>
> **Una sola carpeta raíz.** El ZIP lleva `iris-flujo-de-innovacion/` como única carpeta de
> primer nivel, con el mismo nombre que el `name` del frontmatter. Archivos sueltos en la raíz
> del ZIP se rechazan.
>
> **Un solo `SKILL.md`.** El gestor responde `Zip must contain exactly one SKILL.md file` en
> cuanto hay más de uno. Por eso las 26 sub-skills guardan sus instrucciones en **`AGENTE.md`** y
> el único `SKILL.md` es el de la macro. Al empaquetar una sub-skill suelta, el script le devuelve
> el nombre `SKILL.md`, porque ahí sí es ella la skill del paquete.
>
> **Rutas solo `[A-Za-z0-9._-]`.** Sin acentos, espacios ni `&`, o el gestor responde
> `Zip file contains path with invalid characters`. De ahí que las fases sean `1.Investigacion`,
> `3.Ideacion` y `5.Validacion`, y que los prompts base estén en kebab-case. El acento sí se
> conserva en la prosa y en los nombres de agente.

Los dos scripts avisan si detectan un nombre fuera del juego seguro, más de un `SKILL.md` o una
entrada con barra invertida.

**PowerShell (Windows):**

```powershell
.\empaquetar_skill.ps1                              # ZIP básico (~3 MB)
.\empaquetar_skill.ps1 -IncludeSamples              # + muestras de diseño
.\empaquetar_skill.ps1 -IncludeFlujoMap             # + mapa visual (flujo-agentes-mapa-2.html, ~7.3 MB)
.\empaquetar_skill.ps1 -Output "mi_skill.zip"       # nombre personalizado
```

**Bash (Linux/macOS):**

```bash
./empaquetar_skill.sh                               # ZIP básico
./empaquetar_skill.sh --samples --flujo             # opciones adicionales
./empaquetar_skill.sh -o mi_skill.zip               # nombre personalizado
```

Opciones: `-IncludeSamples`/`--samples` (muestras), `-IncludeFlujoMap`/`--flujo` (mapa visual), `-IncludeDocx`/`--docx` (prompts .docx), `-IncludeTemp`/`--temp` (screenshots).

### Empaquetar una sub-skill sola

Cada sub-skill se publica suelta con **su carpeta + `_plantilla_html/`** al lado (ver «Uso
independiente» en su `README.md`). Ese ZIP se genera con `-SubSkill`/`--sub-skill`:

```powershell
.\empaquetar_skill.ps1 -SubSkill "2.Descubrimiento/persona-profile"
.\empaquetar_skill.ps1 -ListSubSkills                       # rutas válidas
```

```bash
./empaquetar_skill.sh --sub-skill "2.Descubrimiento/persona-profile"
./empaquetar_skill.sh --list-sub-skills
```

El ZIP sale como `<sub-skill>.zip` (~0.13 MB) salvo que pases `-Output`/`-o`, y contiene
`persona-profile/` + `_plantilla_html/`. Con `-IncludeSamples`/`--samples` añade las muestras
de diseño de esa sub-skill en `sample_outputs/`; las opciones de la macro (`--flujo`, `--docx`,
`--temp`) no aplican y avisan. Descomprimido en una carpeta limpia, el generador encuentra el
logo en `assets/logo.png` de la sub-skill:

```bash
python _plantilla_html/scripts/generar_html.py --data reporte.json --sin-flujo -o reporte.html
#   logo embebido: 122 KB (base64) · copia local de la sub-skill
```

**Qué se incluye por defecto:** `SKILL.md`, `pasos.json`, `scripts/`, `STATE.md`, `AGENTS.md`, `CLAUDE.md`, `actualizar_claude.ps1`, `README.md`, `flujo_agentes.md`, `flujo_mermaid.md`, `sub-skills/`, `_plantilla_html/`, `Designs_files/`, `imagenes_iconos_etc/`, `Documentos_prompts_base_md/`. **Se excluyen:** `__pycache__`/`*.pyc`, el mapa visual grande, notebooks y archivos de desarrollo.
