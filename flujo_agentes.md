# Flujo de Agentes de Innovación IRIS

> **Vista descriptiva del flujo.** Sirve para entender qué hace cada agente y qué define.
>
> La **fuente de verdad ejecutable es [`pasos.json`](pasos.json)**: ahí están las rutas
> exactas de las sub-skills, los nodos `N*` del Mermaid, los predecesores de cada paso y
> qué se puede omitir. Si un dato de este documento contradice a `pasos.json`, gana
> `pasos.json`.

## Nombre del agente → carpeta de la sub-skill

Los agentes de este documento no siempre se llaman igual que su carpeta. El mapeo
autoritativo está en `pasos.json`; estos son los casos que más confunden:

| Agente en este documento | Carpeta real |
| --- | --- |
| Agente Simple Landing Page | `4.Prototipado/landing-page` |
| Agente Señales débiles | `1.Investigacion/senales-debiles` |
| Agente Dimensionador Estratégico de Ideas de Negocio | `3.Ideacion/dimensionador-estrategico` |
| Agente Entrevista de empatía | `2.Descubrimiento/entrevistas-empatia` |
| Agente How Might We | `3.Ideacion/how-might-we` |
| Agente Caressing the client | `3.Ideacion/caressing-client` |
| Agente A Day In The Life | `2.Descubrimiento/day-in-the-life` |
| Agente Encuesta Kano | `2.Descubrimiento/encuesta-kano` |
| Agente Pop-Up Store | `5.Validacion/popup-store` |

Para ver el paso actual con sus rutas ya resueltas:

```bash
python scripts/estado_flujo.py mostrar --paso html_N
```

---

## Inicio — HTML_OUTPUT: html_1

### Puntos de decisión

- **Cómo quieres iniciar?**
  - Estado actual → Agente Benchmark
  - Futuros → Agente Foresight
  - Señales débiles de usuarios actuales → Agente Señales débiles
  - Opiniones y comentarios → Agente Discussion Forums

---

## 1. Investigacion — HTML_OUTPUT: html_1

> Esta sección y la de Inicio se consolidan en un único HTML (html_1).
> El diagrama muestra las 4 rutas de entrada desde "Cómo quieres iniciar?" hacia los agentes de investigación.
> Agente Discussion Forums conecta en cadena con Agente Search Trend Analysis antes de converger al bloque de Entrevistas.

### Agentes

#### Agente Benchmark

> Genera benchmarks detallados de industrias y mercados en México (o la región indicada) para desarrollar productos y estrategias de innovación, con datos trazables y supuestos explícitos.

Definir:

- Nicho / mercado
- Moneda y tipo de cambio
- Competidores objetivo
- Acceso a fuentes premium

#### Agente Señales débiles

> Identifica señales emergentes del mercado antes de que se conviertan en tendencias dominantes, a partir de fuentes no estructuradas y conversaciones de usuarios actuales.

#### Agente Foresight

> Analiza escenarios futuros y megatendencias que podrían impactar el mercado o categoría del producto/servicio en el horizonte de 3–10 años.

#### Agente Discussion Forums

> Agente que diseña y planea el experimento de Discussion Forum (no lo ejecuta ni rastrea foros directamente).

Definir:

- Hipótesis a validar
- Producto o servicio a analizar
- Objetivo estratégico
- Foros Objetivo
- Muestra y ventana temporal
- Punto de saturación

#### Agente Search Trend Analysis

> Agente ultraestructurado para el experimento Search Trend Analysis con enfoque C.R.A.F.T., incluyendo Testing Card, planeación y estructura para tus equipos de innovación, discovery y research estratégico.

Definir:

- Región / mercado
- Periodo
- Idioma
- Umbral de éxito
- ...

---

## Decision - Entrevistas — HTML_OUTPUT: html_2

> HTML 2 muestra el Agente Entrevista de empatía conectado a la decisión "¿Ejecución de entrevistas?".
> Rama **Sí** (respuestas e insights reales) y rama **No** (simulación de respuestas e insights → Simular o no).
> Ambas ramas convergen en "Selección de agentes" que dispara el bloque de Descubrimiento.

### Puntos de decisión

- **¿Ejecución de entrevistas?**
  - Sí → Respuestas e insights reales → Selección de agentes
  - No → Simulación de respuestas e insights → Simular o no → Selección de agentes
- **Simular o no**
- **Selección de agentes**

