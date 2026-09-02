# Fase 4: Entrega

## Propósito

Consolidar todas las señales que escalaron de Fase 1, Fase 2 y Fase 3 en un reporte ejecutivo HTML autocontenido con visualizaciones Chart.js, siguiendo las reglas de contenido/formato de `SPEC.md` y el aspecto visual de `references/design-system.md`.

## Input

- `fase1_output.json`: señales cuantitativas, infraestructura, datos para gráficas
- `fase2_output.json`: señales cualitativas, datos para gráficas
- `fase3_output.json`: cruces
- `pregunta_investigacion`
- `SPEC.md`: fuente única de verdad del contenido y formato del reporte (vinculante)
- `references/design-system.md`: fuente única de verdad del aspecto visual (vinculante)

### Manejo de inputs faltantes

Ver `SPEC.md` sección 10 (Manejo de inputs faltantes en Fase 4). Regla general: el reporte NUNCA debe fallar por falta de un input; siempre se genera con lo disponible, declarando las ausencias en advertencias.

## Output

Un solo archivo: `reporte_ejecutivo.html`. **Excepción: si ninguna señal escala, NO se genera el HTML**; Fase 4 escribe `fase4_output.json` con `mapeo_html: {}`, `n_senales: 0`, la advertencia "No se detectaron señales débiles en este análisis." y cierra sin reporte (ver SPEC.md sección 10).

Además, Fase 4 produce un JSON de cierre (`fase4_output.json`) con el resultado de la validación, siguiendo el checklist único de `SPEC.md` sección 10:

```json
{
  "fase": "fase-4-entrega",
  "timestamp": "2026-01-01T00:00:00",
  "pregunta_investigacion": "texto exacto",
  "advertencias": [],
  "mapeo_html": {
    "Señal Débil 1": "CRUCE-001",
    "Señal Débil 2": "SD-CUANT-001"
  },
  "validacion": {},
  "reporte": {
    "titulo": "Reporte de Señales Débiles",
    "fecha": "2026-01-01T00:00:00",
    "pregunta_investigacion": "texto exacto",
    "resumen_ejecutivo": ["Qué se analizó.", "Cuántas señales.", "Hallazgo central."],
    "senales": [
      {
        "titulo": "Título narrativo sobrio",
        "dato": "dato con magnitud",
        "expectativa": "lo que se esperaba",
        "pregunta": "pregunta nueva que abre",
        "hipotesis": "hipótesis de valor",
        "grafica": {"type": "bar", "data": {"labels": [], "datasets": []}, "options": {}},
        "heatmap_svg_path": "heatmap.svg"
      }
    ],
    "decisiones": [
      {"basado_en": "Señal Débil 1", "exploracion": "Decisión exploratoria.", "resultado_esperado": "Resultado esperado."}
    ],
    "footer": {
      "limitaciones": ["Limitación 1"],
      "fuentes": ["Fuente 1"],
      "metodologia": ["Pipeline 5 fases, CSV + transcripciones"]
    }
  }
}
```

El campo `validacion` es obligatorio y se completa con la salida de los scripts de verificación, no con auto-evaluación del LLM (invariante 0.4 de `SPEC.md`). Un punto solo se marca `true` si el script correspondiente pasó; si un script no pudo ejecutarse o falló, el punto se marca `false` con motivo en `puntos_fallidos` y el HTML se corrige antes de entregar. En el caso de **ninguna señal escala**, `fase4_output.json` se escribe con `mapeo_html: {}`, `validacion.n_senales: 0`, la advertencia "No se detectaron señales débiles en este análisis." y sin `reporte_ejecutivo.html` (SPEC.md sección 10).

El campo `mapeo_html` es obligatorio: mapea cada "Señal Débil N" del HTML al ID técnico que la origina (uno a uno, sin repetir IDs). `scripts/verificar_trazabilidad.py` verifica que el mapeo sea completo, sin IDs duplicados ni inexistentes y con la numeración secuencial.

**Gate final obligatorio (antes de cerrar Fase 4):**

Ejecutar el orquestador único:

```bash
python scripts/run_gate.py <directorio_proyecto> -o gate_report.json
```

Esto corre en orden:

