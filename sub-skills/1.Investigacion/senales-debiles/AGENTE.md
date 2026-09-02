---
name: senales-debiles
description: Protocolo de 5 fases para detectar señales débiles en datos mixtos multi-formato (CSV, TXT, PDF, DOCX, XLSX, PPTX). El agente determina por contenido semántico si cada fuente aplica a análisis cuanti o cuali. Orden de filtrado unificado (exclusiones→novedad→redundancia), verificación de citas, rúbrica de calibración con modo fallback, blindaje de cruces transpoblacionales.
category: Investigación
---

# Agente Señales Débiles — Orquestador

Skill modular que ejecuta el protocolo de 5 fases del Agente Señales Débiles, tomando como input datos multi-formato (CSV, TXT, PDF, DOCX, XLSX, PPTX), y entregando como output un reporte ejecutivo HTML autocontenido con visualizaciones Chart.js.

## Cómo está organizado

Este archivo (`AGENTE.md`) contiene las reglas globales, el contrato JSON entre fases y las referencias a cada fase. Cada fase vive en su propio archivo bajo `references/` y es autosuficiente: incluye todas las instrucciones, formatos y criterios que necesita para ejecutarse sin depender de que el modelo "recuerde" fases anteriores. La redundancia entre archivos de fase (no la de las reglas de contenido/formato, consolidadas en `SPEC.md`) es deliberada.

```
AGENTE.md (orquestador — este archivo)
    │
    ├── SPEC.md
    │     Fuente única de verdad del contenido y formato del reporte:
    │     estructura de secciones, campos de tarjeta, checklist de
    │     validación, reglas de tono y trazabilidad. Vinculante para Fase 4.
    │
    ├── references/design-system.md
    │     Design system visual del reporte (tipografía, paleta,
    │     componentes, layout). Vinculante para Fase 4.
    │
    ├── references/fase-0-viabilidad.md
    │     Input:  archivos de datos (CSV, TXT, PDF, DOCX, XLSX, PPTX)
    │     Output: fase0_output.json
    │
    ├── references/fase-1-eda-cuantitativo.md
    │     Input:  fase0_output.json + datos_cuantitativos.csv
    │     Output: fase1_output.json
    │
    ├── references/fase-2-eda-cualitativo.md
    │     Input:  fase0_output.json + transcripciones/*.txt
    │     Output: fase2_output.json
    │     Método: lectura por ventanas (~5 min / ~1,500 palabras c/u)
    │     con consolidación temporal intra y trans-entrevista
    │
    ├── references/fase-3-cruce.md
    │     Input:  fase1_output.json + fase2_output.json
    │     Output: fase3_output.json
    │
    └── references/fase-4-entrega.md
          Input:  fase1_output.json + fase2_output.json + fase3_output.json
                 + SPEC.md + references/design-system.md
          Output: reporte_ejecutivo.html
```

Cada fase recibe un JSON estructurado de la fase anterior y produce un JSON que alimenta la siguiente. Esto mantiene contexto limpio entre fases.

## Pipeline

```
Fase 0 (Viabilidad) → Fase 1 (EDA Cuantitativo) → Fase 2 (EDA Cualitativo) → Fase 3 (Cruce) → Fase 4 (Entrega)
```



---

## Reglas Máximas

1. Orden estricto: Fase 0 → Fase 1 → Fase 2 → Fase 3 → Fase 4. Prohibido fusionar fases.
2. Cada fase tiene su propio encabezado de inicio y cierre.
3. Nunca inventes datos, citas, resultados ni simules código o archivos que no existen.
4. Si no tienes un dato: escribe exactamente `[no disponible]`.
5. Si no puedes localizar una cita: escribe exactamente `[no localizable]`.
6. Si no puedes computar un valor: escribe exactamente `[no computable]`.
7. Dataset original NUNCA sobrescrito. Trabaja sobre copias.
8. No reportes problemas operativos, técnicos, de instrumento o de recolección como señales débiles. El foco es el fenómeno del usuario, no la calidad del método. Para decidir si un hallazgo es señal o limitación, aplica esta prueba: *si eliminas la investigación, ¿el hallazgo sigue existiendo?* Si la respuesta es no —porque el hallazgo solo existe en función de cómo se investigó—, entonces no es una señal débil.

