# Plan de Mejoras — Reportes HTML del Flujo IRIS

> Objetivo: cerrar la brecha entre "diseño visual sólido" y "legible para una base
> generalista". El reporte hoy se ve bien y cumple la trazabilidad, pero no pone al
> frente lo que un lector no especialista necesita primero: **qué me está diciendo este
> reporte** y **qué viene después**.

## Alcance y criterio rector

- **No se rediseña la paleta ni la tipografía.** El sistema corporativo (morado/dorado,
  Sora/Inter) se mantiene intacto.
- **Todo cambio se mide contra una pregunta:** ¿un generalista, sin conocer el flujo,
  entiende en 5–10 segundos qué muestra este reporte, de dónde viene y qué sigue?
- Se priorizan cambios **de bajo riesgo y alto impacto** primero; los estructurales al final.

## Inventario de activos afectados

| Archivo | Rol | Cambio |
| --- | --- | --- |
| `_plantilla_html/templates/reporte_base.html` | Plantilla interactiva (HTML + JS + CSS) | Principal: la mayoría de mejoras viven aquí |
| `_plantilla_html/scripts/generar_html.py` | Generador (inyecta contexto, valida, embebe logo) | Menor: nuevos datos de contexto, promesa offline |
| `_plantilla_html/README.md` | Documentación del esquema y del generador | Sincronizar con los cambios |
| `sub-skills_sample_outputs/` | Galería de muestra | Regenerar al menos una muestra `--estado` + `--paso` |
| `pasos.json` / `scripts/estado_flujo.py` | Fuente del flujo | Solo lectura: proveer "siguiente paso" |

---

## Mejoras priorizadas

### M1. Bloque de "Conclusión / Takeaway" al frente (alta prioridad)

**Problema.** El "¿entonces qué?" vive en `decisiones`, al final de la página. El campo
`meta.resumen` existe en el esquema pero solo se usa como fallback del subtítulo
(`reporte_base.html:359`). Un generalista decide en 5 segundos si el reporte le sirve y
hoy tiene que bajar hasta abajo.

**Propuesta.**

1. Renderizar un bloque de **"En resumen"** inmediatamente después del hero (antes del
   `details` de contexto y del `main`):
   - Usar `meta.resumen` como texto principal (2–3 líneas).
   - Si no hay `resumen`, derivar el texto de la decisión con `veredicto: perseverar`
     más reciente, o de la primera decisión.
2. Mostrar **los veredictos como fila de mini-badges** en el mismo bloque (ej.
   "1 perseverar · 1 pivotear") para que el semáforo sea visible arriba, no solo como
   chips de filtro.
3. Tratamiento visual: caja blanca con borde `--line`, título en Sora y un icono/acento
   dorado, coherente con `.ctx-box` pero con jerarquía de "lo más importante primero".

**Dónde.** `reporte_base.html`: nuevo contenedor tras `</header>` y antes de
`<section class="contexto">`; nueva función `renderResumen()` invocada antes de
`renderFlujo()` en el IIFE. Ajustar `buildChips`/`render` si se mueve la lógica de
veredictos.

**Aceptación.** Al abrir `html_N.html`, un bloque "En resumen" se lee antes del contexto
del flujo; resume la conclusión en ≤3 líneas y muestra los veredictos.

---

### M2. "¿Qué sigue?" visible dentro del reporte (alta prioridad)

**Problema.** El flujo conoce el paso siguiente, pero el reporte no lo anuncia; solo se
infiere del riel del header. Un generalista que cierra el reporte no sabe qué toca.

**Propuesta.**

1. Añadir un elemento "Siguiente paso" en el cierre del reporte (junto a `decisiones` o
   como caja propia antes del footer):
   - Fuente: `flujo.ruta[]` — el primer paso con estado `pendiente` **según el orden de
     `pasos.json`**, no el orden de aparición en el riel.
   - Texto: "**Siguiente paso: Persona Profile** — <objetivo del paso en una línea>".
2. Si el paso actual es `html_11` (cierre), mostrar "Flujo completo — sin pasos pendientes".
3. Para skills sueltas (`--sin-flujo`, sin bloque `flujo`), ocultar el elemento.

**Dónde.** `generar_html.py`: `inyectar_flujo` ya construye el bloque `flujo`; agregar
`flujo.siguiente_paso = { "titulo": …, "objetivo": … }` (o calcularlo en la plantilla).
`reporte_base.html`: nueva caja renderizada en `renderFlujo()` o en una función propia.

