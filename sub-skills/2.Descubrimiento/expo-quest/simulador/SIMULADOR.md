---
name: simulador-expo-quest
description: Simula las interacciones de una visita a un evento, feria o expo con interlocutores sintéticos (asistentes y expositores) y entrega un CSV codificable con hallazgos de Jobs, Pains, Gains y competencia, muestreo reproducible por semilla y curva de saturación, todo etiquetado SIMULADO. Usar cuando el usuario no pueda asistir al evento.
category: Descubrimiento
tipo: simulador
padre: 2.Descubrimiento/expo-quest
---

# Simulador de Expo Quest

Fabrica las conversaciones y observaciones que un equipo habría registrado recorriendo una
feria, y las entrega en **un CSV** en formato largo listo para consolidar. Todo queda
etiquetado **SIMULADO**.

## Alcance

**SÍ hace:** inventar el evento ficticio y los interlocutores (asistentes y expositores),
repartir qué dice cada uno según la prevalencia declarada, separar lo que se aprende de la
competencia, y escribir el CSV con los conteos y la curva de saturación calculados.

**NO hace:**

- **No analiza.** No consolida los hallazgos finales ni concluye: eso es de
  `2.Descubrimiento/expo-quest`, que trata el CSV como trataría notas de campo reales.
- **No genera HTML** ni `reporte.json`, y no cierra pasos del flujo.
- **No localiza eventos reales.** Ni sus fechas, ni sus costos, ni quién expone. Este
  simulador inventa un evento ficticio; para encontrar eventos de verdad hace falta búsqueda
  web, y eso es otra skill.
- **No sustituye asistir.** Si el usuario puede ir, va: una feria es el único sitio donde la
  competencia te explica su propuesta de valor de viva voz.

## Cuándo se activa

Cuando el usuario decide simular en el **paso 2 del flujo** («Decisión — Entrevistas») con
Expo Quest entre los agentes elegidos. Esa decisión enciende la marca de simulación en todo el
proyecto.

## El plan

Tú escribes el material cualitativo; **el script hace los números**:

```jsonc
{
  "proyecto": "Foro de producción audiovisual",
  "hipotesis": "La continuidad de staff se puede vender como garantía contractual",
  "dimension": "B2B",         // B2B o B2C — indispensable: cambia lenguaje e interlocutor
  "seed": 20260819,
  "ruido": 0.15,
  "evento": {
    "nombre": "Expo Producción LATAM (ficticio)",
    "tipo": "Feria de industria audiovisual",
    "ubicacion": "CDMX (ficticia)",
    "asistentes_estimados": "3,500*"
  },
  "interlocutores": [          // 4 asistentes + 2 expositores es el reparto por defecto
    { "rol": "Productor ejecutivo de agencia", "tipo": "asistente",
      "perfil": "Compra 8 jornadas al año", "reaccion": "positiva" },
    { "rol": "Coordinadora independiente", "tipo": "asistente",
      "perfil": "Rodajes cortos, presupuesto propio", "reaccion": "escéptica" },
    { "rol": "Gerente comercial de foro competidor", "tipo": "expositor",
      "perfil": "Foro con 4 sets propios", "reaccion": "neutral" }
  ],
  "codigos": [
    { "codigo": "CONTINUIDAD-STAFF",
      "tipo": "pain",                    // job | pain | gain | competencia
      "prevalencia": 0.7,                // DECLARADA: prob. de que un interlocutor lo diga
      "senal": "valida",                 // valida | refuta | neutral
      "citas": ["Cada jornada me llega gente distinta y pierdo la primera hora."] },
    { "codigo": "COMP-PAQUETE-POST",
      "tipo": "competencia",
      "prevalencia": 0.8,
      "senal": "neutral",
      "solo_tipo": "expositor",          // este código solo lo dicen los expositores
      "citas": ["Nosotros ya vendemos foro y postproducción en una sola cotización."] }
  ]
}
```

Reglas del plan:

1. **`dimension` es obligatoria.** B2B y B2C no se parecen: en B2B se habla de presupuestos,
   procesos de decisión y quién firma; en B2C, de emociones y decisiones de impulso.
2. **El interlocutor se identifica por su rol, no por su nombre.** En un pasillo de feria nadie
   da su nombre completo: «Comprador de empaque» es más útil y más honesto que «Ricardo».
3. **Incluye expositores.** El script avisa si no hay ninguno: la mitad del valor de una feria
   es lo que se aprende de quien ya vende a este mercado. Los códigos de competencia se
   restringen a ellos con `solo_tipo: "expositor"`.
4. **Declara al menos un código `competencia`.** Es lo único que solo se consigue en una feria.
5. **`reaccion`** admite `positiva`, `neutral`, `escéptica` y `negativa`. El script avisa si
   nadie reacciona con escepticismo o en contra: en una feria real siempre hay alguien a quien
   no le interesa, y sin esa reacción el ensayo no sirve de prueba.
6. **Al menos un código con `senal: refuta`.** El script avisa si no hay ninguno.
7. **El evento es ficticio y se declara como tal.** Nombre inventado, con «(ficticio)» a la
   vista. Nunca el nombre de una feria real: nadie asistió.

## Ejecución

Desde la raíz del repositorio:

```bash
python sub-skills/2.Descubrimiento/expo-quest/simulador/scripts/simular_expo.py \
    plan.json -o expo_interacciones_SIMULADO.csv
```

Parámetros sobrescribibles: `--seed`, `--ruido`. El número de interacciones sale de la lista
`interlocutores`.

## Qué produce

**Un CSV** (`expo_interacciones_SIMULADO.csv`), una fila por interacción × código mencionado.
Las interacciones sin ningún código **también dejan fila** (con `codigo` vacío): una
conversación que no dio nada también es información.