1. `scripts/validar_esquema.py` sobre `fase0_output.json` … `fase4_output.json`.
2. `scripts/verificar_trazabilidad.py` sobre los 5 JSON + `reporte_ejecutivo.html`.
3. `scripts/validar_reporte.py` sobre el HTML + fase1-4.
4. `scripts/verificar_citas.py` sobre fase2/fase3 contra el corpus de transcripciones.
5. `scripts/verificar_numeros.py` sobre el dataset CSV + fase1-3.

Opciones útiles:

```bash
python scripts/run_gate.py <directorio_proyecto> -o gate_report.json \
  --corpus <carpeta_txt> \
  --dataset <dataset.csv> \
  --base-pct 0.388 \
  --absentes "termino1,termino2"
```

Si el entorno no dispone de Python, los scripts no son replicables y la Fase 4 **no puede marcar** ningún punto del checklist en `true`: se declara la ausencia de ejecución determinista en las advertencias, `validacion.ejecutada: false` y el reporte se entrega marcado **NO VERIFICADO**. 

**Integridad (fail-closed):** el único actor con autoridad para estampar `true` en `validacion` es `run_gate.py`, que al terminar reescribe el bloque con `ejecutada`, `gate_esquema`, `gate_trazabilidad`, `gate_reporte`, `gate_citas`, `gate_numeros`, `gate_veredicto` y `puntos_fallidos` basados en la salida real. El LLM **nunca** escribe booleanos de validación a mano; si por algún motivo se edita `fase4_output.json` para simular un `true`, la ejecución del gate la corrige y el entregable se considera **NO VERIFICADO** hasta que exista un `gate_report.json` real.

---

## Procedimiento

