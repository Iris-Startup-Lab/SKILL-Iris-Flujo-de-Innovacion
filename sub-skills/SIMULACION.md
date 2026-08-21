# Simulación de evidencia — convención del flujo IRIS

Contrato de las **sub-skills simuladoras** («simuladores»): qué producen, con qué supuestos
estadísticos y cómo queda marcada la simulación en todo lo que viene después.

Se usan cuando el usuario **no tiene acceso a usuarios reales** y decide, en el paso 2 del
flujo («Decisión — Entrevistas»), simular las entrevistas o encuestas en vez de ejecutarlas.

## 1. Qué es un simulador

Un simulador es una **sub-sub-skill**: vive dentro de la sub-skill que normalmente analizaría
esos datos, y solo se ocupa de **fabricar el dato de entrada**.

```text
sub-skills/2.Descubrimiento/encuesta-kano/
├── AGENTE.md                       # la skill: analiza y produce el HTML
├── scripts/clasificar_kano.py      # su análisis
└── simulador/                      # la sub-sub-skill
    ├── SIMULADOR.md                # instrucciones del simulador
    └── scripts/simular_kano.py     # plan.json -> CSV
```

Reglas de la convención:

- **El archivo de instrucciones se llama `SIMULADOR.md`.** No `SKILL.md` (el gestor exige
  exactamente uno por ZIP y lo ocupa la macro) ni `AGENTE.md` (lo ocupa la sub-skill padre).
- **Un simulador entrega un CSV y nada más.** No genera HTML, no escribe `reporte.json` y no
  cierra pasos del flujo. El HTML lo produce la sub-skill padre a partir del CSV, como si el
  dato viniera de campo.
- **El nombre del archivo termina en `_SIMULADO.csv`** y el CSV lleva una columna `simulado`
  con valor `si` en cada fila. Si el archivo se separa de su contexto, sigue declarando qué es.
- **El simulador no analiza.** No prioriza, no clasifica, no concluye: eso es trabajo de la
  sub-skill padre, con los mismos scripts que usaría con datos reales. Es lo que hace la
  simulación auditable: el análisis no sabe —ni necesita saber— que el dato es sintético.

## 2. División del trabajo: el LLM escribe el plan, el script hace los números

Ninguna cifra la inventa el modelo. El LLM aporta el contenido cualitativo —qué códigos,
temas o características existen y con qué prevalencia se espera cada uno— en un **`plan.json`**,
y el script hace el muestreo y todos los cálculos.

```jsonc
{
  "proyecto": "Huertos urbanos MX",
  "perfil": "Familias urbanas 28-45, CDMX",
  "hipotesis": "El costo de mantenimiento es la barrera principal",
  "n": 30,                          // tamaño de muestra simulada
  "seed": 20260819,                 // semilla: misma semilla = mismo CSV
  "ruido": 0.15,                    // prob. de respuesta fuera del patrón declarado
  "segmentos": [
    { "nombre": "Primerizos", "peso": 0.6 },
    { "nombre": "Con experiencia", "peso": 0.4 }
  ],
  "codigos": [
    {
      "codigo": "COSTO-MANT",
      "tipo": "pain",                        // job | pain | gain | workaround | competencia
      "texto": "El mantenimiento mensual sale más caro de lo previsto.",
      "prevalencia": 0.6,                    // DECLARADA: no es un dato medido
      "senal": "valida",                     // valida | refuta | neutral (vs. la hipótesis)
      "citas": ["Llevo tres meses y ya gasté el doble de lo que pensaba."],
      "prevalencia_por_segmento": { "Primerizos": 0.75 }   // opcional
    }
  ]
}
```

- **`prevalencia` es un supuesto declarado, no una medición.** Es la probabilidad con la que
  cada participante sintético menciona ese código. El script la usa como parámetro del sorteo
  y la imprime junto al resultado, para que se pueda contrastar lo declarado con lo obtenido.
- **`citas`** las escribe el LLM: son el material cualitativo, y el script solo las reparte.
- **`seed` es obligatoria en la práctica:** sin ella la simulación no es reproducible y no se
  puede auditar. El script pone una por defecto y la imprime siempre.
- **`ruido`** es lo que evita el resultado de laboratorio: con esa probabilidad el participante
  responde fuera del patrón declarado, así que aparecen disidentes, respuestas neutras y —en
  Kano— categorías minoritarias y algún caso contradictorio.

## 3. Supuestos estadísticos que sí se pueden sostener

Un simulador **no** produce evidencia. Lo que sí puede hacer —y es lo que se exige aquí— es
ser correcto dentro de su propio modelo:

| Supuesto | Cómo se cumple |
| --- | --- |
| **Reproducibilidad** | Semilla explícita. Misma semilla + mismo plan = CSV idéntico, byte a byte. |
| **Muestreo declarado** | Cada mención es un ensayo Bernoulli con la `prevalencia` del plan (multinomial en Kano). El script sortea; el LLM no escribe conteos. |
| **Conteos derivados** | Las frecuencias son el recuento real de las filas del CSV, nunca un número redactado. |
| **Incertidumbre reportada** | Intervalo de **Wilson** al 95% para cada proporción (mejor que la normal con n pequeño y con proporciones cerca de 0 o 1). |
| **Tamaño de muestra justificado** | Cuantitativo: margen de error `e = z·√(p(1−p)/n)` con `p=0.5`. Cualitativo: curva de **saturación** (códigos nuevos por sesión). El script avisa si `n` no sostiene lo que se quiere afirmar. |
| **Heterogeneidad** | Segmentos con peso y prevalencia propia: una muestra homogénea no reproduce el comportamiento de una población real. |
| **Contraste** | El plan debe incluir códigos con `senal: refuta`. Un simulador que solo confirma la hipótesis no es una prueba, es un espejo. |

