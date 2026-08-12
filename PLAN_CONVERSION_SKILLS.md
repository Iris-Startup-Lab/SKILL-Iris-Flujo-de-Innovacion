# Plan de Conversión: Prompts a Skills — Flujo de Innovación IRIS

> **Objetivo:** Convertir los 24 prompts de `Documentos_prompts_base_md/` en Agent Skills dentro de `sub-skills/`, siguiendo el template definido por `sub-skills/senales-debiles/`. La macro-skill orquestadora (`macro_skill_flujo_de_innovacion_iris`) llamará a cada sub-skill según el flujo definido en `flujo_agentes.md`.

---

## 1. Visión General

### 1.1 Artefactos de entrada
| Directorio | Contenido |
|---|---|
| `Documentos_prompts_base_md/` | 24 prompts organizados en 5 fases del flujo de innovación |
| `sub-skills/senales-debiles/` | Template de referencia: `SKILL.md`, `SPEC.md`, `references/`, `scripts/` |
| `flujo_agentes.md` | Definición del flujo de agentes, nodos de decisión y dependencias |
| `flujo_mermaid.md` | Grafo de conexiones entre agentes (formato Mermaid) |

### 1.2 Template de Skill (basado en `senales-debiles`)
Cada sub-skill debe contener:
```
sub-skills/<nombre-skill>/
├── SKILL.md              # YAML frontmatter + instrucciones del agente
├── SPEC.md               # (opcional) especificación de formato/output
├── references/           # Archivos de referencia vinculantes
│   └── *.md
└── scripts/              # Scripts Python de soporte (si aplica)
    └── *.py
```

### 1.3 Principios de diseño
1. **Cada sub-skill es autocontenida e independiente.** Puede invocarse sola o como parte del flujo.
2. **El input/output entre skills se estandariza** mediante un contrato JSON mínimo (parámetros de entrada y salida estructurada).
3. **Los scripts Python se añaden solo cuando son necesarios** (cálculos, validación, generación de archivos). Si la skill es puramente consultiva/diseño (LLM-only), no lleva scripts.
4. **Las referencias se extraen del prompt original** cuando hay catálogos, taxonomías, rúbricas o tablas de referencia que deban ser vinculantes.
5. **La macro-skill orquestadora** lee el contexto del usuario, determina en qué fase del flujo se encuentra y llama a las sub-skills correspondientes.

---

## 2. Inventario Completo: Prompts → Skills

### Fase 1: Investigación (3 skills)

| # | Prompt original | Nombre de skill | Tipo | Scripts necesarios |
|---|---|---|---|---|
| 1 | `Benchmark.md` | `benchmark-mercado` | Mixto (búsqueda web + análisis) | No (LLM-only con `webfetch`) |
| 2 | `Discussion Forums.md` | `discussion-forums` | Diseño/Planeación | No (LLM-only con `webfetch` para investigación contextual) |
| 3 | `Search Trend Analysis.md` | `search-trend-analysis` | **Instrumentado** (pytrends + webfetch + análisis) | `google_trends.py` (datos reales de Google Trends vía pytrends) + `references/benchmarks-industria.md` |

### Fase 2: Descubrimiento (8 skills)

| # | Prompt original | Nombre de skill | Tipo | Scripts necesarios |
|---|---|---|---|---|
| 4 | `A Day In The Life.md` | `day-in-the-life` | Diseño/Planeación | No (LLM-only, plantilla) |
| 5 | `Discovery Survey.md` | `discovery-survey` | Diseño/Cálculo | `calcular_muestra.py` (fórmulas n, n_aj, envíos) |
| 6 | `Encuesta modelo Kano.md` | `encuesta-kano` | Generación | `clasificar_kano.py` (tabla de clasificación funcional × disfuncional) |
| 7 | `Entrevistas de Empatía.md` | `entrevistas-empatia` | Diseño/Planeación | No (LLM-only, guía + plantilla) |
| 8 | `Expo Quest.md` | `expo-quest` | Investigación/Web | No (LLM-only con web search) |
| 9 | `Journey Builder & Structure.md` | `journey-builder` | Análisis/Estructuración | No (LLM-only) |
| 10 | `Persona Profile.md` | `persona-profile` | Generación | No (LLM-only) |
| 11 | `Problem Solution Fit.md` | `problem-solution-fit` | Análisis | `exportar_csv.py` (generación de CSV estructurado) |

