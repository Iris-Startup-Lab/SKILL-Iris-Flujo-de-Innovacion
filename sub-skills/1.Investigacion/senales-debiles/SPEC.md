# SPEC — Especificación Consolidada del Reporte Ejecutivo

Fuente única de verdad para el **contenido y formato** de `reporte_ejecutivo.html`. `AGENTE.md` y `references/fase-4-entrega.md` referencian este archivo en vez de repetir sus reglas. El aspecto **visual** (tipografía, paleta, componentes CSS) vive en `references/design-system.md`; este archivo no lo repite.

---

## 0. Invariantes entre fases (vinculantes para todo el pipeline)

1. **Pregunta congelada.** `pregunta_investigacion` es idéntica byte a byte en `fase0_output.json`, `fase1_output.json`, `fase2_output.json`, `fase3_output.json`, `fase4_output.json` y en el header del HTML. Si Fase 0 ajusta la pregunta del usuario, el texto ajustado se congela ahí y se propaga exacto a todas las fases; ninguna fase posterior lo reescribe ni lo reformula.
2. **Fuente única de verdad para números (SSoT).** Todo conteo, porcentaje, media o frecuencia que aparece en un JSON debe ser recomputable desde los datos de entrada (CSV / transcripciones). El LLM nunca escribe a mano un número que un script pueda calcular; si un número no se puede recomputar, se escribe `[no computable]`. Los conteos de infraestructura se calculan con Python y el resultado alimenta el JSON. En el gate final, `scripts/verificar_numeros.py` recalcula los conteos clave del CSV y los compara contra los JSON.
3. **Trazabilidad de IDs.** Toda señal o cruce de la Fase N+1 que referencia un ID técnico (`SD-CUANT-*`, `SD-CUAL-*`, `CRUCE-*`) debe referenciar un ID emitido por las fases anteriores. No existen señales huérfanas ni fantasmas. Toda "Señal Débil N" del HTML se mapea 1:1 a un ID técnico de los JSON. `scripts/verificar_trazabilidad.py` verifica ambos sentidos.
4. **Validación computada, no auto-reportada.** El bloque `validacion` de `fase4_output.json` se completa con la salida real de los scripts de verificación (`validar_reporte.py`, `verificar_citas.py`, `verificar_numeros.py`, `verificar_trazabilidad.py`), no con la auto-evaluación del LLM. Un punto solo se marca `true` si el script correspondiente pasó; si no se ejecutó o falló, se marca `false` con motivo en `puntos_fallidos`.
5. **Timestamps veraces.** `timestamp` de cada fase refleja el momento real de generación en orden cronológico ascendente (Fase 0 < Fase 1 < Fase 2 < Fase 3 < Fase 4).

## 1. Estructura del reporte

El reporte tiene **exactamente 2 secciones**, en este orden fijo, sin secciones adicionales ("Cruces", "Visualizaciones", "Implicaciones", "Contexto" quedan prohibidas como secciones propias):

1. **Señales Débiles**
2. **Decisiones Estratégicas**

Los cruces de Fase 3 que escalan se integran como señales normales en la Sección 1. Las gráficas van dentro de la tarjeta de su señal, nunca en una sección aparte.

## 2. Sección 1 — Señales Débiles

- Entre **3 y 5 señales**. Si hay más de 5, solo escalan las de mayor score compuesto.
- Cada señal es una tarjeta no colapsable con **exactamente 5 campos**:
  1. **Título narrativo numerado** — Formato "Señal Débil N: [título sobrio]". Sin IDs técnicos, sin adjetivos dramáticos. El título describe el fenómeno, no lo califica.
  2. **El dato** — 2-4 líneas: qué se observó, en qué fuente, con qué magnitud.
  3. **Expectativa que rompe** — 1-2 líneas: qué esperábamos y por qué esto lo contradice.
  4. **Pregunta nueva que abre** — 1-2 líneas: qué nos obliga a preguntarnos.
  5. **Hipótesis de valor** — Formato: *Si [cambio concreto], entonces [resultado de negocio], porque [mecanismo causal].* Incluye en la última línea la **validación pendiente sugerida** ("Validar: [qué medir]"), derivada del campo `validacion_pendiente` del JSON.
