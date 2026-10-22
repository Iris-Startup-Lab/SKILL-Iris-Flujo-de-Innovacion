# Tutorial — IRIS Flujo de Innovación

Tutorial de uso del flujo de innovación IRIS, pensado para una audiencia generalista
(equipos de innovación, gestores de producto, fundadores), sin asumir que conoce la
notación interna del proyecto.

## Qué contiene esta carpeta

| Archivo | Qué es |
| --- | --- |
| `tutorial.html` | El tutorial en una sola página web autocontenida (diseño IRIS + logo embebido en base64). Ábrelo con cualquier navegador. |
| `Logos_GS_Iris_transparent.png` | Logo oficial IRIS (embebido también en el HTML). |
| `Design_iris_main_colors.md` | Sistema de diseño (paleta morado/dorado, tipografías Sora/Inter) usado por el tutorial. |

## Qué cubre el tutorial

- **Qué es IRIS** y para quién es.
- **Cómo funciona**: el ciclo de seis tiempos de cada paso y qué archivos se pueden adjuntar
  (texto e imágenes; audio y video todavía no).
- **Las dos rutas**: comparador interactivo completa (11) / mínima (5), tabla comparativa y
  arranque desde un paso intermedio.
- **Los 11 pasos, uno a uno**: tarjetas expandibles con sus decisiones vigentes según
  `pasos.json`, filtrables por etapa y con buscador. Incluye la landing de demo del paso 11
  (marca e imágenes) y los anexos para otros perfiles.
- **Omitir o pausar**: la diferencia entre declarar un hueco y dejar el paso pendiente.
- **Modo simulación**: los cinco simuladores, la marca «Datos simulados» y su validez.
- **Cómo leer los reportes**: los pasos anteriores embebidos (del más reciente al más
  antiguo), la estadística en tres capas, el semáforo de veredictos y las marcas de
  integridad (`*`, `[REFERENCIA DE INDUSTRIA]`, `[no disponible]`, «Datos simulados»).
- **¿Cómo funcionan los análisis o pruebas estadísticas?**: tamaños de muestra, lectura de resultados, validaciones automáticas y lo que aún no cubre, con ejemplos para principiantes.
- **Al terminar el recorrido**: resumen ejecutivo, auditoría, tablero `index.html` y
  medición de tokens y costo.
- **Puesta en marcha**: cómo empezar conversando con la skill y qué hay dentro de ella, sin comandos.
- **Material propio**: qué entrevistas, benchmarks u otros insumos se pueden aportar y en qué paso.
- **Preguntas frecuentes**, incluida la seguridad de subir datos sensibles.

## Animaciones

Todas son CSS/SVG y JavaScript propio, sin librerías externas: el recorrido de 11 pasos en
el encabezado, el ciclo de un paso, el comparador de rutas, las barras de omitir vs. pausar,
el intervalo de confianza de la capa 2 y la lista de pasos anteriores. Con
`prefers-reduced-motion` activo en el sistema, la página se muestra completa y sin
movimiento.

## Reglas de redacción

- Toda la notación interna está traducida: se dice «Paso 4 de 11 — Persona Profile»,
  nunca `html_4`, y «el agente Benchmark de Mercado», nunca la ruta de carpeta. 
- Las marcas de integridad se explican con palabras la primera vez que aparecen.
- Tono claro, conciso y positivo, sin «AI speak» (ver `AGENTS.md` §7).

## Nota

El objetivo es que este tutorial sea fácil de usar y, potencialmente, pueda
convertirse en una skill generalista reutilizable.
