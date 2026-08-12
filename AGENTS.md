# Reglas e Instrucciones del Proyecto

> Guía de referencia para cualquier agente que trabaje en este repositorio. Léela completa antes de tocar archivos.

## 1. Qué es este proyecto

Repositorio del **flujo de innovación IRIS** (Iris StartUp Lab). Contiene:

- Una **macro-skill orquestadora** (`SKILL.md` en la raíz, nombre `iris-flujo-de-innovacion`) que guía al usuario por el flujo completo de innovación con human-in-the-loop e histórico persistente.
- **26 sub-skills** en `sub-skills/`, organizadas por fase: Investigación, Descubrimiento, Ideación, Prototipado, Validación.
- La **infraestructura de salida HTML** (`_plantilla_html/`) con diseño corporativo IRIS.

## 2. Activación del Entorno de Python (Anaconda)

Cuando ejecutes comandos de Python o scripts dentro de este proyecto, activa siempre el entorno virtual `skills_env` de Anaconda utilizando el siguiente hook en PowerShell:

```powershell
& "E:\Users\1167486\AppData\Local\anaconda3\Scripts\conda.exe" shell.powershell hook | Out-String | Invoke-Expression
conda activate skills_env
```

Python del entorno: **3.12**. Paquetes disponibles: `pandas`, `numpy`, `scipy`, `bs4` (beautifulsoup4), `pytrends`, `python-pptx`, `openpyxl`.

## 3. Estructura del repositorio

```
SKILL.md                        # Macro-skill orquestadora (iris-flujo-de-innovacion)
pasos.json                      # FUENTE ÚNICA del flujo: 11 pasos, decisiones, rutas de
                                # sub-skills, predecesores y qué se puede omitir
scripts/estado_flujo.py         # Máquina de estados: crea/actualiza flujo_estado.json,
                                # construye el contexto que viaja a cada HTML y regenera STATE.md
flujo_estado.json               # Estado del proyecto en curso (lo escribe solo el script)
STATE.md                        # Vista humana GENERADA del estado — no editar a mano
README.md                       # Tutorial de uso y modelos recomendados por herramienta
flujo_agentes.md                # Descripción de cada agente del flujo (vista de pasos.json)
flujo_mermaid.md                # Grafo Mermaid de conexiones (vista de pasos.json)
sub-skills/
  CONTRATO_JSON.md              # Contrato JSON estándar entre skills (decision.siguiente_paso)
  1.Investigación/ ...          # benchmark-mercado, foresight, senales-debiles,
                                # discussion-forums, search-trend-analysis
  2.Descubrimiento/ ...         # entrevistas-empatia, day-in-the-life, encuesta-kano,
                                # discovery-survey, expo-quest, persona-profile,
                                # problem-solution-fit, journey-builder
  3.Ideación/ ...               # how-might-we, ideacion, caressing-client, referral-builder,
                                # dimensionador-estrategico, business-model-navigator
  4.Prototipado/ ...            # landing-page, landing-ux-analyzer
  5.Validación/ ...             # email-campaign, explainer-video, feature-stub,
                                # online-ads, popup-store
_plantilla_html/                # Generador + plantilla HTML compartidos (ver §5)
Designs_files/                  # Design_iris_main_colors.md (sistema de diseño oficial)
imagenes_iconos_etc/            # Logos_GS_Iris_transparent.png (logo oficial)
sub-skills_sample_outputs/      # Muestras de salida HTML por skill (para revisar diseño)
Documentos_prompts_base_md/     # Los 24 prompts originales (fuente de cada skill)
PLAN_CONVERSION_SKILLS.md       # Plan de conversión prompts → skills
_template_generador_skill.py    # Genera esqueleto de SKILL.md desde un prompt .md
```

## 4. Convención de sub-skills

Cada sub-skill vive en `sub-skills/<fase>/<skill>/` con:

```
<skill>/
├── SKILL.md        # frontmatter (name + description) + instrucciones del agente
├── README.md       # qué hace y cómo generar su HTML
├── assets/logo.png # copia del logo oficial
├── references/     # (opcional) taxonomías/catálogos/rúbricas vinculantes
└── scripts/        # (opcional) scripts Python de soporte
```

Reglas:

- **Nombres en kebab-case.** El frontmatter DEBE llevar `name` y `description` (es lo que activa la skill).
- **Autonomía:** los scripts no importan módulos de otras skills; solo stdlib + paquetes PyPI declarados.
- **Integridad de datos:** nunca inventar cifras. Los datos estimados se marcan `*` o `[REFERENCIA DE INDUSTRIA]`; si no hay dato, `[no disponible]`. Si un script puede calcularlo, el script lo calcula (el LLM redacta interpretación, no cifras).
- **Contrato JSON:** toda skill cierra con el contrato de `sub-skills/CONTRATO_JSON.md` (campos `skill`, `timestamp`, `parametros`, `output`, `decision` con `veredicto` + `siguiente_paso`, `advertencias`).

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
- `_plantilla_html/scripts/generar_html.py` — inyecta el contexto del flujo, **valida el esquema** (falla si falta algo) y **embebe el logo oficial en base64**.
- `_plantilla_html/scripts/validar_report_data.py` — validador del esquema `REPORT_DATA`, usable por separado.
- `_plantilla_html/scripts/logo_base64.py` — helper PNG → data URI (también copiado en `senales-debiles/scripts/`).
- Esquema `REPORT_DATA`, bloque `flujo` y guía de uso: `_plantilla_html/README.md`.

