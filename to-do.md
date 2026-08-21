# To-do — 21/08/2026

**Nuevo el 21/08** Script .ps1 y .sh para poder generar una copia de AGENTS.md  para convertirla a CLAUDE.md a demanda del usuario
Esto solo lo actualiza la persona no el agente

**Nuevo el 19/08:** las 5 skills simuladoras de entrevistas se integraron al flujo como
**sub-sub-skills** (`<skill>/simulador/SIMULADOR.md`), con estadística calculada por script y la
marca SIMULADO propagándose sola a todos los reportes. Detalle en «Hecho el 19/08/2026».

Los 5 pendientes del 13/08 están cerrados. El rechazo del ZIP por el gestor de habilidades
también: **subida confirmada el 14/08/2026** tras encontrar la causa raíz (barra invertida en las
entradas del ZIP) y tres problemas reales más por el camino.

Pendiente de aprender del uso real: si la skill se comporta bien ya instalada en el gestor.

Los otros dos sospechosos que quedaron **sin confirmar como problema** —el punto en las carpetas
de fase (`1.Investigacion`) y el guion bajo inicial (`_plantilla_html`)— se dejaron como están a
propósito: renombrarlos costaba decenas de referencias y resultó innecesario.

> **Antes de dar algo por hecho, compruébalo en el código.** La fuente de verdad es el repo,
> no este tracker.

Entorno para cualquier prueba (AGENTS.md y/o CLAUDE.md §2):

```powershell
& "E:\Users\1167486\AppData\Local\anaconda3\Scripts\conda.exe" shell.powershell hook | Out-String | Invoke-Expression
conda activate skills_env
```

Nada está commiteado: los commits los lleva el usuario.

---

### 1. Terminar la medición de tokens — falta el nivel 2

El **nivel 1 está hecho** (17/08): `tiktoken` instalado en `skills_env`, `scripts/medir_tokens.py`
escrito (emite CSV) y los resultados exactos publicados en `PLAN_MEDICION_TOKENS.md` § Resultados.
E1 = 17,899 tok; E3 completa 124,968 vs mínima 52,721; herencia: declarados 14,875 vs cadena
35,754 (2.4×).

Falta el **nivel 2**: sesión instrumentada, 2× por ruta, con el mismo proyecto congelado. No se
automatiza — requiere una sesión real del usuario por ruta. Checklist en `PLAN_MEDICION_TOKENS.md` §8.

### 2. Decidir la estrategia de herencia — cerrado (hecho)

Decidido: **leer solo los predecesores declarados en `pasos.json`** (los que `mostrar` lista),
no toda la cadena. La cadena completa cuesta 2.4× más y no aporta bloques nuevos — los bloques
no son acumulativos (`persona` está en html_4, `psf` en html_5, html_7 necesita ambos). Escrito
en `SKILL.md` § «El ciclo de un paso», punto 5, y en `PLAN_MEDICION_TOKENS.md` § Resultados.

### 3. Partir el `AGENTE.md` de `senales-debiles` — cerrado (superado)

La modularización **ya está hecha**: orquestador `AGENTE.md` (26,409 car) + `SPEC.md` (18,033) +
`references/fase-0…4` y `design-system.md`. El orquestador sigue en **3.4×** la mediana de las 26
sub-skills, pero su contenido son las reglas globales y el contrato JSON entre fases, no detalle
que deba bajar a `references/`. Si se recortara más, sería cosmético y no urge.

### 4. Avisos de markdownlint que quedan (MD013) — cerrado (hecho)

Creado `.markdownlint.json` en la raíz con `"MD013": false`. La prosa del repo usa líneas largas
a propósito (hasta 747 car en los prompts base), así que desactivar la regla es lo correcto en
vez de reescribir 30 documentos. El editor que use markdownlint lo descubre solo.

### 5. Decidir qué se hace con `skills_simuladoras_de_entrevistas/` — decisión del usuario