9. **Lectura completa obligatoria (con exención por rol cuantitativo).** Todo archivo de datos (CSV, TXT, PDF, DOCX, XLSX, PPTX) se consume en su totalidad —todas las filas, todas las columnas, todas las páginas, todas las líneas— sin muestreo, sin resumen previo, sin omitir secciones, y sin inferir el contenido por nombre, extensión o primeras líneas. La "lectura completa literal en contexto" (volcar el archivo entero al contexto del LLM) es obligatoria para todo material que los scripts no interpretan, en especial el cualitativo (TXT, transcripciones), donde es el método mismo (Fase 2, lectura por ventanas). Exención por rol, no por formato: un archivo tabular (CSV/XLSX) queda exento de volcarse en contexto solo si (a) alimenta el pipeline cuantitativo (SSoT) y (b) un script lo consume íntegramente (p. ej. `fase0_enriquecer.py` y `fase1_analisis.py` sobre el CSV enriquecido). En ese caso la evidencia de "lectura completa" la aporta el script (N exacto de filas y columnas procesadas) y el gate la contrasta contra el CSV enriquecido (`verificar_numeros.py`, SSoT). Límites de la exención:
   - Si el entorno no dispone de Python (no hay script capaz de procesar el archivo), NO hay exención: el LLM lee el archivo completo en contexto.
   - Las columnas de **texto abierto** (respuestas libres no codificadas por el script) se marcan en Fase 0 (`variables_texto_abierto`) y su contenido sí se lee en contexto, campo por campo, porque su significado lo interpreta el LLM, no el script.
   - Un XLSX que por contenido es transcripción de entrevista (columna de diálogo + hablante) es cualitativo por contenido semántico (Fase 0 clasifica por contenido, no por extensión): NO queda exento; se lee completo por ventanas en Fase 2 y Fase 0 lo serializa a TXT (ver normalización de transcripciones).
   Como evidencia de lectura completa, cada fase reporta en su JSON de salida: (a) archivos tabulares exentos: N exacto de filas y columnas procesadas por el script; (b) archivos textuales: N exacto de líneas, párrafos o intervenciones leídas por archivo; (c) PDF/DOCX/PPTX/XLSX: N exacto de páginas o diapositivas procesadas. Si un archivo no pudo leerse completo, se declara en advertencias con el motivo.
10. Toda estadística debe declarar N efectivo. Todo porcentaje debe tener numerador y denominador explícitos.
11. Toda cita debe incluir ubicación verificable o `[no localizable]`.

12. No asumas que encuestados y entrevistados son la misma población. Cada fuente se analiza en su propio contexto. Si la encuesta cubre a la población general de un territorio y las entrevistas solo a quienes usan un servicio específico, no infieras características de una población sobre la otra. Las fuentes se declaran explícitamente en `datos.poblaciones` de Fase 0 (mapa `universo → población`) y no se mezclan sin evidencia de que provienen del mismo universo. Los cruces entre fuentes de universos distintos se marcan `tipo_cruce: "transpoblacional"` con `naturaleza_cruce` (`extrapolacion` | `convergencia`) y quedan sujetos al blindaje de `references/fase-3-cruce.md`, verificado a máquina por `verificar_trazabilidad.py` (matching de poblaciones por substring, piso de N por población, cap de severidad Alta, sin notas de extrapolación toleradas).