> La rama de simulación tiene skills propias: cada agente de Descubrimiento lleva dentro un
> **simulador** (`sub-skills/<fase>/<skill>/simulador/SIMULADOR.md`) que fabrica el CSV de
> datos sintéticos que después analiza el agente normal. Las rutas están en el campo
> `simuladores` de cada paso en `pasos.json`. Elegir «No — simulación…» marca todos los
> reportes posteriores como **DATOS SIMULADOS**, automáticamente. Ver
> `sub-skills/SIMULACION.md`.

### Agentes

#### Agente Entrevista de empatía

> Diseña entrevistas de empatía estratégicas usando The Mom Test, Design Thinking y más.

Definir:

- Objetivo
- Hipótesis
- Perfil del usuario
- Número de entrevistas

---

## 2. Descubrimiento — HTML_OUTPUT: html_3

> HTML 3 muestra la decisión "Selección de agentes" desplegando en paralelo los 4 agentes de descubrimiento.
> Todos convergen hacia abajo para alimentar la siguiente etapa de Persona Profile.

### Agentes

#### Agente A Day In The Life

> Agente ultraestructurado para el experimento A Day In The Life con enfoque C.R.A.F.T., incluyendo Testing Card, planeación y estructura para tus equipos de innovación, discovery y research estratégico.

Definir:

- Hipótesis
- Perfil
- Objetivo
- Número de sesiones

#### Agente Encuesta Kano

> Genera la encuesta Kano para evaluar el beneficio potencial y deseabilidad que el cliente tiene sobre cada feature o característica de producto de tu propuesta de valor.

Definir:

- Producto / servicio
- Segmento
- Origen de features

#### Agente Discovery Survey

> Agente encargado de diseñar y revisar encuestas de descubrimiento, incluyendo el apoyo para determinar tamaño de muestra estadísticamente significativa y el revisar, estructurar y corregir Testing Cards, asegurando consistencia y excelencia metodológica en tus equipos.

Definir:

- Hipótesis
- Perfil
- Objetivo
- Nivel de confianza
- Tamaño de la población...

#### Agente Expo Quest

> Encuentra una lista de eventos presenciales (expos, ferias, conferencias, etc.) donde podrías interactuar directamente con un perfil objetivo y/o estudiar a la competencia.

Definir:

- Perfil objetivo
- Dimensión

---

## Persona y Problem-Solution Fit — HTML_OUTPUT: html_4 + html_5 + html_6

> Esta sección se divide en 3 HTMLs consecutivos:
>
> - **html_4** → Agente Persona Profile + decisión "¿Hay datos reales de entrevistas / encuestas?"
>   - Sí: Generación de profiles con data real
>   - No: Generación de profiles a base de supuestos
> - **html_5** → Agente Problem Solution Fit + decisión "Elección de la ficha de persona"
>   - Por problema más grande
>   - Por mayor tamaño en mercado
> - **html_6** → Agente Journey Builder (nodo de paso hacia Agente How Might We)

### Puntos de decisión

- **¿Hay datos reales de entrevistas / encuestas?**
  - Sí → Generación de profiles con data real
  - No → Generación de profiles a base de supuestos
- **Elección de la ficha de persona**
  - Por problema más grande
  - Por mayor tamaño en mercado
- **Ambición estratégica** *(se despliega desde Agente How Might We, ver HTML 7)*
- **Apalancamiento** *(se despliega desde Ambición estratégica, ver HTML 7)*

### Agentes

#### Agente Persona Profile — html_4

> Desarrolla fichas de persona con atributos detallados, integrando el trabajo que quiere hacer (Job To Be Done) con Momentos Vitales para estrategias y nuevos productos.

Definir:

- Industria / mercado
- Objetivo
- Geografía / cultura
- Nivel de detalle
- Número de personas profile a generar
- Tono...

#### Agente Problem Solution Fit — html_5

> Genera un análisis estructurado de Problem-Solution Fit a partir de entrevistas o encuestas, identificando problemas clave, evaluando la solución y extrayendo insights accionables.

Agregar preguntas de identificación para saber a qué persona profile se está aplicando.

#### Agente Journey Builder — html_6

> Genera Journeys de Usuarios y Clientes (por defecto en 10 pasos, flexible) con costos y obstáculos obteniendo información de entrevistas o encuestas.

Definir:

- Industria / contexto
- Moneda y tipo de cambio
- Número de pasos
- Nivel de detalle
- Enfoque
- Formato o terminología

#### Agente How Might We — html_7 (inicio)

> Agente especializado en guiar a equipos en la generación de preguntas "How Might We" que desbloqueen soluciones innovadoras.

Definir:

- Usuario objetivo
- Problema
- Objetivo del reto