Es la carpeta original con las 5 skills hechas en opencode. Su contenido ya está integrado en el
flujo (`<skill>/simulador/`), así que **queda duplicado y fuera del flujo**: quien la encuentre
suelta se llevará una versión sin estadística por script y sin la marca automática.

No la borré: es material del usuario y borrar no es reversible. Cuando confirme que la
integración le sirve, se elimina —o se deja como archivo histórico, pero entonces conviene un
`README.md` dentro que diga «superado por `sub-skills/2.Descubrimiento/*/simulador/`».

### 6. Ver un reporte simulado en el navegador

La marca SIMULADO se verificó en el **markup** del HTML generado (distintivo en cabecera, caja
ámbar del contexto, línea del pie, advertencia automática) y el script inline de la plantilla
pasa `node --check`. Lo que no se hizo es **abrirlo en un navegador** para ver que el distintivo
dorado no se pisa con el de la skill ni rompe la cabecera en móvil.

Está a un comando: generar cualquier reporte con un `flujo_estado.json` que tenga la decisión de
simular registrada, y abrirlo.

### 7. Guardar una muestra de diseño del reporte simulado

`sub-skills_sample_outputs/` es «¿dónde veo ejemplos de diseño?» (AGENTS.md §8) y no tiene
ninguna salida con la marca de simulación. Conviene guardar una: es el único caso del repo donde
la plantilla añade elementos por su cuenta, y sin muestra nadie sabe cómo se ve.

### 8. Estrenar un simulador en un proyecto real

Ningún proyecto ha corrido todavía la cadena completa **decisión → `plan.json` → CSV → skill
padre → HTML marcado → cierre con los dos archivos**. Es la misma prueba de fuego que quedó
pendiente para `--datos`, y ahora se pueden hacer las dos de una: un proyecto corto que simule
las entrevistas del paso 2, construya la ficha de persona del paso 4 con esa evidencia y
compruebe que la ficha sale marcada como simulada sin que nadie se lo pida.

Lo que hay que mirar con ojo crítico en ese estreno: **si los avisos de los scripts ayudan o
estorban**. Están calibrados a ojo (n<20, Q+R>10%, saturación en 2 sesiones sin novedad), y el
uso real es lo único que dice si el umbral es el correcto.

---

## Hecho el 19/08/2026

### Simuladores de entrevistas y encuestas, integrados como sub-sub-skills

Las 5 skills que el usuario había creado en opencode (`skills_simuladoras_de_entrevistas/`)
quedaron dentro del flujo, con tres cambios de fondo respecto al original.

**1. Ubicación y convención.** Cada simulador vive dentro de la sub-skill que analizaría esos
datos, con el archivo de instrucciones llamado **`SIMULADOR.md`** —ni `SKILL.md` (uno por ZIP, y
lo ocupa la macro) ni `AGENTE.md` (lo ocupa la sub-skill padre):

```text
sub-skills/2.Descubrimiento/<skill>/simulador/
├── SIMULADOR.md
└── scripts/simular_<x>.py
```

Convención escrita en **`sub-skills/SIMULACION.md`** (nueva, canónica) y en AGENTS.md §4.1.

**2. Un CSV y nada más.** El simulador fabrica el dato; no analiza, no genera HTML y no cierra
pasos. La skill padre analiza ese CSV con los mismos scripts que usaría con datos reales — por
eso `clasificar_kano.py` se come el CSV simulado sin cambios. Los CSV se llaman `*_SIMULADO.csv`
y llevan columna `simulado` y `seed` en cada fila, para que el archivo se declare solo si se
separa de su contexto.

**3. La estadística la hace el script, no el LLM.** El LLM escribe un `plan.json` con el
contenido cualitativo (panel de personas, códigos, citas) y las **prevalencias declaradas**; el
script sortea, cuenta y calcula. Lo que aporta cada uno:

