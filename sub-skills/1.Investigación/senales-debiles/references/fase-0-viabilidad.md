# Fase 0: Viabilidad y Carga

## Propósito

Evaluar si la pregunta de investigación es clara y accionable, mapear las columnas del dataset al sistema de 6 roles semánticos, ejecutar lectura exploratoria de respuestas abiertas, y producir un JSON estructurado que alimenta Fase 1 y Fase 2. Esta fase **no se detiene** por falta de datos cuantitativos o cualitativos: ejecuta con lo disponible y declara las ausencias para que las fases siguientes sepan qué bloques marcar como `[no aplica]`.

## Input

- `encuesta.csv` — dataset tabular con respuestas de encuesta (preguntas cerradas y abiertas). Opcional si solo hay cualitativos.
- `transcripciones/*.txt` — archivos de transcripción de entrevistas. Opcional si solo hay cuantitativos.
- Pregunta de investigación (provista por el usuario en lenguaje natural)

## Output

Archivo `fase0_output.json` con la siguiente estructura:

```json
{
  "fase": "fase-0-viabilidad",
  "timestamp": "2026-01-01T00:00:00",
  "pregunta_investigacion": "texto exacto de la pregunta",
  "hipotesis_previas": [
    {
      "hipotesis": "texto de la hipótesis",
      "fuente": "contexto inicial del usuario",
      "estado": "activa"
    }
  ],
  "advertencias": [],
  "datos": {
    "viabilidad": {
      "decision": "FLUIR",
      "motivo_detencion": null,
      "datos_cuantitativos": {
        "disponible": true,
        "n_registros": 120,
        "n_variables_numericas": 5,
        "n_variables_categoricas": 3,
        "n_variables_texto": 2,
        "archivo": "encuesta.csv"
      },
      "datos_cualitativos": {
        "disponible": true,
        "n_documentos": 5,
        "formato": "transcripcion",
        "archivos": ["entrevista1.txt", "entrevista2.txt", "entrevista3.txt", "entrevista4.txt", "entrevista5.txt"]
      },
      "pregunta_clara": {
        "sujeto_definido": true,
        "variable_dependiente_implicita": true,
        "es_actionable": true,
        "texto_exacto": "¿Por qué los residentes no participan en los huertos urbanos comunitarios a pesar de expresar interés en alimentación saludable?"
      },
      "estrategia_muestreo": "muestra completa, N=120",
      "faltantes_declarados": {
        "cuantitativo": false,
        "cualitativo": false
      }
    },
    "pre_registro": {
      "expectativas_problema": ["texto de lo que espero que sea la barrera o causa principal"],
      "expectativas_segmentos": ["texto de qué grupos creo que se comportan distinto y cómo"],
      "expectativas_relaciones": ["texto de qué variables creo que correlacionan y en qué dirección"],
      "expectativas_discurso": ["texto de qué temas creo que dominarán las entrevistas"]
    },
    "roles": {
      "intensidad_valor": ["importancia_alimentacion", "satisfaccion_barrio"],
      "esfuerzo_accion": ["horas_semana_huerto", "gasto_mensual_verduras"],
      "categoria_problema": ["tipo_barrera"],
      "categoria_solucion": ["solucion_actual", "herramienta_usada"],
      "segmento_perfil": ["tiene_huerto", "tipo_barrio", "tamano_hogar"],
      "tiempo": ["fecha_encuesta"]
    },
    "roles_no_mapeados": {
      "intensidad_valor": false,
      "esfuerzo_accion": false,
      "categoria_problema": false,
      "categoria_solucion": false,
      "segmento_perfil": false,
      "tiempo": true
    },
    "dataset_enriquecido": {
      "path": "encuesta_enriquecida.csv",
      "n_registros_original": 120,
      "n_registros_final": 120,
      "columnas_originales": ["id", "importancia_alimentacion", "horas_semana_huerto", "tipo_barrera", "solucion_actual", "respuesta_abierta"],
      "columnas_nuevas": ["tipo_barrera_cat", "solucion_actual_cat"],
      "calidad_respuesta": { "baja_calidad": 4, "total_marcados": 4 }
    },
    "codificacion_ligera": {
      "tipo_barrera_cat": {
        "variable_original": "tipo_barrera",
        "criterio": "respuesta corta (1-10 palabras), tema predecible",
        "categorias": {
          "falta_tiempo": { "n": 35, "ejemplos": ["no tengo tiempo", "trabajo todo el día"] },
          "lejania": { "n": 22, "ejemplos": ["queda lejos", "no hay en mi colonia"] },
          "no_se_como": { "n": 20, "ejemplos": ["no sé sembrar", "se me mueren las plantas"] },
          "falta_interes": { "n": 15, "ejemplos": ["no me interesa", "prefiero comprar"] },
          "espacio": { "n": 12, "ejemplos": ["no tengo dónde", "mi depa es chico"] },
          "otro": { "n": 8, "ejemplos": ["inseguridad", "el agua es cara"] },
          "no_clasificable": { "n": 8, "ejemplos": ["no sé", "varios"] }
        },
        "total_clasificados": 112,
        "total_no_clasificables": 8
      }
    },
    "transcripciones": {
      "n_total": 5,
      "detalle": [
        { "archivo": "entrevista1.txt", "participante_id": "E1", "duracion_minutos": 42, "n_intervenciones": 110 },
        { "archivo": "entrevista2.txt", "participante_id": "E2", "duracion_minutos": 35, "n_intervenciones": 88 }
      ]
    },
    "fuentes_adicionales": [
      {
        "archivo": "reporte_tercero.pdf",
        "tipo": "PDF",
        "clasificacion": "cualitativo",
        "justificacion": "Contenido predominantemente narrativo: reporte de mystery shopper con observaciones textuales",
        "n_paginas": 5
      }
    ],
    "exclusiones": {
      "metodologicas": [
        "No se analizaron los audios originales (solo transcripciones); no se pudo verificar tono de voz, pausas exactas o silencios no transcritos.",
        "No se hizo análisis de sentimiento automatizado; la polaridad emocional es lectura cualitativa manual."
      ],
      "por_instrumento": [
        "El 50.5% de los registros no tiene dato de 'Importancia' y no hay evidencia suficiente para saber si es diseño del instrumento o ausencia real de respuesta."
      ],
      "por_cobertura": [
        "La muestra cualitativa (N=5) solo incluye comerciantes que ya usan herramientas digitales; el segmento de efectivo puro no tiene voz cualitativa directa."
      ]
    }
  }
}
```