### Fase 3: Ideación (6 skills)

| # | Prompt original | Nombre de skill | Tipo | Scripts necesarios |
|---|---|---|---|---|
| 12 | `Business Model Navigator.md` | `business-model-navigator` | Recomendación | No (LLM-only, catálogo en `references/`) |
| 13 | `Caressing the client.md` | `caressing-client` | Generación | No (LLM-only) |
| 14 | `Dimensionador Estratégico de Ideas.md` | `dimensionador-ideas` | Análisis/Scoring | `calcular_score.py` (score compuesto /25 + consolidación multi-buyer persona) |
| 15 | `How Might We.md` | `how-might-we` | Facilitación | No (LLM-only) |
| 16 | `Ideación.md` | `ideacion` | Facilitación/Generación | `evaluar_ideas.py` (cálculo de scores Novedad/Utilidad/Factibilidad) |
| 17 | `Referral builder .md` | `referral-builder` | Generación | No (LLM-only) |

### Fase 4: Prototipado (2 skills)

| # | Prompt original | Nombre de skill | Tipo | Scripts necesarios |
|---|---|---|---|---|
| 18 | `Landing Page UX Analyzer.md` | `landing-ux-analyzer` | Auditoría | No (LLM-only, requiere capturas/URL del usuario) |
| 19 | `Landing Page.md` | `landing-page` | Diseño/Planeación | No (LLM-only) |

### Fase 5: Validación (5 skills)

| # | Prompt original | Nombre de skill | Tipo | Scripts necesarios |
|---|---|---|---|---|
| 20 | `E-mail Campaign.md` | `email-campaign` | Diseño/Planeación | `calcular_significancia.py` (tamaño de muestra para email, poder estadístico) |
| 21 | `Explainer Video.md` | `explainer-video` | Diseño/Planeación | No (LLM-only, prompt para Runway) |
| 22 | `Feature Stub.md` | `feature-stub` | Diseño/Planeación | No (LLM-only) |
| 23 | `Online Ads.md` | `online-ads` | Generación (copy + prompts de imagen) | No (LLM-only — **no genera imágenes**, produce prompts listos para herramientas externas: Midjourney, DALL·E, Stable Diffusion, Adobe Firefly) |
| 24 | `Pop Up Store.md` | `popup-store` | Diseño/Planeación | No (LLM-only) |

---

## 3. Estructura Detallada de Cada Skill

### 3.1 Formato de `SKILL.md`

Cada `SKILL.md` sigue este esquema:

```yaml
---
name: <nombre-skill>
description: <descripción corta para activación por triggering>
category: <fase del flujo>
inputs:
  - nombre: <param>
    descripcion: <qué es>
    obligatorio: true/false
outputs:
  - <descripción del entregable principal>
---
```

Seguido de secciones:
1. **Rol y Contexto** — Qué hace el agente, con qué marco teórico.
2. **Alcance** — Qué SÍ y qué NO hace (diseño vs. ejecución).
3. **Parámetros de Entrada** — Lista de variables que el agente debe solicitar/confirmar.
4. **Instrucciones** — El prompt adaptado, con marcadores `{{variable}}`.
5. **Formato de Salida** — Estructura esperada del output.
6. **Reglas y Restricciones** — Reglas de integridad, compliance, verificabilidad.
7. **Referencias** — Enlaces a `references/` y `scripts/` si aplica.

### 3.2 Skills que requieren `references/`

| Skill | Referencias a extraer del prompt |
|---|---|
| `search-trend-analysis` | Benchmarks de industria (CTR, CPC, CPL, volúmenes por región/idioma) para calibrar criterios de éxito |
| `business-model-navigator` | Catálogo de 55+5 patrones de Business Model Navigator (tabla completa) |
| `dimensionador-ideas` | Rúbrica de scoring con los 10 módulos, tabla de consolidación multi-buyer persona |
| `encuesta-kano` | Tabla de clasificación Kano (M/O/A/I/R/Q), opciones de respuesta |
| `how-might-we` | Matriz de ambición estratégica × palancas |
| `ideacion` | Definiciones de metodologías (SCAMPER, Crazy 8s, Doblin, Analogía), rúbrica de evaluación |
| `discovery-survey` | Fórmulas de tamaño de muestra (Z, p, e, n, n_aj), referencias estadísticas |

