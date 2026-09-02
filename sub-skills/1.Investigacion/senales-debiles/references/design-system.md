# Design System — Reporte Ejecutivo (Iris)

Design system vinculante para `reporte_ejecutivo.html` (Fase 4). Cubre únicamente los componentes que existen en el reporte: header, tarjetas de señal, tarjetas de decisión, heatmap SVG y footer. No incluye elementos de interfaz interactiva (buscadores, filtros, modales, carruseles) porque el reporte es un documento estático, no una aplicación.

Las reglas de contenido y formato del reporte (secciones, campos, checklist de validación) viven en `SPEC.md`. Este archivo cubre solo el aspecto visual.

---

## 1. Tipografía

- **Sora** (weights 600, 700, 800): títulos de sección, títulos de señal, títulos de decisión, número de "Señal Débil N".
- **Inter** (weights 400, 500, 600): cuerpo de texto, campos de la tarjeta, footer.
- Importadas vía Google Fonts:
  ```html
  <link href="https://fonts.googleapis.com/css2?family=Sora:wght@600;700;800&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
  ```
- Tamaño base: `16px` en `:root`, `line-height: 1.55` en body.
- H1 del header: `clamp(1.5rem, 3.2vw, 2.35rem)`, peso 800.

## 2. Paleta de color (variables CSS obligatorias)

```css
:root{
  --purple-900:#241B33;
  --purple-700:#3D2766;
  --purple-600:#5A3A8C;
  --purple-200:#D9CCEF;
  --purple-050:#F7F3FC;

  --gold-600:#B8862F;
  --gold-500:#D4A73E;

  --ink:#2A2433;
  --ink-soft:#5C5468;
  --line:#E4DCEF;
  --white:#FFFFFF;

  --radius:14px;
  --shadow-sm:0 1px 3px rgba(42,36,51,.08);
  --shadow-md:0 6px 20px rgba(61,39,102,.12);
}
```

**Uso semántico:**

| Rol | Variable |
|---|---|
| Fondo general de la página | `--purple-050` |
| Fondo header y footer | gradiente `--purple-900 → --purple-700 → #4A2F7A` |
| Texto principal | `--ink` |
| Texto secundario | `--ink-soft` |
| Bordes/divisores | `--line` |
| Acento dorado (Sección 2, hipótesis destacadas) | `--gold-500` / `--gold-600` |
| Icono de sección "Señales Débiles" | `--purple-600` |
| Icono de sección "Decisiones Estratégicas" | `--gold-500` |

No se usa ninguna otra paleta (quedan descartados colores de severidad tipo semáforo, ya que el reporte no lleva badges de severidad).

## 3. Componentes del reporte

### 3.1 Header
```css
header.report{
  background:linear-gradient(135deg,var(--purple-900) 0%,var(--purple-700) 62%,#4A2F7A 100%);
  color:#fff; padding:28px clamp(20px,4vw,56px) 34px; position:relative; overflow:hidden;
}
```
- Mancha decorativa: `::after` con `radial-gradient(circle, rgba(232,185,62,.16), transparent 65%)`, 420×420px, esquina superior derecha.
- Contenido: título del reporte (Sora 800), fecha de generación, pregunta de investigación (texto exacto), resumen ejecutivo de 2-3 líneas (Inter 400).
- No lleva logo, botones ni stats: esos son elementos del catálogo de agentes de otro producto y no aplican aquí.

### 3.2 Encabezado de sección
- Título en Sora 700, con un icono cuadrado de color (`--purple-600` para Sección 1, `--gold-500` para Sección 2).
- Separador inferior: `border-bottom: 2px solid var(--purple-200)`.

### 3.3 Tarjeta de señal (`.card`)
- Fondo blanco, borde `--line`, `border-radius: var(--radius)`, padding 18px, layout en columna con `gap: 9px`.
- **Ocupa una fila completa (una señal por línea)**: cada tarjeta de señal tiene `width: 100%` dentro de un contenedor de una sola columna. Contenedor de señales: `display:grid; grid-template-columns:1fr; gap:20px;` — nunca `repeat(auto-fit,minmax(...))`, que agrupa varias señales por fila.
- **Altura auto-ajustada al contenido**: sin `height` fija ni `max-height` en la tarjeta (crece con su texto). **Las gráficas Chart.js son la excepción**: el contenedor `.chart-wrap` de cada gráfica recibe una **altura ancla** calculada por `scripts/generar_reporte.py` — `min_h = max(260, n_categorías × 48)` px — aplicada como `height` inline. Sin esa altura ancla, `maintainAspectRatio: false` + contenedor auto entra en un **bucle infinito de resize** de Chart.js (la gráfica crece sin fin); las barras horizontales lo amplifican porque su altura crece con el número de categorías. La gráfica nunca excede el ancho de la tarjeta (`max-width:100%`).
- Hover: `transform: translateY(-3px)` + `box-shadow: var(--shadow-md)`.
- No colapsable, no expandible, sin badges de color ni de severidad.
- Contiene exactamente los 5 campos definidos en `SPEC.md` sección 1.
- El bloque de "Hipótesis de valor" lleva tratamiento visual destacado: fondo `--purple-050`, borde izquierdo `--purple-600` (3px), padding 12px.
- Gráfica opcional (`<canvas>` o `<svg>`) va dentro de la misma tarjeta, nunca en sección aparte.

### 3.4 Tarjeta de decisión
- Fondo blanco, borde izquierdo dorado (`--gold-500`, 3px), padding 18px.
- Sin badges, sin campo de plazo.

### 3.5 Heatmap SVG inline
- Grid de `<rect>` coloreados por frecuencia, escala purpura de 5 niveles: `#D9CCEF` (mínimo) → `#B8A3D9` → `#7A4E96` → `#5A3A8C` → `#3D2766` (máximo).
- Celdas de 50px mínimo (56px si el grid es ≤6×6). Ver especificación técnica completa en `SPEC.md` sección 6.
- El margen inferior del viewBox debe ser dinámico (derivado de la etiqueta más larga), no fijo, para que las etiquetas de eje X rotadas 45° nunca se recorten. Regla en `SPEC.md` sección 6.
- Ejes etiquetados en `<text>`, rotados 45° si las etiquetas superan 8 caracteres.
- Tooltip vía atributo `<title>` en cada `<rect>`.

### 3.6 Footer
- Fondo `--purple-900`, texto `#C9BCE0`.
- Grid de columnas: Limitaciones, Fuentes, Metodología.
- Sin sección de trazabilidad ni IDs técnicos.

## 4. Accesibilidad y responsive

- Foco visible: `outline: 3px solid var(--gold-500); outline-offset: 2px`.
- Respeta `prefers-reduced-motion: reduce`.
- Responsive: CSS Grid/Flexbox, mobile-first. Breakpoints: `1150px` y `640px`.
- **Una señal por línea en todos los tamaños de pantalla**: el contenedor de tarjetas de señal usa una sola columna (`grid-template-columns:1fr`) tanto en desktop como en mobile; la tarjeta se ajusta al contenido.
