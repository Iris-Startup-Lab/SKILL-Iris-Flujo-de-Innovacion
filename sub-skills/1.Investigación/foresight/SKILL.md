---
name: foresight
description: Prospectiva estratégica en 4 pasos (PESTEL → Rueda de Futuros → Cono de Futuros → Backcasting) para analizar escenarios futuros y megatendencias que impactarán un mercado o categoría en un horizonte de 3 a 10 años, a partir de un catálogo de tendencias tecnológicas seleccionadas por el usuario. Usar cuando el usuario pida foresight, prospectiva, análisis PESTEL, backcasting, rueda o cono de futuros, escenarios futuros o megatendencias.
category: Investigación
---

# Foresight Estratégico — Análisis en 4 pasos

Guía al usuario a través de una metodología completa de **prospectiva estratégica** usando las capacidades de análisis de Claude: PESTEL → Rueda de Futuros → Cono de Futuros → Backcasting.

## Triggers / Cuándo activar

- "Quiero hacer un análisis estratégico de mi proyecto/idea/negocio"
- "Necesito un análisis PESTEL"
- "Ayúdame con prospectiva o foresight"
- "Quiero explorar escenarios futuros para [X]"
- "Hazme un backcasting / rueda de futuros / cono de futuros"
- El usuario menciona: **foresight, prospectiva, análisis estratégico, PESTEL, backcasting, cono de futuros, rueda de futuros, escenarios futuros**

## Workflow

Sigue **exactamente** este orden. Cada paso depende del anterior. No brinques pasos.

---

### Paso 1: Recopilar información del proyecto

Pídele al usuario que describa su proyecto. Si ya lo describió en el mensaje inicial, usa esa información directamente. Necesitas capturar:

| Dato | Pregunta |
|---|---|
| **Nombre del proyecto** | ¿Cómo se llama tu proyecto? |
| **Descripción** | ¿Qué problema resuelve y cuál es su propuesta de valor? |
| **Ubicación** | ¿Dónde se implementará? (país, ciudad, región) |
| **Modelo de venta** | ¿Cómo llegas al cliente? (directo, digital, intermediarios, etc.) |
| **Tipo de producto** | ¿Es físico, digital, servicio, plataforma? |
| **Alcance** | ¿Está en fase idea, piloto, crecimiento? |
| **Alianzas clave** | ¿Dependes de socios o proveedores estratégicos? |
| **Sector/industria** | ¿En qué sector opera? |

Si el usuario no da todos los detalles, haz preguntas específicas una por una. No te saltes esta recolección.

---

### Paso 2: Selección de tendencias tecnológicas

Presenta al usuario las siguientes **categorías de tendencias** y pídele que seleccione **hasta 5 tecnologías** que considere relevantes para su proyecto:

**Artificial Intelligence**
- Machine Vision — Visión por computadora para automatización
- Deep Fakes — Contenido sintético hiperrealista
- Super AI — IA con capacidades superiores a las humanas
- Computational Creativity — Creatividad generativa autónoma
- Quantum Computing — Computación cuántica
- Mood Responsive System — Sistemas que detectan emociones
- Digital Humans — Avatares virtuales realistas
- AI Multi-Agents — Múltiples agentes de IA colaborando
- Conversational Interfaces — Interfaces de lenguaje natural

**Extended Reality**
- Virtual Reality — Entornos 3D inmersivos
- Metaverse — Mundos digitales persistentes
- Tactile Holograms — Hologramas táctiles
- XR Glasses — Gafas de realidad mixta
- Augmented Reality — Superposición digital en el mundo físico

**Biotechnology**
- Neurochips — Interfaces cerebro-computadora
- DNA Data Storage — Almacenamiento en ADN
- Gene Editing (CRISPR) — Edición genética
- 3D Bioprinting — Impresión de tejidos biológicos
- Personalized Biomedicine — Medicina personalizada
- Synthetic Biology — Diseño de sistemas biológicos

**Distributed Ledger Technology**
- Smart Contract — Contratos autoejecutables en blockchain
- DAOs — Organizaciones autónomas descentralizadas
- Tokenization — Tokenización de activos
- Private Blockchain — Blockchain privadas empresariales
- Smart Coins — Monedas digitales programables

**Data & Cybersecurity**
- Brainwave-based Authentication — Autenticación por ondas cerebrales
- Data Marketplace — Mercados de datos
- Cyber Insurance — Seguros cibernéticos
- Adversarial ML — Machine learning adversarial