| Simulador | Instrumento | Estadística |
| --- | --- | --- |
| `simular_kano.py` | Kano funcional × disfuncional | Matriz oficial (idéntica al clasificador, 25 celdas verificadas), moda por feature, IC de Wilson, coeficientes de Berger CS/DS —suprimidos si la base A+O+M+I no llega a la mitad—, tasa de descartables, margen de error |
| `simular_discovery.py` | Encuesta de descubrimiento | Proporciones con IC de Wilson, `n` requerido con las fórmulas de `calcular_muestra.py` (+ población finita y envíos), prueba z de dos proporciones entre segmentos |
| `simular_entrevistas.py` | Entrevistas 1:1 | Conteos y **curva de saturación** de códigos. Sin porcentajes: con n=6 el margen sería de ±40 pp |
| `simular_aditl.py` | Observación etnográfica | Conteos por tipo (incl. workarounds) y saturación por sesión; avisa de jornadas sin fricciones |
| `simular_expo.py` | Interacciones en feria | Conteos, saturación, asistentes vs. expositores, `solo_tipo` para que los hallazgos de competencia solo salgan de expositores |

Los cinco: semilla obligatoria (reproducible byte a byte), `ruido` que encoge la prevalencia
hacia 0.5 para que el resultado no salga de laboratorio, aviso si ningún código refuta la
hipótesis, y el límite **«validez externa: nula»** impreso en cada ejecución. Sin esa frase los
intervalos serían decoración pseudo-científica: describen al generador, no a una población.

**4. La marca SIMULADO se propaga sola.** La opción de `pasos.json` marcada
`marca_simulacion: true` (dos opciones de `html_2`) enciende `flujo.simulacion` en el contexto
del flujo, y de ahí sale, en **todos** los HTML posteriores: distintivo dorado «Datos simulados»
en la cabecera, caja ámbar «esto no es evidencia de campo» como primer bloque del contexto,
`DATOS SIMULADOS` en el pie, prefijo `SIMULADO ·` en el título de la pestaña y una advertencia
automática si ninguna de las declaradas menciona la simulación. Ninguna skill tiene que
acordarse de etiquetar. Para skills sueltas hay `meta.simulado: true`.

**Archivos tocados:** `sub-skills/SIMULACION.md` (nuevo) · 5 × `simulador/SIMULADOR.md` (nuevos)
· 5 × `simulador/scripts/simular_*.py` (nuevos) · `pasos.json` (`marca_simulacion` + campo
`simuladores` en html_2/html_3) · `scripts/estado_flujo.py` (`detectar_simulacion`, bloque
`flujo.simulacion`, aviso en `mostrar`, banner en `STATE.md`) ·
`_plantilla_html/templates/reporte_base.html` (distintivo, caja, pie, título, advertencia
automática) · `_plantilla_html/scripts/validar_report_data.py` (`_validar_simulacion`: 2 WARN) ·
`_plantilla_html/README.md` · `AGENTS.md` (§3, §4, §4.1, §8) · `SKILL.md` (§5.1) ·
`sub-skills/CONTRATO_JSON.md` (regla 5) · 5 × `AGENTE.md` y 5 × `README.md` de las skills padre ·
`flujo_agentes.md` · `README.md`.

**Verificado:** `py_compile` de los 5 scripts + los 2 modificados; los 5 simuladores ejecutados
con planes reales; reproducibilidad por semilla (mismo hash con la misma, distinto con otra);
matriz Kano del simulador **idéntica** a la del clasificador y conteos coincidentes (200 filas);
`clasificar_kano.py` consume el CSV simulado sin cambios; validaciones de plan inválido devuelven
exit 2 con mensaje útil; detección de la simulación en `mostrar` (antes/después de registrar la
decisión), en los 4 simuladores de html_3 y en `STATE.md`; HTML generado con
`flujo.simulacion.activo` y las cuatro marcas presentes; los 2 WARN del validador cuando la skill
olvida la marca; script inline de la plantilla pasa `node --check`; ZIP de sub-skill suelta con el
simulador dentro, un solo `SKILL.md`, 0 barras invertidas y la referencia `../AGENTE.md` reescrita
a `../SKILL.md`; ZIP completo de la macro con los 5 simuladores (177 entradas, un `SKILL.md`);
comprobación de rutas seguras sin hallazgos.

