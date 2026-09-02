# Fase 3: Cruce Cuantitativo-Cualitativo

## Propósito

Poner a dialogar las señales de Fase 1 y Fase 2. Solo reportar interacciones con valor de ruptura: cuando la combinación de ambos mundos revela algo que ninguno de los dos mostró por separado.

## Input

- `fase1_output.json`: señales cuantitativas (`SD-CUANT-*`)
- `fase2_output.json`: señales cualitativas (`SD-CUAL-*`)
- `pregunta_investigacion`

## Output

`fase3_output.json`. Único archivo de salida.

Nota: `hipotesis_previas` no se repite en este archivo; se hereda de `fase0_output.json` (ver contrato en AGENTE.md). Los cambios de estado de una hipótesis se declaran en `advertencias`.

```json
{
  "fase": "fase-3-cruce",
  "timestamp": "2026-01-01T00:00:00",
  "pregunta_investigacion": "texto exacto",
  "advertencias": ["CRUCE-002 describe un punto ciego del instrumento (SPEC.md sección 2, prueba de pertinencia: no). No escala como señal débil; Fase 4 lo integra en el footer (Limitaciones): 'Sin variable de confianza percibida: la encuesta no mide el miedo a no ser suficiente ni la vergüenza'."],
  "redundancia": [
    {
      "aplicada": true,
      "senal_id": "CRUCE-001",
      "resultado": "escala | absorbida",
      "absorbida_por": null,
      "razon": "mecanismo independiente"
    }
  ],
  "datos": {
    "bloques": [
      {
        "id": "B1",
        "nombre": "Potenciación",
        "aplica": true,
        "expectativa_base": "Cada señal vive en su carril. Cuanti y cuali miden cosas distintas.",
        "expectativa_inferida": true,
        "resultado": "SEÑAL DÉBIL",
        "cruces": [
          {
            "id": "CRUCE-001",
            "fuente_origen": ["datos_cuantitativos.csv", "entrevista1.txt", "entrevista3.txt"],
            "tipo": "potenciacion",
            "senal_cuanti": {
              "id": "SD-CUANT-001",
              "dato": "62% otorga importancia máxima a conseguir empleo pero dedica 0 horas/semana a los talleres"
            },
            "senal_cuali": {
              "id": "SD-CUAL-003",
              "dato": "Metáforas de autoexclusión: 'los puestos no son para gente como yo', 'siempre me toca la fila de la noche'"
            },
            "tipo_potenciacion": "cualitativo explica cuantitativo",
            "sintesis": "El 62% no asiste no por falta de oferta sino por desconfianza. Las metáforas de 'estar afuera' revelan que el residente no se percibe como alguien que 'no quiere' capacitarse, sino como alguien que 'no cree' que el empleo sea para él.",
            "hipotesis_valor": "Si el municipio prioriza el acompañamiento y la orientación laboral individual (no solo más cursos), entonces la inscripción podría crecer, porque la señal integrada indica que el dolor real no es de oferta sino de confianza.",
            "severidad": "Crítica",
            "justificacion_severidad": "Redefine la propuesta de valor completa. No es un ajuste de comunicación; es un cambio de promesa.",
            "sorpresa": "Media",
            "justificacion_sorpresa": "Ninguna hipótesis previa del equipo conectaba la inacción del 62% con una necesidad de reconexión sensorial con la tierra. La expectativa es inferida por el agente (bloque con `expectativa_inferida: true`), por lo que la sorpresa tope es Media.",
            "validacion_pendiente": "Test de mensaje: 'Mirá cómo gente como vos consiguió trabajo' vs 'Inscribite a un curso'. Medir tasa de inscripción.",
            "escala_a_fase4": true,
            "clasificacion_hipotesis_previa": "señal débil",
            "hipotesis_previa_referenciada": null,
            "ancla": "expectativa_inferida",
            "exclusiones": ["El cruce no incluye a los 4 registros de baja calidad marcados en Fase 1"]
          }
        ],
        "grafica": null
      },
      {
        "id": "B2",
        "nombre": "Contradicción encuesta-vs-entrevista",
        "aplica": true,
        "expectativa_base": "Lo que la gente dice en una encuesta y lo que dice en una entrevista apunta en la misma dirección.",
        "expectativa_inferida": true,
        "resultado": "CONSISTENTE",
        "cruces": [],
        "grafica": null
      },
      {
        "id": "B3",
        "nombre": "Silencio cuantitativo explicado por cualitativo",
        "aplica": true,
        "expectativa_base": "Lo que no aparece en los números es ruido o ausencia de fenómeno.",
        "expectativa_inferida": true,
        "resultado": "SEÑAL DÉBIL",
        "cruces": [
          {
            "id": "CRUCE-002",
            "tipo": "silencio_cuanti_explicado_por_cuali",
            "ausencia_cuanti": "La encuesta no mide 'confianza percibida', 'vergüenza por falta de estudios' ni 'miedo a la entrevista'. No existe la variable.",
            "explicacion_cuali": {
              "id": "SD-CUAL-003",
              "dato": "3 de 5 entrevistados usan metáforas de autoexclusión sin que nadie les pregunte por confianza"
            },
            "conclusion": "El silencio cuantitativo no es ausencia del fenómeno; es ausencia de la pregunta correcta. La encuesta fue diseñada para medir barreras prácticas, pero el dolor real es de confianza y de identidad.",
            "hipotesis_valor": "Si la próxima encuesta incluye una dimensión de 'confianza percibida' como variable, entonces el modelo predictivo de inscripción podría mejorar, porque el silencio actual oculta la variable que mejor explica la inacción.",
            "severidad": "Alta",
            "justificacion_severidad": "Revela un punto ciego del instrumento que oculta una dimensión completa del problema.",
            "sorpresa": "Media",
            "justificacion_sorpresa": "El equipo diseñó la encuesta asumiendo que las barreras prácticas eran el universo completo del participante. La expectativa es inferida por el agente (bloque con `expectativa_inferida: true`), por lo que la sorpresa tope es Media.",
            "validacion_pendiente": "Piloto de encuesta con ítems de confianza percibida y autoeficacia.",
            "prueba_pertinencia": {
              "aplicada": true,
              "pregunta": "Si elimino la investigación, ¿el hallazgo sigue existiendo?",
              "respuesta": "no",
              "fenomeno_declarado": null,
              "razon": "El hallazgo es que la encuesta no mide una dimensión; sin encuesta no existe 'punto ciego de la encuesta'."
            },
            "escala_a_fase4": false,
            "clasificacion_hipotesis_previa": "señal débil",
            "hipotesis_previa_referenciada": null,
            "ancla": "expectativa_inferida",
            "motivo_no_escala": "filtro_pertinencia (SPEC.md seccion 2): describe un punto ciego del instrumento, no un fenómeno del objeto de estudio. Va al footer (Limitaciones)."
          }
        ],
        "grafica": null
      },
      {
        "id": "B4",
        "nombre": "Silencio cualitativo explicado por cuantitativo",
        "aplica": true,
        "expectativa_base": "Lo que no se menciona en entrevistas no es relevante.",
        "expectativa_inferida": true,
        "resultado": "CONSISTENTE",
        "cruces": [],
        "grafica": null
      }
    ],
    "resumen": {
      "n_bloques_aplicables": 4,
      "n_bloques_ejecutados": 4,
      "n_bloques_no_aplica": 0,
      "n_cruces_detectados": 2,
      "n_expectativas_confirmadas": 2,
      "cruces_que_escalan": ["CRUCE-001"]
    }
  }
}
```