- **Gráfica opcional:** máximo 1 por señal, dentro de la misma tarjeta (debajo de "Hipótesis de valor"). Si no hay datos de gráfica, el campo simplemente no aparece.
- **Sin badges de severidad.** La severidad es un atributo interno del JSON, nunca se expone visualmente.
- Numeración secuencial ("Señal Débil 1", "Señal Débil 2"...) que las decisiones de Sección 2 referencian.

### Filtro de pertinencia (regla del objeto de estudio)

Una señal débil describe un fenómeno del objeto de estudio (usuario, mercado, producto, categoría), nunca del proceso de investigación. Prueba: *si elimino la investigación, ¿el hallazgo sigue existiendo?*
- **No** → el hallazgo depende de cómo se investigó → no es señal débil, va al footer (Limitaciones).
- **Sí** → describe algo del mundo, no del método → puede escalar.

Esta regla cubre cualquier variante: omisiones del instrumento, sesgos muestrales, decisiones de diseño de cuestionario, limitaciones de formato, y cualquier otra característica del proceso de investigación.

## 3. Sección 2 — Decisiones Estratégicas

- **Exactamente 2 o 3 decisiones.** Nunca 1, nunca más de 3.
- Cada decisión referencia al menos una señal por su número ("Señal Débil 1", "Señal Débil 2").
- **Tono exploratorio, no imperativo:** "Explorar si...", "Probar...", "Investigar si...". Prohibido: "Hacer X", "Implementar Y".
- **Sin campo de plazo ni temporalidad.** La decisión describe qué explorar, no cuándo.
- Formato por decisión: qué probar (tono exploratorio) + "Basado en: Señal Débil N" + resultado esperado (1 línea).

## 4. IDs y nombres

- **Internamente (JSON):** los IDs usan prefijos técnicos de trazabilidad (`SD-CUANT-001`, `SD-CUAL-003`, `CRUCE-002`).
- **En el HTML final:** solo numeración narrativa ("Señal Débil N"). Prohibido incluir IDs técnicos en cualquier parte del HTML.
- **Tono de títulos:** sobrio, descriptivo, sin adjetivos dramáticos.

## 5. Calibración de severidad y sorpresa (rúbrica con modo fallback)

La escala `severidad` (Baja | Media | Alta | Crítica) y `sorpresa` (Baja | Media | Alta) de cada señal en los JSON de entrada **no se asigna por criterio libre**: se puntúa contra una rúbrica con anclas operacionales y se declara el ancla usada.

### Rúbrica de severidad (anclas cualitativas relativas)

| Nivel | Ancla operacional |
|:---|:---|
| **Crítica** | Redefine la pregunta de investigación o la propuesta de valor completa |
| **Alta** | Cambia una decisión de inversión, una hipótesis de negocio o una prioridad de segmento |
| **Media** | Cambia un mensaje, un canal o la definición de un segmento |
| **Baja** | Matiz: afina un mensaje o un detalle de implementación |

Las anclas son relativas a la pregunta de investigación y a las hipótesis previas declaradas: **no requieren ingestar datos nuevos** (presupuestos, cifras, mensajes). "Cambia una decisión de inversión" significa "cambia la prioridad implícita en la pregunta de investigación o en las hipótesis declaradas", no "requiere conocer montos".

### Rúbrica de sorpresa (dependiente del origen del ancla)

| Nivel | Ancla operacional |
|:---|:---|
| **Alta** | Contradice una hipótesis **declarada por el usuario** en Fase 0 (pre-registro o contexto inicial) |
| **Media** | Contradice una expectativa **inferida por el agente** (no declarada por el usuario) |
| **Baja** | Matiz dentro de una expectativa declarada o inferida |