**No verificado:** el render en un navegador (ver pendiente 6).

## Hecho el 17/08/2026

### 1. Medición de tokens — nivel 1 ejecutado

- **`tiktoken` instalado** en `skills_env` (0.14.0) y `scripts/medir_tokens.py` escrito: mide
  E1 (arranque fijo), E3 (sub-skills por ruta) y, con `--proyecto`, E2 (briefing de `mostrar`),
  E4 (herencia en tres estrategias) y S1 (salida). Emite CSV.
- **Resultados publicados** en `PLAN_MEDICION_TOKENS.md` § Resultados. Confirmó que el estimador
  `÷4` subestimaba un 18% (E1 real 17,899 vs ~15,145).
- **Pendiente nivel 2** (sesión instrumentada, 2× por ruta): requiere sesión real del usuario.

### 2. Estrategia de herencia decidida

**Predecesores declarados** (los que `pasos.json` lista), no la cadena completa. La cadena cuesta
2.4× más (35,754 vs 14,875 tokens en el recorrido de 6 pasos) y no aporta bloques: `persona` y
`psf` viven en reportes distintos. Escrito en `SKILL.md` § «El ciclo de un paso», punto 5.

### 3. Avisos de markdownlint (MD013) cerrados

`.markdownlint.json` en la raíz con `"MD013": false`. La prosa larga es la convención del repo
(hasta 747 car en los prompts base), no un defecto.

---

## Hecho el 14/08/2026

### Cuarta ronda: la CAUSA RAÍZ — barra invertida en las entradas del ZIP — **hecho**