---

## Procedimiento

### Paso 1: Carga y reconocimiento

1. Leer `encuesta.csv` (si existe). Obtener:
   - N exacto de registros
   - Nombres de todas las columnas
   - Tipos de datos (numéricas, categóricas, texto)
   - Primeras 5 filas para inspección visual
2. Leer `transcripciones/*.txt` (si existen). Obtener:
   - N de archivos
   - Nombres de archivo
   - Extensión y formato
3. Si no hay archivos de datos en ningún formato soportado (CSV, TXT, PDF, DOCX, XLSX, PPTX): `decision = "DETENER"`, `motivo_detencion = "sin datos de entrada"`.

4. Si el input incluye PDF, DOCX, XLSX o PPTX:
   - Extraer el texto completo de cada archivo.
   - Evaluar por contenido semántico:
     - Si el contenido es predominantemente numérico/tabular (tablas, cifras, estadísticas) → clasificar como fuente cuantitativa.
     - Si el contenido es predominantemente textual/narrativo (párrafos, entrevistas, reportes) → clasificar como fuente cualitativa.
     - Si es mixto → clasificar en ambas y documentar.
   - Documentar la clasificación en el JSON de salida bajo `datos.fuentes_adicionales`.

### Paso 2: Evaluar pregunta de investigación

Responder explícitamente:
- ¿Tiene sujeto de estudio definido? (¿a quién se estudia?)
- ¿Tiene variable dependiente implícita o explícita? (¿qué se quiere explicar/predecir/cambiar?)
- ¿Es accionable? (¿puede traducirse a una decisión de política pública o intervención comunitaria?)

Si la pregunta no es clara: `decision = "DETENER"`, `motivo_detencion = "pregunta de investigación no clara"`. Describir qué falta.

### Paso 3: Mapear columnas a roles semánticos

Para cada columna del CSV, asignar uno de los 6 roles:

| Rol | Pregunta guía |
|:---|:---|
| Intensidad | ¿Mide qué tan fuerte es algo? (Likert, frecuencia, magnitud) |
| Esfuerzo | ¿Mide recursos invertidos? (tiempo, dinero, intentos) |
| Categoría problema | ¿Clasifica el tipo de problema o necesidad? |
| Categoría solución | ¿Clasifica el tipo de solución o herramienta? |
| Segmento | ¿Describe el perfil del respondiente? |
| Tiempo | ¿Es una marca temporal? |