13. Toda señal detectada en cualquier fase debe clasificarse contra las hipótesis previas declaradas en el contrato JSON. La clasificación es obligatoria y usa uno de tres valores: "confirmacion" (la señal refuerza una hipótesis previa — no escala a Fase 4 como señal débil), "señal débil" (la señal cumple las 3 condiciones de la definición: rompe expectativa + abre pregunta nueva + tiene potencial de disrupción), o "tension" (la señal contradice una hipótesis previa). Solo las clasificadas como "señal débil" escalan al reporte final. Si no hay hipótesis previas declaradas, se marca como "señal débil" solo si cumple las 3 condiciones.

    **Regla de cierre (reclasificación auditable, obligatoria):** si una señal o cruce se clasifica "señal débil" y su `ancla` es `hipotesis_usuario` (es decir, se puntúa contra hipótesis previas del usuario y por lo tanto las toca, reforzándolas o contradiciéndolas), debe declarar obligatoriamente el campo estructurado `mecanismo_nuevo` (string no vacío): el mecanismo causal nuevo e independiente que justifica que no sea `confirmacion` ni `tension`. La evidencia del mecanismo puede detallarse en ese campo o en `filtro_2`, pero el campo es el ancla verificable. Sin `mecanismo_nuevo`, la señal queda clasificada `confirmacion`/`tension` y no escala. `scripts/validar_esquema.py` lo verifica a máquina al cierre de Fases 1, 2 y 3 (gate intermedio).

14. El reporte HTML debe respetar el design system definido en `references/design-system.md` (tipografía, paleta, componentes visuales) y el formato de contenido definido en `SPEC.md` (estructura de secciones, campos de tarjeta, checklist de validación, reglas de tono y trazabilidad). `SPEC.md` es la fuente única de verdad para el contenido y formato del reporte; `design-system.md` es la fuente única de verdad para su aspecto visual. Cualquier desviación debe justificarse explícitamente en las advertencias de Fase 4.

15. **Pregunta congelada.** `pregunta_investigacion` se fija en Fase 0 y se propaga idéntica (byte a byte) a todas las fases y al header del HTML. Ninguna fase posterior la reescribe. Ver invariante 0.1 de `SPEC.md`.

16. **Fuente única de verdad para números (SSoT).** Ninguna fase escribe a mano conteos, porcentajes o frecuencias que puedan calcularse con un script. Todo número del JSON debe ser recomputable desde los datos de entrada; los cálculos de infraestructura se hacen con Python y el resultado alimenta el JSON (el LLM redacta interpretaciones, no cifras). Ver invariante 0.2 de `SPEC.md`.

17. **Validación computada, no auto-reportada.** El bloque `validacion` de `fase4_output.json` se completa con la salida de los scripts de verificación (`validar_reporte.py`, `verificar_citas.py`, `verificar_numeros.py`, `verificar_trazabilidad.py`). Prohibido marcar `true` un punto que un script no verificó. **El único actor con autoridad para estampar `true` es `run_gate.py`**: al terminar, el orquestador reescribe el bloque `validacion` (con `ejecutada`, `gate_*` por verificador, `gate_veredicto` y `puntos_fallidos`). El LLM nunca escribe booleanos de validación a mano; sin `gate_report.json` real el reporte se entrega marcado **NO VERIFICADO** y `validacion.ejecutada: false`. Además, `validar_esquema.py` funciona como **gate intermedio**: valida el invariante de clasificación (Filtro 2) al cierre de Fases 1, 2 y 3, deteniendo el pipeline con un error claro antes de que el problema se propague al reporte HTML. Ver invariante 0.4 y 0.6 de `SPEC.md`.

18. **Persistencia de clarificaciones semánticas.** Cualquier aclaración del usuario sobre el significado de una columna (ej. `gasto_mensual` = esfuerzo invertido, no intensidad) se registra en `notas_semanticas.md` del proyecto y los mapeos de roles de todas las fases posteriores deben consultarla. Una re-interpretación que contradice una nota previa es una regresión y se corrige.

---

## Definición de Señal Débil

Una señal débil es una observación —cuantitativa o cualitativa— que cumple **las tres** condiciones siguientes:

1. **Rompe una expectativa:** contradice lo que el sentido común del dominio, la pregunta de investigación o el equipo esperaba encontrar. La expectativa debe estar declarada explícitamente en el pre-registro de Fase 0, no inferida a posteriori.
2. **Abre una pregunta nueva:** no se limita a confirmar o refutar una hipótesis previa, sino que obliga a preguntarse algo que no nos estábamos preguntando.
3. **Tiene potencial de disrupción:** si la señal resultara cierta, cambiaría una decisión, una hipótesis de negocio o una prioridad de inversión.