```
1. RECOLECTAR SEÑALES QUE ESCALAN
   De fase1_output.json: toda SD-CUANT-* con escala_a_fase4 = true.
   De fase2_output.json: toda SD-CUAL-* con escala_a_fase4 = true.
   De fase3_output.json: todo CRUCE-* con escala_a_fase4 = true.

   RE-VERIFICACIÓN DE PERTINENCIA (obligatoria, antes de numerar):
   NO confiar ciegamente en `escala_a_fase4: true`. Cada señal recolectada, y en especial los
   cruces de silencio cuantitativo (tipo `silencio_cuanti_explicado_por_cuali`), se re-evalúa
   contra la prueba de SPEC.md sección 2: si elimino la investigación, ¿el hallazgo sigue existiendo?
   Si un hallazgo describe el proceso de investigación (punto ciego del instrumento, variable
   no medida, sesgo de diseño de cuestionario), se DEMUEVE: no se numera como "Señal Débil N"
   y va al footer (Limitaciones), declarándose en advertencias. Las banderas
   `filtro_pertinencia_aplicado` y `silencio_de_instrumento_a_footer` del bloque `validacion`
   reflejan que esta revisión ocurrió y que ningún hallazgo de instrumento quedó numerado.

2. CONSOLIDAR Y CORTAR A MÁXIMO 5
   Unificar en una sola lista con IDs trazables.
   Si una señal de Fase 3 referencia señales de Fase 1 o 2 que NO escalaron,
   esas señales padre escalan automáticamente — salvo que la señal padre haya
   sido excluida por el Filtro 2 (clasificación `confirmacion`/`tension`):
   su evidencia puede integrarse como insumo del cruce, pero la señal no escala
   por sí misma.

   El reporte final debe contener **entre 3 y 5 señales si las hay** (SPEC.md sección 2).
   Con 1 o 2 señales genuinas que pasaron filtros, citas y corte de score, se publican tal
   cual y la escasez se declara en las `advertencias` de `fase4_output.json`; prohibido
   fabricar o re-clasificar señales para alcanzar el piso de 3. Si más de 5 señales escalan,
   aplicar el corte por score compuesto documentado en SPEC.md sección 5 y dejar las 5
   mejores. El desempate y la justificación del corte se registran en `advertencias` de
   `fase4_output.json`.

   **Estructura del corte (obligatoria cuando hay >5 candidatos):** el corte se documenta
   en un bloque estructurado `datos.corte` de `fase4_output.json`, no solo en prosa de
   advertencias:
   ```json
   "datos": {
     "corte": {
       "aplicado": true,
       "criterio": "score_compuesto",
       "score": { "SD-CUANT-001": { "severidad": 3, "sorpresa": 2, "robustez": 0.28, "score": 1.68 } },
       "desempate": { "aplicado": true, "regla": "co-referencia en cruces", "resultado": "SD-CUANT-001" },
       "excluidas": ["SD-CUANT-004"]
     }
   }
   ```
   `score = severidad × sorpresa × robustez` (SPEC sección 5). `scripts/validar_reporte.py`
   verifica que los mapeados sean el top-5 por score y que toda excluida esté declarada en
   `excluidas`.

3. ORDENAR EN SECUENCIA NARRATIVA
   Las señales se ordenan en una sola secuencia numérica (Señal Débil 1, Señal Débil 2, ...)
   que integre cuanti, cuali y cruces en un orden natural de lectura.
   Criterios de orden:
   - Primero las señales que redefinen el problema (las de mayor severidad y sorpresa).
   - Luego las que revelan matices o confirman patrones.
   - Finalmente las que abren preguntas nuevas.
   - No se agrupan por fase de origen (cuanti/cuali/cruce).

4. INFERIR TÍTULO
   De la pregunta de investigación o del contexto de los datos.
   Si no es posible: "Reporte de Señales Débiles".

5. GENERAR HTML (vía plantilla)
    El LLM **no escribe HTML a mano**. En su lugar:
      a) Construye el bloque `reporte` completo dentro de `fase4_output.json` (ver esquema arriba)
         con: título, fecha, pregunta_investigacion, resumen_ejecutivo (2-3 líneas),
         señales (cada una con los 5 campos + grafica opcional + heatmap_svg_path si aplica),
         decisiones (basado_en, exploracion, resultado_esperado) y footer (3 columnas).
      b) Si hay heatmap: generar `frecuencias.json` y ejecutar
         `python scripts/generar_heatmap.py frecuencias.json -o heatmap.svg`
         (igual que antes; el script ya calcula márgenes dinámicos).
         **Heatmap obligatorio ausente:** si Fase 0 mapeó `categoría_problema ×
         categoría_solución` (SPEC sección 6) y el heatmap NO se genera, se declara
         obligatoriamente en `advertencias` de `fase4_output.json` con el motivo
         (p. ej. "texto libre no codificable determinísticamente"). No basta con la
         justificación registrada en Fase 1: el reporte declara sus propias omisiones.
      c) Ejecutar el generador:
         `python scripts/generar_reporte.py <directorio_proyecto> -o reporte_ejecutivo.html`
         El script lee `fase4_output.json`, usa `scripts/plantilla_reporte.html` y produce el HTML
         autocontenido con Chart.js, SVG incrustado y CSS del design system.
      d) **Dejar `validacion: {}` como placeholder**; el gate (`run_gate.py`) la reescribe
         con los resultados reales (fail-closed). El LLM nunca estampa booleanos.

6. VALIDACIÓN POST-GENERACIÓN (gate final obligatorio)
    Ejecutar el orquestador único `scripts/run_gate.py` (checklist único de
    `SPEC.md` sección 12). El bloque `validacion` de `fase4_output.json`
    se completa con la salida real de los scripts, NO con auto-evaluación:
    el gate lo reescribe (fail-closed). **El LLM deja `validacion: {}`
    como placeholder y nunca estampa booleanos**.
    Si algún punto falla, corregir y re-verificar antes de entregar. Un gate
    que falla tras 3 reintentos detiene la entrega. Sin `gate_report.json`
    real, el reporte se declara NO VERIFICADO.
```

---

## Referencia rápida

Todo el contenido y formato del reporte (estructura de 2 secciones, los 5 campos de cada tarjeta de señal, reglas de decisiones estratégicas, whitelist de gráficos, especificación técnica del heatmap SVG, requisitos técnicos del HTML, contenido de header y footer) está definido en `SPEC.md` y es vinculante para esta fase. El aspecto visual (tipografía, paleta, componentes CSS) está definido en `references/design-system.md`.

**El HTML se produce con `scripts/generar_reporte.py` + `scripts/plantilla_reporte.html`** (no a mano). El LLM escribe el bloque `reporte` en `fase4_output.json`; el generador aplica la plantilla, incrusta heatmap SVG y gráficas Chart.js, y emite `reporte_ejecutivo.html`. Esta fase no repite las reglas de `SPEC.md` ni `design-system.md`: el generador las implementa.
