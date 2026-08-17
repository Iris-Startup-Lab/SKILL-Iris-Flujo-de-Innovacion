# Plan de medición de tokens del flujo IRIS

> Objetivo: saber cuánto cuesta en tokens recorrer el flujo, por paso y por sub-skill, para
> poder comparar la **ruta completa** (11 pasos) contra la **mínima** (5) con números en vez
> de intuición.

Estado: **plan definido, medición pendiente**. La línea base de §5 ya está tomada sobre un
recorrido real; lo que falta es el nivel 2 (sesión instrumentada) y la comparación de las dos
rutas sobre el mismo proyecto.

---

## 1. Alcance: qué se mide y qué no

El alcance no estaba escrito en ninguna parte. Queda fijado así.

### Entra en la medición

| # | Concepto | Qué es | Dónde se mide |
| --- | --- | --- | --- |
| E1 | **Arranque fijo** | Lo que el gestor carga una vez por sesión: `SKILL.md`, `pasos.json`, `AGENTS.md`, `_plantilla_html/README.md`, `CONTRATO_JSON.md` | Archivos del repo |
| E2 | **Briefing del paso** | La salida de `estado_flujo.py mostrar` que abre cada paso | stdout del script |
| E3 | **Sub-skills del paso** | El `SKILL.md` de cada sub-skill invocada + sus `references/` vinculantes | Archivos del repo |
| E4 | **Herencia** | Los `reporte.json` de los predecesores que el paso abre por el canal `--datos` | Archivos del proyecto |
| S1 | **Salida generada** | El `reporte.json` que el modelo escribe en el paso | Archivo del proyecto |

### Queda fuera (y por qué)

- **El HTML entregado.** Lo escribe `generar_html.py`, no el modelo. En el recorrido real medido
  los 6 HTML pesan **20.8×** lo que pesan sus `reporte.json`: contarlos como salida del modelo
  inflaría la cifra ~21 veces. Se mide el `reporte.json`, que es lo único que el modelo emite.
- **Los turnos del human-in-the-loop.** Dependen de cuánto pregunte y responda el usuario, no
  del flujo. Medirlos mezclaría el coste del diseño con el coste de la conversación.
- **Los tokens de razonamiento.** No todos los gestores los exponen, así que no son comparables
  entre herramientas.
- **El system prompt del gestor.** Es constante y ajeno al repo.
- **Los insumos que aporta el usuario** (transcripciones de entrevistas, CSV de encuestas). Son
  del proyecto, no del flujo, y su tamaño es ilimitado.
- **Los scripts Python.** El modelo los ejecuta, no los lee. Solo cuenta el `--help` si lo pide.

### La pregunta que la medición tiene que contestar

1. ¿Cuánto cuesta la ruta completa contra la mínima, en el mismo proyecto?
2. ¿Qué paso es el más caro y por qué: por su sub-skill o por la herencia acumulada?
3. ¿Cuánto crece la herencia paso a paso? Es el único coste que **no** es constante.
4. ¿Vale la pena releer toda la cadena de `reporte.json` o basta el predecesor directo?

---

## 2. Unidad y estimador

- **Unidad:** tokens de entrada y de salida, contados por separado. No se suman: tienen precio
  distinto en toda API.
- **Estimador actual:** `caracteres ÷ 4`, marcado `*` en cada cifra. Es una aproximación de
  orden de magnitud, no una medida.
- **Estimador objetivo:** un tokenizador real. `skills_env` **no** tiene `tiktoken` ni
  `transformers` instalados (comprobado el 13/08/2026), así que el nivel 1 arranca aproximado.
  Instalar `tiktoken` es el primer paso de la medición fina.
- **Advertencia de comparabilidad:** el tokenizador varía por familia de modelo. Las cifras
  sirven para **comparar rutas entre sí**, no para presupuestar una factura. El español y los
  acentos de las rutas (`3.Ideacion/ideacion`) tokenizan peor que el inglés.

Regla de integridad del repo (AGENTS.md §4): toda cifra estimada va con `*`. Este documento la
respeta.