### 3.3 Skills que requieren `scripts/`

| Skill | Script | Función |
|---|---|---|
| `search-trend-analysis` | `google_trends.py` | Consulta Google Trends vía pytrends: obtiene interés relativo 0-100, tendencia temporal, consultas relacionadas, desglose por región. Datos **reales** (no estimaciones del modelo). |
| `discovery-survey` | `calcular_muestra.py` | Calcula n, n_aj, envíos requeridos dados N, confianza, margen de error, tasa de respuesta |
| `encuesta-kano` | `clasificar_kano.py` | Dado un CSV de respuestas (funcional × disfuncional), clasifica cada feature y genera tabla M/O/A/I/R/Q |
| `problem-solution-fit` | `exportar_csv.py` | Estructura el análisis en CSV con columnas estándar (problema, impacto, costo, etc.) |
| `dimensionador-ideas` | `calcular_score.py` | Calcula score /25 a partir de los 10 módulos, consolida multi-buyer persona, genera ranking |
| `ideacion` | `evaluar_ideas.py` | Calcula scores Novedad/Utilidad/Factibilidad, genera ranking y tabla de evaluación |
| `email-campaign` | `calcular_significancia.py` | Calcula tamaño de muestra mínimo para detectar diferencias en open rate / CTR con poder estadístico dado |

### 3.4 Skills LLM-only (sin scripts ni references)
Estas skills son puramente conversacionales/de diseño. El LLM ejecuta las instrucciones directamente. Algunas usan `webfetch` para búsqueda web de datos reales, pero no dependen de scripts Python:

`benchmark-mercado`, `discussion-forums`, `day-in-the-life`, `entrevistas-empatia`, `expo-quest`, `journey-builder`, `persona-profile`, `caressing-client`, `referral-builder`, `landing-ux-analyzer`, `landing-page`, `explainer-video`, `feature-stub`, `online-ads`, `popup-store`

### 3.5 Estrategia de Instrumentación: Skills con Datos Reales

Algunas skills se benefician de **ejecutar consultas reales** en lugar de depender únicamente de los pesos del modelo. Se definen tres niveles de instrumentación:

| Nivel | Herramienta | Qué obtiene | Precisión | Ejemplos de skills |
|---|---|---|---|---|
| **A. Scripts Python** | `bash` → `pytrends`, `requests`, `pandas` | Datos estructurados desde APIs o cálculo determinista | **Real verificable** | `search-trend-analysis`, `encuesta-kano`, `calcular_muestra.py` |
| **B. Búsqueda web** | `webfetch` (fetch URLs reales) | Información actualizada de fuentes públicas (foros, eventos, benchmarks, competidores) | **Real (fuente pública)** | `benchmark-mercado`, `expo-quest`, `discussion-forums` |
| **C. Síntesis LLM** | Modelo | Interpretación de datos reales (A+B), insights, decisiones estratégicas, redacción | **Basada en datos reales** | Todas las skills (capa final) |

**Principio rector:** El LLM **nunca inventa cifras** si un script o `webfetch` puede obtenerlas. El modelo redacta interpretaciones y recomendaciones, no datos crudos.

#### Ejemplo: `search-trend-analysis` instrumentada

```
sub-skills/search-trend-analysis/
├── SKILL.md                              # Instrucciones del agente
├── scripts/
│   ├── google_trends.py                  # pytrends → interés relativo, tendencia, queries relacionados, top regiones
│   └── generar_reporte.py                # Consolida datos reales + tabla markdown + testing card
└── references/
    └── benchmarks-industria.md           # Rangos de CTR/CPC/volumen por industria e idioma
```

**Flujo de ejecución:**
1. Usuario da hipótesis + parámetros (región, periodo, idioma)
2. Skill confirma keywords principales con el usuario
3. `bash python scripts/google_trends.py --keywords "..." --region MX` → datos reales de Google Trends
4. `webfetch` busca volúmenes de búsqueda públicos (blogs SEO, informes de industria) para cada keyword
5. LLM interpreta los datos reales: genera Testing Card, tabla de evidencia, análisis de tendencias, recomendación (perseverar/pivotear/descartar)
6. `generar_reporte.py` consolida en markdown estructurado

#### Ejemplo: `online-ads` (genera prompts de imagen, no imágenes)

