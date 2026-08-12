**Nombre:** Feature Stub  
**Descripción:** Este experimento es clave para validar el interés y la demanda de una funcionalidad específica antes de construirla.  
**Área:** Validación

**Prompt**

**C – Contexto**

Necesitas validar si una nueva funcionalidad (feature) es relevante y deseada por los usuarios, sin desarrollarla completamente. El experimento Feature Stub consiste en mostrar la funcionalidad como si existiera (a través de UI, botones o enlaces), pero sin estar implementada aún. Se rastrean clics, interacciones o formularios para medir el interés real del usuario. Se utiliza en fases tempranas de desarrollo, prototipado o testing para evitar esfuerzos de programación innecesarios y validar valor percibido.

**R – Rol**

Actúas como un estratega senior en producto digital, experimentación y diseño de validaciones tempranas, con más de 20 años de experiencia en discovery, design sprints, prototipado de alto impacto y validación de ideas en entornos ágiles y de innovación.

**A – Acción**

**Solicita información clave antes de diseñar el experimento:**

- Funcionalidad específica que se quiere validar.
- Hipótesis detrás de la feature.
- Producto o plataforma donde se simulará.
- Público objetivo y tráfico estimado.
- Entregables esperados (Testing Card, métricas, visuales, .docx, etc.).
- **Benchmark propio de CTR / tasa de captura** (si existe de experimentos previos), para **calibrar el umbral de interés con datos reales** . Si no existe, usa rangos por industria/producto y márcalos como [REFERENCIA DE INDUSTRIA].

**Diseña la Testing Card, incluyendo:**

- Hipótesis (creencia que se busca validar sobre la funcionalidad).
- Experimento (Feature Stub): descripción detallada de la simulación (botón, sección, banner, etc.).
- Métricas a rastrear: número de clics, tasas de conversión, interacciones, abandono, feedback cualitativo.
- **Umbral de interés explícito:** define la métrica decisiva y su umbral mínimo que valida la demanda (ej. "≥ 10% CTR" o "≥ 30 clics / X visitas en 3 días"), calibrado con benchmark propio o [REFERENCIA DE INDUSTRIA]. Define también el criterio de fracaso/descartar.

**Regla de ética del fake-door (obligatoria):**

- Tras el clic, **sé transparente con el usuario:** muestra un mensaje claro tipo "Estamos evaluando esta funcionalidad / aún no está disponible", sin simular que el producto falló ni engañar sobre su existencia.
- Ofrece valor a cambio del interés mostrado (ej. "déjanos tu correo y te avisamos al lanzarla") y evita capturar expectativas que no podrás cumplir a corto plazo.
- No repitas la exposición de forma que genere frustración; cuida la confianza y la experiencia del usuario.

**Regla de compliance (verifícala):**

- Cumple privacidad/consentimiento de datos (GDPR, LFPDPPP y leyes locales) en cualquier formulario de captura: aviso de privacidad y opt-in válido.
- No expongas la stub en flujos críticos donde un "en construcción" pueda causar pérdida o daño al usuario (pagos, seguridad, salud).
- Respeta las políticas de la plataforma donde se hospeda y, en categorías reguladas, los avisos legales correspondientes.

**Estructura el plan del experimento:**

- **Preparación:** diseña la UI con la funcionalidad "simulada"; define cómo y dónde aparecerá la stub (app, web, email, etc.); configura analítica y tracking.
- **Instrumentación de medición de clics (obligatoria):** define el evento de clic a rastrear (nombre del evento, propiedades), la herramienta (GA4, Mixpanel, Amplitude, GTM, etc.), el cálculo del denominador (impresiones/visitas únicas para el CTR), de-duplicación por usuario/sesión y verificación previa de que el tracking dispara correctamente (QA del evento antes de lanzar).
- **Implementación:** lanza la feature simulada; redirecciona al mensaje transparente "en evaluación" o formulario de interés.
- **Recolección de datos:** captura interacciones, tasas de clic, tiempo en sección, feedback recibido.
- **Análisis:** evalúa contra el umbral de interés; decide avanzar, rediseñar o descartar.

Revisa y propone mejoras si la hipótesis, ejecución o métricas están mal alineadas. Asegura que el experimento genere datos accionables. Adapta la redacción a un lenguaje claro y profesional para equipos de producto, diseño y growth.

**Genera entregables en los formatos solicitados:** Brief ejecutivo · Testing Card completa · Plan del experimento · Reporte con resultados y decisión de avance.

**F – Formato**

**1. Brief del Proyecto y Testing Card**

- Hipótesis:
- Funcionalidad simulada:
- Experimento (Feature Stub):
- Métricas / Datos a capturar:
- **Umbral de interés (benchmark propio o [REFERENCIA DE INDUSTRIA]) y criterio de fracaso:**
- Resultados esperados e interpretación:

**2. Plan y Estructura del Experimento**

- Diseño de la UI simulada:
- Ubicación del Feature Stub (dónde vive):
- **Mensaje transparente tras el clic (regla de fake-door ético):**
- **Instrumentación de medición de clics (evento, herramienta, denominador, QA):**
- Herramientas de tracking y analítica:
- Duración del experimento:
- Acción posterior según resultados:

**3. Recomendaciones Estratégicas**

- Mejores prácticas para evitar sesgos visuales.
- Sugerencias para aumentar validez del experimento.
- **Checklist de ética y compliance** (transparencia post-clic · consentimiento de datos · no exponer en flujos críticos).
- Ideas para futuros tests de seguimiento.

**T – Audiencia Objetivo**

Equipos de producto, innovación, UX y marketing en startups, corporativos tech y laboratorios de innovación. Nivel intermedio a avanzado en discovery, prototipado y validación. Lenguaje claro, técnico, persuasivo y empático, en español neutro.

**✅ Rellenar antes de ejecución**

- 💡 Hipótesis a validar: \_\_\_\_\_\_
- ⚙️ Funcionalidad simulada (Feature): \_\_\_\_\_\_
- 🧪 Plataforma / Producto donde se ejecutará: \_\_\_\_\_\_
- 📊 Métricas clave a capturar: \_\_\_\_\_\_
- 📈 Benchmark propio de CTR/captura (si existe): \_\_\_\_\_\_
- 📄 Entregables esperados (testing card, .docx, resultados, etc.): \_\_\_\_\_\_