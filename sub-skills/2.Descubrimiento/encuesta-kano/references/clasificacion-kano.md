# Tabla de Clasificación Kano — Encuesta Kano

Referencia vinculante para interpretar el cruce de respuestas **funcional × disfuncional** y para `scripts/clasificar_kano.py`.

## Opciones de respuesta

Para preguntas **funcionales y disfuncionales**:
1. Me gusta que sea así
2. Espero que sea así
3. Indiferente
4. Lo tolero
5. No me gusta

Para la pregunta de **importancia (opcional)**:
- Extremadamente importante
- No es importante

## Matriz de clasificación (funcional × disfuncional)

| Funcional ↓ / Disfuncional → | Me gusta | Espero | Indiferente | Lo tolero | No me gusta |
|---|---|---|---|---|---|
| **Me gusta que sea así** | Q | A | A | A | **O** |
| **Espero que sea así** | R | I | I | I | **M** |
| **Indiferente** | R | R | I | I | **M** |
| **Lo tolero** | R | R | I | I | **M** |
| **No me gusta** | Q | R | R | R | Q |

## Leyenda

| Código | Categoría | Significado |
|---|---|---|
| **M** | Must-be / Obligatorio | Su ausencia genera insatisfacción; su presencia no añade satisfacción extra. Imprescindible. |
| **O** | Unidimensional / Rendimiento | La satisfacción es proporcional a su presencia/rendimiento. |
| **A** | Atractivo | Sorprende positivamente; su ausencia no molesta, su presencia deleita. |
| **I** | Indiferente | No cambia la satisfacción ni su presencia ni su ausencia. |
| **R** | Inverso | Su presencia causa insatisfacción (el usuario lo rechaza). |
| **Q** | Cuestionable | Respuesta contradictoria (suele indicar pregunta mal formulada o respuesta al azar). |

## Interpretación por feature

La categoría se asigna por la **combinación más frecuente** entre los respondientes de cada feature. `scripts/clasificar_kano.py` produce el conteo por categoría. Las features **Must-be (M)** y **Unidimensional (O)** son las de mayor impacto; las **Atractivo (A)** son las oportunidades de diferenciación; las **Indiferente (I)** no deben priorizarse; **Inverso (R)** y **Cuestionable (Q)** requieren revisión del enunciado.