---

## Procedimiento

### Declaración de cobertura

Antes de ejecutar, declarar qué tipos de hallazgo se buscarán:

| Tipo de hallazgo | Descripción |
|:---|:---|
| Potenciación | Cuanti y cuali revelan lo mismo desde ángulos distintos, o uno explica al otro |
| Contradicción encuesta-vs-entrevista | Los números dicen A, las historias dicen no-A |
| Silencio cuantitativo explicado por cualitativo | Lo que los números no muestran, el texto lo explica |
| Silencio cualitativo explicado por cuantitativo | Lo que el texto no menciona, los números lo revelan |

### Por cada tipo de hallazgo

1. **Potenciación:** buscar señales de Fase 1 y Fase 2 que apunten al mismo fenómeno. Evaluar si la combinación revela algo nuevo.
2. **Contradicción:** buscar señales que se opongan entre fuentes. Generar hipótesis que explique ambas.
3. **Silencio cuanti → cuali:** buscar temas presentes en entrevistas pero ausentes en la encuesta. Detectar el hallazgo y luego aplicar la prueba de pertinencia (SPEC.md sección 2): si el hallazgo es el punto ciego del instrumento ("la encuesta no mide X"), no escala y va al footer; si es un fenómeno del objeto de estudio que la entrevista revela ("X impulsa el comportamiento"), escala re-anclado sobre ese fenómeno.
4. **Silencio cuali → cuanti:** buscar patrones en los números que nadie menciona en entrevistas. ¿Es un tabú, un sesgo de deseabilidad social, o algo que simplemente no se verbaliza?