**No es señal débil:**
- Un hallazgo que confirma una hipótesis previa (es evidencia confirmatoria, no señal).
- Una crítica retrospectiva ("debieron preguntar X en la encuesta").
- Una ausencia sin contraste ("nadie mencionó X" sin evidencia de que sí mencionan Y en su lugar).
- Un problema operativo del instrumento de medición.
- Una queja aislada sin patrón.
- Un problema operativo del negocio (métricas internas, canales, procesos del equipo). La señal débil debe originarse en el comportamiento, lenguaje o contradicción del usuario/cliente/mercado, no en cómo opera internamente la organización.

### Ejemplos Genéricos

Los patrones ilustrativos de "sí/no es señal débil" viven en `references/ejemplos-senales.md`; léelo bajo demanda, no en cada activación.

### Prueba de Redundancia (obligatoria antes de escalar a Fase 4)

Antes de que cualquier señal con `escala_a_fase4: true` llegue al reporte final, el agente debe aplicar esta prueba:

> *"¿Este hallazgo existiría si elimino las otras señales que ya tengo en la lista?"*

- Si la respuesta es **no** —porque el hallazgo es una consecuencia lógica de otra señal más fundamental—, la señal es **redundante** y no escala. Se documenta en advertencias como "señal absorbida por [ID de la señal que la subsume]".
- Si la respuesta es **sí** —el hallazgo describe un fenómeno independiente con su propio mecanismo causal—, la señal es **no redundante** y puede escalar.

Esta prueba se aplica en Fase 1, Fase 2 y Fase 3 antes de marcar `escala_a_fase4: true`. En Fase 4, el checklist de validación verifica que ninguna señal redundante haya llegado al HTML.

### Orden de Filtrado (obligatorio, secuencia única)

Antes de marcar cualquier señal con `escala_a_fase4: true`, el agente debe aplicar **los tres filtros en este orden estricto**. La secuencia es vinculante: cada filtro se evalúa hasta agotar su veredicto antes de pasar al siguiente. Un hallazgo que muere en un filtro no se evalúa contra los posteriores.

```
1. EXCLUSIONES   → ¿Es problema operativo (regla 8), del instrumento de medición,
                   queja aislada sin patrón, crítica retrospectiva o ausencia
                   sin contraste?  → NO ESCALA (fin, se documenta como limitación)
                   ¿No? → continúa al filtro 2

2. NOVEDAD       → Clasificar contra hipótesis previas (Regla 13):
                   ¿"confirmacion" o "tension"? → NO ESCALA (fin)
                   ¿"señal débil" (cumple las 3 condiciones)? → continúa al filtro 3

3. REDUNDANCIA   → Prueba de redundancia (sección anterior):
                   ¿existiría sin las otras señales de la lista? → absorbida, NO ESCALA (fin)
                   ¿independiente con mecanismo propio? → ESCALA a Fase 4
```

**Reglas de la secuencia:**

- **El filtro 1 es independiente de las hipótesis previas.** Un problema operativo que *no* está ingresado como hipótesis previa igual muere en el filtro 1: la lista de exclusiones bloquea por la *naturaleza* del hallazgo (métrica interna, proceso del equipo, defecto del instrumento), no por su novedad.
- **El filtro 2 nunca evalúa un hallazgo que el filtro 1 ya descartó.** No se clasifica contra hipótesis algo que primero no pasó la lista de exclusiones.
- **El filtro 3 nunca se aplica antes que el 2.** No se evalúa redundancia de un hallazgo que aún no está confirmado como señal débil.
- La evaluación de cada filtro se documenta en el JSON de la fase correspondiente (resultado + motivo, ej. "filtro_1: descartado — problema operativo del negocio").

**Invariante de clasificación (obligatorio, comprobable a máquina):** `clasificacion_hipotesis_previa ≠ "señal débil"` ⇒ `escala_a_fase4 = false`. Toda señal con clasificación `confirmacion` o `tension` se escribe con `escala_a_fase4: false` y se documenta como evidencia confirmatoria o contrastante en el JSON; no compite en la priorización de Fase 3 ni aparece en el HTML. `scripts/validar_reporte.py` verifica este invariante sobre los JSON de Fases 1–3.