### Modo fallback (obligatorio cuando faltan hipótesis del usuario)

Si el usuario no declaró hipótesis previas, el ancla de una señal solo puede ser `expectativa_inferida` y la sorpresa **no puede puntuar "Alta"**: el nivel Alta exige contradecir una premisa declarada, y una premisa inferida por el propio agente no califica.

Cada señal lleva el campo `ancla` en su JSON:

- `ancla: "hipotesis_usuario"` — puntuada contra hipótesis declaradas por el usuario.
- `ancla: "expectativa_inferida"` — puntuada contra expectativas que el agente infirió. Sorpresa tope en Media.

### Corte de señales (máximo 5)

Cuando más de 5 señales escalan, se priorizan con **score compuesto documentado**: `severidad × sorpresa × robustez`, donde:
- `severidad` = 4 (Crítica) / 3 (Alta) / 2 (Media) / 1 (Baja)
- `sorpresa` = 3 (Alta) / 2 (Media) / 1 (Baja)
- `robustez` = fracción de la muestra que sostiene la señal (ej. N que la respalda / N total de la fuente)

El score y su desglose se documentan en el JSON. El corte por score reemplaza la regla "solo escalan las de mayor severidad".

**Desempate:** si dos señales empatan en score en el borde del corte, escala la de mayor `severidad`; si persiste el empate, la que integre más fuentes o poblaciones (un cruce gana a una señal de una sola fuente); si persiste, la que co-referencie más señales de la misma población. El desempate aplicado se documenta en el JSON.

### Regla de tasa base (obligatoria en Fase 1)

Toda señal cuantitativa basada en la tasa de un subgrupo (ej. "el X% del segmento Y hace Z") se evalúa contra la tasa base del mismo fenómeno en la población total. Si la tasa del subgrupo **no difiere materialmente** de la tasa base —diferencia ≤ ~5 puntos porcentuales o sin evidencia de que la diferencia sea real más allá del redondeo—, el hallazgo se clasifica **CONSISTENTE** (expectativa confirmada), **nunca** como señal débil. Ejemplo: un segmento con 39.0% vs una base de 38.8% no es una señal: es la misma tasa con ruido. El `dato` declara numerador y denominador de ambas tasas (subgrupo y base). `scripts/verificar_numeros.py` puede marcar con `--base-pct` cualquier porcentaje del JSON que quede dentro de ese margen.

## 6. Heatmap SVG inline (especificación técnica)

Obligatorio cuando Fase 0 mapeó dos variables categóricas con 3+ niveles cada una (ej. categoría_problema × categoría_solución). Se renderiza con SVG inline, nunca con `chartjs-chart-matrix`.

- `cell_w` / `cell_h`: **50px mínimo absoluto**; usar 56px si el grid es ≤6×6.
- `viewBox`: `0 0 [offset_x + n_cols*cell_w + margin_right] [offset_y + n_rows*cell_h + margin_bottom]`. `max-width` de al menos `min(700px, 100%)`.
- `margin_bottom` se calcula **dinámicamente** a partir de la etiqueta de eje X más larga, nunca fijo: cada etiqueta rotada 45° desciende ~`0.707 × ancho` desde su ancla (ancho ≈ `n_caracteres × 6px` a font-size 11) más ~15px de separación y el espacio del título del eje. Regla: `margin_bottom = max(90, ceil(0.707 × max_len_etiqueta × 6) + 40)`. Un margen fijo recorta etiquetas largas en grids grandes (8+ columnas).
- Envolver en `<div class="chart-wrap" style="overflow-x:auto">`, sin `max-height` en el contenedor.
- Colores: escala de 5 niveles morada — `#D9CCEF` (mínimo) → `#B8A3D9` → `#7A4E96` → `#5A3A8C` → `#3D2766` (máximo).
- Ejes con etiquetas en `<text>`, rotadas 45° si superan 8 caracteres.
- Tooltip: atributo `<title>` en cada `<rect>` con el valor exacto.
- Si las variables son texto libre, categorizar antes en buckets (máximo 8 por eje).