La skill **no tiene acceso a modelos de generación de imágenes** (DALL·E, Midjourney, Stable Diffusion). En lugar de intentar generar imágenes, produce **prompts listos para que el usuario los pegue en su herramienta de imagen favorita**.

Cada variante de campaña incluye:
```
✍️ Copy principal: "¿Cansado de perder horas en...? Prueba X y recupera tu tiempo."
🎨 Prompt de imagen (Midjourney/DALL·E): "Flat vector illustration of a young professional
   working from a laptop on a sunny terrace, minimalist style, pastel colors, 16:9 aspect ratio,
   no text in image, modern Latin American aesthetic, warm lighting --ar 16:9 --style modern"
📱 Formato: Story (9:16)
🧩 Racional: Conecta con el JTBD "optimizar mi tiempo" validado en Persona Profile...
```

Esto aplica también a `explainer-video` (genera el prompt para Runway AI, no el video).

#### Skills que usan `webfetch` para datos reales

| Skill | Qué busca con `webfetch` |
|---|---|
| `benchmark-mercado` | Tamaños de mercado, ingresos de competidores, market share, tendencias de industria |
| `expo-quest` | Eventos reales con fechas, ubicaciones y costos verificados en sitios oficiales |
| `discussion-forums` | Hilos reales en Reddit/foros para fundamentar supuestos sobre el nicho |
| `search-trend-analysis` | Volúmenes de búsqueda públicos, benchmarks de industria, informes de mercado |
| `referral-builder` | Casos reales de modelos extend verificables (con etiqueta [VERIFICADO]) |
| `caressing-client` | Ejemplos reales de modelos de relación con métricas verificables |

---

## 4. Plan de Implementación por Fase

### Fase 1 — Investigación (3 skills)
**Prioridad:** ALTA (son el punto de entrada del flujo)

| Skill | Complejidad | Scripts | Estimación |
|---|---|---|---|
| `benchmark-mercado` | Media (parámetros extensos, `webfetch` para datos de mercado) | No | ~1.5h |
| `discussion-forums` | Baja (CRAFT estándar, diseño/planeación) | No | ~30min |
| `search-trend-analysis` | **Alta** (script pytrends + webfetch + análisis + reporte) | Sí (`google_trends.py`, `generar_reporte.py`) | ~2.5h |

### Fase 2 — Descubrimiento (8 skills)
**Prioridad:** ALTA (alimentan Persona y Problem-Solution Fit)

| Skill | Complejidad | Scripts | Estimación |
|---|---|---|---|
| `day-in-the-life` | Media (plantilla ADITL + esquema codificación) | No | ~45min |
| `discovery-survey` | Alta (fórmulas estadísticas, revisión Testing Cards) | Sí | ~2h |
| `encuesta-kano` | Media (taxonomía Kano, tabla clasificación) | Sí | ~1.5h |
| `entrevistas-empatia` | Media (guía + plantilla codificación) | No | ~45min |
| `expo-quest` | Media (búsqueda web, verificación eventos) | No | ~45min |
| `journey-builder` | Baja (estructura fija, 10 pasos) | No | ~30min |
| `persona-profile` | Media (JTBD + Momentos Vitales) | No | ~45min |
| `problem-solution-fit` | Media (análisis + CSV) | Sí | ~1.5h |

### Fase 3 — Ideación (6 skills)
**Prioridad:** MEDIA (dependen de outputs de Descubrimiento)

| Skill | Complejidad | Scripts | Estimación |
|---|---|---|---|
| `business-model-navigator` | Alta (catálogo 60 patrones en `references/`) | No | ~1.5h |
| `caressing-client` | Baja (dos tablas, formato fijo) | No | ~30min |
| `dimensionador-ideas` | **Muy Alta** (10 módulos, scoring, multi-buyer) | Sí | ~3h |
| `how-might-we` | Media (matriz ambición × palancas en `references/`) | No | ~1h |
| `ideacion` | Media (5 metodologías, rúbrica evaluación) | Sí | ~1.5h |
| `referral-builder` | Baja (dos tablas, reglas de verificabilidad) | No | ~30min |

### Fase 4 — Prototipado (2 skills)
**Prioridad:** MEDIA-BAJA

| Skill | Complejidad | Scripts | Estimación |
|---|---|---|---|
| `landing-ux-analyzer` | Media (checklist WCAG, requiere input visual) | No | ~45min |
| `landing-page` | Media (Testing Card + copy checklist + compliance) | No | ~1h |