**Disuasión (antídoto contra la trampa del valor):** si un hallazgo te parece demasiado valioso para descartarlo pero su clasificación es `confirmacion` o `tension`, no escala. Documenta el hallazgo como evidencia confirmatoria en el JSON y sigue adelante. El protocolo no negocia.

Esta secuencia reemplaza la aplicación dispersa de las reglas 8 (exclusiones), 13 (novedad) y la prueba de redundancia: unifica los tres criterios en un solo pipeline declarado.

**Alcance de la secuencia (cruces incluidos):** el Orden de Filtrado se aplica también a los cruces de Fase 3 y a toda señal que llegue con `escala_a_fase4: true` a Fase 4. El filtro 1 (EXCLUSIONES, cláusula "del instrumento de medición") es la prueba de pertinencia de SPEC.md sección 2: un cruce de silencio cuantitativo cuyo hallazgo sea "la encuesta no midió X" describe el proceso de investigación → no escala y va al footer (Limitaciones), nunca como "Señal Débil N". Fase 4 re-aplica esta prueba antes de numerar cada señal y demueve las que fallen (ver `references/fase-4-entrega.md` y `references/fase-3-cruce.md`).

---

## Sistema de Variables: 6 Roles Semánticos

Toda columna del CSV debe mapearse a uno de estos 6 roles. Si una columna no encaja en ninguno, se marca como `[sin rol]` y se documenta.

| Rol | Descripción | Ejemplos |
|:---|:---|:---|
| **Intensidad** | Magnitud, frecuencia o severidad de un fenómeno | Horas dedicadas, N de visitas, score de acuerdo (Likert) |
| **Esfuerzo** | Recursos invertidos (tiempo, dinero, personal) | Horas/semana, intentos de participar, gasto mensual |
| **Categoría problema** | Tipo de problema o necesidad | "Falta de tiempo", "Lejanía", "No sé cómo empezar" |
| **Categoría solución** | Tipo de solución o herramienta usada | "Buscar tutorial en línea", "Preguntar a un conocido", "Contratar un servicio" |
| **Segmento** | Perfil o grupo del respondiente | Zona de residencia, grupo de edad, situación laboral |
| **Tiempo** | Dimensión temporal | Fecha de encuesta, antigüedad en la zona, mes |

---

## Reglas de Calidad de Respuesta

Si un respondiente usa la misma opción en ≥70% de ítems Likert consecutivos, o sus respuestas abiertas son monosílabos genéricos ("bien", "no sé", "regular"), se marca como respuesta de baja calidad y se excluye del análisis de señales. El criterio se documenta en el JSON de salida de la fase correspondiente.

---

## Modo de Ejecución Conversacional

19. **Ejecución continua con pausa adaptativa.** El agente ejecuta las 5 fases de principio a fin sin pausas fijas ni solicitar confirmación entre fases. El pipeline solo se detiene si: (a) un gate de validación falla tras 3 reintentos, (b) falta información indispensable, o (c) **el runtime impone un límite de herramientas por turno (`pause_turn`) o el trabajo pendiente de la fase actual superaría el cap de ~20 llamadas**. En caso (c), el agente corta en el borde natural de fase (ideal tras Fase 2), emite el JSON de salida de esa fase como handoff, y reanuda en el siguiente turno leyendo **solo ese último JSON**; nunca repite trabajo completado ni pide aprobación al usuario.

20. **Modo silencioso por defecto.** El agente no narra en el chat el proceso interno de análisis (lectura de ventanas, bloques B1-B6, razonamiento intermedio, decisiones de codificación, etc.). Ese detalle vive únicamente en los JSON estructurados de cada fase, que son el artefacto de trabajo real. Durante la ejecución, el agente solo debe emitir mensajes breves de progreso (ej. "Fase 2 completada y validada. Continuando con Fase 3.") y, al finalizar, un resumen ejecutivo conciso con los hallazgos principales y los archivos entregables. Si el usuario solicita explícitamente ver el detalle del proceso de alguna fase, el agente puede exponerlo bajo pedido, pero no por defecto.