---

## 3. Los dos niveles de medición

### Nivel 1 — Estático y reproducible (sin API)

Cuenta los tokens de los archivos que el flujo obliga a leer y escribir. Es determinista: el
mismo repo da el mismo número siempre, así que sirve de regresión —si una sub-skill engorda, se
ve.

- **Qué da:** el **suelo** del coste. Nadie recorre el flujo por menos.
- **Qué no da:** lo que el modelo gasta de más al razonar, repreguntar o reintentar.
- **Cómo:** un script `scripts/medir_tokens.py` que recorra `pasos.json`, resuelva las
  sub-skills de cada paso y sume E1–E4 y S1 por paso y por ruta.

### Nivel 2 — Sesión real instrumentada

Recorre un proyecto de punta a punta anotando, paso a paso, el uso que reporta el propio gestor.

- **Qué da:** el coste real, razonamiento y reintentos incluidos.
- **Qué no da:** reproducibilidad exacta — dos sesiones del mismo proyecto no dan lo mismo.
- **Cómo:** al cerrar cada paso, anotar en una tabla el uso reportado por la herramienta. En
  Claude Code, `/explain-usage` al final del flujo (ya está en `SKILL.md` § «¿Qué hacer al final
  de todo el flujo?»); en el resto, el contador de la herramienta.
- **Mínimo de repeticiones:** 2 sesiones por ruta. Con una sola no se distingue el coste del
  flujo del ruido de la sesión.

---

## 4. Procedimiento

1. **Instalar el tokenizador** en `skills_env` y sustituir el estimador `÷4` por el conteo real.
2. **Escribir `scripts/medir_tokens.py`** con esta salida: una fila por paso con E1–E4, S1 y el
   acumulado, más un total por ruta. Formato CSV, para poder comparar corridas.
3. **Correr el nivel 1** sobre las dos rutas. Es puro cálculo sobre `pasos.json`: no hace falta
   ejecutar nada.
4. **Elegir un proyecto de prueba y congelarlo** (nombre, objetivo, audiencia y las mismas
   decisiones en cada nodo). Sin esto la comparación mide proyectos distintos, no rutas.
5. **Correr el nivel 2 dos veces por ruta**, con el mismo proyecto y las mismas decisiones.
6. **Publicar la comparación** en este documento, § «Resultados».

---

## 5. Línea base del nivel 1 (13/08/2026)

> **La línea base de abajo está caducada para tres archivos.** Los arreglos del 14/08 (subida
> al gestor, comando `rutas`, sección «Cómo nombrar las cosas ante el usuario», introducción de
> la skill) engordaron el arranque fijo un **22%**:
>
> | Archivo | 13/08 | 14/08 | Delta | Tokens\* |
> | --- | --- | --- | --- | --- |
> | `SKILL.md` | 9,304 | 15,211 | **+63%** | ~3,803 |
> | `AGENTS.md` | 11,537 | 15,687 | +36% | ~3,922 |
> | `pasos.json` | 14,351 | 15,057 | +5% | ~3,764 |
> | **Total fijo** | **49,816** | **60,579** | **+22%** | **~15,145** |
>
> **`SKILL.md` es el que hay que vigilar:** creció un 63% y es el que se carga en **cada
> activación** de la skill. Con ~3,800 tokens\* sigue por debajo de los 5k que Anthropic
> recomienda para el cuerpo de un `SKILL.md`, así que no urge — pero si vuelve a crecer, el
> siguiente movimiento es mover a `references/` lo que no se lee en cada paso (las secciones de
> notación y primer contacto son candidatas).
>
> Es exactamente el caso que justifica que el nivel 1 sea **un script y no una tabla escrita a
> mano** (§9): esta caducó en un día.

Medida sobre el recorrido real de `output/huertos-urbanos-mx/`: 6 pasos ejecutados
(`html_1 → html_4 → html_5 → html_7 → html_8 → html_11`) y 5 omitidos. Todas las cifras con `*`
son la aproximación `caracteres ÷ 4`.