5. **Clasificar contra hipótesis previas:** cada cruce detectado debe clasificarse obligatoriamente como:
   - "confirmacion": el cruce refuerza una hipótesis que el equipo ya tenía.
   - "señal débil": el cruce revela un fenómeno nuevo que ninguna hipótesis previa anticipaba.
   - "tension": el cruce contradice directamente una hipótesis previa del equipo.

### Formato de cruce

```json
{
  "id": "CRUCE-001",
  "fuente_origen": ["datos_cuantitativos.csv", "entrevista1.txt", "entrevista3.txt"],
  "tipo": "potenciacion | contradiccion | silencio_cuanti_explicado_por_cuali | silencio_cuali_explicado_por_cuanti",
  "tipo_cruce": "intra_poblacion | transpoblacional",
  "naturaleza_cruce": "extrapolacion | convergencia | null (obligatorio si tipo_cruce = transpoblacional)",
  "poblaciones": { "encuesta": { "nombre": "población general del municipio", "n": 115 }, "entrevistas": { "nombre": "participantes de los talleres", "n": 5 } },
  "senal_cuanti": { "id": "...", "dato": "..." },
  "senal_cuali": { "id": "...", "dato": "..." },
  "sintesis": "una línea que integre ambos hallazgos",
  "hipotesis_valor": "Si [cambio], entonces [resultado], porque [mecanismo].",
  "severidad": "Baja | Media | Alta | Crítica",
  "justificacion_severidad": "...",
  "sorpresa": "Baja | Media | Alta",
  "justificacion_sorpresa": "...",
  "validacion_pendiente": "...",
  "exclusiones": ["El cruce no incluye a los 4 registros de baja calidad marcados en Fase 1"],
  "escala_a_fase4": true,
  "prueba_pertinencia": {
    "aplicada": true,
    "pregunta": "Si elimino la investigación, ¿el hallazgo sigue existiendo?",
    "respuesta": "sí | no",
    "fenomeno_declarado": "frase que describe el fenómeno del objeto de estudio (null si respuesta = no)",
    "razon": "una línea de justificación del veredicto"
  },
  "motivo_no_escala": null,
  "clasificacion_hipotesis_previa": "confirmacion | señal débil | tension",
  "hipotesis_previa_referenciada": "texto de la hipótesis previa o null",
  "ancla": "hipotesis_usuario | expectativa_inferida",
  "mecanismo_nuevo": null
}
```

---

## Cierre de Fase 3 (obligatorio, antes de Fase 4)

Antes de consolidar el reporte, ejecutar la verificación de citas sobre `fase2_output.json` y `fase3_output.json` (SPEC sección 13). **Este paso no se salta**: es lo que impide que las citas se verifiquen "al final" cuando el HTML ya existe y corregirlas obliga a re-correr fases.

```bash
python scripts/verificar_citas.py fase2_output.json fase3_output.json --corpus <transcripciones>/
```

- `NO_ENCONTRADA`: corregir la cita a verbatim o eliminarla; no avanzar con citas no verificadas.
- `PARAFRASIS_APROXIMADA` / `PARAFRASIS_NO_SOPORTADA`: **el agente (LLM-juez) las resuelve aquí**, leyendo las ventanas que el script imprime. Si la ventana respalda la cita → registra el veredicto en `juicio.json` (se pasará al gate con `--juicio`); si no → corrige la cita o la ubicación en el JSON **antes** de Fase 4.
- `SIN_ANCLA`: citas entre comillas sin ancla de ubicación — avisos no bloqueantes; anclarlas (`E<ID>/L<ini>`) o descartarlas antes del reporte.
- `CONTRADICCION` de ausencias: corregir o descartar la señal.

Resolver aquí evita re-generar el HTML: se genera una sola vez. El gate final (`run_gate.py --juicio juicio.json`) re-verifica y escribe el bloque `validacion`.

---

## Reglas

