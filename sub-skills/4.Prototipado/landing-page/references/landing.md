# La landing de validación: `landing.json`

La página ya no se escribe a mano. El diseño lo ponen `templates/landing_base.html` y
`scripts/generar_landing.py`; tú decides el **contenido**: qué bloques van, qué dicen, con qué
marca y con qué imágenes. Por eso sirve para cualquier producto: la plantilla no sabe de
ninguno, y la calidad visual no depende de cada ejecución.

```bash
python sub-skills/4.Prototipado/landing-page/scripts/generar_landing.py \
    --data landing.json -o landing_demo.html
python sub-skills/4.Prototipado/landing-page/scripts/generar_landing.py --listar-estilos
python sub-skills/4.Prototipado/landing-page/scripts/generar_landing.py --listar-iconos
```

El script **falla a propósito** si el texto sale ilegible (contraste), si falta el aviso de
privacidad de un formulario, si una prueba de «puerta falsa» no dice que el producto aún no
existe, o si hay prueba social inventada. Corrige el JSON; no hay forma de saltárselo.

## Esquema

```jsonc
{
  "id": "drones-elektra",                  // opcional: separa el registro local de eventos
  "estilo": "industrial",                  // references/estilos.json (--listar-estilos)
  "portada_tono": "oscura",                // opcional: clara | oscura | degradado (si no, el del estilo)
  "marca": {
    "tipo": "real",                        // real | nueva | neutra  (decisión «Marca de la landing»)
    "nombre": "Elektra Vuela",
    "logo": "logo",                        // opcional: clave en `imagenes`; sin logo se dibuja un símbolo + nombre
    "icono": "dron",                       // símbolo si no hay logo
    "colores": { "primario": "#E30613", "acento": "#FFC20E" },   // opcional: pisa los del estilo
    "tipografias": { "titulos": "Archivo", "texto": "Inter" },   // opcional (Google Fonts)
    "origen": "Colores del sitio oficial elektra.com.mx, confirmados por el usuario"
  },
  "cta": {
    "texto": "Quiero probarlo",            // UNA llamada a la acción, la misma en toda la página
    "accion": "formulario",                // formulario | puerta_falsa | enlace
    "url": null                            // solo con accion = enlace
  },
  "formulario": {                          // opcional; obligatorio si accion = formulario
    "campos": [
      { "tipo": "email", "etiqueta": "Tu correo", "ejemplo": "nombre@correo.com" },
      { "tipo": "cp", "etiqueta": "Código postal", "requerido": false }
    ],
    "boton": "Avísame cuando llegue",
    "endpoint": null                        // opcional: URL que recibe el envío (Formspree, Google Forms, webhook)
  },
  "privacidad": {                          // obligatorio si hay formulario (LFPDPPP)
    "texto": "Acepto que Elektra use mi correo solo para avisarme de este servicio.",
    "url": "https://…/aviso-de-privacidad"
  },
  "aviso_transparente": {                  // obligatorio si accion = puerta_falsa
    "titulo": "Todavía no está disponible",
    "texto": "Estamos midiendo el interés antes de lanzarlo. No se hizo ningún cobro; si nos dejaste tu correo, te avisaremos primero."
  },
  "gracias": { "titulo": "¡Listo!", "texto": "Te avisaremos en cuanto llegue a tu zona." },
  "edad": { "activa": false, "minima": 18, "texto": "…" },   // categorías reguladas
  "medicion": { "ga4_id": "G-XXXX", "gtm_id": null },       // sin esto, solo se mide en el navegador (?panel=1)
  "seo": { "titulo": "…", "descripcion": "…" },
  "evidencia": [                                              // opcional: la única vía para una cifra de clientes
    { "texto": "Más de 1,200 tiendas en México", "fuente": "Informe anual 2025, p. 14" }
  ],
  "imagenes": {
    "portada": { "fuente": "usuario", "archivo": "dron_entrega.jpg", "alt": "Dron entregando una caja en una azotea" },
    "logo":    { "fuente": "usuario", "archivo": "logo.png", "alt": "Logo" },
    "familia": { "fuente": "banco", "url": "https://images.unsplash.com/…", "alt": "…",
                 "credito": "Foto de Ana Pérez en Unsplash", "licencia": "Licencia Unsplash" },
    "escena":  { "fuente": "ia", "archivo": "escena.png", "alt": "…", "generada_con": "Firefly",
                 "prompt": "…" }
  },
  "bloques": [ … ]                         // ver el catálogo; el primero es la portada
}
```