### Arranque fijo (E1) — una vez por sesión

| Archivo | Caracteres | Tokens |
| --- | --- | --- |
| `pasos.json` | 14,351 | ~3,588* |
| `AGENTS.md` | 11,537 | ~2,884* |
| `_plantilla_html/README.md` | 10,470 | ~2,618* |
| `SKILL.md` (macro) | 9,304 | ~2,326* |
| `sub-skills/CONTRATO_JSON.md` | 4,154 | ~1,038* |
| **Total** | **49,816** | **~12,454**\* |

### Sub-skills del recorrido (E3) — una vez por paso que las invoca

| Sub-skill | `SKILL.md` | `references/` | Tokens |
| --- | --- | --- | --- |
| `persona-profile` | 11,226 | 8,203 | ~4,857* |
| `problem-solution-fit` | 10,290 | 7,843 | ~4,533* |
| `ideacion` | 7,085 | 2,181 | ~2,316* |
| `benchmark-mercado` | 8,597 | 0 | ~2,149* |
| `how-might-we` | 6,805 | 1,345 | ~2,038* |
| `online-ads` | 7,446 | 0 | ~1,862* |
| `landing-page` | 7,279 | 0 | ~1,820* |
| **Total (7 sub-skills)** | | | **~19,575**\* |

Para dimensionar el ahorro de cargar por paso: las **26** `SKILL.md` suman 236,426 car
(~59,106*) y todas sus `references/` otros 106,570 car (~26,642*). Cargar el repo entero de una
vez costaría **~85,700 tokens\*** de entrada; el recorrido de 6 pasos usó ~19,575* — un 23%.
Mediana de `SKILL.md`: 7,593 car; el mayor (`senales-debiles`) 25,868 car, 3.4× la mediana.

### Coste por paso (E2 y S1)

| Paso | `mostrar` (E2) | `reporte.json` producido (S1) |
| --- | --- | --- |
| `html_1` | ~692* | ~2,022* |
| `html_4` | ~737* | ~1,684* |
| `html_5` | ~643* | ~2,263* |
| `html_7` | ~861* | ~2,590* |
| `html_8` | ~609* | ~3,083* |
| `html_11` | ~873* | ~2,552* |
| **Total** | **~4,415**\* | **~14,194**\* |

`mostrar` es barato y plano: entre 609 y 873 tokens* por paso, sin crecer con el avance del
flujo. El briefing no es un problema de coste.

### Herencia (E4) — el único coste que crece

Acumulado heredable después de cerrar cada paso:

| Tras cerrar | Cadena disponible | Tokens |
| --- | --- | --- |
| `html_1` | 1 reporte | ~2,022* |
| `html_4` | 2 reportes | ~3,706* |
| `html_5` | 3 reportes | ~5,969* |
| `html_7` | 4 reportes | ~8,560* |
| `html_8` | 5 reportes | ~11,642* |
| `html_11` | 6 reportes | ~14,194* |

De aquí sale la pregunta 4 del alcance, que es la decisión de diseño con más impacto:

| Estrategia de lectura | Coste total de herencia |
| --- | --- |
| **Solo el predecesor directo** | ~11,642* |
| **Toda la cadena en cada paso** | ~31,899* |

Releer la cadena completa cuesta **2.7× más** y es lo que hoy no está acotado en `SKILL.md`.

### Total del recorrido medido

| Concepto | Tokens |
| --- | --- |
| Entrada: arranque fijo (E1) | ~12,454* |
| Entrada: sub-skills (E3) | ~19,575* |
| Entrada: briefings (E2) | ~4,415* |
| Entrada: herencia (E4) | ~11,642*a ~31,899* |
| **Entrada total** | **~48,086* a ~68,343*** |
| **Salida total (S1)** | **~14,194*** |

Referencia de lo que **no** se cuenta: los 6 HTML entregados pesan 1,182,993 car (~295,748
tokens*) que el modelo nunca emite.

---

## 6. Protocolo de comparación: completa contra mínima

