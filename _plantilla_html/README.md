# Plantilla de Salidas HTML Interactivas — IRIS

Infraestructura compartida para que cualquier skill del flujo de innovación IRIS genere su **salida principal como un reporte HTML interactivo** con el diseño corporativo oficial (logo + paleta morado/dorado, tipografías Sora/Inter), sin que cada skill tenga que escribir HTML a mano.

## Cómo funciona

Cada skill produce un **`reporte.json`** estructurado y luego ejecuta el generador
**desde la raíz del repositorio** (la carpeta que contiene `pasos.json` y `sub-skills/`):

```bash
# como paso del flujo: el contexto del flujo se inyecta solo
python _plantilla_html/scripts/generar_html.py --data reporte.json \
    --estado flujo_estado.json --paso html_4 -o html_4.html

# skill suelta, fuera de un proyecto del flujo
python _plantilla_html/scripts/generar_html.py --data reporte.json \
    --sin-flujo -o reporte.html
```

El generador hace tres cosas antes de escribir el archivo:

1. **Inyecta el contexto del flujo** (con `--estado` y `--paso`): construye el bloque
   `flujo` desde `flujo_estado.json` + `pasos.json`. No lo escribas a mano.
2. **Valida el esquema** con `validar_report_data.py` y **falla si algo falta**, para que
   un reporte incompleto no se entregue como HTML en blanco.
3. **Embebe el logo oficial en base64**.

El resultado es un `.html` autocontenido para el contenido y el logo (embebido en
base64). Las fuentes y Chart.js se cargan por CDN: sin conexión las fuentes caen al
sistema y las gráficas muestran un aviso «no disponible sin conexión» en vez de romperse.

### Opciones

| Flag | Para qué |
| --- | --- |
| `--paso html_N` | Inyecta el contexto del flujo de ese paso |
| `--estado <ruta>` | `flujo_estado.json` (default: raíz del repo) |
| `--pasos <ruta>` | `pasos.json` (default: raíz del repo) |
| `--sin-flujo` | Skill suelta: no exige contexto del flujo |
| `--no-strict` | Salta la validación. **No lo uses para esquivar un error**: corrige el JSON |

Códigos de salida: `0` ok · `1` error de archivo/uso · `2` esquema o flujo inválido.

## Estructura

```
_plantilla_html/
├── templates/
│   └── reporte_base.html         # HTML interactivo genérico (riel del flujo, contexto,
│                                 # header, toolbar, cards expandibles, charts, footer)
├── scripts/
│   ├── generar_html.py           # reporte.json + contexto + template + logo -> html
│   ├── validar_report_data.py    # valida el esquema REPORT_DATA (usable por separado)
│   └── logo_base64.py            # helper: PNG -> data URI base64
└── README.md
```

- **Logo oficial:** `imagenes_iconos_etc/Logos_GS_Iris_transparent.png` (se resuelve automáticamente). Cada skill conserva además una copia en `assets/logo.png`.
- **Diseño oficial:** `Designs_files/Design_iris_main_colors.md` (paleta `--purple-*` / `--gold-*`, fuentes Sora/Inter).

## Esquema `REPORT_DATA`

```jsonc
{
  "meta": {
    "titulo": "Search Trend Analysis — Evidencia",
    "skill": "search-trend-analysis",
    "fase": "Investigación",
    "subtitulo": "Resumen de una línea del análisis",
    "resumen": "Resumen ejecutivo (2-3 líneas)",
    "fecha": "2026-08-12",
    "metodologia": "Opcional: texto para el modal de metodología",
    "simulado": false          // opcional: marca datos simulados en una skill suelta
  },
  "kpis": [
    { "label": "Keywords analizadas", "value": "12", "accent": false }
  ],
  "secciones": [
    {
      "titulo": "Evidencia por keyword",
      "items": [
        {
          "titulo": "huerto urbano",
          "subtitulo": "Interés promedio 38/100",
          "tags": ["primaria", "alta demanda"],
          "score": 23,                                  // opcional
          "veredicto": "perseverar",                     // perseverar | pivotear | descartar
          "body": [
            { "label": "Dato", "texto": "Interés relativo 0-100 con delta +12 en 12 meses." },
            { "label": "Interpretación", "texto": "Tendencia creciente sostenida." }
          ],
          "chart": {                                     // opcional
            "tipo": "line",                              // bar | horizontalBar | line | doughnut | pie
            "titulo": "Evolución del interés",
            "eje_x": "Mes", "eje_y": "Interés (0-100)",
            "labels": ["Ene","Feb","Mar"],
            "datasets": [ { "label": "huerto urbano", "data": [20,28,38] } ]
          },
          "fuentes": ["Google Trends (pytrends)"],
          "persona": { },                                // opcional: ficha de protopersona
          "psf": { }                                     // opcional: análisis Problem-Solution Fit
        }
      ]
    }
  ],
  "decisiones": [
    { "titulo": "Perseverar en 'huerto urbano'", "texto": "Supera el umbral...", "veredicto": "perseverar" }
  ],
  "advertencias": ["Datos estimados marcados con *"],
  "fuentes": ["Fuente 1", "Fuente 2"]
}
```

