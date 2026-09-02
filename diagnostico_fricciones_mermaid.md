# Diagnóstico de fricciones y plan de mejora — flujo IRIS

Mapa de causa → cambio → método, a partir de la evaluación de los ejemplos reales
(`real_examples/`, 01/09/2026) y de las propuestas estadísticas de Fernando (pendiente 10 del
`to-do.md`).

## Diagrama

```mermaid
flowchart LR
    %% ================= Origen de los hallazgos =================
    subgraph DIANA[Problemas detectados por Diana — Reclutalia]
        D1[F1 · Zips de transcripciones entraron sin protocolo<br/>paso 3]
        D2[F2 · Clic en enlaces del HTML daba error<br/>paso 4]
        D3[F3 · Lista de problemas del PSF en desorden<br/>paso 5]
        D4[F4 · html_9 sin justificación del score<br/>paso 9]
        D5[F5 · Reporte final de insights no se generó solo<br/>paso 11]
        D6[F6 · PSF/Journey de Reclutadores y Candidatos<br/>quedó fuera del flujo]
    end

    subgraph JONATHAN[Problemas detectados por Jonathan — Divisas]
        J1[F9 · Prompts de imagen de los ads<br/>demasiado genéricos · paso 11]
        J2[Duda del usuario · tamaño de mercado<br/>con datos supuestos · paso 1]
    end

    subgraph HTML[Detectado en los HTML · no reportado]
        H1[F7 · Marca SIMULADO global sobre<br/>42 entrevistas reales]
        H2[F8 · Ideas del html_9 numeradas 1,2,3,7,4,6…<br/>mezcla nº original y score]
    end

    subgraph FERNANDO[Propuestas de Fernando — métodos estadísticos]
        FE1[calcular_tam_sam_som.py<br/>TAM/SAM/SOM determinista]
        FE2[calcular_modelo.py<br/>unidad económica del Dimensionador]
        FE3[calcular_score.py<br/>score /25 con justificación obligatoria]
        FE4[analizar_resultados.py<br/>IC de Wilson + prueba vs. umbral/control]
        FE5[Baseline / grupo control explícito<br/>en las Testing Cards de validación]
        FE6[Explicación accesible + honestidad +<br/>gráficos por script · transversal]
        FE7[BMN · indicadores del catálogo o<br/>ranking determinista]
    end

    subgraph CAMBIOS[Cambios a hacer en la skill]
        C1[Protocolo de ingesta de material<br/>SKILL.md + entrevistas/discovery]
        C2[Regenerar muestras con plantilla data-salto<br/>ya cubierto el 01/09]
        C3[Orden declarado de problemas<br/>problem-solution-fit]
        C4[Justificación del score obligatoria en<br/>reporte.json · dimensionador]
        C5[Resumen ejecutivo en el cierre del flujo<br/>¿Qué hacer al final?]
        C6[PSF/Journey multi-perfil con contexto de flujo<br/>o regenerar con --estado]
        C7[Marca SIMULADO por reporte/sección<br/>decisión de diseño]
        C8[Dimensionador ordena por score con<br/>tabla resumen visible]
        C9[Dirección de arte ejecutable en online-ads<br/>composición, luz, estilo, qué evitar]
    end

    subgraph METODOS[Métodos para resolverlos]
        M1[TAM base × reducciones geografía/vertical/canal<br/>+ CAGR → proyección 1/3/5 años]
        M2[Métricas unitarias → CLV · CAC · CLV:CAC ·<br/>payback · ROI · ARR]
        M3[5 criterios + justificación → score /25<br/>umbrales 20-25 / 13-19 / ≤12]
        M4[k/n observado → IC Wilson + prueba z<br/>contra umbral o contra control]
        M5[A/B con baseline: dos muestras con<br/>tasa base y grupo control]
        M6[p · alpha · IC · n explicados «en palabras»<br/>+ gráficos Chart.js / Plotly / matplotlib]
        M7[Catálogo con indicadores, o desempate<br/>evidencia → costo → configuración → ejecución]
    end

    %% ===== Problemas → Cambios =====
    D1 --> C1
    D2 --> C2
    D3 --> C3
    D4 --> C4
    D5 --> C5
    D6 --> C6
    J1 --> C9
    J2 --> FE1
    H1 --> C7
    H2 --> C8

    %% ===== Cambios → Propuestas estadísticas =====
    C4 --> FE3
    C8 --> FE3
    J2 --> FE1
    C1 -.-> FE6
    C3 -.-> FE6
    C9 -.-> FE6

    %% ===== Propuestas estadísticas → Métodos =====
    FE1 --> M1
    FE2 --> M2
    FE3 --> M3
    FE4 --> M4
    FE5 --> M5
    FE6 --> M6
    FE7 --> M7

    %% ===== Métodos que alimentan otros =====
    M3 -.-> C4
    M4 -.-> C5
    M6 -.-> C3
```

## Lectura

- **Lado izquierdo (colores de origen):** las 9 fricciones. Las 6 primeras vienen de las notas de
  Diana (Reclutalia), la 9 de las notas de Jonathan (Divisas), y las 7 y 8 se detectaron al leer
  los HTML (nadie las reportó). El bloque amarillo son las propuestas de Fernando (pendiente 10).
- **Centro:** los cambios de diseño que resuelven cada fricción (tabla del `to-do.md`).
- **Derecha:** los métodos concretos que implementan las propuestas de Fernando (script → fórmula
  → salida).
- Las flechas punteadas son refuerzos transversales (la explicación accesible aplica a cualquier
  número, el score alimenta la justificación del `html_9`, etc.).