---

## 3. Ideacion — HTML_OUTPUT: html_7 + html_8 + html_9 + html_10

> Esta sección se divide en 4 HTMLs:
>
> - **html_7** → Agente How Might We + árbol de "Ambición estratégica" → "Apalancamiento" → "Selección de agentes de ideación"
>   - Ambición estratégica: Optimizar Negocio Actual | Crecer Negocio Actual | Expandir Negocio | Crear Nuevos Negocios | Reinventar el Futuro
>   - Apalancamiento (según ambición): Reducir Costos, Productividad, Nuevos clientes, Mayor frecuencia, Mayor ticket, Recuperación, Participación de mercado, Ampliar mercado, Nuevos casos de uso, Ecosistema, Nuevo producto, Nuevo modelo de negocio, Disrupción, Nuevas categorías, IA
> - **html_8** → Agentes de ideación en paralelo (Ideación, Caressing the client, Referral Builder) + decisión "Selección de ideas"
> - **html_9** → Agente Dimensionador Estratégico de Ideas de Negocio
> - **html_10** → Agente Business Model Navigator

### Puntos de decisión

- **Selección de agentes de ideación**
- **Selección de ideas**

### Árbol de Ambición estratégica y Apalancamiento — html_7

| Ambición estratégica     | Opciones de Apalancamiento                                           |
|--------------------------|----------------------------------------------------------------------|
| Optimizar Negocio Actual | Reducir Costos, Productividad                                        |
| Crecer Negocio Actual    | Nuevos clientes, Mayor frecuencia, Mayor ticket, Recuperación, Participación de mercado |
| Expandir Negocio         | Ampliar mercado, Nuevos casos de uso, Ecosistema                     |
| Crear Nuevos Negocios    | Nuevo producto, Nuevo modelo de negocio                              |
| Reinventar el Futuro     | Disrupción, Nuevas categorías, IA                                    |

### Agentes

#### Agente Caressing the client — html_8

> Encuentra modelos de relación con el cliente potenciales para tu producto/servicio. Ponlos a prueba y descubre cómo es que tu cliente quiere ser tratado.

Definir:

- Producto / servicio
- El trabajo que quiere hacer (Job To Be Done) principal
- Mercado/categoría y geografía
- N° de modelos por tabla

#### Agente Ideación — html_8

> Tu rol no es solo generar ideas, sino guiar un proceso de pensamiento innovador y colaborativo. Tu objetivo principal es ayudar a desbloquear el potencial creativo para generar soluciones radicalmente innovadoras y factibles.

Definir:

- El reto creativo (How Might We) a resolver
- Contexto y restricciones
- Número de ideas

#### Agente Referral Builder — html_8

> Genera 10 propuestas de modelo extend (5 con inspiración y 5 disruptivas) para poner a prueba la deseabilidad de incentivos sobre la propuesta de valor, su capacidad de generación de referidos y de lograr que un cliente vuelva a tu producto.

Definir:

- Descripción de producto
- Objetivo
- Mercado / segmento

#### Agente Dimensionador Estratégico de Ideas de Negocio — html_9

> Agente con capacidad de dimensionar el potencial de negocio de cada idea para decidir cuáles pasan a prototipado y validación.

Definir:

- Contexto del portafolio (sector / vertical, geografía objetivo, Etapa del negocio, recursos para prototipado ($), criterio de fit estratégico)
- Buyer personas (1 a 5)
- Ideas a dimensionar

#### Agente Business Model Navigator — html_10

> Tu rol es el de un Consultor Experto en Modelos de Negocio, Investigación e Inteligencia Comercial, especializado en diseño de negocios y validación ágil. Tu objetivo principal es recomendar los mejores "patterns" (patrones de modelos de negocio) y "experimentos".

Definir:

- Hipótesis a validar
- Experimentos a evitar

---

## 4. Prototipado y Validacion — HTML_OUTPUT: html_11

> HTML 11 muestra la decisión "Selección de agente para validar" desplegando en paralelo los 7 agentes de prototipado y validación.
> Todos los agentes reciben entrada desde Agente Business Model Navigator.

### Puntos de decisión

- **Selección de agente para validar**

### Agentes

#### Agente Explainer Video

> Diseña un experimento de Explainer Video, compatible tanto con Runway AI (generación de video) como con Deep Agent de Abacus AI (para testing, análisis y automatización). Está pensado para validar la claridad, interés o comprensión de una propuesta de valor a través de un video explicativo corto.

Definir:

- Hipótesis
- Propuesta de valor a comunicar
- Público objetivo
- Canal de difusión...