## Bloques

Elige **5 a 7** según el producto. El primero es siempre `portada`; el último, `cta_final`.

| `tipo` | Para qué | Campos |
| --- | --- | --- |
| `portada` | La promesa en 5 segundos | `variante` (`dividida` · `centrada` · `inmersiva`), `etiqueta`, `titular` (≤ 12 palabras; `*palabra*` la resalta), `subtitulo`, `titular_b` / `subtitulo_b` (variante B), `puntos` [{icono, texto}] (≤ 3, solo afirmaciones verdaderas), `enlace_secundario` {texto, bloque}, `visual`, `imagen_fondo` (inmersiva) |
| `problema_solucion` | El dolor que salió del flujo contra la propuesta | `titulo`, `problema` {titulo, puntos[]}, `solucion` {titulo, puntos[]} |
| `beneficios` | Por qué elegirlo | `titulo`, `texto`, `items` [{icono, titulo, texto}] — **máximo 3** |
| `como_funciona` | Quitar el miedo a lo nuevo | `titulo`, `pasos` [{titulo, texto, icono}] (3-4) |
| `destacado` | Una función clave con su visual | `etiqueta`, `titulo`, `texto`, `puntos[]`, `visual`, `invertir` |
| `antes_despues` | El cambio en la vida del cliente | `titulo`, `titulo_antes`, `antes[]`, `titulo_despues`, `despues[]` |
| `comparativa` | Contra la alternativa de hoy (no contra un competidor con nombre) | `titulo`, `columnas` [criterio, alternativa, nosotros], `filas` [[criterio, "sí"/"no"/texto, "sí"/"no"/texto]] |
| `preguntas` | Objeciones del journey y del PSF | `titulo`, `items` [{pregunta, respuesta}] |
| `cta_final` | Donde se convierte | `titulo`, `texto` (si hay `formulario`, aparece aquí) |

Comunes: `titulo`, `texto`, `etiqueta`, `centrado` (true por omisión), `fondo: "superficie"` para
alternar el fondo entre bloques.

**De dónde sale cada texto.** No inventes: la persona (paso 4), los problemas priorizados (paso 5),
el journey (paso 6), la idea elegida (paso 8) y el modelo (paso 10) ya lo dicen. El `problema` es
el pain con mayor importancia; `preguntas` responde las objeciones que aparecieron en el journey.

## Visuales (`visual`)

Son las maquetas que dibuja la plantilla con los colores de la marca: no necesitan archivos. Elige
la que mejor enseñe **qué es** el producto:

| `tipo` | Para | Campos |
| --- | --- | --- |
| `celular` | Apps, servicios digitales, cualquier cosa que se use desde el teléfono | `saludo`, `titulo`, `filas` [{icono, titulo, detalle}] (≤ 4), `boton`, `alt` |
| `navegador` | Plataformas web, B2B, paneles | `url`, `titulo`, `tarjetas[]` (≤ 3 etiquetas), `lista[]` (≤ 3), `alt` |
| `producto` | Producto físico, empaque, kit | `nombre`, `variante`, `icono`, `sello` («Preventa», «Nuevo»), `alt` |
| `ruta` | Entregas, logística, servicios a domicilio, movilidad | `origen`, `destino`, `icono_origen`, `icono_destino`, `icono_movil` (dron, camion, moto…), `estado_titulo`, `estado_texto`, `alt` |
| `ilustracion` | Respaldo universal: un icono grande sobre una forma de la marca | `icono` |
| `imagen` | Una imagen real de `imagenes` | `imagen` (clave), `marco` (`celular` o ninguno), `credito_visible`, `respaldo` (otro visual si la imagen no llega) |