- Solo reportar interacciones con valor de ruptura. No re-describir lo ya dicho en Fase 1 o 2.
- No reportar coincidencias descriptivas sin valor de ruptura.
- Si una señal de Fase 3 referencia señales de Fase 1 o 2 que no escalaron, esas señales padre escalan automáticamente — salvo que la señal padre haya sido excluida por el Filtro 2 (clasificación `confirmacion`/`tension`): en ese caso su evidencia puede integrarse como insumo del cruce, pero la señal no escala por sí misma.
- Los IDs usan prefijo `CRUCE-`. En el reporte final se simplificarán a "Señal Débil N".
- **Trazabilidad de IDs (obligatoria):** todo `senal_cuanti.id` y `senal_cuali.id` referenciado por un cruce DEBE existir en `fase1_output.json` / `fase2_output.json` respectivamente. No se referencia un ID que la fase de origen no emitió (prohibido referenciar señales fantasma). `scripts/verificar_trazabilidad.py` verifica esto sobre los JSON.
- **SSoT en cruces:** los números citados en `senal_cuanti.dato`, `senal_cuali.dato` y `sintesis` se copian del JSON de origen sin recalcularlos ni reescribirlos. Si dos fases discrepan sobre la misma cifra, manda la de menor fase y se corrige el resto (SPEC.md invariante 0.2). `scripts/verificar_numeros.py` detecta fracciones discrepantes entre fases.
- **Filtro de pertinencia obligatorio antes de escalar (SPEC.md sección 2):** todo cruce, y en especial los de tipo `silencio_cuanti_explicado_por_cuali`, debe pasar la prueba del objeto de estudio antes de marcar `escala_a_fase4: true`: *si elimino la investigación, ¿el hallazgo sigue existiendo?*
  - **No** → el hallazgo describe un punto ciego del instrumento o una característica del proceso de investigación (variable no medida, ítem mal diseñado, sesgo muestral). NO escala: `escala_a_fase4: false` y `motivo_no_escala: "filtro_pertinencia"`. Se declara en `advertencias` para que Fase 4 lo integre en el footer (Limitaciones), nunca como "Señal Débil N".
  - **Sí** → el hallazgo describe un fenómeno del objeto de estudio que existe con o sin la investigación. Puede escalar, pero **re-anclado sobre el fenómeno**: la `sintesis` y la `hipotesis_valor` describen el comportamiento del usuario/mercado/producto; el déficit del instrumento se menciona solo como mecanismo explicativo, nunca como el hallazgo en sí.
  - **Regla operativa para cruces de silencio:** si al quitar la encuesta el hallazgo deja de existir (ej. "la encuesta no midió diferenciación percibida"), es un hallazgo del instrumento → footer. Si al quitar la encuesta el hallazgo sigue en pie porque lo sostiene la evidencia cualitativa y describe el mundo (ej. "la diferenciación percibida impulsa el abandono"), escala como fenómeno.
  - **Pertinencia necesaria pero no suficiente:** pasar el filtro de pertinencia NO anula el blindaje de cruces transpoblacionales. Un cruce transpoblacional que describe un fenómeno real aun así **no escala solo** (`escala_a_fase4: false`) y se declara como hipótesis de validación en `advertencias`.
  - Esta regla es el mismo filtro 1 del Orden de Filtrado de AGENTE.md (cláusula "del instrumento de medición"), re-aplicado en Fase 3 sobre el resultado del cruce. El campo `prueba_pertinencia` del JSON documenta la prueba y su veredicto.

### Blindaje de cruces transpoblacionales

Cuando Fase 0 declara que las poblaciones de la encuesta y de las entrevistas **no** provienen del mismo universo (`datos.poblaciones` de Fase 0; regla 12 de AGENTE.md), todo cruce entre fuentes se marca `tipo_cruce: "transpoblacional"` y queda sujeto a estas restricciones. El discriminador **no es la declaración de población sino la síntesis**: depende de si el fenómeno se sostiene en cada población por sí sola o solo se sostiene transfiriendo una medición entre poblaciones. Por eso todo cruce transpoblacional declara `naturaleza_cruce`:

- **`"extrapolacion"`** — la síntesis solo se sostiene transfiriendo una medición de una población a la otra (ej. usar el % de una medición de la encuesta general para concluir sobre los participantes de los talleres).
  - Nunca escala: `escala_a_fase4: false`; rol de hipótesis a validar, declarada en `advertencias`.
  - Cap de severidad: `Alta` (nunca `Crítica`).
  - Nota obligatoria en `exclusiones`: "Cruce entre poblaciones distintas (encuesta ≠ entrevistas); la síntesis es una hipótesis de validación, no un hallazgo transferible entre poblaciones."

