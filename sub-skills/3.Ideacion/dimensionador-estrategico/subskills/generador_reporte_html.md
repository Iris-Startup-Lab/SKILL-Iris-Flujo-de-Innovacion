---
name: generador-reporte-html
description: Subskill para compilar los resultados del Dimensionador Estratégico en un dashboard ejecutivo interactivo en formato HTML autónomo, aplicando el sistema de diseño visual Design_2.md (Sora, Inter, paleta morado-dorado, selector de horizonte 1/3/5 años ajustables, gráfica de trayectoria de ingresos con filtros por tipo de idea, tarjetas expandibles y modal metodológico).
---

# Generador de Reportes HTML — Dimensionador Estratégico

## Propósito

Esta subskill convierte el análisis estructurado de negocio producido por el **Dimensionador Estratégico** en un entregable visual interactivo en un solo archivo `.html` (`reporte_dimensionamiento.html`).

El reporte generado implementa el sistema de diseño corporativo definido en `Design_2.md` con:

- **Header Hero**: Morado profundo (`--purple-900` / `--purple-700`) con degradado, mancha radial dorada, eyebrow y hero stats (Total Ideas, Top Score, SOM Total ajustado por horizonte, Ideas a Prototipar).
- **Panel de Contexto**: Objetivos estratégicos, etapa de negocio, sector y recursos.
- **Toolbar de Filtros & Ajuste de Horizonte**:
  - Buscador en vivo.
  - Select de ordenamiento.
  - Chips de filtro por veredicto (Prototipar / Validar Más / Descartar).
  - Select / Chips de filtro por **Tipo de Idea / Modelo de Negocio** (B2B SaaS, Marketplace, Suscripción, Transaccional, etc.).
  - **Selector de Horizonte Temporal Ajustable**: Botones interactivos **[1 Año | 3 Años | 5 Años]** que recalculan y ajustan dinámicamente las cifras de SOM y ARR en todo el dashboard.
- **Módulo Visual de Gráfica de Ingresos**:
  - Gráfica interactiva (Chart.js) que proyecta la **Trayectoria de Ingresos (Año 1 a Año 5)** por idea.
  - Filtrado en vivo según el tipo de idea seleccionada o búsqueda global.
- **Parte 1 — Tabla Ejecutiva de Priorización**: Resumen tabular interactivo ordenado por viabilidad con columnas dinámicas según el horizonte activo.
- **Parte 2 — Grilla de Tarjetas & Fichas Expandibles (Inline)**: Despliegue dinámico de los 10 módulos completos por idea.
- **Modal Metodológico**: Explicación interactiva de la escala /25 y umbrales de veredicto.

---

## Flujo de Ejecución

1. **Requerimiento**: Esta subskill se activa cuando el usuario solicita pasar el análisis del Dimensionador Estratégico a HTML, o al finalizar el análisis si el usuario acepta la propuesta de entregables visuales.
2. **Origen de Datos**: Lee los resultados de los 10 módulos del análisis del chat.
3. **Generación del Entregable**: Toma el código de `templates/reporte_template.html` y reemplaza el bloque `window.REPORT_DATA` con los datos reales del análisis.
4. **Archivo Final**: Crea o actualiza el archivo `reporte_dimensionamiento.html` en el directorio de trabajo del usuario.

---

## Estructura del JSON de Datos (`window.REPORT_DATA`)

```javascript
window.REPORT_DATA = {
  meta: {
    objetivoEstrategico: "[Paso 0A: Ej. 📈 Incrementar mercado]",
    etapaNegocio: "[Paso 0B: Ej. Pre-seed / Seed / Growth / Corporativo]",
    sector: "[Paso 0B: Ej. Fintech B2B]",
    geografia: "[Paso 0B: Ej. México / LATAM]",
    recursosPrototipado: "[Paso 0B: Ej. $50,000 USD / 90 días]",
    criterioFit: "[Paso 0B: Ej. Sinergia con canal de distribución]"
  },
  ideas: [
    {
      id: "idea-1",
      rank: 1,
      name: "[Nombre de la Idea]",
      model: "B2B SaaS", // Modelo/Tipo de Idea
      ideaType: "B2B SaaS", // Categorización para filtros
      shortDesc: "[Descripción breve]",
      score: 23, // Score /25
      verdict: "PROTOTIPAR", // "PROTOTIPAR" | "VALIDAR MÁS" | "DESCARTAR"
      tam: "$X.XB USD",
      sam: "$X.XM USD",
      som1y: "$X.XK USD",
      som3y: "$X.XM USD",
      som5y: "$X.XM USD",
      arr1y: "$X.XK USD",
      arr3y: "$X.XM USD",
      arr5y: "$X.XM USD",
      revenueTimeline: [150000, 450000, 1200000, 2500000, 4800000], // Ingresos proyectados del Año 1 al Año 5 (USD)
      clvCacAdjusted: "X.X:1",
      buyerPersonas: ["BP-1: Nombre", "BP-2: Nombre"],
      sizing: {
        topDown: "Muestreo Top-down con pasos explícitos de reducción",
        bottomUp: "Suma de mercados accesibles por Buyer Persona",
        sources: "Fuentes consultadas (Statista, Banxico, INEGI, etc.)"
      },
      sourcesList: [
        { name: "Banxico Informes Sectoriales", url: "https://www.banxico.org.mx", verified: true },
        { name: "INEGI Estadística Industrial", url: "https://www.inegi.org.mx", verified: true },
        { name: "Estimación interna del equipo", url: "", verified: false }
      ],
      competitors: [
        { name: "Competidor 1", share: "X%", threat: "🔴 Alta | 🟡 Media | 🟢 Baja", moat: "Ventaja defensible" }
      ],
      unitEconomics: [
        {
          bpName: "Nombre Buyer Persona",
          clvBase: "$X USD",
          crossSellBoost: "+$X USD (Cross-selling)",
          clvAdjusted: "$X USD (+X%)",
          cac: "$X USD",
          clvCac: "X:1",
          payback: "X meses"
        }
      ],
      scoreBreakdown: [
        { criterion: "Urgencia del problema", points: 5, note: "Justificación" },
        { criterion: "Diferenciación", points: 4, note: "Justificación" },
        { criterion: "Escalabilidad", points: 5, note: "Justificación" },
        { criterion: "Velocidad al mercado", points: 4, note: "Justificación" },
        { criterion: "Fit estratégico", points: 5, note: "Justificación" }
      ],
      risks: [
        { risk: "Nombre del riesgo", prob: "Alta", impact: "Alto", level: 5, mitigation: "Estrategia de mitigación" }
      ],
      verdictReason: "Razonamiento ejecutivo final de 4 a 6 líneas sobre por qué avanza o se descarta."
    }
  ]
};
```

---

## Verificación del Archivo Generado

Al escribir `reporte_dimensionamiento.html`, la subskill debe verificar que:

1. El archivo HTML contenga la declaración `<!DOCTYPE html>`, cargue Chart.js e incluya las fuentes `Sora` e `Inter`.
2. Incluya los controles interactivos de ajuste de horizonte temporal (1y, 3y, 5y) y el filtro por tipo de idea.
3. La gráfica de trayectoria de ingresos responda activamente a los filtros.
4. El script `window.REPORT_DATA` contenga todas las ideas analizadas con sus datos de 1, 3 y 5 años.