Todos admiten `chips` [{icono, texto}] (≤ 3): tarjetas flotantes que dan profundidad. **Solo
afirmaciones verdaderas o de producto** («Llega en el día», «Pago al recibir»), nunca métricas
inventadas. Los números de una maqueta son decorativos: no escribas cifras de uso en ella.

## La marca (decisión «Marca de la landing»)

- **`real`** — pide al usuario nombre, logo y colores. Si no los tiene a mano, **búscalos** en el
  sitio oficial o en la guía de marca publicada (con las herramientas de búsqueda que tengas), y
  **confírmalos con el usuario antes de usarlos**. Anota la fuente en `marca.origen`. Solo para
  marcas de su organización o con permiso para usarlas: si la marca es de un tercero, dilo y
  propón una marca nueva.
- **`nueva`** — propón nombre, `estilo`, dos colores y tipografías, y espera la aprobación del
  usuario (la opción lleva `requiere_propuesta`). Comprueba en la red que el nombre no sea ya una
  marca conocida de la misma categoría.
- **`neutra`** — `estilo: "neutro"` y un nombre descriptivo («Entrega Express»), sin logo.

Si los colores de la marca no dan contraste suficiente, el script falla y dice cuál: no lo
fuerces, ajusta el tono (por ejemplo, usa el color de marca como `acento` y uno más oscuro como
`primario`).

## Las imágenes (decisión «Imágenes de la landing»)

| Fuente | Qué haces | Qué exige el script |
| --- | --- | --- |
| `usuario` | Pide las fotos, renders o capturas; ponlas junto a `landing.json` | `archivo`, `alt` |
| `ia` | Escribe el *prompt* (producto, escena, luz, encuadre, colores de la marca, sin texto dentro de la imagen). Si tu herramienta genera imágenes, genéralas; si no, entrégale el prompt al usuario y espera los archivos | `archivo`, `alt`, `generada_con`; `prompt` recomendado |
| `banco` | Busca en Unsplash, Pexels o Pixabay; revisa que la licencia permita uso comercial; usa la URL directa de la imagen | `url`, `alt`, `credito`, `licencia` |
| `url` | Una imagen propia publicada en la red | `url`, `alt` |

- Todas se **incrustan** en el HTML (base64): la página sigue funcionando sin conexión. Una URL
  que no descarga cae al `respaldo` y el script lo avisa (`--sin-red` fuerza el respaldo).
- **Nunca** presentes una foto de banco o generada como si fuera un cliente real, ni pongas
  personas reconocibles con frases de testimonio.
- Peso: avisa sobre 900 KB y rechaza sobre 5 MB por imagen. Una portada de 1600 px de ancho en
  JPG o WebP al 80 % basta.
- Incluye siempre alguna maqueta: es el respaldo si una imagen no llega.

## Medición incluida

- Eventos: `vista`, `clic_cta` (con su ubicación), `envio_formulario` (sin los datos de la
  persona), `seccion_vista`, `aviso_transparente_visto`, `edad_confirmada`. Van a `dataLayer`
  (GTM) y a `gtag` (GA4) si pones sus identificadores en `medicion`.
- Origen: los parámetros `utm_*` de la URL viajan en cada evento y en el formulario.
- Variante B: `?v=b` cambia el titular y el subtítulo por `titular_b` / `subtitulo_b`. Reparte el
  tráfico entre las dos URL y compara con `analizar_resultados.py` (dos variantes → Bonferroni).
- `?panel=1` muestra un panel con lo que se registró en ese navegador: sirve para comprobar que
  los eventos salen, **no** para medir el experimento.

## Integridad (el script lo comprueba)

- Nada de prueba social que un producto en validación no puede tener: cifras de clientes
  satisfechos, estrellas, «4.9/5», «el más vendido», logos de clientes, testimonios. Si una cifra
  es real y de la empresa, va en `evidencia` con su fuente y deja de ser error.
- Una prueba de puerta falsa dice, al hacer clic, que el producto aún no existe y qué pasa con los
  datos (`aviso_transparente`).
- Un formulario lleva aviso de privacidad y casilla de aceptación.
- Los `puntos` y `chips` son afirmaciones del producto que se está probando: si no se puede
  cumplir («Llega en 30 minutos»), no se promete.