`Compress-Archive` escribía las 171 entradas con la barra invertida de Windows
(`iris-flujo-de-innovacion\SKILL.md`). El formato ZIP exige `/`, y el validador del gestor —que
corre en Linux— lee el `\` como **parte del nombre del archivo**: de ahí
`Zip file contains path with invalid characters`. Las tres rondas anteriores arreglaron problemas
reales, pero ninguno era este.

**Aviso lo dio Gemini**, y mi verificación previa lo había ocultado: `zipfile` de Python
**normaliza** `\` a `/` en Windows dentro de `ZipInfo.__init__`, así que `namelist()` devolvía 0
backslashes. Falso negativo. La comprobación válida es `orig_filename` o los bytes del directorio
central:

```text
namelist()      -> 0 entradas con backslash   (MIENTE en Windows)
orig_filename   -> 171 de 171
bytes del ZIP   -> 171 con 0x5C, 0 con 0x2F
```

**Arreglo:** `empaquetar_skill.ps1` ya no usa `Compress-Archive`. Construye el ZIP con
`System.IO.Compression.ZipArchive` y escribe el nombre de cada entrada a mano, normalizando a `/`.
De paso desaparecen las 6 entradas de directorio (171 → 165 entradas, solo archivos).

**Guardia nuevo:** los dos scripts **releen el directorio central del ZIP escrito** y avisan si
alguna entrada lleva `0x5C`. Es la única comprobación que no se puede falsear con herramientas que
normalizan rutas.

**Verificado:** el ZIP final tiene 165 entradas, **0 con `0x5C` y 165 con `0x2F`**; el guardia se
validó en los dos sentidos (avisa en un ZIP con backslashes hecho a propósito, calla en el bueno);
extraído en limpio el flujo corre y las 26 rutas resuelven. La sub-skill suelta también sale con
barras normales.

**No reproducible a demanda:** en pruebas posteriores con estructuras equivalentes,
`Compress-Archive` (módulo 1.2.5, PowerShell 7.6.3) sí escribió `/`. No documento un mecanismo que
no pude aislar; lo que consta es que el paquete real salió con `\` 171 de 171 veces, que ya no
dependemos de ese cmdlet y que el guardia detectaría cualquier regresión.

### Tercera ronda: `Zip must contain exactly one SKILL.md file` — **hecho**

Con los caracteres y la estructura ya arreglados, el gestor pasó al siguiente validador:
**exactamente un `SKILL.md` por ZIP**, y el paquete llevaba 27 (el de la macro más los 26 de las
sub-skills).

**Solución:** el archivo de instrucciones de cada sub-skill se llama ahora **`AGENTE.md`** —el
repo ya llamaba «agente» a cada sub-skill (`flujo_agentes.md`, «Agente HMW»…)—. Los 26 se
renombraron con `git mv`; el único `SKILL.md` del repositorio es el de la macro, en la raíz.

**El truco que evita dos verdades:** al empaquetar una sub-skill suelta (`-SubSkill`), el script
le devuelve el nombre `SKILL.md` —el archivo **y** las referencias de texto dentro del paquete—,
porque en ese ZIP la sub-skill sí es la skill. Así cada paquete es coherente consigo mismo y el
repo tiene una sola convención.

Referencias actualizadas: `pasos.json` (`nota_rutas`), `SKILL.md` de la macro (paso 5 del ciclo),
`AGENTS.md` (§3, §4 y §5), `scripts/estado_flujo.py` (lo que imprime `mostrar`),
`_template_generador_skill.py`, `README.md` y las 13 auto-referencias dentro de `sub-skills/`
(casi todas de `senales-debiles`).

**Guardia nuevo:** los dos scripts cuentan los `SKILL.md` del stage y avisan si no hay exactamente
uno, nombrando los culpables.

**Verificado:** el ZIP tiene 1 `SKILL.md` y 26 `AGENTE.md`; extraído en limpio, `init` y `mostrar`
funcionan y las 26 rutas de `pasos.json` resuelven a un `AGENTE.md` real; el ZIP de
`senales-debiles` suelta trae 1 `SKILL.md`, 0 `AGENTE.md` y su texto ya dice `SKILL.md`; el
guardia se probó duplicando un `SKILL.md` y avisa con la lista.

### Segunda ronda: eran DOS problemas — **hecho**

Quitar los acentos no bastó: el gestor seguía respondiendo `Zip file contains path with invalid
characters`. La auditoría carácter por carácter del ZIP encontró **dos causas más**, una de
caracteres y otra de estructura.

**a) Caracteres.** Además de los acentos sobraban:

- **40 espacios** en 22 rutas (`How Might We.md`, `Landing Page.md`…), incluida
  `Referral builder .md` con un espacio antes de la extensión.
- **un `&`** en `Journey Builder & Structure.md`.

Las 22 estaban todas en `Documentos_prompts_base_md/` y `_docx/`. Los 48 archivos de las dos
carpetas se renombraron a kebab-case con `git mv` (`journey-builder-structure.md`,
`referral-builder.md`, `how-might-we.md`…). Referencias actualizadas en la tabla de
`PLAN_CONVERSION_SKILLS.md`. **Regla nueva, más estricta que «solo ASCII»:** los nombres usan
solo `[A-Za-z0-9._-]`.

**b) Estructura.** La documentación oficial exige **una sola carpeta de primer nivel llamada
igual que el `name` del frontmatter**; el ZIP ponía los archivos sueltos en la raíz. Los dos
scripts ahora leen el `name` del `SKILL.md`, envuelven todo en `iris-flujo-de-innovacion/` y
avisan si ese `name` no es `[a-z0-9-]`. En el modo `-SubSkill`, `_plantilla_html/` pasó a ir
**dentro** de la carpeta de la sub-skill, porque todo el ZIP tiene que colgar de una sola raíz.

**Verificado:** el ZIP tiene una única carpeta raíz que coincide con el frontmatter, 0
caracteres fuera de `[A-Za-z0-9._-]`, 0 espacios, 0 `&`, 27 `SKILL.md` (1 de la skill + 26 de
sub-skills como recurso). Extraído en limpio, el flujo corre entero desde dentro: `init`,
`mostrar` con rutas ASCII y generación de HTML con el logo oficial.

**Pendiente de confirmar contigo:** si 27 `SKILL.md` en un mismo ZIP molestan al gestor. La
documentación no lo prohíbe —los recursos empaquetados son explícitamente compatibles— y el error
que da es de caracteres, no de estructura, pero no está documentado. En
`output/diagnostico-zip/` quedaron 3 ZIP para aislarlo subiéndolos en orden: `1-minimo.zip`
(1 `SKILL.md`), `2-con-subskills.zip` (27) y `3-completo.zip`.

### Rutas solo ASCII: primer intento — **hecho, pero insuficiente por sí solo**

El gestor rechazaba el ZIP con `Zip file contains path with invalid characters`. **Causa:** las
rutas con acento. El ZIP estaba bien formado (separador `/`, bandera UTF-8 correcta, sin
backslashes); lo que sobraba eran 103 rutas no-ASCII —88 en `sub-skills/` y 15 en
`Documentos_prompts_base_md/`— por tres caracteres: `ó`, `í` y `é`. Los espacios en los nombres
no eran el problema.

Renombrado en el repo con `git mv` (historial preservado, git lo registra como *rename*):

| Antes | Ahora |
| --- | --- |
| `1.Investigación/` | `1.Investigacion/` |
| `3.Ideación/` | `3.Ideacion/` |
| `5.Validación/` | `5.Validacion/` |
| `Entrevistas de Empatía.md` / `.docx` | `Entrevistas de Empatia.…` |
| `Dimensionador Estratégico de Ideas.md` / `.docx` | `Dimensionador Estrategico de Ideas.…` |
| `Ideación.md` / `.docx` | `Ideacion.…` |

Las 9 carpetas se renombraron en `sub-skills/`, `Documentos_prompts_base_md/` y
`Documentos_prompts_base_docx/`, más `sub-skills_sample_outputs/Investigación`.

Referencias de ruta actualizadas: `pasos.json` (32), `flujo_agentes.md` (5), `AGENTS.md` (3),
`scripts/estado_flujo.py` (1), `PLAN_MEDICION_TOKENS.md` (1) y los 3 nombres de prompt en
`PLAN_CONVERSION_SKILLS.md`. **La prosa conserva el acento** a propósito: «Entrevistas de
Empatía», «Dimensionador Estratégico de Ideas de Negocio» y los `> Fase: 1.Investigación` de los
README no son rutas. La `nota_rutas` de `pasos.json` ya no dice «acentos incluidos»: dice por qué
van sin tilde.

**Prevención:** los dos scripts de empaquetado escanean el stage antes de comprimir y avisan con
la lista de rutas culpables y el mensaje exacto del gestor. La regla quedó escrita en `AGENTS.md`
§5 («Rutas solo ASCII») con el comando para comprobarlo, y en `README.md`.

**Verificado:** las 26 rutas de `pasos.json` resuelven en disco y son ASCII; el ZIP tiene 170
entradas, **0 no-ASCII**, 0 backslashes, `SKILL.md` en la raíz y las 26 sub-skills; un `init`
nuevo y el `mostrar` de un paso devuelven rutas ASCII; la cadena `--datos` del proyecto real
sigue pasando entera; el guardia se probó plantando un archivo acentuado y avisa en `.ps1` y
en `.sh`.

## Hecho el 13/08/2026 (tarde)

### 1. Empaquetar una sub-skill sola — **hecho**

`empaquetar_skill.ps1` y `empaquetar_skill.sh` producen el ZIP de una sub-skill suelta:

```powershell
.\empaquetar_skill.ps1 -SubSkill "2.Descubrimiento/persona-profile"
.\empaquetar_skill.ps1 -ListSubSkills          # las 26 rutas válidas
```

```bash
./empaquetar_skill.sh --sub-skill "2.Descubrimiento/persona-profile"
./empaquetar_skill.sh --list-sub-skills
```

Contenido: `<sub-skill>/` + `_plantilla_html/`, nada más. El ZIP sale como `<sub-skill>.zip`
(0.13 MB) salvo que se pase `-Output`/`-o`. `-IncludeSamples`/`--samples` añade las muestras de
esa sub-skill en `sample_outputs/`; `--flujo`, `--docx` y `--temp` no aplican y avisan. Ruta
inexistente → error con la lista de sub-skills válidas. Documentado en `README.md` § «Empaquetar
una sub-skill sola» y en la regla «Extraíble» de `AGENTS.md` §4.

**Verificado:** descomprimido en carpeta limpia y generado el HTML con `--sin-flujo` sin
`--logo` → `logo embebido: 122 KB (base64) · copia local de la sub-skill`. Los dos scripts
producen **exactamente los mismos 9 archivos** (comparado ZIP contra tar.gz). El modo macro
sigue en 3 MB.

De paso se arreglaron dos fallos del `.sh`, uno de ellos heredado: el `find -exec sh -c` trataba
el directorio destino como un archivo más (`cp: -r not specified`), y el respaldo `tar` no podía
escribir en rutas con `:` (ahora va a stdout redirigido).

### 2. Estrenar `--datos` en un proyecto real — **hecho**

Proyecto **«Huertos urbanos MX»** recorrido de punta a punta en `output/huertos-urbanos-mx/`
(carpeta ya ignorada por `.gitignore`): 11 pasos resueltos, 6 ejecutados
(`html_1 → html_4 → html_5 → html_7 → html_8 → html_11`) y 5 omitidos, 8 decisiones registradas,
17 artefactos.

Lo que confirma el recorrido:

- **`problem-solution-fit` hereda de verdad.** Los 4 problemas de `html_5` son los 4
  `persona.pains[]` de `html_4` con **texto idéntico y el mismo número** — el `reporte.json` del
  predecesor se abre y se lee, no se reteclea del resumen. Comprobado campo por campo.
- **La frontera persona ↔ PSF se sostiene.** `html_4` entrega los pains sin `importancia`,
  `satisfaccion`, `solucion` ni `costo`; `html_5` es quien los puntúa. La matriz sale derivada,
  sin ningún `chart` escrito a mano.
- **El canal llega hasta el final.** `flujo.ruta[]` de `html_11` propaga los `datos` de los 5
  pasos previos; el `mostrar` de cada paso imprime `datos estructurados: reporte_html_N.json`.
- **`exportar_csv.py` cierra el círculo:** el CSV sale del mismo `reporte.json`, 4 filas, con el
  texto del pain 1 intacto.
- **El script de `ideacion` manda en los scores:** `evaluar_ideas.py` calculó promedios y
  ranking, y el reporte los leyó sin recalcularlos.

**Sobre los avisos de la barrera de predecesores:** en un recorrido bien ordenado —cerrar o
omitir cada paso a su turno— **no salió ni un solo aviso**. No estorban. Los que sí salen son
los de `completar` sin `--resumen` o sin `--datos`, y ahí ayudan.

**Contenido SIMULADO a propósito.** Sin acceso a usuarios reales, el recorrido entra por la
rama de supuestos (el `auto_si` de `pasos.json` la fuerza al estar `html_2` y `html_3` omitidos)
y los 6 reportes lo declaran en `meta.metodologia` y en `advertencias`. Sirve como prueba de la
máquina, **no** como investigación de mercado.

### 3. Verificar la línea nueva de `STATE.md` — **hecho**

Comprobada a ojo: cerrar `html_7` con `--forzar` saltando `html_4` imprime en el Historial

```text
  - **predecesores saltados con `--forzar`:** html_4