La comparación solo es válida si las dos corridas comparten proyecto y decisiones. Condiciones:

1. **Mismo proyecto congelado:** nombre, objetivo y audiencia idénticos.
2. **Mismas decisiones** en los nodos que las dos rutas comparten (`html_1`, `html_4`, `html_7`,
   `html_8`, `html_11`).
3. **Ruta mínima con `init --ruta minima`**, no omitiendo pasos a mano: así los 6 pasos fuera del
   recorrido quedan omitidos de entrada, como en uso real.
4. **Ruta completa sin omisiones.** Es el techo del coste.
5. **La misma estrategia de herencia** en las dos, declarada antes de empezar (predecesor directo
   o cadena completa).

Lo que se reporta por ruta: entrada y salida, el desglose E1–E4/S1, el paso más caro y el
acumulado de herencia al cerrar.

**El recorrido de la línea base no es ninguna de las dos rutas** (6 pasos: la mínima más
`html_5`), así que sus cifras son punto de partida, no el resultado de la comparación.

---

## 7. Qué decisiones puede cambiar esta medición

La medición no es un ejercicio contable: cada resultado tiene una acción asociada.

- **Si la herencia domina el coste** → acotar en `SKILL.md` qué `reporte.json` abre cada paso
  (solo predecesores directos) o hacer que `mostrar` imprima un extracto de los bloques
  heredables en vez de la ruta del archivo completo.
- **Si una sub-skill se sale de la mediana** → partir su `SKILL.md`, moviendo el detalle a
  `references/` que solo se lean cuando toca. `senales-debiles` (3.4× la mediana) es la
  candidata evidente.
- **Si el arranque fijo pesa demasiado** → `AGENTS.md` y `_plantilla_html/README.md` (~6,500
  tokens* juntos tras el crecimiento del 14/08) no hacen falta en cada paso: se pueden citar
  bajo demanda.
- **Si `SKILL.md` pasa de 5k tokens\*** → partirlo: mover a `references/` lo que no se lee en
  cada paso. Va por ~3,800* y creció un 63% en un día, así que es el archivo con más riesgo de
  cruzar el umbral. Es el único que se carga en **cada activación**.
- **Si la diferencia entre rutas es pequeña** → la ruta mínima deja de venderse como «más
  barata» y se justifica solo por tiempo del usuario, que es un argumento distinto.
- **Si el `reporte.json` de un paso se dispara** → revisar si está duplicando datos que ya
  vienen heredados del predecesor.

---

## 8. Definición de terminado

Este plan se considera ejecutado cuando:

- [ ] `skills_env` tiene un tokenizador y las cifras dejan de llevar `*` por estimación.
- [ ] `scripts/medir_tokens.py` existe, corre desde la raíz y emite CSV.
- [ ] El nivel 1 está corrido sobre las dos rutas.
- [ ] El nivel 2 está corrido 2 veces por ruta con el proyecto congelado.
- [ ] La sección «Resultados» de este documento tiene la tabla comparativa.
- [ ] Cada hallazgo de §7 que se cumpla tiene su acción abierta o descartada por escrito.

---

## 9. Limitaciones declaradas

- El estimador `÷4` puede desviarse de forma apreciable en texto español con acentos y en JSON,
  donde las llaves y comillas gastan tokens propios. Ninguna cifra de §5 sirve para presupuestar.
- El nivel 2 no es reproducible: se reporta el rango de las repeticiones, nunca un solo número.
- La medición es de un repo en una fecha. Cada vez que crezca un `SKILL.md`, la línea base
  caduca: por eso el nivel 1 tiene que ser un script y no una tabla escrita a mano.

## Referencias

| Para | Mira |
| --- | --- |
| Definición del flujo y rutas | `pasos.json` |
| El ciclo de un paso y qué se lee en cada uno | `SKILL.md` |
| Regla de herencia entre pasos | `AGENTS.md` § 6 y `sub-skills/CONTRATO_JSON.md` § Encadenamiento |
| Recorrido real de la línea base | `output/huertos-urbanos-mx/STATE.md` |