**Internet of Things**
- Mobility as a Service — Movilidad integrada bajo demanda
- Smart Homes — Hogares inteligentes IoT
- Smart Wearables — Dispositivos portátiles inteligentes
- Active Packaging — Empaques inteligentes con sensores

**Manufacturing & Robotics**
- 4D Printing — Materiales que cambian de forma
- Robotic Swarm — Enjambres de robots colaborativos
- Exoskeleton — Exoesqueletos para aumento humano
- General Purpose Robot — Robots multiusos programables

Una vez seleccionadas, genera un breve análisis de cómo estas tendencias se relacionan con su proyecto.

---

### Paso 3: Análisis PESTEL

Genera un análisis PESTEL **profundo y detallado** usando los datos del proyecto y las tendencias seleccionadas. Debe incluir **oportunidades y amenazas** en cada categoría, y **recomendaciones estratégicas** al final.

Estructura obligatoria de la respuesta:

```markdown
### ANÁLISIS PESTEL

#### POLÍTICO
[Estabilidad gubernamental, políticas fiscales, comerciales, regulaciones,
relaciones internacionales. Menciona cómo las tendencias seleccionadas
impactan este factor. Oportunidades y amenazas.]

#### ECONÓMICO
[Crecimiento económico, inflación, tipos de cambio, desempleo, poder
adquisitivo, tendencias del mercado. Menciona tendencias seleccionadas.]

#### SOCIAL
[Demografía, cambios culturales, educación, conciencia social, patrones
de consumo. Menciona tendencias seleccionadas.]

#### TECNOLÓGICO
[Innovaciones disruptivas, automatización, I+D, obsolescencia tecnológica.
Menciona tendencias seleccionadas.]

#### ECOLÓGICO
[Regulaciones ambientales, cambio climático, recursos naturales,
sostenibilidad. Menciona tendencias seleccionadas.]

#### LEGAL
[Leyes y normativas: protección de datos, propiedad intelectual, salud,
competencia. Menciona tendencias seleccionadas.]

#### OPORTUNIDADES Y AMENAZAS
[Síntesis de oportunidades y amenazas principales detectadas.]

#### RECOMENDACIONES ESTRATÉGICAS
[Acciones concretas basadas en el análisis.]
```

---

### Paso 4: Rueda de Futuros

Basado en el análisis PESTEL anterior, explora las **consecuencias en cadena** en 6 dimensiones. Identifica para cada una:

- **Contexto** de la dimensión frente al proyecto
- **Consecuencia directa** (1er orden)
- **Consecuencia indirecta** (2do/3er orden)

Estructura obligatoria:

```markdown
### RUEDA DE FUTUROS

#### POLÍTICO
Contexto: [descripción del contexto político]
- Consecuencia directa: [efecto inmediato]
- Consecuencia indirecta: [efecto en cadena]

#### ECONÓMICO
Contexto: [descripción]
- Consecuencia directa:
- Consecuencia indirecta:

#### SOCIAL
Contexto:
- Consecuencia directa:
- Consecuencia indirecta:

#### TECNOLÓGICO
Contexto:
- Consecuencia directa:
- Consecuencia indirecta:

#### ECOLÓGICO
Contexto:
- Consecuencia directa:
- Consecuencia indirecta:

#### LEGAL
Contexto:
- Consecuencia directa:
- Consecuencia indirecta:
```

---

### Paso 5: Cono de Futuros

Construye **6 escenarios futuros** basados en los análisis anteriores (PESTEL + Rueda). Sé creativo pero anclado en los datos.

Estructura obligatoria:

```markdown
### CONO DE FUTUROS

## 1. FUTURO PROYECTADO
[Extrapolación del presente: tendencias actuales continúan su curso.]

## 2. FUTURO PLAUSIBLE
[Lo que puede ocurrir según el conocimiento actual y las tendencias identificadas.]

## 3. FUTURO POSIBLE
[Escenarios más disruptivos que podrían surgir de innovaciones radicales.]

## 4. FUTURO POTENCIAL
[Más allá de suposiciones actuales. Pensamiento expansivo.]

## 5. FUTURO ABSURDO
[Escenarios que parecen imposibles hoy pero desafían paradigmas. Útil para romper sesgos.]

## 6. FUTURO PREFERIBLE
[Visión aspiracional: lo que queremos que suceda. El destino deseado.]
```

---

### Paso 6: Backcasting

Parte del **Futuro Preferible** (o del que el usuario elija) y construye un plan inverso desde la visión futura hasta el presente. Define acciones concretas para cada año.

Pídele al usuario que confirme qué tipo de futuro usar como visión deseada (por defecto usa el Futuro Preferible).