```

junto con los tres avisos correspondientes (predecesor duro saltado, predecesores blandos
abiertos y falta de `--datos`).

### 4. Cosmético — **hecho**

- **Los 3 README atípicos** (`foresight`, `senales-debiles`, `dimensionador-estrategico`) ya no
  se contradicen: el encabezado principal es «Salida principal — su propio HTML detallado» (o
  «su propio dashboard HTML (+ PPTX)») y el reporte de la plantilla compartida pasó a un segundo
  encabezado, «Resumen del paso». Se fue la nota aclaratoria que corregía al título.
- **`AGENTS.md`** quedó sin los avisos que listaba el to-do: listas de §7 con `-` en vez de `*`
  (MD004), los dos bloques de código sin lenguaje ahora son ```text (MD040) y la tabla de §8 usa
  `| --- | --- |` como el resto del repo (MD060). Se arregló también el `### Autor` de `README.md`
  que saltaba de H1 a H3 (MD001).
- **`render_state_md`** genera la tabla de `STATE.md` con el mismo estilo `| --- |`.

### 5. Plan de medición de tokens — **hecho** (escrito, no ejecutado)

`PLAN_MEDICION_TOKENS.md`. El alcance, que era lo que faltaba definir, queda fijado: entran el
arranque fijo, el briefing de `mostrar`, las sub-skills del paso, la herencia y el `reporte.json`
generado; quedan fuera los turnos del human-in-the-loop, el razonamiento, el system prompt del
gestor y los insumos del usuario.

