"""
fase1_analisis.py

Análisis cuantitativo exploratorio (EDA) genérico para la skill 'senales-debiles'.
Lee el CSV enriquecido y el fase0_output.json (roles, pregunta, hipotesis,
pre_registro) y produce un borrador de fase1_output.json con bloques B0-B7
precalculados.

El borrador incluye:
  - Conteos, porcentajes, tasas base y métricas de robustez.
  - Alertas para que el LLM decida si escala, descarta o marca como consistente.
  - Datos listos para gráficas (barras, heatmap).
  - Cálculos adicionales: tamaño de efecto, concentración, correlaciones.

Uso:
    python fase1_analisis.py <csv_enriquecido> <fase0_output.json> -o <fase1_borrador.json>

El LLM debe revisar el borrador y generar el fase1_output.json final,
seleccionando qué candidatos escalan, ajustando severidad/sorpresa y redactando
expectativa_rota / hipotesis_valor.
"""
import argparse
import json
import math
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------
_CODIFICACION_LIGERA = None  # se establece en analizar() para mapeos de columna


def chi2_contingency(table):
    """Calcula el estadistico chi2 y p-valor para una tabla de contingencia.

    El chi2, los grados de libertad y los esperados se calculan con numpy, sin
    dependencias. El p-valor se obtiene de scipy **si esta disponible**; si no,
    queda en None y el script sigue: los tamanos de efecto (Cramer's V) no lo
    necesitan. La importacion va dentro de la funcion a proposito, para que la
    skill corra suelta en un entorno sin scipy.
    """
    if table.shape[0] < 2 or table.shape[1] < 2:
        return None, None, None, None
    total = table.sum().sum()
    if total == 0:
        return None, None, None, None
    row_sums = table.sum(axis=1).values.reshape(-1, 1)
    col_sums = table.sum(axis=0).values.reshape(1, -1)
    expected = row_sums @ col_sums / total
    expected = np.where(expected == 0, np.nan, expected)
    chi2 = np.nansum((table.values - expected) ** 2 / expected)
    dof = (table.shape[0] - 1) * (table.shape[1] - 1)
    try:
        from scipy.stats import chi2 as chi2_dist
        p_value = float(chi2_dist.sf(chi2, dof))
    except Exception:
        p_value = None
    return chi2, p_value, dof, expected


def fmt_pct(num, den):
    if den == 0:
        return None
    return {"numerador": int(num), "denominador": int(den),
            "porcentaje": round(num / den * 100, 1)}


def safe_median(series):
    s = series.dropna()
    return float(s.median()) if len(s) > 0 else None


def safe_mean(series):
    s = series.dropna()
    return float(s.mean()) if len(s) > 0 else None


def iqr_outliers(series, k=1.5):
    s = series.dropna()
    if len(s) == 0:
        return pd.Series(dtype=float), None, None
    q1, q3 = s.quantile([0.25, 0.75])
    iqr = q3 - q1
    low = q1 - k * iqr
    high = q3 + k * iqr
    return s[(s < low) | (s > high)], low, high


def cohens_d(x, y):
    """Tamaño de efecto para diferencia de medias entre dos grupos."""
    x = x.dropna()
    y = y.dropna()
    if len(x) < 2 or len(y) < 2:
        return None
    pooled_std = math.sqrt(((len(x) - 1) * x.var() + (len(y) - 1) * y.var()) /
                           (len(x) + len(y) - 2))
    if pooled_std == 0:
        return 0.0
    return float((x.mean() - y.mean()) / pooled_std)


def cramers_v(x, y):
    """Tamaño de efecto para tablas de contingencia."""
    table = pd.crosstab(x, y)
    if table.shape[0] < 2 or table.shape[1] < 2:
        return None
    chi2, _, _, _ = chi2_contingency(table)
    if chi2 is None:
        return None
    n = table.sum().sum()
    if n == 0:
        return None
    phi2 = chi2 / n
    r, k = table.shape
    phi2corr = max(0, phi2 - ((k - 1) * (r - 1)) / (n - 1))
    rcorr = r - ((r - 1) ** 2) / (n - 1)
    kcorr = k - ((k - 1) ** 2) / (n - 1)
    denom = min((kcorr - 1), (rcorr - 1))
    if denom == 0:
        return None
    return math.sqrt(phi2corr / denom)