Y el límite, que va escrito en toda salida:

> **Validez externa: nula.** El intervalo de confianza describe la variabilidad del generador
> sintético, no la de una población. Estos números dicen cómo se leerían los resultados si el
> mundo se pareciera a las prevalencias declaradas; no dicen que el mundo se les parezca.
> Ninguna decisión de inversión debe apoyarse solo en esto.

Por eso el criterio de calidad de una simulación no es la significancia, sino **si el plan es
discutible**: prevalencias que alguien del equipo pueda mirar y decir «esa no, esa es más
baja». Ahí está el valor — la simulación hace explícitos los supuestos que, sin ella, se
quedan implícitos en la cabeza de quien decide.

## 4. La marca SIMULADO viaja sola

Cuando el usuario elige simular, el flujo lo registra y **la marca se propaga sin depender de
que ninguna skill se acuerde de escribirla**:

1. La opción elegida está marcada en `pasos.json` con `marca_simulacion: true`.
2. `scripts/estado_flujo.py` la detecta al construir el contexto y añade el bloque
   `flujo.simulacion` (`activo`, `desde`, `nodo`, `opcion`, `nota`) que viaja a cada reporte.
3. `_plantilla_html/` lo renderiza en **todos** los HTML posteriores: distintivo
   «DATOS SIMULADOS» en la cabecera, caja ámbar en «De dónde viene este reporte», una
   advertencia automática en «Advertencias y limitaciones» y una línea en el pie.

Lo que sí le toca a cada skill que trabaje con datos simulados:

- `base` (o el campo equivalente) empieza con `SIMULADO · …`.
- Los `tags` del item llevan `SIMULADO`.
- `advertencias` incluye qué se simuló, con qué `n`, con qué semilla y el límite de validez
  externa del punto 3.
- El CSV simulado se declara en `output.archivos_generados`.

## 5. Cómo se invoca dentro del flujo

En el paso 2 («Decisión — Entrevistas») el usuario decide si ejecuta las entrevistas o las
simula. Si simula, el orden es siempre el mismo:

```bash
# 1. registrar la decisión (activa la marca en todo lo que viene después)
python scripts/estado_flujo.py decision --paso html_2 \
    --nodo "¿Ejecución de entrevistas?" --opcion "No — simulación de respuestas e insights"

# 2. el simulador fabrica el dato
python sub-skills/2.Descubrimiento/entrevistas-empatia/simulador/scripts/simular_entrevistas.py \
    plan.json -o entrevistas_SIMULADO.csv

# 3. la sub-skill padre analiza el CSV y genera su HTML, como con datos reales
python _plantilla_html/scripts/generar_html.py --data reporte.json \
    --estado flujo_estado.json --paso html_2 -o html_2.html

# 4. cerrar el paso declarando los dos archivos
python scripts/estado_flujo.py completar --paso html_2 \
    --skills 2.Descubrimiento/entrevistas-empatia \
    --outputs html_2.html entrevistas_SIMULADO.csv --datos reporte.json \
    --resumen "6 entrevistas SIMULADAS (semilla 20260819): 4 pains, saturación en la 5.ª"
```

Qué simulador corresponde a cada paso está en `pasos.json`, campo `simuladores` del paso — no
se deduce del nombre de la carpeta.

**En el paso 3 la decisión ya viene dada.** Su nodo «Origen de las respuestas de descubrimiento»
tiene `auto_si`: si en el paso 2 se eligió simular, la opción está decidida por el propio flujo.
Infórmasela al usuario en vez de volver a preguntarla —y regístrala igual, porque el paso no
cierra sin ella. Los simuladores que toca usar son los de los agentes que el usuario **eligió**
en «Selección de agentes de descubrimiento»: `mostrar` ya los lista filtrados, no los cuatro.

## 6. Los cinco simuladores

| Simulador | Dentro de | Instrumento | CSV |
| --- | --- | --- | --- |
| `simulador-entrevistas-empatia` | `2.Descubrimiento/entrevistas-empatia` | Entrevistas 1:1 (Mom Test) | `entrevistas_SIMULADO.csv` |
| `simulador-day-in-the-life` | `2.Descubrimiento/day-in-the-life` | Observación etnográfica | `aditl_observaciones_SIMULADO.csv` |
| `simulador-encuesta-kano` | `2.Descubrimiento/encuesta-kano` | Encuesta Kano funcional × disfuncional | `kano_respuestas_SIMULADO.csv` |
| `simulador-discovery-survey` | `2.Descubrimiento/discovery-survey` | Encuesta de descubrimiento | `discovery_respuestas_SIMULADO.csv` |
| `simulador-expo-quest` | `2.Descubrimiento/expo-quest` | Interacciones en evento/feria | `expo_interacciones_SIMULADO.csv` |

Los tres cualitativos (entrevistas, ADITL, expo) trabajan con `n` pequeña y se justifican por
**saturación**, no por margen de error: con 6 entrevistas no se calculan porcentajes de
población, se cuenta cuántos de 6 mencionaron cada cosa y en qué sesión dejaron de aparecer
códigos nuevos. Los dos cuantitativos (Kano, Discovery Survey) sí reportan proporciones con su
intervalo, y avisan cuando `n` no alcanza para el margen de error pedido.
