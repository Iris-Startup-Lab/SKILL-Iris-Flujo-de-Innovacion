**Nombre:** Caressing the client

**Descripción:** Encuentra modelos de relación con el cliente potenciales para tu producto/servicio. Ponlos a prueba y descubre cómo es que tu cliente quiere ser tratado.

**Área:** Ideación

**Prompt:**

Quiero que actúes como un experto en diseño de experiencias de relación con el cliente y validación estratégica. Antes de mostrar resultados, hazme las siguientes preguntas clave:

- ¿Cuál es el producto o servicio para el que quieres diseñar o validar la relación con el cliente?
- ¿Cuál es el Job To Be Done (JTBD) principal de tu cliente al usar ese producto o servicio?
- ¿Cuál es el **mercado/categoría y geografía** del producto? {{mercado\_categoria}} (para anclar ejemplos y benchmarks relevantes).
- ¿Cuántos **modelos por tabla** deseas? {{n\_filas}} (por defecto 10).

Con base en mis respuestas, genera DOS tablas en formato markdown con exactamente el siguiente formato (usa texto compacto y visual):

| Nº | Nombre del Modelo | Tipo de Relación con el Cliente (Transaccional, Proactiva, Consultiva, Colaborativa, Comunidades, Asistencia personal, Asistencia personal exclusiva, Autoservicio o Servicios automatizados) | Propuesta Extendida de Aplicación | Aplicabilidad (casos de uso por necesidad del usuario) | Evidencia/Data | Factibilidad (Alta/Media/Baja) | Hipótesis de Validación |

🔹 La **primera tabla** debe contener {{n\_filas}} (por defecto 10) modelos de relación con el cliente que ya han demostrado funcionar, tomando inspiración de marcas reales, con la métrica específica de éxito (ej. aumento de retención, NPS, ventas) y su fuente.

🔹 La **segunda tabla** debe contener {{n\_filas}} (por defecto 10) modelos extend o muy innovadores/disruptivos, que valga la pena experimentar, con justificación clara, aplicabilidad detallada y fuente o razonamiento de por qué vale probarlos.

⚠️ **Regla de integridad de la evidencia (obligatoria):** En la columna **Evidencia/Data** , distingue siempre de forma explícita:

- **[VERIFICADO]** — cuando la métrica tiene una cifra real respaldada por una fuente identificable (incluye la fuente).
- **[ESTIMACIÓN/BENCHMARK]** — cuando es una aproximación, rango de industria o razonamiento, no un dato confirmado.

**Está prohibido presentar cifras inventadas como verificadas.** Si no hay dato confiable, indícalo claramente.

**Priorización:** Dentro de cada tabla, **ordena los modelos por Factibilidad** (de mayor a menor) para facilitar la selección de qué experimentar primero.

**Hipótesis de validación:** Para cada modelo, formula en la última columna una hipótesis testable en formato *"Creemos que [modelo] aumentará [métrica] en [segmento] porque [razón]"*, de modo que cada fila quede lista para diseñar un experimento.

Considera tanto productos físicos como digitales o híbridos. Usa un lenguaje claro, profesional y orientado a ejecución.

Tu salida debe estar completamente estructurada como una tabla por cada grupo de modelos, sin explicaciones externas. Sé concreto, visual y accionable.

**Nota de cambios e impacto**

- **Regla de integridad de evidencia ([VERIFICADO] vs. [ESTIMACIÓN/BENCHMARK]):** añadida para la columna Evidencia/Data. **Impacto:** evita inventar métricas y distingue datos reales de aproximaciones.
- **Mercado/categoría ({{mercado\_categoria}}):** añadido como pregunta previa. **Impacto:** ancla ejemplos y benchmarks al contexto real del producto.
- **N variable de filas ({{n\_filas}}):** permite ajustar el número de modelos por tabla. **Impacto:** controla longitud y adapta el entregable.
- **Priorización por factibilidad + columna Factibilidad:** añadidas al formato. **Impacto:** facilita decidir qué modelos experimentar primero.
- **Hipótesis de validación por modelo:** nueva columna en formato testable. **Impacto:** conecta directamente la ideación con el diseño de experimentos.
- **Estructura de dos tablas, tipos de relación y estilo original:** intactos; solo se enriquecieron con los puntos anteriores.