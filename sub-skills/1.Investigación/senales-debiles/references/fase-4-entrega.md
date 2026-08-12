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

Ver `SPEC.md` § 9 (Manejo de inputs faltantes en Fase 4). Regla general: el reporte NUNCA debe fallar por falta de un input; siempre se genera con lo disponible, declarando las ausencias en advertencias.

## Output

Un solo archivo: `reporte_ejecutivo.html`.

Además, Fase 4 produce un JSON de cierre (`fase4_output.json`) con el resultado de la validación, siguiendo el checklist único de `SPEC.md` § 10:

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
  "validacion": {
    "ejecutada": true,
    "estructura_2_secciones": true,
    "n_senales": 5,
    "senales_en_rango": true,
    "n_decisiones": 3,
    "decisiones_en_rango": true,
    "badges_ausentes": true,
    "numeracion_correcta": true,
    "decisiones_referencian_senales": true,
    "tono_exploratorio": true,
    "sin_temporalidad": true,
    "ancla_declarada": true,
    "fallback_respetado": true,
    "design_system_aplicado": true,
    "graficas_en_tarjetas": true,
    "heatmap_svg_presente": true,
    "footer_sin_trazabilidad": true,
    "senales_escalan_correctas": true,
    "exclusion_clasificacion_respetada": true,
    "sin_ids_tecnicos": true,
    "citas_verificadas": true,
    "filtro_pertinencia_aplicado": true,
    "silencio_de_instrumento_a_footer": true,
    "puntos_fallidos": []
  }
}
```

El campo `validacion` es obligatorio y se completa con la salida de los scripts de verificación, no con auto-evaluación del LLM (invariante 0.4 de `SPEC.md`). Un punto solo se marca `true` si el script correspondiente pasó; si un script no pudo ejecutarse o falló, el punto se marca `false` con motivo en `puntos_fallidos` y el HTML se corrige antes de entregar.

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

Si el entorno no dispone de Python, los scripts se replican manualmente y se declara la ausencia de ejecución determinista en las advertencias.

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
   contra la prueba de SPEC.md § 2: si elimino la investigación, ¿el hallazgo sigue existiendo?
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

   El reporte final debe contener **entre 3 y 5 señales** (SPEC.md § 2). Si más
   de 5 señales escalan, aplicar el corte por score compuesto documentado en
   SPEC.md § 5 y dejar las 5 mejores. El desempate y la justificación del corte
   se registran en `advertencias` de `fase4_output.json`.

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

5. GENERAR HTML
   Aplicar la estructura de secciones y campos de `SPEC.md` §§ 1-8, y el
   aspecto visual de `references/design-system.md`.

   LOGO OFICIAL (obligatorio): embebe el logo de IRIS en base64 en el header
   (`.logo-chip`), obteniendo el data URI con:
     `python scripts/logo_base64.py assets/logo.png`
   y pegándolo como `src="data:image/png;base64,..."` (ver design-system.md § 3.1).

   EL HEATMAP SVG SE GENERA CON `scripts/generar_heatmap.py`, NUNCA A MANO.
   Prohibido dibujar el SVG del heatmap manualmente o con un script ad-hoc:
   la geometría (márgenes, viewBox, rotación de etiquetas) es propensa a
   recortes, y el encoding a corrupciones si se redirige stdout. El flujo es:
     a) Escribir `frecuencias.json` con la estructura esperada por el script
        (ver docstring de `scripts/generar_heatmap.py`).
     b) Ejecutar con salida a archivo UTF-8:
        `python scripts/generar_heatmap.py frecuencias.json -o heatmap.svg`
        (NO usar redirección `>`: en Windows re-codifica UTF-8 y corrompe
        tildes/acentos; `-o` escribe el archivo con encoding UTF-8 explícito).
     c) Verificar que el viewBox resultante no recorta ninguna etiqueta
        (el script ya calcula `margin_bottom` dinámicamente, pero se revisa
        visualmente el SVG o se inspeccionan las coordenadas si hay dudas).
     d) Incrustar el contenido del SVG generado en la tarjeta de la señal
        correspondiente, respetando `SPEC.md` § 6 y `design-system.md` § 3.5.

6. VALIDACIÓN POST-GENERACIÓN (gate final obligatorio)
   Ejecutar el checklist único de `SPEC.md` § 10 y los cuatro scripts de
   verificación (ver arriba). El bloque `validacion` de `fase4_output.json`
   se completa con la salida real de los scripts, no con auto-evaluación.
   Si algún punto falla, corregir y re-verificar antes de entregar. Un gate
   que falla tras 3 reintentos detiene la entrega.
```

---

## Referencia rápida

Todo el contenido y formato del reporte (estructura de 2 secciones, los 5 campos de cada tarjeta de señal, reglas de decisiones estratégicas, whitelist de gráficos, especificación técnica del heatmap SVG, requisitos técnicos del HTML, contenido de header y footer) está definido en `SPEC.md` y es vinculante para esta fase. El aspecto visual (tipografía, paleta, componentes CSS) está definido en `references/design-system.md`. Esta fase no repite esas reglas: consulta ambos archivos antes de generar el HTML.
