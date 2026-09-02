# Fase 0: Viabilidad y Carga

## Propósito

Evaluar si la pregunta de investigación es clara y accionable, mapear las columnas del dataset al sistema de 6 roles semánticos, ejecutar lectura exploratoria de respuestas abiertas, y producir un JSON estructurado que alimenta Fase 1 y Fase 2. Esta fase **no se detiene** por falta de datos cuantitativos o cualitativos: ejecuta con lo disponible y declara las ausencias para que las fases siguientes sepan qué bloques marcar como `[no aplica]`.

## Input

- `datos_cuantitativos.csv` — dataset tabular con respuestas de encuesta (preguntas cerradas y abiertas). Opcional si solo hay cualitativos.
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
        "variables_texto_abierto": ["respuesta_abierta", "comentario_final"],
        "archivo": "datos_cuantitativos.csv"
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
        "texto_exacto": "¿Por qué los residentes no asisten a los talleres de capacitación laboral a pesar de expresar interés en conseguir empleo?"
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
      "intensidad_valor": ["importancia_empleo", "satisfaccion_zona"],
      "esfuerzo_accion": ["horas_semana_taller", "gasto_mensual_capacitacion"],
      "categoria_problema": ["tipo_barrera"],
      "categoria_solucion": ["solucion_actual", "herramienta_usada"],
      "segmento_perfil": ["tiene_empleo", "zona_residencia", "tamano_hogar"],
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
    "poblaciones": {
      "encuesta": { "nombre": "población general del municipio", "n": 115 },
      "entrevistas": { "nombre": "participantes de los talleres", "n": 5 }
    },
    "mapeo_transcripcion": {
      "hoja": "Transcripciones",
      "col_archivo": "Nombre del archivo",
      "col_hablante": "Persona quien habla",
      "col_texto": "Texto"
    },
    "dataset_enriquecido": {
      "path": "datos_cuantitativos_enriquecido.csv",
      "n_registros_original": 120,
      "n_registros_final": 120,
      "columnas_originales": ["id", "importancia_empleo", "horas_semana_taller", "tipo_barrera", "solucion_actual", "respuesta_abierta"],
      "columnas_nuevas": ["tipo_barrera_cat", "solucion_actual_cat"],
      "variables_binarias": ["asistio_primer_taller"],
      "calidad_respuesta": { "baja_calidad": 4, "total_marcados": 4 }
    },
    "codificacion_ligera": {
      "reglas": {
        "problem": [
          ["falta_tiempo", ["no tengo tiempo", "trabajo todo el día"]],
          ["informacion", ["no se como", "no sé cómo", "no encuentro"]],
          ["ubicacion", ["queda lejos", "no hay en mi zona"]],
          ["motivacion", ["no me interesa", "no me llama"]],
          ["otro", ["no hay cupo", "ya no"]]
        ],
        "solution": [
          ["buscar", ["tutorial", "internet", "video"]],
          ["preguntar", ["conocido", "familia", "preguntar"]],
          ["ninguna", ["no he intentado", "no hago"]]
        ],
        "segment": [
          ["con_empleo", ["trabajo", "empleo"]],
          ["sin_empleo", ["desemple", "sin trabajo"]]
        ]
      },
      "tipo_barrera_cat": {
        "variable_original": "tipo_barrera",
        "criterio": "respuesta corta (1-10 palabras), tema predecible",
        "categorias": {
          "falta_tiempo": { "n": 35, "ejemplos": ["no tengo tiempo", "trabajo todo el día"] },
          "informacion": { "n": 20, "ejemplos": ["no sé cómo inscribirme", "no encuentro la convocatoria"] },
          "ubicacion": { "n": 22, "ejemplos": ["queda lejos", "no hay en mi zona"] },
          "motivacion": { "n": 15, "ejemplos": ["no me interesa", "no me llama la atención"] },
          "horario": { "n": 12, "ejemplos": ["no encaja con mi horario", "es en la tarde"] },
          "otro": { "n": 8, "ejemplos": ["no hay cupo", "ya no quedan inscripciones"] },
          "no_clasificable": { "n": 8, "ejemplos": ["no sé", "varios"] }
        },
        "total_clasificados": 112,
        "total_no_clasificables": 8
      }
    },
    "transcripciones": {
      "n_total": 5,
      "formato": "txt_normalizado",
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
        "justificacion": "Contenido predominantemente narrativo: bitácora de campo del facilitador con observaciones textuales",
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
        "La muestra cualitativa (N=5) solo incluye participantes que ya completaron un taller; el segmento de nunca inscritos no tiene voz cualitativa directa."
      ]
    }
  }
}
```

---

## Procedimiento

### Paso 1: Consulta inicial (única interacción con el usuario)

Antes de procesar los datos, el agente ejecuta `scripts/preview_columnas.py` sobre la fuente tabular (encabezados, tipo, cardinalidad y muestras por columna) y propone un mapeo provisional de columnas a roles. Entonces hace una sola consulta que combina validación del mapeo y captura de contexto:

"Recibí los datos y la pregunta. Este es el mapeo que propongo:
- [columna] → [rol]
- [columna] → [rol]

¿Te parece bien? ¿Tienes alguna hipótesis que ya tengan mapeada, alguna aclaración sobre el significado de una columna, o contexto de cómo se recolectaron los datos? Si no hay nada más, dime 'adelante' y sigo con todo el análisis."

El usuario responde una sola vez. Las hipótesis se incorporan a `hipotesis_previas` (fuente: "contexto inicial del usuario") y las aclaraciones de columnas a `notas_semanticas.md` (Regla 18 de AGENTE.md) antes de generar `fase0_output.json`. A partir de aquí el pipeline corre de corrido (Regla 19 de AGENTE.md); no se vuelve a pedir confirmación entre fases.

### Paso 2: Carga y reconocimiento

1. Leer `datos_cuantitativos.csv` (si existe). Obtener:
   - N exacto de registros
   - Nombres de todas las columnas
   - Tipos de datos (numéricas, categóricas, texto)
   - Primeras 5 filas para inspección visual
   - **Marcar las columnas de texto abierto** en `variables_texto_abierto` (respuestas libres cuyo significado interpreta el LLM y que el script no codifica completamente). El resto del CSV no se vuelca al contexto: la evidencia de lectura completa la aportan los scripts (`fase0_enriquecer.py`, `fase1_analisis.py`) y la verifica el gate contra el CSV enriquecido (Regla 9 de AGENTE.md).
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
   - **Caso transcriptor→planilla:** si el XLSX/DOCX es una transcripción de entrevista (columna de diálogo + columna de hablante/sesión), es cualitativo por contenido, NO cuantitativo: no se exime de lectura completa (Regla 9) y Fase 0 lo serializa a `transcripciones/*.txt` antes del análisis cualitativo.
   - Documentar la clasificación en el JSON de salida bajo `datos.fuentes_adicionales`.

**Normalización de transcripciones en planilla (obligatoria si hay fuentes cualitativas XLSX/DOCX):**

Cuando una fuente cualitativa llega como planilla, se ejecuta `scripts/normalizar_transcripciones.py` para exportar un campo TXT por entrevista y declarar el rol de hablante:

```bash
python scripts/normalizar_transcripciones.py <planilla.xlsx|.docx> -o transcripciones/ \
    --manifesto transcripciones/manifesto.json [--mapeo mapeo_transcripcion.json]
```

- Acepta XLSX y DOCX en tabla-planilla (columnas archivo/hablante/texto). Un **DOCX narrativo** (sin tabla) se vuelca como un solo TXT (`formato: "docx_narrativo"` en el manifiesto). **PDF/PPTX** no los lee el script: serializar a TXT por otro medio (o con pypdf/pdfminer si están) y declarar en `advertencias` que la fuente se serializó externamente.

- El layout de columnas se declara en Fase 0 (`datos.mapeo_transcripcion`: hoja + columnas de archivo/hablante/texto por letra o por nombre de cabecera). Fallback: detección por cabecera; si el layout no es parseable, se declara en `advertencias` y se lee la planilla directamente en contexto.
- **Rol de hablante siempre inferido por heurística lingüística, nunca por etiqueta de diarización** (p. ej. `persona_N`, `speaker_1`): la etiqueta numérica no indica rol — el entrevistador puede llevar cualquier número —, por eso el script decide por el contenido del turno y etiqueta `entrevistador`/`entrevistado_N`, declarando la advertencia `"rol_hablante inferido por heurística, no por etiqueta del transcriptor"`.
- El manifiesto integra `n_hablantes` y `n_entrevistados` por archivo (una entrevista puede tener más de dos hablantes, p. ej. dos entrevistados de un mismo hogar; cada `entrevistado_N` cuenta como población distinta, regla 12 y blindaje transpoblacional).

### Paso 3: Evaluar pregunta de investigación

Responder explícitamente:
- ¿Tiene sujeto de estudio definido? (¿a quién se estudia?)
- ¿Tiene variable dependiente implícita o explícita? (¿qué se quiere explicar/predecir/cambiar?)
- ¿Es accionable? (¿puede traducirse a una decisión de política pública o intervención comunitaria?)

Si la pregunta no es clara: `decision = "DETENER"`, `motivo_detencion = "pregunta de investigación no clara"`. Describir qué falta.

### Paso 4: Mapear columnas a roles semánticos

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

### Paso 5: Codificación ligera

Solo para columnas de texto con respuestas cortas (1-10 palabras) y temas predecibles:
1. Leer todas las respuestas únicas.
2. Agrupar por tema/sentido común.
3. Crear columna nueva `[nombre_original]_cat` con la categoría asignada.
4. Documentar criterio, categorías, frecuencias y ejemplos.
5. Las respuestas que no encajan van a `no_clasificable`.

No aplica para: respuestas largas (>1 oración), texto narrativo, transcripciones.

### Paso 6: Calidad de respuesta

- Detectar respondientes con ≥70% de ítems Likert idénticos consecutivos → marcar como baja calidad.
- Detectar respuestas abiertas monosílabas/genéricas → marcar como baja calidad.
- No eliminar registros. Marcar en columna `calidad_respuesta`.
- Documentar N total de marcados.

### Paso 7: Generar dataset enriquecido

- Ejecutar `scripts/fase0_enriquecer.py <csv_limpio> <fase0_output.json> -o <csv_enriquecido> --update-fase0` después de mapear los roles (Paso 4).
  - Este script normaliza espacios, aplica codificación ligera solo con las reglas semánticas declaradas, detecta variables binarias y calcula métricas de calidad de respuesta de forma determinística.
  - Las reglas de codificación se leen de `codificacion_ligera.reglas` de este JSON o de `--rules <json>`. El script NO aplica reglas de dominio por defecto: si una columna temática no tiene reglas, lo advierte y preserva el valor original (passthrough) en lugar de inventar categorías de un dominio ajeno.
- El agente debe revisar el resultado del script: ajustar categorías atípicas, corregir reglas si una columna fue mal clasificada y validar que las variables binarias detectadas tengan sentido.
- Guardar copia del CSV original con columnas nuevas agregadas. El original no se toca.
- Documentar en `fase0_output.json`: path, N original, N final, columnas nuevas, columnas originales.

### Paso 8: Declarar viabilidad

| Ítem | Estado | Evidencia |
|:---|:---|:---|
| Datos cuantitativos | [Sí/No] | N=[valor], archivo=[nombre] |
| Datos cualitativos | [Sí/No] | N=[valor], archivos=[lista] |
| Pregunta clara | [Sí/No] | Copiar pregunta exacta |
| Decisión | [FLUIR/DETENER] | [motivo si DETENER] |

### Paso 9: Generar `fase0_output.json`

Ensamblar el JSON con todas las secciones anteriores. Si algún dato no está disponible, usar `[no disponible]`.

### Paso 10: Reporte de viabilidad (no bloqueante)

Al terminar `fase0_output.json`, el agente informa el resultado y continúa sin esperar confirmación (Regla 19 de AGENTE.md):

"Fase 0 lista. Mapeo de columnas: [resumen]. Decisión: FLUIR. Continúo con el análisis."

No se detiene. Si el usuario interviene después, el agente aplica los ajustes en la siguiente fase sin rehacer lo ya completado (Regla 18 de AGENTE.md).

---

## Reglas

- No te detengas si falta cuanti o cuali. Ejecuta con lo que haya y declara la ausencia en `faltantes_declarados`.
- No verifiques el entorno de ejecución. Asume que el entorno está listo y ejecuta directamente.
- El dataset original nunca se sobrescribe.
- Toda transformación se documenta.
- Si un rol no puede mapearse, se declara explícitamente.

- No asumas que distintas fuentes provienen de la misma población. Si el input incluye una encuesta y entrevistas, no infieras que los entrevistados son un subconjunto de los encuestados a menos que el usuario lo confirme explícitamente. Cada fuente se analiza en su propio contexto y las conclusiones no se transfieren automáticamente entre fuentes sin evidencia.
- Declara los universos en `datos.poblaciones` (mapa `universo → {nombre, n}`: nombre de la población y **N de la población** para el piso adaptativo de Fase 3, p. ej. `encuesta`, `entrevistas`). Formato legado aceptado: `universo → "nombre"` (sin N; el piso por población cae a 30 fijo). Es la lista contra la que el gate contrasta por substring los cruces transpoblacionales (regla 12 de AGENTE.md y blindaje de `references/fase-3-cruce.md`).
- Si una fuente cualitativa viene en planilla (XLSX/DOCX con columna de diálogo y hablante), Fase 0 la serializa a `transcripciones/*.txt` (normalización de transcripciones) y lo declara en `datos.fuentes_adicionales` y en `datos.transcripciones`; el archivo original no se lee en contexto (Regla 9 de AGENTE.md).