**Aceptación.** Todo reporte con contexto del flujo muestra el siguiente paso al final;
los reportes sueltos no lo muestran.

---

### M3. Reordenar/collapsar el bloque "De dónde viene este reporte" (media prioridad)

**Problema.** El `<details open>` (`reporte_base.html:261`) empuja el contenido real
hacia abajo. La procedencia es secundaria para un generalista; la conclusión (M1) debe
ir primero.

**Propuesta.**

1. Cambiar el bloque de contexto a **colapsado por defecto** (`open` removido), con un
   `summary` que resuma lo esencial en una línea: "Contexto del flujo · paso 4 de 11 ·
   2 decisiones · 1 omitido".
2. Mantener el comportamiento actual: al abrir, se despliega la caja ámbar de omitidos y
   de datos simulados.
3. Opcional: mover el bloque **debajo** del `main` si las pruebas indican que aun
   colapsado estorba.

**Dónde.** `reporte_base.html:260-268` (markup) y `renderFlujo()` (el `ctx-tally` ya
calcula el resumen de una línea; reutilizarlo en el `summary`).

**Aceptación.** Al abrir el reporte, lo primero que se ve es el hero + "En resumen" (M1)
+ contenido; el contexto del flujo está a un clic.

---

### M4. Leyenda del semáforo de veredictos (media prioridad)

**Problema.** `perseverar / pivotear / descartar` son jerga del flujo y no se explican en
ningún lado del HTML (`VERDICT_LABEL` en `reporte_base.html:348`). Un generalista no
sabe qué significa "pivotear".

**Propuesta.**

1. Añadir una leyenda corta, visible la primera vez que aparecen veredictos:
   - **Perseverar** = la evidencia respalda continuar con esta hipótesis/idea.
   - **Pivotear** = la evidencia sugiere ajustar la hipótesis o el enfoque.
   - **Descartar** = la evidencia recomienda abandonar esta línea.
2. Colocación: un tooltip/`title` sobre cada badge `.verdict`, más una línea fija bajo el
   bloque "En resumen" (M1) o junto a los chips de filtro.
3. Mantener el texto en español, sin jerga, siguiendo `AGENTS.md` §7.

**Dónde.** `reporte_base.html`: `buildCard` (badge), `renderDecisiones` y `buildChips`;
texto de leyenda en una constante reutilizable.

**Aceptación.** Cualquier badge de veredicto muestra su significado al hover, y la leyenda
aparece una vez por reporte cuando hay veredictos.

---

### M5. Guía de autor para que cada skill sea "generalista-friendly" (media prioridad)

**Problema.** La plantilla es genérica; la legibilidad final depende de que cada skill
redacte bien `subtitulo`, `resumen`, KPIs y `body`. La muestra de `benchmark-mercado`
tiene KPIs excelentes, pero "5 Fuerzas de Porter" son tarjetas con un único `body`
("Análisis: …"), poco escaneables.

**Propuesta.**

1. Redactar una **guía de autor** (nueva sección en `_plantilla_html/README.md`, o archivo
   `_plantilla_html/PAUTAS_REDACCION.md`) con ejemplos buenos/malos de:
   - `meta.subtitulo` y `meta.resumen` (qué diferencia hay entre ambos y cuándo usar cada uno).
   - `kpis` (3–5 máximos, un número grande + label corto).
   - `body` de item: evitar un único bloque genérico; preferir 2–4 bloques con `label`
     específico ("Segmento", "Modelo de ingresos", "Interpretación").
   - `veredicto`: cuándo usar cada uno y cómo redactar la decisión asociada.
2. Incluir una lista de verificación mínima ("checklist del reporte") que el validador o
   la macro puedan pedir antes de cerrar un paso.

**Dónde.** `_plantilla_html/README.md` (o documento nuevo) + enlace desde `SKILL.md`
§ Referencias.

**Aceptación.** Existe una guía concreta que cualquier skill puede seguir para que su
`reporte.json` produzca un HTML legible por una base generalista.

---

### M6. Regenerar muestras con contexto del flujo (media prioridad)

**Problema.** Todas las salidas de `sub-skills_sample_outputs/` están generadas con
`--sin-flujo` (verificado: no contienen el bloque `"flujo"` / `"ruta"`). El rasgo
estrella del producto —riel de progreso + "De dónde viene este reporte"— no está
demostrado en la galería.

**Propuesta.**