#### Agente Pop-Up Store

> Diseña el experimento Pop-Up Store, basado en Testing Business Ideas. Enfocado en probar hipótesis de mercado, comportamiento de compra, experiencia física y validación de modelo de negocio en un entorno presencial, temporal y controlado.

Definir:

- Hipótesis
- Ubicación, duración y formato del espacio
- Perfil del usuario
- Interacción deseada...

#### Agente Feature Stub

> Este experimento es clave para validar el interés y la demanda de una funcionalidad específica antes de construirla.

Definir:

- Funcionalidad específica
- Hipótesis detrás de la feature
- Producto o plataforma donde se simulará
- Público objetivo y tráfico estimado
- Benchmark propio de CTR / tasa de captura

#### Agente Online Ads

> Este GPT genera copys, imágenes y artes promocionales para cualquier tipo de canal.

Definir:

- Producto
- Audiencia
- El trabajo que quiere hacer (Job To Be Done)
- Tono
- Plataformas
- Modo...

#### Agente Landing Page UX Analyzer

> Identifica áreas de mejora de UX/UI en la landing page de un negocio operativo o en una propuesta de landing para experimentos de validación.

Definir:

- Objetivo
- Insumos (URL renderizable, renders visuales, CSS computado, vistas desktop /móvil)

#### Agente Simple Landing Page

> Diseña el experimento "Simple Landing Page", adaptado para un responsable con experiencia construyendo landing pages para validación de productos. Va directo al grano, pero conserva la rigurosidad estratégica de Testing Business Ideas.

Definir:

- Hipótesis
- Segmento Objetivo
- CTA esperada
- Herramienta para construir
- Volumen de tráfico esperado...

#### Agente Email Campaign

> Genera el experimento Email Campaign, incluyendo diseño de la Testing Card, estructura del experimento y modelo de email enfocado en la validación temprana de hipótesis, basado en Testing Business Ideas.

Definir:

- Hipótesis
- Segmento
- Oferta
- Herramienta de envío
- Benchmark...

---

## Mapa de HTMLs de salida

| HTML | Sección del flujo                        | Contenido principal                                                                 |
|------|------------------------------------------|-------------------------------------------------------------------------------------|
| html_1  | Inicio + 1. Investigación             | Decisión inicio → 4 agentes investigación (Benchmark, Foresight, Señales débiles, Discussion Forums → Search Trend Analysis) |
| html_2  | Decision - Entrevistas                | Agente Entrevista de empatía → ¿Ejecución? → Simular o no → Selección de agentes   |
| html_3  | 2. Descubrimiento                     | Selección de agentes → 4 agentes descubrimiento en paralelo                         |
| html_4  | Persona Profile                       | Agente Persona Profile → ¿Hay datos reales?                                         |
| html_5  | Problem-Solution Fit                  | Agente Problem Solution Fit → Elección de la ficha de persona                              |
| html_6  | Journey Builder                       | Agente Journey Builder (nodo de paso)                                               |
| html_7  | El reto creativo (How Might We) + Ambición estratégica | Agente How Might We → Árbol Ambición estratégica → Apalancamiento → Selección de ideación |
| html_8  | Agentes de ideación                   | Ideación, Caressing the client, Referral Builder → Selección de ideas               |
| html_9  | Dimensionador                         | Agente Dimensionador Estratégico de Ideas de Negocio                                |
| html_10 | Business Model Navigator              | Agente Business Model Navigator                                                     |
| html_11 | 4. Prototipado y Validación           | Selección de agente para validar → 7 agentes en paralelo                            |

---

## Nodos de referencia (contexto de decisiones del flujo)

- **¿Ejecución de entrevistas?** → Sí: Respuestas e insights reales / No: Simulación de respuestas e insights
- **Simular o no** → Sub-decisión cuando no se ejecutan entrevistas reales
- **¿Hay datos reales de entrevistas / encuestas?** → Sí: Generación de profiles con data real / No: Generación de profiles a base de supuestos
- **Elección de la ficha de persona** → Por problema más grande / Por mayor tamaño en mercado
- **Ambición estratégica** → Optimizar / Crecer / Expandir / Crear Nuevos Negocios / Reinventar el Futuro
- **Apalancamiento** → Reducir Costos, Productividad, Nuevos clientes, Mayor frecuencia, Mayor ticket, Recuperación, Participación de mercado, Ampliar mercado, Nuevos casos de uso, Ecosistema, Nuevo producto, Nuevo modelo de negocio, Disrupción, Nuevas categorías, IA