### Bloques especializados de item: `persona` y `psf`

Además de `body` y `chart`, un item puede llevar un bloque con estructura propia. La
plantilla lo renderiza con su layout (fichas, tablas adaptativas, matriz de cuadrantes) y
el validador comprueba su esquema:

| Bloque | Lo produce | Estructura vinculante |
| --- | --- | --- |
| `persona` | `persona-profile` (`html_4`) | `sub-skills/2.Descubrimiento/persona-profile/references/ficha-persona.md` |
| `psf` | `problem-solution-fit` (`html_5`) | `sub-skills/2.Descubrimiento/problem-solution-fit/references/analisis-psf.md` |

Dos reglas de render que valen para los dos:

- **Las tablas son adaptativas:** una columna solo aparece si al menos una fila trae ese
  dato. La ficha de persona sin evaluar (sin `solucion` / `costo` / `importancia` /
  `satisfaccion` en sus pains) imprime la tabla de dos columnas más una nota que remite a
  Problem-Solution Fit — ese análisis es el paso siguiente, así que la ficha **no** debe
  rellenar esas columnas con `[no disponible]` ni con cifras estimadas.
- **La matriz Importancia × Satisfacción se deriva**, nunca se escribe. La plantilla la
  arma con los pares `importancia` + `satisfaccion` de `persona.pains` o de
  `psf.problemas`; si no hay ningún par completo, no hay gráfica. Escribir un `chart` a
  mano duplicaría la fuente de verdad (y gana el `chart` explícito).

### El bloque `flujo` (contexto del flujo)

**No lo escribas a mano.** Lo inyecta el generador con `--estado` y `--paso`; se
documenta aquí solo para saber qué se renderiza:

```jsonc
{
  "flujo": {
    "proyecto": "Huertos urbanos MX",
    "objetivo_proyecto": "Validar demanda de kits de huerto",
    "audiencia": "Familias urbanas 28-45, CDMX",
    "paso_actual": "html_4",
    "paso_titulo": "Persona Profile",
    "paso_objetivo": "Convertir la evidencia en protopersonas…",
    "paso_orden": 4,
    "total_pasos": 11,
    "avance": { "completados": 1, "omitidos": 1, "pendientes": 8 },
    "siguiente_paso": { "id": "html_5", "titulo": "Problem-Solution Fit",
                        "etapa": "Descubrimiento", "orden": 5, "objetivo": "…" },
    "ruta": [
      { "id": "html_1", "titulo": "Inicio + Investigación", "estado": "completado",
        "resumen": "TAM MX 4.2 mil M*…", "archivo": "html_1.html",
        "archivos": ["html_1.html", "benchmark.csv"], "datos": "reporte_h1.json",
        "veredicto": "perseverar" },
      { "id": "html_2", "titulo": "Decisión — Entrevistas", "estado": "omitido",
        "motivo": "Ya tiene 12 entrevistas hechas", "impacto": "persona-profile usa supuestos *" },
      { "id": "html_4", "titulo": "Persona Profile", "estado": "actual" }
    ],
    "decisiones": [{ "paso": "html_1", "nodo": "¿Cómo quieres iniciar?", "opcion": "Estado actual" }],
    "omitidos": [{ "id": "html_2", "titulo": "…", "motivo": "…", "impacto": "…", "forzada": false }],
    "simulacion": { "activo": true, "desde": "html_2",
                    "nodo": "¿Ejecución de entrevistas?",
                    "opcion": "No — simulación de respuestas e insights",
                    "nota": "Las entrevistas y encuestas de este proyecto son SIMULADAS…" }
  }
}
```

Se renderiza como:

- **Riel de progreso** en el header: los 11 pasos con color por estado (completado en
  verde, omitido tachado, el actual en dorado). Los pasos con `archivo` son enlaces.
- **«De dónde viene este reporte»**: el proyecto, las decisiones tomadas, lo que ya se
  sabe de los pasos previos y —en caja ámbar— los pasos omitidos con su impacto, para que
  quien lea el reporte sepa qué le falta.
- **«En resumen»**: `meta.resumen` y la fila de veredictos al frente, antes del contexto,
  para que la conclusión se lea en los primeros segundos.
- **«Siguiente paso»** (`flujo.siguiente_paso`, lo calcula el generador): el cierre del
  reporte anuncia qué paso toca después.
- **Pie**: proyecto y posición en el flujo.
- **Marca de datos simulados** (si `simulacion.activo`): distintivo dorado «Datos simulados» en
  la cabecera, caja ámbar «esto no es evidencia de campo» como primer bloque del contexto,
  `DATOS SIMULADOS` en el pie, prefijo `SIMULADO ·` en el título de la pestaña y una
  advertencia automática si ninguna de las declaradas menciona la simulación. Lo enciende la
  decisión registrada en el flujo (opción marcada `marca_simulacion` en `pasos.json`), así que
  **ninguna skill tiene que acordarse de etiquetar**. Una skill que corre suelta, sin contexto
  de flujo, consigue lo mismo con `meta.simulado: true`. Convención completa:
  `sub-skills/SIMULACION.md`.