### Fase 5 — Validación (5 skills)
**Prioridad:** MEDIA

| Skill | Complejidad | Scripts | Estimación |
|---|---|---|---|
| `email-campaign` | Media (significancia estadística, compliance email) | Sí | ~1.5h |
| `explainer-video` | Media (prompt Runway + Deep Agent) | No | ~45min |
| `feature-stub` | Media (fake-door ethics, tracking setup) | No | ~1h |
| `online-ads` | Media (3 campañas por modo, **prompts de imagen** para herramientas externas, compliance ads) | No | ~1h |
| `popup-store` | Alta (logística, compliance, protocolo captura) | No | ~1.5h |

---

## 5. Diseño de la Macro-Skill Orquestadora

### 5.1 Nombre
`macro_skill_flujo_de_innovacion_iris` (ya existe la carpeta, se crea `SKILL.md` en la raíz)

### 5.2 Propósito
Skill principal que orquesta el flujo completo de innovación IRIS. Recibe el contexto del usuario, determina en qué fase del proceso se encuentra y llama a las sub-skills correspondientes siguiendo el grafo de `flujo_mermaid.md`.

### 5.3 Flujo de decisión (extraído de `flujo_agentes.md` y `flujo_mermaid.md`)

```
INICIO → [¿Cómo quieres iniciar?]
  │
  ├─→ 1. INVESTIGACIÓN
  │     ├── benchmark-mercado
  │     ├── senales-debiles (ya existe)
  │     ├── discussion-forums
  │     ├── search-trend-analysis
  │     └── foresight (no tiene prompt aún — placeholder)
  │
  ├─→ [¿Ejecución de entrevistas?] → entrevistas-empatia
  │     └── [¿Simular o no?] ──→ Selección de agentes de Descubrimiento
  │
  ├─→ 2. DESCUBRIMIENTO
  │     ├── day-in-the-life
  │     ├── discovery-survey
  │     ├── encuesta-kano
  │     ├── expo-quest
  │     ├── journey-builder
  │     ├── persona-profile
  │     └── problem-solution-fit
  │
  ├─→ [¿Datos reales?] ──→ Persona & Problem-Solution Fit
  │     ├── persona-profile (con datos reales)
  │     ├── problem-solution-fit (con datos reales)
  │     ├── journey-builder
  │     └── how-might-we
  │           └── [Ambición estratégica] → [Apalancamiento]
  │
  ├─→ 3. IDEACIÓN
  │     ├── ideacion
  │     ├── caressing-client
  │     ├── referral-builder
  │     ├── dimensionador-ideas
  │     └── business-model-navigator
  │
  └─→ 4. PROTOTIPADO Y VALIDACIÓN
        ├── landing-page
        ├── landing-ux-analyzer
        ├── online-ads
        ├── email-campaign
        ├── explainer-video
        ├── popup-store
        └── feature-stub
```

### 5.4 Contrato de comunicación entre skills
Cada sub-skill recibe un JSON de entrada y produce un JSON de salida estandarizado:

```json
{
  "skill": "<nombre-skill>",
  "timestamp": "<ISO 8601>",
  "parametros": {
    "<var1>": "<valor1>"
  },
  "output": {
    "formato": "<markdown|csv|json|html>",
    "contenido": "<resultado estructurado>",
    "archivos_generados": ["<path1>", "<path2>"]
  },
  "decision": {
    "veredicto": "<perseverar|pivotear|descartar>",
    "siguiente_paso": "<nombre-skill-siguiente>",
    "razon": "<por qué>"
  },
  "advertencias": ["<lista de limitaciones>"]
}
```

### 5.5 `SKILL.md` de la macro-skill

```yaml
---
name: flujo-innovacion-iris
description: Orquestador del flujo completo de innovación IRIS. Guía al usuario por las fases de Investigación, Descubrimiento, Ideación, Prototipado y Validación, invocando sub-skills especializadas según el contexto y los puntos de decisión del proceso. Usar cuando el usuario quiera ejecutar el proceso de innovación completo o necesite orientación sobre qué herramienta/experimento aplicar.
---
```