## 7. Whitelist de gráficos

Solo estos 6 tipos; cualquier otro requiere justificación explícita en advertencias.

| Tipo | Config | Uso |
|:---|:---|:---|
| bar | `type:'bar'` | Comparar categorías |
| horizontalBar | `type:'bar'` + `indexAxis:'y'` | Muchas categorías, etiquetas largas |
| line | `type:'line'` | Tendencias, evolución temporal |
| doughnut | `type:'doughnut'` | Proporciones (máx. 6 segmentos) |
| scatter | `type:'scatter'` | Correlación entre 2 variables continuas |
| heatmap | SVG inline | Cruces categoría × categoría |

Reglas de ejes: toda gráfica con ejes lleva `scales.x.title.text` y `scales.y.title.text` (excepción: doughnut). `plugins.tooltip.enabled: true` en todas.

## 8. Requisitos técnicos del HTML

- HTML5 válido, autocontenido.
- Chart.js 4.4.7 desde CDN (jsdelivr), exactamente:
  ```html
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
  ```
- CSS inline en `<style>`, sin hojas externas (excepto Google Fonts).
- Datos de cada gráfica embebidos en `<script>` como objetos JavaScript.
- **Una señal por línea**: cada tarjeta de señal ocupa el ancho completo de su contenedor (una por fila, en desktop y mobile), con altura ajustada a su contenido (texto y gráfica). Prohibido `repeat(auto-fit,minmax(...))` u otro layout que agrupe varias señales por fila.

## 9. Header y footer del reporte

- **Header:** logo oficial de IRIS (embebido en base64, ver `references/design-system.md` § 3.1), título del reporte, fecha de generación, pregunta de investigación (texto exacto), resumen ejecutivo (2-3 líneas): qué se analizó, cuántas señales, hallazgo central.
- **Footer:** solo 3 columnas — Limitaciones, Fuentes (archivos, N total, fechas), Metodología (pipeline, fases, formato de hipótesis). **Prohibido** incluir sección de trazabilidad o mapeo de IDs técnicos.

## 10. Manejo de inputs faltantes en Fase 4

| Input faltante | Acción |
|:---|:---|
| `fase1_output.json` no existe | Reporte solo con señales cualitativas y cruces. Advertencia: "Fase 1 no ejecutada — sin datos cuantitativos." |
| `fase2_output.json` no existe | Reporte solo con señales cuantitativas y cruces. Advertencia: "Fase 2 no ejecutada — sin datos cualitativos." |
| `fase3_output.json` no existe | Reporte sin cruces. Advertencia: "Fase 3 no ejecutada — sin cruces cuanti-cuali." |
| Ninguna señal escala | Mensaje: "No se detectaron señales débiles en este análisis." Se omite Sección 2. |
| `design-system.md` no accesible | Usar variables CSS de este documento como fallback. Declarar en advertencias. |

**Regla general:** el reporte nunca falla por falta de un input; siempre se genera con lo disponible, declarando ausencias en advertencias.

## 11. Checklist de validación post-generación (obligatorio, único)

Antes de entregar el HTML, verificar cada punto. Si alguno falla, corregir y re-verificar. Este es el checklist único — reemplaza cualquier versión anterior duplicada en `AGENTE.md` o `fase-4-entrega.md`:

