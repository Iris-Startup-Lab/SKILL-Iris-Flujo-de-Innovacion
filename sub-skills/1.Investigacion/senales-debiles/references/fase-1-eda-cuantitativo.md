# Fase 1: EDA Cuantitativo

## Propósito

Detectar señales débiles en los datos numéricos mediante un motor de juego sistemático: generar expectativas, diseñar cruces que puedan romperlas, ejecutarlos, y evaluar si lo observado es consistente o es una señal débil.

## Input

`fase0_output.json` con:
- `roles`: mapeo de columnas a los 6 roles semánticos
- `dataset_enriquecido.path`: ruta al CSV con categorías codificadas y calidad de respuesta marcada
- `pregunta_investigacion`
- `advertencias`

## Output

`fase1_output.json`. Único archivo de salida. Contiene todos los datos que Fase 4 necesita para renderizar el reporte HTML: señales, datos crudos para gráficas Chart.js, y tablas de infraestructura.

### Borrador automático

El script `scripts/fase1_analisis.py` genera un borrador determinista (`fase1_borrador.json`) a partir del CSV enriquecido y `fase0_output.json`:

```bash
python scripts/fase1_analisis.py <csv_enriquecido> <fase0_output.json> -o fase1_borrador.json
```

El borrador incluye los bloques B0-B7, conteos, tasas base, alertas, datos para gráficas y cálculos adicionales (Gini, correlaciones Spearman, Cramér's V). El LLM debe revisar cada hallazgo, decidir si escala, ajustar severidad/sorpresa y redactar `expectativa_rota` e `hipotesis_valor`.

Nota: `hipotesis_previas` no se repite en este archivo; se hereda de `fase0_output.json` (ver contrato en AGENTE.md). Los cambios de estado de una hipótesis se declaran en `advertencias`.

```json
{
  "fase": "fase-1-eda-cuantitativo",
  "timestamp": "2026-01-01T00:00:00",
  "pregunta_investigacion": "texto exacto",
  "advertencias": [],
  "redundancia": [
    {
      "aplicada": true,
      "senal_id": "SD-CUANT-001",
      "resultado": "escala | absorbida",
      "absorbida_por": null,
      "razon": "mecanismo independiente"
    }
  ],
  "datos": {
    "infraestructura": {
      "descriptivos": [
        {
          "variable": "importancia_alimentacion",
          "rol": "intensidad_valor",
          "media": 4.3,
          "mediana": 5.0,
          "moda": 5,
          "desv_estandar": 0.9,
          "min": 1,
          "max": 5,
          "n": 120,
          "n_faltantes": 0
        }
      ],
      "faltantes": [
        {
          "variable": "horas_semana_huerto",
          "n_faltantes": 5,
          "pct_faltantes": 4.2,
          "clasificacion": "no disponible",
          "patron": "sin patrón discernible con otras variables",
          "accion": "excluir del análisis de esa variable, N efectivo=115"
        }
      ],
      "outliers": {
        "criterio": "IQR 1.5",
        "n_total": 3,
        "columna": "posible_anomalia"
      },
      "duplicados": {
        "n_exactos": 0,
        "n_parciales": 0,
        "decision": "no aplica"
      },
      "calidad_respuesta": {
        "baja_calidad": 4,
        "total": 4,
        "accion": "marcados en calidad_respuesta, no eliminados"
      }
    },
    "bloques": [
      {
        "id": "B1",
        "nombre": "Tensión intensidad-esfuerzo",
        "aplica": true,
        "roles_requeridos": ["intensidad_valor", "esfuerzo_accion"],
        "expectativa_base": "A mayor importancia de la alimentación saludable, mayor participación en el huerto comunitario",
        "expectativa_inferida": true,
        "cruce": "importancia_alimentacion × horas_semana_huerto, color por tipo_barrera_cat",
        "resultado": "CONTRADICCIÓN",
        "senales": [
          {
            "id": "SD-CUANT-001",
            "fuente_origen": ["encuesta.csv"],
            "tipo": "Multivariante",
            "dato": "62% (71/115) otorga importancia máxima (5) a la alimentación saludable pero dedica 0 horas/semana al huerto comunitario",
            "contexto": "N=115, muestra completa, todos los barrios",
            "expectativa_rota": "Esperábamos que a mayor importancia de la alimentación saludable, mayor participación en el huerto. Observamos un cluster mayoritario (62%) con máxima importancia y cero acción.",
            "severidad": "Alta",
            "justificacion_severidad": "Afecta la variable central de la pregunta de investigación: si la importancia no predice participación, el modelo mental del programa está equivocado",
            "sorpresa": "Alta",
            "justificacion_sorpresa": "Contradice la creencia fundamental de que el residente no participa porque no le importa la alimentación saludable",
            "hipotesis_valor": "Si se reduce la fricción de la primera visita (sesión guiada de 30 min sin compromiso), entonces la tasa de participación podría aumentar, porque la señal indica que la barrera no es motivación sino fricción inicial.",
            "validacion_pendiente": "Medir si una sesión introductoria guiada incrementa la tasa de primera visita",
            "robustez": "71 de 115 registros (62%). Generalizable a la muestra.",
            "escala_a_fase4": true,
            "clasificacion_hipotesis_previa": "confirmacion | señal débil | tension",
            "hipotesis_previa_referenciada": "texto de la hipótesis previa contra la que se clasifica, o null si es señal débil nueva",
            "exclusiones": ["Se excluyen 4 registros marcados como baja calidad de respuesta", "N efectivo=115 (5 faltantes en variable horas_semana_huerto)"]
          }
        ],
        "grafica": {
          "tipo": "heatmap",
          "datos_frecuencias": {
            "eje_x": ["Falta de tiempo", "Lejanía", "No sé cómo"],
            "eje_y": ["App de recetas", "Comprar en supermercado", "Ninguna"],
            "eje_x_titulo": "Categoría problema",
            "eje_y_titulo": "Categoría solución",
            "valores": [
              [18, 3, 8],
              [12, 15, 2],
              [5, 4, 10]
            ]
          },
          "descripcion": "Heatmap: cruce categoría_problema × categoría_solución. Intensidad de color = frecuencia. Se entregan los datos como matriz de frecuencias en el JSON; Fase 4 lo renderiza como SVG inline (SPEC.md § 6). Nunca se usa chartjs-chart-matrix."
        }
      }
    ],
    "resumen": {
      "n_bloques_aplicables": 7,
      "n_bloques_ejecutados": 7,
      "n_bloques_no_aplica": 0,
      "n_senales_detectadas": 3,
      "n_expectativas_confirmadas": 4,
      "senales_que_escalan": ["SD-CUANT-001", "SD-CUANT-002", "SD-CUANT-003"]
    }
  }
}
```

---

## Procedimiento

### Bloque 0: Infraestructura mínima

No produce señales. Solo deja el dataset listo y documentado.

1. **Descriptivos:** media, mediana, moda, desv. estándar, min, max, N, N faltantes por variable numérica. Sin narrativa.
2. **Faltantes:** contar, mapear co-ocurrencia, clasificar (No aplica / No disponible / No declarado). Sin imputar.
3. **Outliers:** marcar en columna `posible_anomalia` (IQR 1.5 o Z-score >3). No eliminar.
4. **Duplicados:** identificar exactos y parciales. Documentar decisión.
5. **Calidad de respuesta:** marcar respondientes con ≥70% ítems Likert idénticos consecutivos o respuestas abiertas monosílabas. No eliminar.

### Bloques generadores B1–B7

Cada bloque sigue el mismo loop:

```
1. Leer expectativa base (según sentido común del dominio)
2. Diseñar cruce usando roles que pueda romperla
3. Ejecutar el cruce
4. Evaluar: ¿consistente o señal débil?
5. Si es señal débil → documentar con formato estándar
6. Clasificar contra hipótesis previas:
   - Si la señal refuerza una hipótesis previa → "confirmacion"
   - Si la señal revela algo nuevo no anticipado → "señal débil"
   - Si la señal contradice una hipótesis previa → "tension"
7. Si es consistente → documentar como "expectativa confirmada"
```

Los 7 bloques:

| Bloque | Tipo de cruce | Roles necesarios | Pregunta guía |
|---|---|---|---|
| **B1** | Tensión intensidad-esfuerzo | Intensidad + Esfuerzo | ¿La gente actúa sobre lo que dice que le importa? |
| **B2** | Desacople problema-solución | Categoría problema + Categoría solución | ¿Resuelven como esperaríamos? **Visualización obligatoria: heatmap en SVG inline.** Si las variables `categoría_problema` y `categoría_solución` están mapeadas en Fase 0, el heatmap es output obligatorio de esta fase, sin excepción. Si las respuestas son texto libre, primero se categorizan en buckets (máximo 8 por eje) y luego se genera el heatmap. El heatmap se entrega como datos crudos (matriz de frecuencias) en el JSON; Fase 4 lo renderiza como SVG inline. |
| **B3** | Co-ocurrencia inesperada | Categoría problema + Categoría solución | ¿Hay combinaciones que no deberían existir y existen? |
| **B4** | Segmentos invertidos | Segmento + Intensidad (o Esfuerzo) | ¿El segmento que creemos prioritario realmente lo es? |
| **B5** | Outliers de comportamiento | Intensidad + Esfuerzo | ¿Hay casos extremos que revelan un patrón no obvio? |
| **B6** | Ausencia estructurada | Cualquier variable + missingness | ¿El silencio tiene patrón? ¿Quiénes no responden qué? |
| **B7** | Tendencia temporal contra-intuitiva | Tiempo + cualquier numérica | ¿La dirección del cambio es la esperada? |

**Reglas de ejecución de bloques:**

- El orden no es fijo. Ejecuta según disponibilidad de roles.
- Si un rol requerido no está mapeado, el bloque se marca `"aplica": false` con justificación.
- Las expectativas base se infieren del sentido común del dominio si el usuario no las proporciona. Cuando son inferidas, se marca `"expectativa_inferida": true`.
- Cada bloque que detecta señal débil debe incluir un objeto `grafica` con datos en formato Chart.js.

### Formato de señal débil cuantitativa

```json
{
  "id": "SD-CUANT-001",
  "fuente_origen": ["encuesta.csv"],
  "tipo": "Univariante | Multivariante | Temporal | De silencio",
  "dato": "valor exacto con N efectivo",
  "contexto": "N, segmento, condición",
  "expectativa_rota": "Esperábamos X, observamos Y",
  "severidad": "Baja | Media | Alta | Crítica",
  "justificacion_severidad": "por qué, según implicación estratégica",
  "sorpresa": "Baja | Media | Alta",
  "justificacion_sorpresa": "por qué, según distancia a premisas del equipo",
  "hipotesis_valor": "Si [cambio], entonces [resultado], porque [mecanismo].",
  "validacion_pendiente": "qué medir para confirmar o descartar",
  "robustez": "N que la sostienen. ¿Generalizable o caso único?",
  "exclusiones": ["Se excluyen 4 registros marcados como baja calidad de respuesta", "N efectivo=115 (5 faltantes en variable horas_semana_huerto)"],
  "escala_a_fase4": true,
  "clasificacion_hipotesis_previa": "confirmacion | señal débil | tension",
  "hipotesis_previa_referenciada": "texto de la hipótesis previa contra la que se clasifica, o null si es señal débil nueva",
  "ancla": "hipotesis_usuario | expectativa_inferida"
}
```

---

## Reglas

- No generes archivos CSV ni PNG. Todo viaja en el JSON.
- No reportes problemas del instrumento como señales débiles.
- Toda estadística con N efectivo. Todo porcentaje con numerador/denominador.
- Si un bloque no justifica gráfica, `grafica` es `null`.
- Los IDs usan prefijo `SD-CUANT-`. En el reporte final se simplificarán a "Señal Débil N".
- **Regla de heatmap:** cuando un bloque cruza dos variables categóricas con 3+ niveles cada una (ej. B2: categoría_problema × categoría_solución), el heatmap es la visualización obligatoria. Se entregan los datos como matriz de frecuencias en el JSON; Fase 4 lo renderiza como SVG inline. El scatter solo se usa cuando al menos una variable es continua.
- **Calibración:** `severidad` y `sorpresa` se puntúan contra la rúbrica de SPEC.md § 5, con el campo `ancla` declarado (`hipotesis_usuario` o `expectativa_inferida`). Si el ancla es `expectativa_inferida`, la sorpresa tope es Media.
- **Regla de tasa base (obligatoria):** toda señal basada en la tasa de un subgrupo se compara contra la tasa base del mismo fenómeno en la población total. Si la tasa del subgrupo no difiere materialmente de la base (diferencia ≤ ~5 puntos porcentuales, o sin evidencia de que la diferencia sea real), el bloque se clasifica `CONSISTENTE`, no señal débil. Ambas tasas se declaran en `dato` con numerador y denominador explícitos (SPEC.md § 5). Un ejemplo: "39.0% (48/123) del segmento X hace Y" con base 38.8% (123/317) es la misma tasa con ruido; no es señal.
- **SSoT (fuente única de verdad):** los conteos de infraestructura y de señales se calculan con Python contra el CSV; el JSON cita el resultado del cálculo, nunca cifras inventadas. `scripts/verificar_numeros.py` recalcula los conteos y los compara contra este JSON (SPEC.md § 0.2).