| Columna | Contenido |
| --- | --- |
| `interaccion_id` | `I01`, `I02`, … |
| `interlocutor`, `tipo_interlocutor`, `perfil` | Con quién se habló (`asistente` / `expositor`) |
| `reaccion` | `positiva` / `neutral` / `esceptica` / `negativa` |
| `dimension`, `evento` | B2B o B2C y el nombre ficticio del evento |
| `codigo`, `tipo` | Código y Job/Pain/Gain/Competencia (vacíos si no hubo hallazgo) |
| `senal` | `valida` / `refuta` / `neutral` |
| `cita` | La frase repartida por el script |
| `simulado` | `si` en todas las filas |
| `seed` | La semilla, para que el archivo sea auditable por sí solo |

Además **imprime en pantalla** (no genera archivo): conteos por código, tabla
**asistentes vs. expositores** por tipo de hallazgo, curva de saturación, reparto de señales,
reacciones declaradas y avisos. Ese bloque es lo que se cita en el reporte: **no lo reescribas
de memoria.**

## Supuestos estadísticos y sus límites

**Aquí no hay porcentajes de población, y es a propósito.** Seis conversaciones de pasillo no
son una muestra probabilística: **quien se acerca a un stand ya está autoseleccionado**. Ese
sesgo de autoselección existe igual en la visita real, y el script lo declara en cada
ejecución. Se reportan conteos («4 de 6») y saturación de códigos.

Lo que el script garantiza:

- **Reproducibilidad:** semilla explícita; misma semilla + mismo plan = CSV idéntico.
- **Muestreo declarado:** cada mención es un ensayo Bernoulli con la prevalencia del plan
  (modulada por la reacción del interlocutor), encogida hacia 0.5 según el `ruido`.
- **Restricción por tipo:** los códigos con `solo_tipo` solo pueden salir de ese interlocutor,
  así que los hallazgos de competencia no aparecen mágicamente en boca de un asistente.
- **Conteos derivados:** el recuento real de las filas del CSV.
- **Curva de saturación:** códigos nuevos por interacción; saturación = 2 seguidas sin novedad.
- **Avisos** si hay menos de 4 interacciones, si faltan expositores, si no hay códigos de
  competencia, si nadie reacciona con escepticismo, si un código no apareció, si no hay
  saturación o si ningún código refuta.

El límite, que va escrito en toda salida:

> **Validez externa: nula.** El evento, los interlocutores y sus reacciones son inventados. Ni
> el nombre del evento ni las cifras de asistencia corresponden a algo que ocurrió. Y lo que
> esta simulación no puede darte es precisamente lo que hace valiosa una feria: enterarte de lo
> que no sabías que existía —el competidor que no tenías en el radar, la objeción que nadie del
> equipo había pensado. Una simulación solo puede devolverte lo que ya declaraste.

## La marca SIMULADO

La propaga el flujo solo (`flujo.simulacion` → distintivo en la cabecera del HTML, caja ámbar
en el contexto, advertencia automática y línea en el pie). Lo que te toca:

1. `base` empieza con `SIMULADO · 6 interacciones sintéticas en evento ficticio (semilla 20260819)`.
2. Los `tags` del item llevan `SIMULADO`.
3. `advertencias` recoge las interacciones, la semilla, el sesgo de autoselección y el límite
   de validez externa.
4. El CSV se declara en `output.archivos_generados` y en `--outputs` al cerrar el paso.
5. **Las cifras de asistencia y los precios van marcados `*`.** Y los hallazgos de competencia
   **no se atribuyen a competidores reales con nombre**: son perfiles ficticios, no
   inteligencia de mercado.

## Contrato JSON (salida)

```json
{
  "skill": "simulador-expo-quest",
  "timestamp": "<ISO 8601>",
  "parametros": { "interacciones": 6, "dimension": "B2B", "seed": 20260819, "ruido": 0.15 },
  "output": {
    "formato": "csv",
    "contenido": "<resumen del bloque que imprimió el script: conteos y saturación>",
    "archivos_generados": ["expo_interacciones_SIMULADO.csv"]
  },
  "decision": {
    "veredicto": "perseverar",
    "siguiente_paso": "expo-quest",
    "razon": "Interacciones sintéticas listas para consolidar hallazgos.",
    "contexto_usado": ["html_1"]
  },
  "advertencias": [
    "DATOS SIMULADOS: evento ficticio, 6 interlocutores sintéticos, semilla 20260819. No hubo asistencia real.",
    "Muestra de conveniencia: sin porcentajes de población. Validez externa nula.",
    "Los hallazgos de competencia son perfiles ficticios, no inteligencia de mercado."
  ]
}
```

## Reglas y Restricciones

1. **Nunca redactes conteos ni porcentajes.** Los conteos los calcula el script.
2. **Un CSV, nada más.** Ni HTML ni `reporte.json` ni cierre de paso.
3. **El nombre del archivo termina en `_SIMULADO.csv`.**
4. **Ni eventos ni marcas reales** como participantes. El evento lleva «(ficticio)» en el
   nombre.
5. **Registra la semilla** en `parametros` y en el resumen del paso.
6. **Contraste obligatorio:** reacciones positivas y negativas. Si el script avisa de que nadie
   reaccionó en contra, ajusta el plan en vez de entregarlo.

## Referencias

- Convención de simuladores y propagación de la marca: `sub-skills/SIMULACION.md` (canónica,
  si tienes acceso).
- Guion de interacción y consolidación de hallazgos: `../AGENTE.md` de la skill padre.
- Contrato JSON: `sub-skills/CONTRATO_JSON.md` (canónico) o la estructura de arriba, que es
  equivalente y autocontenida.