La macro-skill:
1. **Evalúa el contexto inicial** del usuario (¿tiene una idea? ¿un problema? ¿datos de usuarios?).
2. **Determina la fase de entrada** en el flujo.
3. **Invoca la sub-skill correspondiente** mediante `skill()`.
4. **Interpreta el output** (especialmente el campo `decision.siguiente_paso`).
5. **Presenta opciones al usuario** en los nodos de decisión.
6. **Encadena skills** automáticamente cuando el flujo es lineal, y pregunta en bifurcaciones.

---

## 6. Orden de Ejecución para la Implementación

### Prioridad 1 — Template y herramientas base
1. Crear el script `_template_generador_skill.py` que tome un prompt .md y genere el esqueleto inicial de `SKILL.md`.
2. Estandarizar el contrato JSON input/output para todas las skills.

### Prioridad 2 — Fase 1: Investigación (3 skills)
3. `search-trend-analysis`
4. `discussion-forums`
5. `benchmark-mercado`

### Prioridad 3 — Fase 2: Descubrimiento (8 skills)
6. `persona-profile`
7. `entrevistas-empatia`
8. `problem-solution-fit` (+ `scripts/exportar_csv.py`)
9. `journey-builder`
10. `encuesta-kano` (+ `scripts/clasificar_kano.py`, `references/`)
11. `discovery-survey` (+ `scripts/calcular_muestra.py`, `references/`)
12. `day-in-the-life`
13. `expo-quest`

### Prioridad 4 — Fase 3: Ideación (6 skills)
14. `how-might-we` (+ `references/matriz-ambicion-palancas.md`)
15. `ideacion` (+ `scripts/evaluar_ideas.py`, `references/`)
16. `caressing-client`
17. `referral-builder`
18. `business-model-navigator` (+ `references/catalogo-patrones.md`)
19. `dimensionador-ideas` (+ `scripts/calcular_score.py`, `references/`)

### Prioridad 5 — Fase 4-5: Prototipado y Validación (7 skills)
20. `landing-page`
21. `landing-ux-analyzer`
22. `online-ads`
23. `email-campaign` (+ `scripts/calcular_significancia.py`)
24. `explainer-video`
25. `feature-stub`
26. `popup-store`

### Prioridad 6 — Macro-Skill orquestadora
27. `macro_skill_flujo_de_innovacion_iris/SKILL.md` — skill principal

---

## 7. Scripts a Desarrollar

| Script | Skill | Lenguaje | Input | Output | Dificultad |
|---|---|---|---|---|---|
| `google_trends.py` | `search-trend-analysis` | Python (pytrends) | keywords[], region, timeframe, idioma | JSON: interés histórico, promedio 12m, tendencia, queries relacionados, top regiones | Media |
| `generar_reporte.py` | `search-trend-analysis` | Python | JSON de google_trends + datos webfetch | Markdown estructurado con tabla de evidencia y testing card | Baja |
| `calcular_muestra.py` | `discovery-survey` | Python | N, confianza, margen_error, tasa_respuesta | n, n_aj, envíos, interpretación | Baja |
| `clasificar_kano.py` | `encuesta-kano` | Python | CSV de respuestas (funcional, disfuncional, importancia) | CSV clasificado (M/O/A/I/R/Q) + conteo por categoría | Media |
| `exportar_csv.py` | `problem-solution-fit` | Python | JSON de análisis (problemas, scores) | CSV estructurado para Problem-Solution Fit | Baja |
| `calcular_score.py` | `dimensionador-ideas` | Python | JSON de módulos 1-10 por idea × buyer persona | Score /25, ranking, tabla consolidación | Alta |
| `evaluar_ideas.py` | `ideacion` | Python | JSON de ideas con scores manuales | Tabla de evaluación, ranking, promedio ponderado | Media |
| `calcular_significancia.py` | `email-campaign` | Python | tamaño_lista, tasa_esperada, confianza, margen | Tamaño mínimo requerido, poder estadístico | Baja |

---

## 8. Consideraciones Adicionales

### 8.1 Agent `Foresight`
Aparece en `flujo_agentes.md` (nodo N13) pero NO tiene prompt en `Documentos_prompts_base_md/`. Se debe:
- Dejar como placeholder en la macro-skill con mensaje "en desarrollo"
- O crear un prompt base desde cero basado en foresight estratégico