21. **No re-lectura / handoff JSON estricto.** Una vez que un archivo de datos (CSV, transcripciones, PDF) o el corpus cualitativo ha sido consumido y sus hallazgos volcado al JSON de la fase correspondiente, **no se vuelve a leer**. Fases 3 y 4 consumen exclusivamente los JSON de fases anteriores (`fase1_output.json`, `fase2_output.json`, `fase3_output.json`); solo `scripts/verificar_citas.py` accede al corpus original en Fase 4 para auditoría de citas. Los JSON son la única fuente de verdad (SSoT) entre fases; no se re-abren archivos de origen para "completar" o "verificar" nada que ya esté en el JSON.

---

## Contrato JSON entre Fases

Cada fase produce un JSON que es consumido por la(s) fase(s) siguiente(s). El contrato mínimo que todo JSON de salida debe cumplir. La lista `hipotesis_previas` es obligatoria **completa solo en `fase0_output.json`**: en Fases 1-3 puede omitirse (se hereda de Fase 0) y cualquier cambio de estado se declara en `advertencias` (ej. "Hipótesis X pasó a descartada en Fase 1"). `pregunta_investigacion` sí se repite exacta en cada fase (texto corto, clave de trazabilidad).

**Semántica de campos (evita duplicación):** `contexto` solo ubica (fuente, momento, muestra); `dato` describe lo observado con su magnitud; `expectativa_rota` formula "esperábamos X, observamos Y". Ninguno de los tres debe repetir el contenido de los otros. Los campos de justificación (`justificacion_severidad`, `justificacion_sorpresa`) son una frase máxima y no re-narran el `dato`.

```json
{
  "fase": "nombre de la fase",
  "timestamp": "momento de generación",
  "pregunta_investigacion": "texto exacto",
  "hipotesis_previas": [
    {
      "hipotesis": "texto de la hipótesis que el equipo ya tiene mapeada",
      "fuente": "quién la declaró (ej. 'contexto inicial del usuario', 'entrevista con stakeholders')",
      "estado": "activa | descartada | en validación"
    }
  ],
  "advertencias": ["lista de limitaciones detectadas en esta fase"],
  "redundancia": [
    {
      "aplicada": true,
      "senal_id": "ID de la señal evaluada",
      "resultado": "escala | absorbida",
      "absorbida_por": "ID de la señal que la subsume (solo si resultado=absorbida)",
      "razon": "mecanismo causal compartido o consecuencia lógica de otra señal"
    }
  ],
  "datos": { }
}
```

Los formatos específicos de `datos` están definidos en el archivo de cada fase, bajo
`references/fase-N-*.md`.

---

## Ejecución

1. El usuario proporciona archivos de datos (CSV, TXT, PDF, DOCX, XLSX, PPTX) y la pregunta de investigación. El agente determina por contenido semántico si cada archivo aplica al análisis cuantitativo, cualitativo, o ambos. Los formatos aceptados son: CSV (cuanti), TXT (cuali), PDF/DOCX/PPTX/XLSX (el agente evalúa si su contenido es predominantemente numérico/tabular → cuanti, o textual/narrativo → cuali).
2. **Consulta inicial única (antes de Fase 0).** El agente ejecuta `scripts/preview_columnas.py` sobre la fuente tabular (encabezados, tipo, cardinalidad y muestras por columna), propone el mapeo provisional de columnas a roles y hace UNA consulta al usuario: valida el mapeo y recoge hipótesis previas, aclaraciones de columnas y contexto de recolección. El usuario responde una sola vez (o confirma con "adelante"); las hipótesis se incorporan a `hipotesis_previas` y las aclaraciones a `notas_semanticas.md` antes de generar `fase0_output.json` (ver `references/fase-0-viabilidad.md` Paso 1). A partir de aquí el pipeline corre de corrido sin pausas (Regla 19).
3. El agente lee `references/fase-0-viabilidad.md` y ejecuta Fase 0. En esta fase, el agente realiza el **pre-registro de expectativas**: declara explícitamente qué espera encontrar en los datos antes de analizarlos, basándose en la pregunta de investigación y el dominio. Estas expectativas son el estándar contra el cual se evalúa si una observación "rompe una expectativa" en fases posteriores.
4. El agente lee `references/fase-1-eda-cuantitativo.md` y ejecuta Fase 1.
5. El agente lee `references/fase-2-eda-cualitativo.md` y ejecuta Fase 2 (lectura eficiente 1-2 accesos por transcripción, bitácora interna, ver `fase-2-eda-cualitativo.md` "Mecánica de lectura eficiente").
6. El agente lee `references/fase-3-cruce.md` y ejecuta Fase 3. En esta fase se aplica el blindaje de cruces transpoblacionales cuando las fuentes provienen de poblaciones distintas.
7. El agente lee `references/fase-4-entrega.md` y ejecuta Fase 4. **El HTML se genera con `scripts/generar_reporte.py` + `scripts/plantilla_reporte.html`** (no a mano); el LLM escribe el bloque `reporte` en `fase4_output.json`, el generador aplica la plantilla (design system congelado: Sora/Inter, paleta purple→gold, radius 14px, Chart.js CDN) y emite `reporte_ejecutivo.html`.
8. El agente entrega `reporte_ejecutivo.html`.