**Convención de rutas (obligatoria):** todos los comandos de este repo se ejecutan desde la
raíz. No uses rutas relativas tipo `../../../` dentro de las sub-skills.

**Diseño oficial:** `Designs_files/Design_iris_main_colors.md` (tipografías Sora/Inter, paleta morado `--purple-*` + dorado `--gold-*`). **Logo oficial:** `imagenes_iconos_etc/Logos_GS_Iris_transparent.png`.

## 6. Flujo de la macro-skill (orquestación)

Tres invariantes, detallados en `SKILL.md`:

1. **`pasos.json` manda.** Nunca deduzcas qué sub-skill toca ni el nombre de su carpeta:
   está escrito ahí, acentos incluidos. Ningún otro documento define el flujo — `flujo_agentes.md`
   y `flujo_mermaid.md` son vistas suyas.
2. **El estado se cambia con `scripts/estado_flujo.py`,** nunca editando `flujo_estado.json`
   ni `STATE.md` a mano. `mostrar` da el briefing del paso (histórico, decisiones ya tomadas,
   omisiones y su impacto); `completar` / `omitir` / `decision` lo actualizan.
3. **Todo HTML lleva el contexto del flujo,** inyectado por el generador con `--estado` y
   `--paso`. Si falta, el generador falla a propósito.

Además:

- La macro invoca sub-skills **leyendo** `sub-skills/<fase>/<skill>/SKILL.md` por ruta (no depende de registro global).
- **Human-in-the-loop:** se detiene en cada nodo de decisión y espera confirmación.
- **Omisión:** el usuario puede omitir pasos. Los marcados `omitible: false` en `pasos.json`
  requieren `--forzar` y quedan registrados como omisión forzada. El `si_omitido` del paso
  ausente se hereda a los siguientes: lo que falte se sustituye por supuestos marcados `*`
  y se declara en `advertencias`.
- **Ruta mínima:** `html_1 → html_4 → html_7 → html_8 → html_11` (`init --ruta minima`).

## 7. Estilo de Redacción y Tono (Reglas Estilísticas)

**Regla:** Todos los textos generados por la IA para uso con usuarios o clientes (manuales, guías, respuestas, resúmenes) deben seguir estas pautas de estilo y tono.

### 7.1. Propósito y Audiencia

* **Propósito:** Guiar, educar e inspirar a los usuarios del sistema.
* **Audiencia:** Equipos de innovación, gestores de producto y usuarios finales de soluciones tecnológicas.

### 7.2. Tono y Personalidad

El tono de los textos debe ser:

* **Claro:** Lenguaje directo, evitando jerga innecesaria.
* **Conciso:** Máxima información con mínimo texto.
* **Positivo:** Enfocado en soluciones y posibilidades.
* **Profesional pero Cercano:** Técnico cuando sea necesario, pero siempre accesible.

### 7.3. Directrices de Redacción

* **Evitar el "AI Speak":** No usar frases como "Como modelo de IA...", "Estoy aquí para ayudarte...", "Es importante señalar que...".
* **Verbos de Acción:** Usar verbos fuertes para inspirar e instruir.
* **Estructura:**
  * **Inicio:** Captar la atención con el beneficio clave.
  * **Cuerpo:** Instrucciones claras y paso a paso.
  * **Cierre:** Resumen del impacto o siguiente paso.

## 8. Referencias rápidas para agentes

| Pregunta | Dónde mirar |
|---|---|
| ¿Qué sub-skill invoca el paso N y qué decisiones tiene? | `pasos.json` (fuente única) |
| ¿En qué paso va el proyecto y qué se decidió? | `python scripts/estado_flujo.py mostrar` |
| ¿Qué comandos hay para mover el estado? | `python scripts/estado_flujo.py --help` |
| ¿Qué hace cada agente del flujo? | `flujo_agentes.md` |
| ¿Cómo se conectan los agentes? | `flujo_mermaid.md` |
| ¿Cómo se comunican las skills? | `sub-skills/CONTRATO_JSON.md` |
| ¿Cómo genero un HTML de salida? | `_plantilla_html/README.md` |
| ¿Qué se renderiza del contexto del flujo? | `_plantilla_html/README.md` § bloque `flujo` |
| ¿Cuál es el diseño/logo oficial? | `Designs_files/Design_iris_main_colors.md` + `imagenes_iconos_etc/Logos_GS_Iris_transparent.png` |
| ¿Dónde veo ejemplos de diseño? | `sub-skills_sample_outputs/` |
| ¿Cuál es el prompt original de una skill? | `Documentos_prompts_base_md/<fase>/<archivo>.md` |
| ¿Cómo valido scripts? | Activar `skills_env` y `python -m py_compile <script>` |

---

**[Regla generada por el sistema para futura incorporación en las directrices de la macro skill].**
