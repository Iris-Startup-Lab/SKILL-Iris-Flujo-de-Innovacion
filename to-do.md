# To-do — 13/08/2026 (cierre)

Los 5 pendientes que quedaban abiertos están **cerrados**. Abajo está qué se hizo, cómo se
comprobó y lo que queda abierto de aquí en adelante.

> **Antes de dar algo por hecho, compruébalo en el código.** La fuente de verdad es el repo,
> no este tracker.

Entorno para cualquier prueba (AGENTS.md §2):

```powershell
& "E:\Users\1167486\AppData\Local\anaconda3\Scripts\conda.exe" shell.powershell hook | Out-String | Invoke-Expression
conda activate skills_env
```

Nada está commiteado: los commits los lleva el usuario.

---

## Abierto

### 1. Ejecutar el plan de medición de tokens

`PLAN_MEDICION_TOKENS.md` define el alcance, los dos niveles de medición, el protocolo de
comparación y una línea base tomada sobre el recorrido real. Lo que falta es **ejecutarlo**:

- Instalar un tokenizador en `skills_env` (no hay `tiktoken` ni `transformers`), para que las
  cifras dejen de ser la aproximación `caracteres ÷ 4` marcada `*`.
- Escribir `scripts/medir_tokens.py` (nivel 1, determinista, salida CSV).
- Correr el nivel 2 dos veces por ruta con el proyecto congelado.
- Publicar la comparación en la sección «Resultados» del plan.

La checklist completa está en `PLAN_MEDICION_TOKENS.md` §8.

### 2. Decidir la estrategia de herencia

El hallazgo con más impacto de la línea base: releer **toda** la cadena de `reporte.json` en
cada paso cuesta **2.7×** más que leer solo el predecesor directo (~31,900 contra ~11,640
tokens\* en el recorrido de 6 pasos). Hoy `SKILL.md` no acota cuál de las dos se espera.

Decidirlo y escribirlo en `SKILL.md` § «El ciclo de un paso», punto 5.

### 3. Partir el `SKILL.md` de `senales-debiles`

25,868 caracteres: **3.4×** la mediana de las 26 sub-skills (7,593). Es la candidata evidente
a mover detalle a `references/`, que solo se lee cuando toca. Pendiente de confirmar con la
medición fina antes de tocarlo.

### 4. Avisos de markdownlint que quedan (MD013)

`AGENTS.md` y el resto de los `.md` siguen con avisos de longitud de línea (>80). Es la
convención de todo el repo, no un defecto de un archivo: si se quiere cerrar, se cierra con un
`.markdownlint.json` que suba el límite, no reescribiendo 30 documentos.

---

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