**Verificación determinista (gate final obligatorio antes de cerrar):**

El bloque `validacion` de `fase4_output.json` se completa con la salida real de los scripts (invariante 0.4 de `SPEC.md`), nunca con auto-evaluación del LLM. El orquestador `scripts/run_gate.py` los ejecuta en orden con **progreso por verificador y timeout** (`--timeout`, default 120s; un check que excede su límite se marca `PENDIENTE`, nunca colga el orquestador) y genera un `gate_report.json` unificado que **reescribe el bloque `validacion`** de la Fase 4 (fail-closed: sin ejecución real, los booleanos quedan `false`):

```bash
python scripts/run_gate.py <directorio_proyecto> -o gate_report.json
```

Los verificadores individuales son:

- `scripts/validar_esquema.py` — estructura mínima de cada `faseN_output.json`.
- `scripts/verificar_trazabilidad.py` — pregunta congelada, IDs referenciados y mapeo HTML↔JSON.
- `scripts/validar_reporte.py` — estructura del HTML, campos de tarjetas, numeración, ausencia de IDs técnicos, heatmap, footer y el invariante de clasificación (Filtro 2) sobre los JSON de entrada contra SPEC.md.
- `scripts/verificar_citas.py fase2_output.json fase3_output.json --corpus <carpeta_de_transcripciones>` — audita las citas contra el corpus y los claims de ausencia. `NO_ENCONTRADA` y `CONTRADICCION` bloquean la escala; `APROXIMADA` exige justificación. Las citas truncadas con `...` se toleran como `ENCONTRADA_TRUNCADA` (no bloquea); con `--exacto` se exige coincidencia literal.
- `scripts/verificar_numeros.py <dataset.csv> fase1_output.json fase2_output.json fase3_output.json` — recalcula los conteos clave del CSV y los compara contra los JSON (SSoT).

Estos scripts complementan la revisión del LLM; su ejecución requiere Python. Sin Python no se replican manualmente con `true`: se declara la ausencia de ejecución determinista en las advertencias de Fase 4, ningún punto se marca `true`, `validacion.ejecutada: false` y el reporte se entrega marcado **NO VERIFICADO**.

Cada fase se ejecuta con contexto limpio: solo recibe el JSON de la fase anterior y los archivos de datos originales. No depende de que el modelo "recuerde" lo que hizo en fases anteriores.

---

## Contexto del flujo (entrada)

Esta skill puede ejecutarse suelta o como paso del **flujo de innovación IRIS**. Si la
invoca la macro-skill, recibes un bloque `flujo` con el histórico del proyecto (también
disponible en `flujo_estado.json`, o con
`python scripts/estado_flujo.py mostrar --paso <html_N>` desde la raíz del repositorio).

Cuando ese contexto existe:

1. **No vuelvas a preguntar lo ya decidido.** Las decisiones registradas y los datos del
   proyecto (objetivo, audiencia) ya están ahí. Afecta directamente a la **consulta inicial
   única** del paso 2 de «Ejecución»: el objetivo y la audiencia del proyecto salen del
   contexto, y la consulta se reduce a lo que solo el usuario sabe —el mapeo de columnas a
   roles, sus hipótesis previas y las aclaraciones semánticas—.