def gini(series):
    """Coeficiente de Gini (0 = igualdad, 1 = concentración total)."""
    s = series.dropna().sort_values()
    n = len(s)
    if n == 0:
        return None
    index = np.arange(1, n + 1)
    return float((2 * np.sum(index * s.values)) / (n * np.sum(s.values)) - (n + 1) / n)


def sanitize_json(obj):
    """Reemplaza NaN/Inf por None para que json.dump no falle y aplana tipos
    numpy (int64, float64, bool_) a tipos nativos serializables."""
    if isinstance(obj, dict):
        return {k: sanitize_json(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [sanitize_json(v) for v in obj]
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        v = float(obj)
        if math.isnan(v) or math.isinf(v):
            return None
        return v
    if isinstance(obj, np.bool_):
        return bool(obj)
    return obj


def material_diff(pct1, pct2, threshold=5.0):
    """Diferencia material en puntos porcentuales."""
    if pct1 is None or pct2 is None:
        return False
    return abs(pct1 - pct2) > threshold


PISO_N_ABS = 15

Z_95 = 1.96


def wilson_ci(x, n):
    """Intervalo de Wilson al 95% para una proporcion x/n."""
    if n <= 0:
        return 0.0, 0.0
    p = x / n
    denom = 1 + Z_95 * Z_95 / n
    center = (p + Z_95 * Z_95 / (2 * n)) / denom
    half = Z_95 * math.sqrt(p * (1 - p) / n + Z_95 * Z_95 / (4 * n * n)) / denom
    return (center - half) * 100, (center + half) * 100


def wilson_distinto_de_base(x, n, base_pct):
    """True si la tasa x/n difiere de base_pct: su intervalo de Wilson al 95%
    no contiene la base (SPEC.md seccion 5)."""
    lo, hi = wilson_ci(x, n)
    return not (lo <= base_pct <= hi)


def find_cat_column(df, source_col, codificacion_ligera=None):
    """Busca la versión categorizada de una columna.

    1. Mapeo explícito de codificacion_ligera (variable_original -> columna nueva).
    2. Sufijo _Cat sobre el nombre original.
    3. Heurística por prefijo (quita _Texto, _Original_Texto, _Normalizado).
    4. La propia columna si ya es categórica.
    """
    if codificacion_ligera is None:
        codificacion_ligera = _CODIFICACION_LIGERA
    if codificacion_ligera:
        for new_col, meta in codificacion_ligera.items():
            if meta.get("variable_original") == source_col and new_col in df.columns:
                return new_col
    candidates = [f"{source_col}_Cat", f"{source_col}_cat"]
    for c in candidates:
        if c in df.columns:
            return c
    # heurística por prefijo
    prefix = re.sub(r"_(Texto|Original_Texto|Normalizado)$", "", source_col)
    for c in df.columns:
        if c.endswith("_Cat") and (c == f"{prefix}_Cat" or prefix.lower() in c.lower()):
            return c
    if source_col in df.columns and df[source_col].dtype.name in ("object", "string", "category"):
        return source_col
    return None


def get_role_columns(df, roles, role_name):
    """Devuelve columnas disponibles para un rol, priorizando versiones _Cat."""
    cols = []
    for col in roles.get(role_name, []):
        cat_col = find_cat_column(df, col)
        if cat_col:
            cols.append(cat_col)
    return list(dict.fromkeys(cols))  # preserve order, remove dups


def get_numeric_role_columns(df, roles, role_name):
    """Devuelve columnas numéricas disponibles para un rol."""
    cols = []
    for col in roles.get(role_name, []):
        if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
            cols.append(col)
    return cols


# ---------------------------------------------------------------------------
# Variables binarias genéricas (B4 / heatmaps)
# ---------------------------------------------------------------------------
BINARIO_STR = {
    "1": 1, "0": 0, "1.0": 1, "0.0": 0,
    "true": 1, "false": 0, "verdadero": 1, "falso": 0,
    "si": 1, "sí": 1, "no": 0, "s": 1, "n": 0, "y": 1,
}


def es_binaria(series):
    """True si todos los valores no nulos son pares binarios típicos
    (0/1, Sí/No, verdadero/falso, s/n, y/n)."""
    s = series.dropna()
    if len(s) == 0:
        return False
    valores = set(s.astype(str).str.strip().str.lower())
    return valores.issubset(BINARIO_STR)


def coerce_binaria(series):
    """Numérico 0/1 de una columna binaria, o None si no es binaria."""
    if not es_binaria(series):
        return None
    return series.map(lambda x: BINARIO_STR[str(x).strip().lower()])


def get_binaria_columns(df, fase0):
    """Columnas binarias: las declaradas en `dataset_enriquecido.variables_binarias`
    de Fase 0; si no hay, detección por contenido sobre el CSV."""
    declaradas = (fase0.get("datos", {})
                       .get("dataset_enriquecido", {})
                       .get("variables_binarias", []))
    cols = [c for c in declaradas if c in df.columns and es_binaria(df[c])]
    if not cols:
        for c in df.columns:
            if c.endswith("_Cat"):
                continue
            if es_binaria(df[c]):
                cols.append(c)
    return list(dict.fromkeys(cols))


# ---------------------------------------------------------------------------
# Bloques
# ---------------------------------------------------------------------------
def b0_infraestructura(df, roles):
    numeric_intensity = get_numeric_role_columns(df, roles, "intensidad_valor")
    numeric_effort = get_numeric_role_columns(df, roles, "esfuerzo_accion")
    numeric_cols = list(dict.fromkeys(numeric_intensity + numeric_effort))

    descriptivos = []
    for col in numeric_cols:
        s = df[col].dropna()
        Q1 = s.quantile(0.25)
        Q3 = s.quantile(0.75)
        outliers, low, high = iqr_outliers(df[col])
        descriptivos.append({
            "variable": col,
            "n": int(len(s)),
            "n_faltantes": int(df[col].isna().sum()),
            "pct_faltantes": round(df[col].isna().mean() * 100, 1),
            "media": round(s.mean(), 2) if len(s) else None,
            "mediana": round(s.median(), 2) if len(s) else None,
            "moda": float(s.mode().iloc[0]) if len(s.mode()) > 0 else None,
            "desv_estandar": round(s.std(), 2) if len(s) else None,
            "min": float(s.min()) if len(s) else None,
            "max": float(s.max()) if len(s) else None,
            "outliers_iqr": {"n": len(outliers), "umbral_inferior": float(low) if low is not None else None,
                              "umbral_superior": float(high) if high is not None else None},
        })

    duplicados = int(df.duplicated().sum())
    faltantes = []
    for col in df.columns:
        pct = df[col].isna().mean()
        if pct > 0:
            faltantes.append({"variable": col, "n_faltantes": int(df[col].isna().sum()),
                              "pct_faltantes": round(pct * 100, 1)})

    return {
        "aplica": True,
        "descriptivos": descriptivos,
        "duplicados": {"n_exactos": duplicados},
        "faltantes": faltantes,
    }


def b1_tension_intensidad_esfuerzo(df, roles):
    intensity_cols = get_numeric_role_columns(df, roles, "intensidad_valor")
    effort_cols = get_numeric_role_columns(df, roles, "esfuerzo_accion")
    if not intensity_cols:
        return {"aplica": False, "motivo": "No hay variable numerica de intensidad mapeada"}

    primary_intensity = intensity_cols[0]
    hallazgos = []

    # Cruzar intensidad (Likert) con cada variable numérica de esfuerzo/valor
    for target_col in effort_cols + [c for c in intensity_cols if c != primary_intensity]:
        if target_col not in df.columns:
            continue
        both = df[[primary_intensity, target_col]].dropna()
        if len(both) < 10:
            continue
        grupos = []
        for val in sorted(both[primary_intensity].unique()):
            sub = both[both[primary_intensity] == val][target_col]
            if len(sub) == 0:
                continue
            grupos.append({
                "intensidad": float(val),
                "n": len(sub),
                "mediana": round(sub.median(), 2),
                "media": round(sub.mean(), 2),
                "min": float(sub.min()),
                "max": float(sub.max()),
            })
        if len(grupos) < 2:
            continue

        # Detectar monotonía directa / inversa / mixta
        medians = [g["mediana"] for g in grupos if g["mediana"] is not None]
        monotona_creciente = all(medians[i] <= medians[i+1] for i in range(len(medians)-1))
        monotona_decreciente = all(medians[i] >= medians[i+1] for i in range(len(medians)-1))
        alertas = []
        if monotona_decreciente and len(grupos) >= 3:
            alertas.append("relacion_monotona_inversa")
        if any(g["n"] < 5 for g in grupos):
            alertas.append("n_bajo_en_extremos")

        # La expectativa es "a mayor intensidad, mayor esfuerzo" (creciente).
        # Solo una relación monótona decreciente contradice la expectativa.
        recomendacion = "escalar" if monotona_decreciente else "revisar"

        hallazgos.append({
            "id_propuesto": f"SD-CUANT-{len(hallazgos)+1:03d}",
            "tipo": "Multivariante",
            "cruce": f"{primary_intensity} x {target_col}",
            "dato": grupos,
            "robustez": {"n_total": len(both), "pct_muestra": round(len(both) / len(df) * 100, 1)},
            "alertas": alertas,
            "recomendacion_llm": recomendacion,
            "grafica": {
                "tipo": "bar",
                "eje_x": primary_intensity,
                "eje_y": target_col,
            }
        })

    return {
        "aplica": len(hallazgos) > 0,
        "expectativa_base": "A mayor intensidad percibida, mayor esfuerzo o impacto reportado",
        "resultado": "CONTRADICCIÓN" if any(h["recomendacion_llm"] == "escalar" for h in hallazgos) else "CONSISTENTE",
        "hallazgos": hallazgos,
    }


def b2_desacople_problema_solucion(df, roles):
    problem_cols = get_role_columns(df, roles, "categoria_problema")
    solution_cols = get_role_columns(df, roles, "categoria_solucion")
    if not problem_cols or not solution_cols:
        return {"aplica": False, "motivo": "Faltan roles categoria_problema o categoria_solucion"}

    primary_problem = problem_cols[0]
    primary_solution = solution_cols[0]

    cross = pd.crosstab(df[primary_problem], df[primary_solution])
    if cross.shape[0] < 2 or cross.shape[1] < 2:
        return {"aplica": False, "motivo": "Crosstab muy pequeño"}

    # Celdas destacadas: altas concentraciones y ceros inesperados
    total = cross.sum().sum()
    celdas_destacadas = []
    for row in cross.index:
        for col in cross.columns:
            n = cross.loc[row, col]
            pct = n / total * 100 if total else 0
            if n >= 5 and pct >= 3:
                celdas_destacadas.append({
                    "dificultad": str(row), "solucion": str(col), "n": int(n), "pct_total": round(pct, 1)
                })
    celdas_destacadas.sort(key=lambda x: x["n"], reverse=True)

    # Filas con alta proporcion en 'otro' (sin solución articulada)
    if "otro" in cross.columns:
        otro_pct = (cross["otro"] / cross.sum(axis=1)).fillna(0) * 100
    else:
        otro_pct = pd.Series(0, index=cross.index)

    hallazgos = []
    for problema in cross.index:
        fila_total = cross.loc[problema].sum()
        if fila_total < 5:
            continue
        otro_n = cross.loc[problema].get("otro", 0)
        alertas = []
        if otro_pct.get(problema, 0) > 30:
            alertas.append("alta_proporcion_otro")
        top_soluciones = cross.loc[problema].sort_values(ascending=False).head(3).to_dict()
        hallazgos.append({
            "id_propuesto": f"SD-CUANT-{len(hallazgos)+1:03d}",
            "tipo": "Multivariante",
            "problema": str(problema),
            "n": int(fila_total),
            "top_soluciones": {str(k): int(v) for k, v in top_soluciones.items()},
            "pct_en_otro": round(otro_pct.get(problema, 0), 1),
            "alertas": alertas,
            "recomendacion_llm": "escalar" if alertas else "revisar",
        })

    return {
        "aplica": True,
        "expectativa_base": "Cada problema se resuelve con una solución coherente",
        "resultado": "MIXTO" if hallazgos else "CONSISTENTE",
        "hallazgos": hallazgos,
        "grafica": {
            "tipo": "heatmap",
            "eje_x": list(cross.columns),
            "eje_y": list(cross.index),
            "valores": cross.values.tolist(),
        },
        "efecto": {"cramers_v": round(cramers_v(df[primary_problem], df[primary_solution]) or 0, 3)},
    }


def b3_coocurrencia_inesperada(df, roles):
    problem_cols = get_role_columns(df, roles, "categoria_problema")
    segment_cols = get_role_columns(df, roles, "segmento_perfil")
    if not problem_cols or not segment_cols:
        return {"aplica": False, "motivo": "Faltan roles categoria_problema o segmento_perfil"}

    primary_problem = problem_cols[0]
    hallazgos = []

    for seg_col in segment_cols:
        cross = pd.crosstab(df[primary_problem], df[seg_col])
        if cross.shape[1] < 2:
            continue
        base_rates = (cross.sum(axis=0) / cross.sum().sum()).fillna(0)
        for problema in cross.index:
            fila = cross.loc[problema]
            fila_total = fila.sum()
            if fila_total < 5:
                continue
            for segmento in cross.columns:
                n = cross.loc[problema, segmento]
                if n < 3:
                    continue
                n_segmento = int(df[seg_col].value_counts().get(segmento, 0))
                if n_segmento < PISO_N_ABS:
                    # Piso de N (SPEC.md seccion 5): denominador menor a 15
                    # registros; la desviacion se considera CONSISTENTE.
                    continue
                pct_segmento = n / n_segmento * 100 if n_segmento else 0
                pct_base = fila_total / cross.sum().sum() * 100
                # Regla de tasa base + significancia (SPEC.md seccion 5):
                # diferencia material > 5 pp y el intervalo de Wilson del
                # subgrupo no contiene la base.
                if material_diff(pct_segmento, pct_base, threshold=5.0) and \
                        wilson_distinto_de_base(n, n_segmento, pct_base):
                    hallazgos.append({
                        "id_propuesto": f"SD-CUANT-{len(hallazgos)+1:03d}",
                        "tipo": "Co-ocurrencia",
                        "problema": str(problema),
                        "segmento": str(segmento),
                        "n": int(n),
                        "n_segmento": n_segmento,
                        "pct_del_segmento": round(pct_segmento, 1),
                        "pct_base_problema": round(pct_base, 1),
                        "alertas": ["desviacion_de_base"],
                        "recomendacion_llm": "escalar",
                    })

    return {
        "aplica": len(hallazgos) > 0,
        "expectativa_base": "Los problemas se distribuyen proporcionalmente entre segmentos",
        "resultado": "CONTRADICCIÓN" if hallazgos else "CONSISTENTE",
        "hallazgos": hallazgos[:10],  # limitar para no saturar
    }


def b4_segmentos_invertidos(df, roles, fase0):
    segment_cols = get_role_columns(df, roles, "segmento_perfil")
    binaria_cols = get_binaria_columns(df, fase0)
    if not segment_cols or not binaria_cols:
        return {"aplica": False, "motivo": ("No hay segmentos mapeados o no existe "
                                            "variable binaria (0/1, Sí/No) para "
                                            "medir tasa por segmento")}

    binaria = binaria_cols[0]
    # Excluir la columna _Cat derivada de la propia variable binaria para no
    # cruzar la variable consigo misma (tautologia, p. ej. tiene_empleo vs
    # tiene_empleo_Cat).
    binaria_cat = find_cat_column(df, binaria)
    segment_cols = [s for s in segment_cols if s != binaria_cat]
    if not segment_cols:
        return {"aplica": False, "motivo": ("La unica variable de segmento es la "
                                            "categorizacion de la propia variable "
                                            "binaria; no hay segmentos independientes.")}
    serie_bin = coerce_binaria(df[binaria])
    if serie_bin is None:
        return {"aplica": False, "motivo": "Variable binaria no convertible a 0/1"}

    hallazgos = []
    for seg_col in segment_cols:
        rates = []
        for segmento in df[seg_col].dropna().unique():
            idx = df[seg_col] == segmento
            n = int(idx.sum())
            if n < 5:
                continue
            if n < PISO_N_ABS:
                # Piso de N (SPEC.md seccion 5): denominador menor a 15
                # registros; la diferencia entre segmentos es CONSISTENTE.
                continue
            positivos = int(serie_bin[idx].sum())
            rates.append({
                "segmento": str(segmento),
                "n": int(n),
                "positivos": positivos,
                "pct_positivos": round(positivos / n * 100, 1),
            })
        if len(rates) < 2:
            continue
        rates.sort(key=lambda x: x["pct_positivos"])
        min_rate, max_rate = rates[0], rates[-1]
        if material_diff(max_rate["pct_positivos"], min_rate["pct_positivos"], threshold=10):
            hallazgos.append({
                "id_propuesto": f"SD-CUANT-{len(hallazgos)+1:03d}",
                "tipo": "Segmentos invertidos",
                "segmento": seg_col,
                "variable_binaria": binaria,
                "dato": rates,
                "alertas": ["diferencia_entre_segmentos"],
                "recomendacion_llm": "escalar",
                "grafica": {"tipo": "bar", "eje_x": seg_col,
                            "eje_y": f"% de positivos en {binaria}"},
            })

    return {
        "aplica": len(hallazgos) > 0,
        "expectativa_base": f"La tasa de positivos de `{binaria}` es homogénea entre segmentos",
        "resultado": "CONTRADICCIÓN" if hallazgos else "CONSISTENTE",
        "hallazgos": hallazgos,
    }


def b5_outliers_comportamiento(df, roles):
    numeric_cols = (get_numeric_role_columns(df, roles, "intensidad_valor") +
                    get_numeric_role_columns(df, roles, "esfuerzo_accion"))
    numeric_cols = list(dict.fromkeys(numeric_cols))
    segment_cols = get_role_columns(df, roles, "segmento_perfil")

    hallazgos = []
    for col in numeric_cols:
        outliers, low, high = iqr_outliers(df[col])
        if len(outliers) < 3:
            continue
        # Concentración por segmento
        outlier_df = df.loc[outliers.index]
        segmento_dominante = None
        if segment_cols:
            seg_counts = outlier_df[segment_cols[0]].value_counts()
            if len(seg_counts) > 0:
                segmento_dominante = {"segmento": str(seg_counts.index[0]),
                                      "n": int(seg_counts.iloc[0]),
                                      "pct_outliers": round(seg_counts.iloc[0] / len(outliers) * 100, 1)}
        hallazgos.append({
            "id_propuesto": f"SD-CUANT-{len(hallazgos)+1:03d}",
            "tipo": "Outliers",
            "variable": col,
            "n_outliers": int(len(outliers)),
            "umbral_superior": float(high) if high is not None else None,
            "rango": {"min": float(outliers.min()), "max": float(outliers.max())},
            "segmento_dominante": segmento_dominante,
            "alertas": ["concentracion_desproporcionada"] if segmento_dominante and segmento_dominante["pct_outliers"] > 50 else [],
            "recomendacion_llm": "escalar" if segmento_dominante and segmento_dominante["pct_outliers"] > 50 else "revisar",
        })

    return {
        "aplica": len(hallazgos) > 0,
        "expectativa_base": "La pérdida/extremos se distribuyen proporcionalmente entre segmentos",
        "resultado": "CONTRADICCIÓN" if any(h["recomendacion_llm"] == "escalar" for h in hallazgos) else "CONSISTENTE",
        "hallazgos": hallazgos,
    }


def b6_ausencia_estructurada(df, roles):
    segment_cols = get_role_columns(df, roles, "segmento_perfil")
    numeric_cols = (get_numeric_role_columns(df, roles, "intensidad_valor") +
                    get_numeric_role_columns(df, roles, "esfuerzo_accion"))
    numeric_cols = list(dict.fromkeys(numeric_cols))

    hallazgos = []
    for col in numeric_cols + [c for c in df.columns if c.endswith("_Cat")]:
        if df[col].isna().sum() == 0:
            continue
        missing_pct_global = df[col].isna().mean() * 100
        if missing_pct_global < 10:
            continue
        for seg_col in segment_cols:
            rates = df.groupby(seg_col)[col].apply(lambda x: x.isna().mean() * 100).to_dict()
            if len(rates) < 2:
                continue
            vals = list(rates.values())
            if max(vals) - min(vals) > 15:
                hallazgos.append({
                    "id_propuesto": f"SD-CUANT-{len(hallazgos)+1:03d}",
                    "tipo": "Ausencia estructurada",
                    "variable": col,
                    "segmento": seg_col,
                    "pct_missing_por_segmento": {str(k): round(v, 1) for k, v in rates.items()},
                    "alertas": ["missingness_diferencial"],
                    "recomendacion_llm": "escalar",
                })
                break  # una alerta por variable basta

    return {
        "aplica": len(hallazgos) > 0,
        "expectativa_base": "La ausencia de datos es aleatoria entre segmentos",
        "resultado": "CONTRADICCIÓN" if hallazgos else "CONSISTENTE",
        "hallazgos": hallazgos,
    }


def b7_temporal(df, roles):
    time_cols = roles.get("tiempo", [])
    if not time_cols:
        return {"aplica": False, "motivo": "No hay variable temporal mapeada"}
    return {"aplica": False, "motivo": "Analisis temporal no implementado en este borrador"}


def calculos_adicionales(df, roles):
    resultados = {}
    numeric_cols = (get_numeric_role_columns(df, roles, "intensidad_valor") +
                    get_numeric_role_columns(df, roles, "esfuerzo_accion"))
    numeric_cols = list(dict.fromkeys(numeric_cols))
    for col in numeric_cols:
        s = df[col].dropna()
        if len(s) == 0:
            continue
        resultados[col] = {
            "gini": round(gini(s), 3),
            "concentracion_top10pct": round(s.quantile(0.9) / s.sum() * 100, 1) if s.sum() > 0 else None,
        }

    # Correlaciones entre numéricas
    if len(numeric_cols) >= 2:
        corr = df[numeric_cols].corr(method="spearman").round(3)
        raw = corr.where(np.tril(np.ones(corr.shape), k=-1).astype(bool)).stack().to_dict()
        resultados["correlaciones_spearman"] = {
            f"{a}:::{b}": float(v)
            for (a, b), v in raw.items()
            if a != b and pd.notna(v) and math.isfinite(v)
        }

    return resultados


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def analizar(csv_path, fase0_path, output_path):
    global _CODIFICACION_LIGERA
    df = pd.read_csv(csv_path, encoding="utf-8-sig")
    with open(fase0_path, encoding="utf-8-sig") as f:
        fase0 = json.load(f)

    roles = fase0.get("datos", {}).get("roles", {})
    _CODIFICACION_LIGERA = fase0.get("datos", {}).get("codificacion_ligera", {})
    pregunta = fase0.get("pregunta_investigacion", "")

    bloques = {
        "B0": b0_infraestructura(df, roles),
        "B1": b1_tension_intensidad_esfuerzo(df, roles),
        "B2": b2_desacople_problema_solucion(df, roles),
        "B3": b3_coocurrencia_inesperada(df, roles),
        "B4": b4_segmentos_invertidos(df, roles, fase0),
        "B5": b5_outliers_comportamiento(df, roles),
        "B6": b6_ausencia_estructurada(df, roles),
        "B7": b7_temporal(df, roles),
    }

    # Renumerar IDs propuestos globalmente
    counter = 1
    for bloque in bloques.values():
        for h in bloque.get("hallazgos", []):
            h["id_propuesto"] = f"SD-CUANT-{counter:03d}"
            counter += 1

    borrador = {
        "fase": "fase-1-eda-cuantitativo-borrador",
        "pregunta_investigacion": pregunta,
        "advertencias": [
            "Este es un borrador generado por script. El LLM debe revisar cada hallazgo, "
            "decidir si escala, ajustar severidad/sorpresa y redactar expectativa_rota / hipotesis_valor.",
            f"N total: {len(df)} registros.",
        ],
        "datos": {
            "infraestructura": bloques["B0"],
            "bloques": [
                {"id": "B1", **bloques["B1"]},
                {"id": "B2", **bloques["B2"]},
                {"id": "B3", **bloques["B3"]},
                {"id": "B4", **bloques["B4"]},
                {"id": "B5", **bloques["B5"]},
                {"id": "B6", **bloques["B6"]},
                {"id": "B7", **bloques["B7"]},
            ],
            "calculos_adicionales": calculos_adicionales(df, roles),
            "resumen": {
                "n_registros": len(df),
                "n_bloques_aplicables": sum(1 for b in bloques.values() if b.get("aplica")),
                "n_hallazgos_detectados": counter - 1,
            }
        }
    }

    borrador = sanitize_json(borrador)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(borrador, f, ensure_ascii=False, indent=2)

    print(f"Borrador de Fase 1 guardado en: {output_path}")
    print(f"Bloques aplicables: {borrador['datos']['resumen']['n_bloques_aplicables']}")
    print(f"Hallazgos detectados: {borrador['datos']['resumen']['n_hallazgos_detectados']}")


def main():
    parser = argparse.ArgumentParser(description="Análisis cuantitativo exploratorio genérico.")
    parser.add_argument("csv", help="CSV enriquecido de entrada")
    parser.add_argument("fase0", help="fase0_output.json con roles mapeados")
    parser.add_argument("-o", "--output", required=True,
                        help="Ruta del borrador de fase1_output.json")
    args = parser.parse_args()
    analizar(args.csv, args.fase0, args.output)


if __name__ == "__main__":
    main()
