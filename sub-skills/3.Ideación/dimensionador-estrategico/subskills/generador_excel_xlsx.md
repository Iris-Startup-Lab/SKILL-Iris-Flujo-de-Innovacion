---
name: generador-excel-xlsx
description: Subskill para compilar los resultados del Dimensionador Estratégico en un modelo financiero interactivo en Excel (.xlsx) con tablas estructuradas y gráficos nativos integrados ejecutando el script scripts/xlsx_generator.py (evolución de ingresos a 1, 3 y 5 años, comparativa TAM/SAM/SOM y Score de Atractivo).
---

# Generador de Modelos Financieros Excel — Dimensionador Estratégico

## Propósito

Esta subskill guía la generación de un libro de Excel autónomo (`modelo_financiero_dimensionamiento.xlsx`) que consolida todo el análisis del **Dimensionador Estratégico**. Utiliza el script ejecutable [scripts/xlsx_generator.py](scripts/xlsx_generator.py) para construir automáticamente las pestañas y **gráficos nativos de Excel**.

---

## Guía Estilística e Identidad Visual (Design_2.md)

1. **Paleta de Colores en Tablas & Gráficos**:
   - Cabeceras de Tabla: Morado Oscuro `#241B33` con texto blanco en negrita.
   - Filas Alternas: Morado Ultra Claro `#F7F3FC`.
   - Totales / Highlights: Dorado Iris `#D4A73E` / `#E8B93E`.
   - Veredictos (Semáforo):
     - PROTOTIPAR: Verde `#15803D` / Fondo `#DCFCE7`.
     - VALIDAR MÁS: Dorado `#B8862F` / Fondo `#FEF9C3`.
     - DESCARTAR: Rojo `#B84A3D` / Fondo `#FEE2E2`.

2. **Tipografía**:
   - Títulos y Encabezados: `Calibri` / `Sora` Negrita.
   - Datos y Cuerpo: `Calibri` / `Inter`.

---

## Estructura del Libro de Excel (`.xlsx`)

El script crea las siguientes pestañas organizadas con sus respectivos gráficos:

1. **`01_Resumen_Priorizacion`**:
   - Tabla de priorización ordenada por Score /25.
   - Columnas: Rank, Idea, Modelo, Score /25, SOM 1y, SOM 3y, SOM 5y, CLV:CAC, Buyer Personas, Veredicto.
   - **Gráfico Nativo 1**: Gráfico de Columnas/Barras — *Score de Atractivo (/25) por Idea*.

2. **`02_Proyeccion_Ingresos`**:
   - Tabla de evolución temporal de Ingresos (Año 1 a Año 5).
   - Columnas: Idea, Modelo, Veredicto, Año 1 (USD), Año 2 (USD), Año 3 (USD), Año 4 (USD), Año 5 (USD), CAGR 5y.
   - **Gráfico Nativo 2**: Gráfico de Líneas — *Trayectoria de Ingresos (Año 1 a Año 5) por Idea*.

3. **`03_TAM_SAM_SOM`**:
   - Desglose de mercados por idea.
   - Columnas: Idea, TAM Global/Reg, SAM Accesible, SOM 1 Año, SOM 3 Años, SOM 5 Años, Fuentes Verificadas.

4. **`04_Unit_Economics`**:
   - Tabla consolidada por Buyer Persona.
   - Columnas: Idea, Buyer Persona, CLV Base, Cross-Sell Boost, CLV Ajustado, CAC, Ratio CLV:CAC, Payback Period.

---

## Ejecución del Script Python (`scripts/xlsx_generator.py`)

Para generar el entregable `.xlsx`, ejecuta el script desde la línea de comandos pasando un archivo JSON de datos o con los datos por defecto:

```bash
python scripts/xlsx_generator.py --data report_data.json --output modelo_financiero_dimensionamiento.xlsx
```

### Ejemplo de integración desde Python

```python
from scripts.xlsx_generator import generate_excel_model

report_data = {
    "ideas": [
        # Lista de objetos de ideas estructurados de window.REPORT_DATA
    ]
}

generate_excel_model(report_data, "modelo_financiero_dimensionamiento.xlsx")
```

---

## Verificación

Al generar `modelo_financiero_dimensionamiento.xlsx`, comprueba que:

1. El script finalice sin errores de dependencias de `openpyxl`.
2. El archivo contenga las 4 pestañas con datos tabulares estilizados según `Design_2.md`.
3. Los gráficos nativos de Excel (`BarChart`, `LineChart`) sean totalmente editables e interactivos dentro de Excel.