2. **Parte de los resúmenes previos** en lugar de reconstruir el contexto desde cero.
3. **Lee los datos del predecesor, no solo su resumen.** Cada paso cerrado deja en
   `flujo.ruta[]` un campo `datos` (la ruta de su `reporte.json`) y la lista `archivos`.
   Abre ese `reporte.json` y toma de ahí los bloques que necesites —`secciones[].items[]`
   y los especializados como `persona` o `psf`— en vez de reescribirlos a partir del
   resumen: **el resumen es el índice, los datos están en el archivo.** Si un paso no
   registró `datos`, su HTML (`archivo`) lleva lo mismo embebido en `window.REPORT_DATA`.
4. **Las hipótesis previas del proyecto son hipótesis previas de la Fase 0.** Lo que el
   flujo ya dio por sentado entra en `hipotesis_previas` con
   `fuente: "contexto del flujo IRIS"`, y por lo tanto pasa por el Filtro 2 (novedad) como
   cualquier otra: un hallazgo que confirma lo que el proyecto ya creía **no escala**.
5. **Los pasos con estado `omitido` no aportan datos.** Su campo `impacto` dice qué falta:
   sustitúyelo por un supuesto marcado `*` y decláralo en `advertencias`.
6. **Declara qué usaste** en `decision.contexto_usado` del contrato JSON.

**La Regla 19 (ejecución continua) no contradice el human-in-the-loop de la macro.** El
flujo se detiene **entre pasos** y en los nodos de decisión de `pasos.json`; el pipeline de
5 fases es el interior de un solo paso y corre de corrido. Es decir: pregunta antes de
empezar y al cerrar, no entre Fase 1 y Fase 2.

## Como paso del flujo IRIS

Esta skill tiene su **propia salida HTML** (`reporte_ejecutivo.html`, generado por
`scripts/generar_reporte.py`), que se conserva tal cual: es el entregable detallado y no lo
sustituye nada.

Cuando corre dentro del flujo, además de ese HTML propio:

1. Resume tus resultados en un `reporte.json` con el esquema `REPORT_DATA`
   (ver `_plantilla_html/README.md`). Una señal débil por `item`; el bloque `tabla` del
   esquema sirve para la matriz de señales (señal → severidad → sorpresa → robustez →
   score) sin reescribirla como párrafo.
2. Declara la procedencia en `meta.origen_datos`
   (`{tipo: "reales"|"simulados"|"mixtos", nota: "…"}`). Este paso normalmente corre sobre
   datos propios del usuario, y ese `tipo: "reales"` es lo que evita que los pasos
   posteriores hereden una duda que no existe.
3. Genera el HTML del paso **desde la raíz del repositorio**, para que lleve el contexto
   completo del flujo (avance, decisiones previas, pasos omitidos):

   ```bash
   python _plantilla_html/scripts/generar_html.py --data reporte.json \
       --estado flujo_estado.json --paso html_1 -o html_1.html
   ```

4. Declara **ambos** archivos en `output.archivos_generados`: `html_1.html` (el paso del
   flujo, con contexto) y `reporte_ejecutivo.html` (tu entregable detallado, como anexo).
   Si el gate se cerró como **NO VERIFICADO**, dilo también en `advertencias`: el HTML del
   paso viaja a los siguientes y la duda tiene que viajar con él.

Fuera del flujo, entrega solo tu HTML propio y omite los pasos 1–3.

## Contrato JSON (salida)

Cierra con el contrato estándar de `sub-skills/CONTRATO_JSON.md`: `skill`, `timestamp`,
`parametros`, `output` (con los dos archivos en `archivos_generados`), `decision`
(`veredicto`, `siguiente_paso`, `razon`, `contexto_usado`) y `advertencias`. El veredicto
del gate (`gate_veredicto` de `gate_report.json`) no reemplaza a `decision.veredicto`: uno
dice si el reporte es válido, el otro qué hacer con lo que encontró.