Estructura obligatoria:

```markdown
### PLAN DE BACKCASTING

### VISIÓN FUTURA DESEADA (5 AÑOS)
[Estado ideal del proyecto/industria en 5 años.]

### Plan de Acción a 5 Años: Consolidación y Liderazgo
[Hitos críticos y recursos necesarios. ¿Qué debe ser realidad en 5 años?]

### Plan de Acción a 4 Años: Escalada y Optimización
[¿Qué debe estar funcionando a gran escala en 4 años?]

### Plan de Acción a 3 Años: Desarrollo y Prueba
[¿Qué soluciones deben estar validadas en 3 años?]

### Plan de Acción a 2 Años: Experimentación y Diseño
[¿Qué experimentos y prototipos deben estar en marcha?]

### Plan de Acción a 1 Año: Fundación y Exploración Inicial
[¿Qué acciones tomar HOY para comenzar el camino?]

### INDICADORES DE ÉXITO
[Métricas para monitorear el progreso en cada etapa.]
```

Al finalizar, entrega un resumen ejecutivo con los hallazgos más importantes de todo el análisis y ofrece sugerencias de siguientes pasos.

---

## Notas importantes

- **Siempre responde en español**
- Usa **Markdown** bien estructurado
- Sé específico y contextual: aplica cada análisis al proyecto concreto del usuario
- No inventes datos macroeconómicos específicos (tasas, inflación) si no los conoces; usa rangos o lenguaje cualitativo
- Si el usuario no tiene claro qué tendencias seleccionar, ofrécele recomendaciones basadas en su sector
- Al final del Paso 6, ofrece generar un resumen ejecutivo descargable o formateado para copiar

---

## Contexto del flujo (entrada)

Esta skill puede ejecutarse suelta o como paso del **flujo de innovación IRIS**. Si la
invoca la macro-skill, recibes un bloque `flujo` con el histórico del proyecto (también
disponible en `flujo_estado.json`, o con
`python scripts/estado_flujo.py mostrar --paso <html_N>` desde la raíz del repositorio).

Cuando ese contexto existe:

1. **No vuelvas a preguntar lo ya decidido.** Las decisiones registradas y los datos del
   proyecto (objetivo, audiencia) ya están ahí.
2. **Parte de los resúmenes previos** en lugar de reconstruir el contexto desde cero.
3. **Lee los datos del predecesor, no solo su resumen.** Cada paso cerrado deja en
   `flujo.ruta[]` un campo `datos` (la ruta de su `reporte.json`) y la lista `archivos`.
   Abre ese `reporte.json` y toma de ahí los bloques que necesites —`secciones[].items[]`
   y los especializados como `persona` o `psf`— en vez de reescribirlos a partir del
   resumen: **el resumen es el índice, los datos están en el archivo.** Si un paso no
   registró `datos`, su HTML (`archivo`) lleva lo mismo embebido en `window.REPORT_DATA`.
4. **Los pasos con estado `omitido` no aportan datos.** Su campo `impacto` dice qué falta:
   sustitúyelo por un supuesto marcado `*` y decláralo en `advertencias`.
5. **Declara qué usaste** en `decision.contexto_usado` del contrato JSON.

## Como paso del flujo IRIS

Esta skill tiene su **propia salida HTML**, que se conserva tal cual: es el entregable
detallado y no lo sustituye nada.

Cuando corre dentro del flujo, además de ese HTML propio:

1. Resume tus resultados en un `reporte.json` con el esquema `REPORT_DATA`
   (ver `_plantilla_html/README.md`).
2. Genera el HTML del paso **desde la raíz del repositorio**, para que lleve el contexto
   completo del flujo (avance, decisiones previas, pasos omitidos):

   ```bash
   python _plantilla_html/scripts/generar_html.py --data reporte.json \
       --estado flujo_estado.json --paso html_1 -o html_1.html
   ```

3. Declara **ambos** archivos en `output.archivos_generados`: `html_1.html` (el paso del
   flujo, con contexto) y `el resumen ejecutivo del análisis en 4 pasos` (tu entregable detallado, como anexo).

Fuera del flujo, entrega solo tu HTML propio y omite el paso 2.

## Contrato JSON (salida)

Cierra con el contrato estándar de `sub-skills/CONTRATO_JSON.md`: `skill`, `timestamp`,
`parametros`, `output` (con los dos archivos en `archivos_generados`), `decision`
(`veredicto`, `siguiente_paso`, `razon`, `contexto_usado`) y `advertencias`.