- **`"convergencia"`** — el fenómeno se sostiene en cada población por sí sola, sin depender del cruce; se replica entre universos distintos. Avanza a Fase 4 descrito en la síntesis como "convergencia entre poblaciones", pero **siempre con `escala_a_fase4: false`**: el invariante de clasificación prohíbe `escala_a_fase4: true` en todo cruce transpoblacional (inferencia entre universos distintos).
  - **Señal intra-población previa exigida:** debe existir en `fase1_output.json`/`fase2_output.json` una señal ya emitida que sustente el fenómeno en CADA población (o un bloque cuanti/cuali con evidencia y N propios por población). Si alguna población carece de señal propia, el cruce cae a `"extrapolacion"`.
  - **Piso de N por población (cada señal declara `poblacion` y `n`):** la regla de piso de N (SPEC.md sección 5) se aplica por población, no al total combinado:
    - señales cuantitativas → `max(30, 10% del N de su población)` con el `n` de `datos.poblaciones.<universo>` de Fase 0;
    - señales cualitativas → `n >= 2` entrevistas que sostienen el patrón (el N de una muestra cualitativa, no el de registros).
  - **La síntesis no atribuye:** describe el fenómeno común; NO se atribuye a la población B una métrica medida solo en la A.
  - Cap de severidad: `Alta` (nunca `Crítica`): la convergencia entre universos distintos tiene una capa de inferencia extra al afirmar lo común entre universos.
  - Co-referencia de señales intra-población obligatoria: las patas del cruce (`senal_cuanti`/`senal_cuali`) la satisfacen al citar las señales de cada población. `poblaciones` declara el nombre por universo (para verificación a máquina).

**Verificación a máquina (obligatoria):** `scripts/verificar_trazabilidad.py` audita los cruces transpoblacionales de Fase 3:
- si `naturaleza_cruce = "convergencia"` → existen señales intra-población referenciadas y cada una declara `n` propio (estructurado) que alcanza su piso: cuantitativas, `max(30, 10% del N de la población)` de Fase 0; cualitativas, `>= 2` entrevistas. Los nombres de población se contrastan contra `datos.poblaciones` de Fase 0 por **substring matching (nunca igualdad exacta)**;
- si `naturaleza_cruce = "extrapolacion"` → `escala_a_fase4: false` + la nota exacta en `exclusiones`;
- ningún cruce transpoblacional (cualquiera sea su naturaleza) con `severidad = "Crítica"`. Los errores bloquean el veredicto del gate.

**Excepción:** un cruce que integra cuanti y cuali **dentro de la misma población** (por ejemplo, ambas fuentes provienen de usuarios del mismo producto) no es transpoblacional y escala con el formato normal.

### Calibración y verificación

- `severidad` y `sorpresa` se puntúan contra la rúbrica de SPEC.md sección 5, con el campo `ancla` declarado. Si el ancla es `expectativa_inferida`, la sorpresa tope es Media.
- Las citas que integran un cruce se verifican con `scripts/verificar_citas.py` (SPEC.md sección 13) igual que las de Fase 2. Si no son verbatim, aplica la misma verificación de paráfrasis anclada (cobertura ≥ 0.6 auto-aprueba; bandas media/baja las resuelve el agente como juez en el cierre de Fase 3, registrando `juicio.json` para pasarlo al gate con `--juicio`; la confirmación humana es opcional).
- **Formato de citas inline (contrato con `verificar_citas.py`):** las citas en prosa de `senal_cuali.dato`, `senal_cuanti.dato` y `sintesis` usan el mismo formato que en Fase 2 — `E<ID>/L<ini>[-L<fin>]: '<texto>'` (canónico, ubicación antes) o `'<texto>' (E<ID>/L<ini>[-L<fin>])` / `'<texto>' [L<ini>[-L<fin>]]` / `'<texto>' [min <n>]` (ubicación después). Comillas dobles rectas, dobles tipográficas o simples tipográficas; la comilla simple recta solo como delimitador si va pegada al ancla de ubicación. Sin ancla de ubicación: `[no localizable]` (el script la reporta `NO_ENCONTRADA`).