1. Generar **al menos una muestra de extremo a extremo** con un `flujo_estado.json` de
   ejemplo (puede ser el del documento `ejemplos_para_testear.md`), invocando:
   ```bash
   python _plantilla_html/scripts/generar_html.py --data reporte.json \
       --estado flujo_estado.json --paso html_4 -o html_4.html
   ```
2. Conservar esa muestra bajo `sub-skills_sample_outputs/` con un nombre explícito
   (ej. `html_4_persona_profile_con_flujo.html`).
3. Documentar en el README de muestras qué representa cada archivo (con flujo vs. suelta).

**Dónde.** `sub-skills_sample_outputs/` y su README (si existe) o `_plantilla_html/README.md`.

**Aceptación.** La galería demuestra el riel, el contexto, el bloque de omitidos y el
distintivo de datos simulados en al menos un reporte.

---

### M7. Aclarar la promesa "offline" y endurecer la autosuficiencia (baja/estructural)

**Problema.** El logo va embebido en base64, pero Chart.js y Google Fonts se cargan por
CDN (`reporte_base.html:7-8`). El README dice "funciona offline" (`_plantilla_html/README.md:29`),
lo cual es impreciso: sin conexión las gráficas no se dibujan.

**Propuesta (opción A — mínima).**

1. Corregir el texto del README: "autocontenido para el contenido y el logo; requiere
   conexión para Chart.js y Google Fonts (las fuentes caen al sistema)".
2. Añadir un fallback visible cuando Chart.js no cargue: si `typeof Chart === 'undefined'`,
   mostrar en cada `.chart-wrap` un mensaje "Gráfica no disponible sin conexión" en lugar
   de un canvas roto.

**Propuesta (opción B — completa).**

3. Vendorizar Chart.js dentro de la plantilla (descargar la build UMD una vez y embeberla
   en `<script>`) para que las gráficas funcionen realmente sin conexión. Incrementa el
   tamaño del HTML en ~200 KB.
4. Igual con Google Fonts: dejarlo como mejora progresiva (si no carga, fuente del sistema).

**Dónde.** `_plantilla_html/templates/reporte_base.html` (fallback + vendor) y
`_plantilla_html/README.md` (promesa).

**Aceptación.** La documentación refleja la realidad; opción A: sin red, el reporte se
lee íntegro y las gráficas muestran un aviso en vez de romperse. Opción B: las gráficas
también funcionan sin red.

---

### M8. "Siguiente paso" y "en resumen" en el contrato JSON (baja prioridad, coherencia)

**Problema.** Si M1 y M2 dependen de datos que hoy no están en `REPORT_DATA`, conviene
formalizarlos para que el validador los controle y no dependan de la buena voluntad del
autor.

**Propuesta.**

1. Documentar en el esquema `REPORT_DATA`:
   - `meta.resumen` pasa a ser **recomendado** (ya es opcional hoy) y se usa para el
     bloque "En resumen".
   - `decisiones[]` ya existe; M1 lo usa para la fila de veredictos, sin cambios de esquema.
   - `flujo.siguiente_paso` lo calcula el generador (M2), no se escribe a mano.
2. El validador `validar_report_data.py` **avisa** (no falla) si falta `meta.resumen`.

**Dónde.** `_plantilla_html/README.md` (esquema) y `_plantilla_html/scripts/validar_report_data.py`.

**Aceptación.** El esquema documentado y el validador reflejan las nuevas expectativas.

---

## Orden de implementación recomendado

| Fase | Items | Esfuerzo | Impacto |
| --- | --- | --- | --- |
| 1. Quick wins | M1, M2 | Bajo | Alto (generalista) |
| 2. Usabilidad | M3, M4 | Bajo-medio | Medio |
| 3. Consistencia | M5, M6, M8 | Medio | Medio |
| 4. Infraestructura | M7 | Medio | Bajo-medio (pero evita promesa rota) |

## Fuera de alcance (por ahora)

- Rediseño de paleta/tipografía o del sistema de diseño.
- Cambios en la máquina de estados (`estado_flujo.py`) salvo lo necesario para M2.
- Internacionalización (los reportes son en español por diseño).
- Nuevos tipos de gráfica más allá de los ya soportados.

## Definición de hecho

El plan está completo cuando, sobre un reporte de muestra con contexto de flujo:

1. Se lee "En resumen" y la conclusión antes que el contexto (M1).
2. Se ve el siguiente paso al final (M2).
3. El contexto del flujo está colapsado y a un clic (M3).
4. Los veredictos se explican solos (M4).
5. Existe guía de autor y una muestra con flujo (M5, M6).
6. La documentación no promete más offline de lo que cumple (M7, M8).
