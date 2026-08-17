---
name: generador-deck-pptx
description: Subskill para generar la presentación ejecutiva en PowerPoint (.pptx) del Dimensionador Estratégico aplicando rigurosamente el sistema de diseño visual Design_2.md (tipografías Sora e Inter, paleta morado-dorado de Iris StartUp Lab, slides temáticas, cards de métricas, gráficos de TAM/SAM/SOM y fuentes verificadas).
---

# Generador de Presentaciones PowerPoint — Dimensionador Estratégico

## Propósito

Esta subskill guía la creación de un deck de priorización de ideas en PowerPoint (`deck_priorizacion_dimensionador.pptx`) garantizando que **todas las diapositivas sigan exactamente el diseño visual y colores de `Design_2.md`**.

---

## Guía Estilística e Identidad Visual (Design_2.md)

### 1. Paleta de Colores Corporativa
- **Fondo de Portada y Conclusión (Dark Slide)**: Fondo degradado morado oscuro `#241B33` → `#3D2766`. Texto blanco y dorado `#E8B93E`.
- **Fondo de Diapositivas Internas (Light Slide)**: Fondo ultra claro `--purple-050` (`#F7F3FC`) o blanco puro (`#FFFFFF`).
- **Encabezados y Texto Principal**: Morado corporativo `--purple-900` (`#241B33`).
- **Acentos y CTAs Destacados**: Dorado Iris `--gold-500` (`#D4A73E`) / `--gold-400` (`#E8B93E`).
- **Semáforo de Veredicto & Riesgo**:
  - 🚀 PROTOTIPAR (Score 20–25): Verde `#15803D` / Fondo `#DCFCE7`.
  - 🔍 VALIDAR MÁS (Score 13–19): Dorado `#B8862F` / Fondo `#FEF9C3`.
  - ⛔ DESCARTAR (Score ≤12): Rojo `#B84A3D` / Fondo `#FEE2E2`.

### 2. Tipografía
- **Títulos y Cabeceras de Slide**: `Sora` (Negrita 700 / Extra-negrita 800).
- **Cuerpo de Texto, Tablas y Leyendas**: `Inter` (Regular 400 / Semi-negrita 600).

### 3. Elementos Gráficos & Badges
- **Tarjetas de KPI / Stat Cards**: Cajas con bordes redondeados, fondo morado claro (`#EDE6F7`) o blanco con sombra suave.
- **Flags de Fuentes Verificadas**:
  - `[✓ Fuente Verificada: Nombre]` en caja verde suave (`#DCFCE7`) con hipervínculo.
  - `[⚠️ Estimación / Por Validar]` en caja amarilla suave (`#FEF9C3`).

---

---

## Ejecución del Script Python (`scripts/pptx_generator.py`)

Para generar el entregable `.pptx`, ejecuta el script desde la línea de comandos en el entorno `skills_env` de Anaconda pasando un archivo JSON de datos o con los datos por defecto:

```bash
python scripts/pptx_generator.py --data report_data.json --output deck_priorizacion_dimensionador.pptx
```

### Ejemplo de integración desde Python

```python
from scripts.pptx_generator import generate_pptx_deck

report_data = {
    "meta": {
        "objetivoEstrategico": "📈 Incrementar mercado",
        "etapaNegocio": "Growth / Corporativo",
        "sector": "Fintech B2B / SaaS",
        "geografia": "México / LATAM",
        "recursosPrototipado": "$50,000 USD / 90 días"
    },
    "ideas": [
        # Lista de objetos de ideas estructurados de window.REPORT_DATA
    ]
}

generate_pptx_deck(report_data, "deck_priorizacion_dimensionador.pptx")
```

---

## Verificación

Al generar `deck_priorizacion_dimensionador.pptx`, comprueba que:

1. El script finalice sin errores de dependencias de `python-pptx`.
2. La presentación contenga la portada oscura corporativa, la matriz resumen y 1 diapositiva por cada idea prioritaria en formato 16:9.
3. Los badges de veredicto (**PROTOTIPAR**, **VALIDAR MÁS**, **DESCARTAR**) y los colores de `Design_2.md` coincidan con el informe original.