1. **Estructura:** exactamente 2 secciones, en el orden (1) Señales Débiles, (2) Decisiones Estratégicas.
2. **Señales:** entre 3 y 8, cada una con exactamente 5 campos, sin badges de severidad.
3. **Numeración:** cada título usa "Señal Débil N:" secuencial; las decisiones referencian por ese número.
4. **Decisiones:** 2 o 3 exactas, cada una referencia ≥1 señal, tono exploratorio, sin plazos.
5. **Calibración:** toda señal en los JSON de entrada declara `ancla` (`hipotesis_usuario` | `expectativa_inferida`); si `ancla = expectativa_inferida`, la sorpresa no es "Alta".
6. **Design system:** variables CSS de `design-system.md` aplicadas (Sora + Inter, paleta purple/gold, header con degradado y mancha dorada, footer `--purple-900`).
7. **Gráficas:** cada una dentro de la tarjeta de su señal, con ejes titulados; heatmap SVG presente si Fase 0 mapeó categoría_problema × categoría_solución.
8. **Señales que escalan:** toda señal seleccionada por el corte de `SPEC.md` § 5 (score compuesto con desempate documentado) está presente en el HTML.
9. **Sin IDs técnicos:** ningún `SD-CUANT-*`, `SD-CUAL-*`, `CRUCE-*` visible en el HTML.
10. **Footer:** solo Limitaciones, Fuentes y Metodología, sin trazabilidad.
11. **Exclusión por clasificación:** ninguna señal con `clasificacion_hipotesis_previa` distinta de `"señal débil"` está presente en el HTML (ni como tarjeta de señal ni como base única de una decisión); su evidencia solo puede integrarse como insumo de un cruce (invariante de AGENTE.md).
12. **Pregunta congelada:** `pregunta_investigacion` idéntica byte a byte en fase0..fase4 y en el header del HTML (invariante 0.1).
13. **Números recomputables:** los conteos clave de cada JSON fueron verificados contra el CSV por `scripts/verificar_numeros.py` sin errores (invariante 0.2).
14. **Trazabilidad de señales:** cada "Señal Débil N" del HTML se mapea a un ID técnico existente en fase1/fase2/fase3 a través de `mapeo_html` de `fase4_output.json` (uno a uno, sin IDs repetidos ni fantasmas, numeración secuencial); sin señales huérfanas ni duplicadas (`scripts/verificar_trazabilidad.py` sin errores, invariante 0.3).
15. **Validación por scripts:** los campos `validacion` de `fase4_output.json` reflejan la salida real de los scripts, no la auto-evaluación del LLM (invariante 0.4).

El resultado se documenta en el bloque `validacion` del JSON de cierre de Fase 4 (`fase4_output.json`), con un campo booleano por punto y `puntos_fallidos: []`.

## 12. Verificación determinista (scripts) — gate final obligatorio

Antes de considerar la Fase 4 completa se ejecutan obligatoriamente los scripts de verificación sobre los artefactos generados. Sus salidas completan el bloque `validacion` de `fase4_output.json` (invariante 0.4); un punto solo se marca `true` si el script correspondiente pasó. Si el entorno no dispone de Python, el checklist se replica manualmente y la ausencia de ejecución determinista se declara en las advertencias de Fase 4.

- `scripts/validar_reporte.py` — verifica estructura, campos, numeración, ausencia de IDs técnicos, heatmap, footer y el invariante de clasificación sobre los JSON.
- `scripts/verificar_numeros.py` — recalcula los conteos clave del CSV y los compara contra los JSON (SSoT, invariante 0.2).
- `scripts/verificar_trazabilidad.py` — verifica pregunta congelada, IDs referenciados y mapeo HTML↔JSON (invariantes 0.1 y 0.3).
- `scripts/verificar_citas.py` — verifica citas textuales y claims de ausencia contra el corpus.

## 13. Verificación de citas (scripts)

Las citas de las señales cualitativas y cruces se verifican contra el corpus con `scripts/verificar_citas.py`. Salidas por cita: `ENCONTRADA`, `UBICACION_INCORRECTA` (no bloquea, corrige ubicación), `APROXIMADA` (requiere justificación del analista), `NO_ENCONTRADA` (única que bloquea la escala). El script además detecta **claims de ausencia** (tipo "nadie menciona X"): si el término declarado ausente SÍ aparece en el corpus, la cita/claim se marca `CONTRADICCION` y bloquea la escala hasta corregirse o descartarse. Es obligatorio ejecutarlo sobre los JSON de Fase 2 y Fase 3 antes de consolidar el reporte.