**El HTML también queda fuera, y es el hallazgo que justifica la decisión:** lo escribe
`generar_html.py`, no el modelo. Los 6 HTML del recorrido pesan **20.8×** sus `reporte.json`
(~295,700 contra ~14,200 tokens\*), así que contarlos como salida inflaría la cifra 21 veces.

El plan incluye una línea base real: arranque fijo ~12,450 tokens\*, las 7 sub-skills del
recorrido ~19,575\* (23% de lo que costaría cargar las 26 y sus `references`), `mostrar` plano
entre 609 y 873\* por paso, y la herencia como único coste que crece.

## Hecho el 13/08/2026 (mañana — contexto)

1. **`exportar_csv.py` lee el bloque `psf`.** Deriva las filas de `secciones[].items[].psf`
   aplicando el mapeo de `references/analisis-psf.md`. Sigue aceptando la entrada anterior
   (`[{...}]`, `{"filas": [...]}`) y un `{"psf": {...}}` suelto.
2. **Barrera de predecesores en la máquina de estados.** `iniciar` y `completar` avisan si un
   predecesor sigue abierto y **bloquean** (exit 2) si no es omitible, con `--forzar` como
   escape. Los `predecesores` de `pasos.json` son alternativos entre sí, así que un paso cuenta
   como resuelto si está completado, omitido o fallido.
3. **Muestras de diseño de los bloques nuevos** en `sub-skills_sample_outputs/2.Descubrimiento/`.

## Hecho el 12/08/2026 (contexto)

1. **Frontera persona ↔ PSF.** Las secciones 11–13 del template *Persona Profile* pertenecen a
   `problem-solution-fit` (`html_5`) y ya no se rellenan en `html_4`.
2. **Autonomía de las 26 sub-skills.** El logo cae en `assets/logo.png`; 24 rutas `../../../`
   corregidas y «Uso independiente» añadido a las 26. Regla «Extraíble» en AGENTS.md §4.
3. **Herencia de datos entre pasos.** `completar --datos reporte.json` viaja como
   `flujo.ruta[].datos`; `CONTRATO_JSON.md` ganó `decision.contexto_usado` y «Encadenamiento».