Si una columna no encaja: marcar como `[sin rol]` y documentar. Si un rol queda sin columnas: marcar como `false` en `roles_no_mapeados`.

### Paso 4: Codificación ligera

Solo para columnas de texto con respuestas cortas (1-10 palabras) y temas predecibles:
1. Leer todas las respuestas únicas.
2. Agrupar por tema/sentido común.
3. Crear columna nueva `[nombre_original]_cat` con la categoría asignada.
4. Documentar criterio, categorías, frecuencias y ejemplos.
5. Las respuestas que no encajan van a `no_clasificable`.

No aplica para: respuestas largas (>1 oración), texto narrativo, transcripciones.

### Paso 5: Calidad de respuesta

- Detectar respondientes con ≥70% de ítems Likert idénticos consecutivos → marcar como baja calidad.
- Detectar respuestas abiertas monosílabas/genéricas → marcar como baja calidad.
- No eliminar registros. Marcar en columna `calidad_respuesta`.
- Documentar N total de marcados.

### Paso 6: Generar dataset enriquecido

- Ejecutar `scripts/fase0_enriquecer.py <csv_limpio> <fase0_output.json> -o <csv_enriquecido> --update-fase0` después de mapear los roles en el paso anterior.
  - Este script normaliza espacios, aplica codificación ligera por reglas semánticas, normaliza métodos de pago detectados, deriva flags binarios (p. ej. `tiene_app`) y calcula métricas de calidad de respuesta de forma determinística.
  - Las reglas por defecto cubren encuestas de pequeño comercio en español; se pueden sobreescribir con `--rules <json>`.
- El agente debe revisar el resultado del script: ajustar categorías atípicas, corregir reglas si una columna fue mal clasificada y validar que `tiene_app` o flags derivados tengan sentido.
- Guardar copia del CSV original con columnas nuevas agregadas. El original no se toca.
- Documentar en `fase0_output.json`: path, N original, N final, columnas nuevas, columnas originales.

### Paso 7: Declarar viabilidad

| Ítem | Estado | Evidencia |
|:---|:---|:---|
| Datos cuantitativos | [Sí/No] | N=[valor], archivo=[nombre] |
| Datos cualitativos | [Sí/No] | N=[valor], archivos=[lista] |
| Pregunta clara | [Sí/No] | Copiar pregunta exacta |
| Decisión | [FLUIR/DETENER] | [motivo si DETENER] |

### Paso 8: Generar `fase0_output.json`

Ensamblar el JSON con todas las secciones anteriores. Si algún dato no está disponible, usar `[no disponible]`.

### Paso 9: Consulta al usuario

Después de generar `fase0_output.json`, el agente DEBE preguntar al usuario:

"Fase 0 completada. Antes de continuar con el análisis:
- ¿Tienes dudas sobre el mapeo de columnas o la clasificación de alguna variable?
- ¿Hay alguna indicación especial que quieras darme? Por ejemplo: el significado exacto de alguna columna, contexto sobre cómo se recolectaron los datos, o alguna hipótesis que ya tengan mapeada y quieras que tome en cuenta.
- ¿Quieres ajustar algo antes de que empiece el análisis de señales?"

El agente NO avanza a Fase 1 hasta que el usuario confirme explícitamente que puede continuar (ej. "adelante", "ok", "continúa").

Si el usuario proporciona hipótesis previas o contexto adicional en este paso, se incorporan al campo `hipotesis_previas` del JSON y se actualiza `fase0_output.json` antes de continuar.

---

## Reglas

- No te detengas si falta cuanti o cuali. Ejecuta con lo que haya y declara la ausencia en `faltantes_declarados`.
- No verifiques el entorno de ejecución. Asume que todo corre en Claude.
- El dataset original nunca se sobrescribe.
- Toda transformación se documenta.
- Si un rol no puede mapearse, se declara explícitamente.

- No asumas que distintas fuentes provienen de la misma población. Si el input incluye una encuesta y entrevistas, no infieras que los entrevistados son un subconjunto de los encuestados a menos que el usuario lo confirme explícitamente. Cada fuente se analiza en su propio contexto y las conclusiones no se transfieren automáticamente entre fuentes sin evidencia.