`estado` admite: `pendiente`, `en_curso`, `completado`, `omitido`, `fallido`, `actual`
(solo uno puede ser `actual`).

Tres campos de `ruta[]` son la **herencia entre pasos** —lo que la skill del paso siguiente
lee para no reconstruir el contexto desde cero:

| Campo | Qué es | Para qué |
| --- | --- | --- |
| `resumen` | Una línea: qué se aprendió | El índice. Se pinta en el riel y en «De dónde viene este reporte» |
| `datos` | Ruta del `reporte.json` de ese paso | **Los datos estructurados**: de aquí se heredan `persona`, `psf`, `secciones[].items[]` |
| `archivos` | Todos los outputs declarados | El resto de entregables (CSV, PPTX, HTML propios). `archivo` es el primero, el que enlaza el riel |

Los rellena `estado_flujo.py completar` con `--resumen`, `--datos` y `--outputs`.

### Reglas del esquema

- `meta` y `secciones` son obligatorias; el resto es opcional.
- `veredicto` usa uno de: `perseverar` / `pivotear` / `descartar` (se renderiza con semáforo verde/ámbar/rojo).
- `chart.tipo` admite `bar`, `horizontalBar`, `line`, `doughnut`, `pie`, `scatter`.
- `persona` y `psf` son opcionales y se validan con su esquema propio (ver arriba).
- Todo texto del `body` se muestra con salto de línea preservado (`pre-wrap`).
- Los valores con cifras **estimadas** se marcan `*` o `[REFERENCIA DE INDUSTRIA]` según las reglas de integridad del flujo.

## Componentes interactivos (ya incluidos en la plantilla)

- Header hero con gradiente morado, mancha dorada y **logo oficial**.
- KPIs en el hero (stat cards translúcidas).
- Toolbar con **buscador en vivo**, **orden** (original / A–Z / score) y **chips de filtro** por veredicto y por tag.
- Tarjetas **expandibles inline** (una a la vez) con bloques de detalle y **gráficas Chart.js**.
- Sección de **Decisiones** con semáforo de veredicto.
- Secciones de **Advertencias** y **Fuentes**.
- Modal de **Metodología** (si `meta.metodologia` está definido).
- Accesibilidad: `aria-*`, foco visible dorado, `prefers-reduced-motion`, responsive.

## Guía para que el reporte se lea sin manual (base generalista)

La plantilla pone la forma; el autor pone el contenido. Un generalista —alguien que no
conoce el flujo— debe poder responder en 10 segundos **qué muestra este reporte**, **de
dónde viene** y **qué sigue**. Para eso, al escribir `reporte.json`:

- **`meta.resumen` (2–3 líneas)**: la conclusión. Es lo que alimenta el bloque «En
  resumen» del reporte. No es una descripción del método, es el «¿y entonces qué?».

  - Mal: «Se analizaron 10 competidores con las 5 Fuerzas de Porter».
  - Bien: «El nicho B2B SME es el hueco con mejor relación demanda/competencia: SOM
    proyectado $52M y solo dos jugadores directos.»

- **`meta.subtitulo` (1 línea)**: la bajada descriptiva del hero, complementaria al
  título. Si `resumen` ya dice todo, el subtítulo puede ser la descripción del método.

- **`kpis` (3–5 máximos)**: un número grande + `label` corto. Son el primer vistazo;
  no conviertas en KPI una cifra que no resuma el resultado.

- **`body` de cada item (2–4 bloques con `label` específico)**: evita un único bloque
  genérico tipo «Análisis: …». Prefiere etiquetas que respondan algo («Segmento»,
  «Modelo de ingresos», «Interpretación», «Riesgo»). La tarjeta expandida se lee por
  etiquetas.

- **`veredicto`**: úsalo solo cuando hay una decisión respaldada. El reporte lo pinta con
  semáforo y lo explica al hover (perseverar = continuar · pivotear = ajustar ·
  descartar = abandonar). Sin veredicto, la tarjeta no lleva semáforo, y está bien.

- **`advertencias`**: declara aquí todo supuesto, cifra estimada (`*`) y ausencia
  (`[no disponible]`). El footer explica las marcas; las advertencias son donde se usan.

Checklist mínimo antes de dar por bueno un `reporte.json`: ¿tiene `resumen`? ¿los KPIs
resumen el resultado? ¿cada item se entiende por sus `body.label` sin abrir el detalle?
¿los supuestos están en `advertencias`?

## Verificación del HTML generado

El generador ya valida el esquema y falla si algo falta. Si además quieres revisar el
archivo a mano, verifica que contenga:

1. `<!DOCTYPE html>` y las fuentes Sora/Inter.
2. `window.REPORT_DATA` con los datos y el bloque `flujo`.
3. El logo embebido como `data:image/png;base64,...`.
4. El riel del flujo con el paso actual en dorado y los omitidos tachados.
5. Los controles interactivos y la(s) gráfica(s) si `chart` está definido.

Para validar solo el JSON, sin generar HTML:

```bash
python _plantilla_html/scripts/validar_report_data.py reporte.json
```