### 8.2 Skills que ya existen
- `senales-debiles` (completa, en `sub-skills/senales-debiles/`) — no requiere conversión
- `skill-creador-de-skills` (global, en `~/.agents/skills/`) — puede usarse como guía para crear cada SKILL.md

### 8.3 Convención de nombres
- Nombres de skill: `kebab-case`, en español o inglés consistente
- Se recomienda español para alinearse con el lenguaje de los prompts originales
- Formato: `sub-skills/<nombre-skill>/`

### 8.4 YAML frontmatter obligatorio
Toda skill DEBE incluir en su `SKILL.md`:
```yaml
---
name: <nombre>
description: <descripción optimizada para triggering>
---
```

La `description` es crítica: determina cuándo el sistema activa la skill. Debe describir qué hace la skill y en qué contexto se usa (ver `skill-creador-de-skills` para mejores prácticas de triggering).

### 8.5 Dependencia de herramientas externas y limitaciones

**Herramientas con limitación parcial (se mitiga con scripts):**
- **Google Trends:** el script `google_trends.py` consulta datos reales vía `pytrends` (no requiere API key). El skill obtiene interés relativo 0-100, tendencia, queries relacionados y desglose regional. Limitación: `pytrends` no devuelve volúmenes absolutos (solo relativos). Para volumen absoluto se requiere Google Keyword Planner (cuenta de Google Ads), que queda fuera del alcance del script. La skill complementa con `webfetch` para buscar estimaciones públicas.
- **SEMrush / Ahrefs:** requieren API key de pago. La skill usa `webfetch` para buscar benchmarks públicos y los marca como `[REFERENCIA DE INDUSTRIA]`.

**Herramientas sin acceso (generación de contenido multimedia):**
- **Generación de imágenes:** el entorno **no tiene modelos de generación de imágenes** (DALL·E, Midjourney, Stable Diffusion). Las skills `online-ads` y `explainer-video` **no generan imágenes ni video**. En su lugar, producen **prompts detallados** listos para que el usuario los ingrese en su herramienta de generación favorita (Midjourney, DALL·E, Adobe Firefly, Runway AI, etc.). Cada prompt incluye: estilo visual, composición, paleta, aspect ratio, tono y parámetros específicos de la herramienta destino.
- **Runway AI / Deep Agent:** `explainer-video` diseña el guion, el prompt para Runway y la Testing Card. La generación real del video y el testing son ejecutados por el usuario en esas plataformas.

**Herramientas externas (ejecutadas por el humano):**
- **Envío de encuestas** (Typeform, Google Forms, SurveyMonkey): las skills de diseño (`discovery-survey`, `encuesta-kano`, `entrevistas-empatia`) preparan el cuestionario y el plan, no ejecutan el envío.
- **Envío de emails** (Mailchimp, Sendgrid, Customer.io): `email-campaign` diseña el experimento, la Testing Card y la estructura del correo; el envío real es externo.
- **Publicación de anuncios** (Meta Ads, TikTok Ads, Google Ads): `online-ads` genera copys, prompts de imagen y configuración de campaña; la publicación y el presupuesto los gestiona el usuario.

---

## 9. Resumen de Métricas

| Concepto | Cantidad |
|---|---|
| Total de prompts a convertir | 24 |
| Skills LLM-only (sin scripts) | 15 |
| Skills con scripts Python | 7 |
| Skills con `references/` | 8 |
| Scripts Python a desarrollar | 8 |
| Horas totales estimadas | ~40-45h |
| Skills en Fase 1 (Investigación) | 3 |
| Skills en Fase 2 (Descubrimiento) | 8 |
| Skills en Fase 3 (Ideación) | 6 |
| Skills en Fase 4 (Prototipado) | 2 |
| Skills en Fase 5 (Validación) | 5 |
| Macro-skill orquestadora | 1 |

---

## 10. Siguientes Pasos (Post-Plan)

1. **Validar el plan** con stakeholders.
2. **Crear el script `_template_generador_skill.py`** para automatizar la generación de esqueletos `SKILL.md`.
3. **Ejecutar en orden de prioridad** (Fase 1 → Fase 2 → Fase 3 → Fase 4-5 → Macro).
4. **Probar cada skill individualmente** antes de integrarla en la macro-skill.
5. **Integrar en la macro-skill orquestadora** una vez que todas las sub-skills estén listas.
6. **Documentar el sistema completo** en un README.md dentro de `sub-skills/`.
