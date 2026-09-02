"""
preparar_heatmap.py

Genera tablas de frecuencias y matrices para heatmaps a partir del CSV enriquecido
y los roles semánticos de fase0_output.json.

Salida JSON:
  - frecuencias_univariadas: conteos y porcentajes por columna categórica.
  - heatmap_principal: matriz problema x solución (si existen ambos roles).
  - otros_heatmaps: matrices adicionales útiles (problema x segmento, etc.).

Uso:
    python preparar_heatmap.py <csv_enriquecido> <fase0_output.json> -o <frecuencias.json>
"""
import argparse
import json
import re

import pandas as pd


BINARIO_STR = {
    "1": 1, "0": 0, "1.0": 1, "0.0": 0,
    "true": 1, "false": 0, "verdadero": 1, "falso": 0,
    "si": 1, "sí": 1, "no": 0, "s": 1, "n": 0, "y": 1,
}


def es_binaria(series):
    s = series.dropna()
    if len(s) == 0:
        return False
    valores = set(s.astype(str).str.strip().str.lower())
    return valores.issubset(BINARIO_STR)


def get_binaria_columns(df, fase0):
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


_CODIFICACION_LIGERA = None


def find_cat_column(df, source_col):
    """Busca la columna categorizada asociada a un rol."""
    global _CODIFICACION_LIGERA
    if _CODIFICACION_LIGERA:
        for new_col, meta in _CODIFICACION_LIGERA.items():
            if meta.get("variable_original") == source_col and new_col in df.columns:
                return new_col
    candidates = [f"{source_col}_Cat", f"{source_col}_cat"]
    for c in candidates:
        if c in df.columns:
            return c
    prefix = re.sub(r"_(Texto|Original_Texto|Normalizado)$", "", source_col)
    for c in df.columns:
        if c.endswith("_Cat") and (c == f"{prefix}_Cat" or prefix.lower() in c.lower()):
            return c
    if source_col in df.columns and df[source_col].dtype.name in ("object", "string", "category"):
        return source_col
    return None


def get_role_columns(df, roles, role_name):
    cols = []
    for col in roles.get(role_name, []):
        cat_col = find_cat_column(df, col)
        if cat_col:
            cols.append(cat_col)
    return list(dict.fromkeys(cols))


def frecuencias(df, col):
    counts = df[col].value_counts(dropna=False)
    total = counts.sum()
    return {
        "variable": col,
        "n_total": int(total),
        "categorias": [
            {
                "categoria": str(k) if pd.notna(k) else "__MISSING__",
                "n": int(v),
                "pct": round(v / total * 100, 1) if total else 0,
            }
            for k, v in counts.items()
        ],
    }


def heatmap_matrix(df, col_y, col_x):
    cross = pd.crosstab(df[col_y], df[col_x])
    return {
        "eje_y": list(cross.index),
        "eje_x": list(cross.columns),
        "eje_y_titulo": col_y,
        "eje_x_titulo": col_x,
        "valores": cross.values.tolist(),
    }


def preparar(csv_path, fase0_path, output_path):
    global _CODIFICACION_LIGERA
    df = pd.read_csv(csv_path, encoding="utf-8-sig")
    with open(fase0_path, encoding="utf-8-sig") as f:
        fase0 = json.load(f)

    roles = fase0.get("datos", {}).get("roles", {})
    _CODIFICACION_LIGERA = fase0.get("datos", {}).get("codificacion_ligera", {})

    # Frecuencias univariadas para todas las columnas categóricas con rol
    cat_role_cols = []
    for role_name in ["categoria_problema", "categoria_solucion", "segmento_perfil"]:
        cat_role_cols.extend(get_role_columns(df, roles, role_name))
    # Añadir variables binarias detectadas/declaradas si existen
    binarias = get_binaria_columns(df, fase0)
    cat_role_cols.extend(binarias)
    cat_role_cols = list(dict.fromkeys(cat_role_cols))

    frecuencias_univariadas = {col: frecuencias(df, col) for col in cat_role_cols}

    # Heatmap principal: problema x solución
    problemas = get_role_columns(df, roles, "categoria_problema")
    soluciones = get_role_columns(df, roles, "categoria_solucion")
    heatmap_principal = None
    if problemas and soluciones:
        heatmap_principal = heatmap_matrix(df, problemas[0], soluciones[0])

    # Otros heatmaps: problema x segmento, solución x segmento, app x segmento
    segmentos = get_role_columns(df, roles, "segmento_perfil")
    otros_heatmaps = []
    if problemas and segmentos:
        for seg_col in segmentos:
            otros_heatmaps.append({
                "titulo": f"{problemas[0]} x {seg_col}",
                **heatmap_matrix(df, problemas[0], seg_col),
            })
    if soluciones and segmentos:
        for seg_col in segmentos:
            otros_heatmaps.append({
                "titulo": f"{soluciones[0]} x {seg_col}",
                **heatmap_matrix(df, soluciones[0], seg_col),
            })
    if binarias and segmentos:
        for seg_col in segmentos:
            for bcol in binarias:
                otros_heatmaps.append({
                    "titulo": f"{bcol} x {seg_col}",
                    **heatmap_matrix(df, bcol, seg_col),
                })

    resultado = {
        "metadatos": {
            "n_registros": len(df),
            "columnas_usadas": {
                "categoria_problema": problemas,
                "categoria_solucion": soluciones,
                "segmento_perfil": segmentos,
                "variables_binarias": binarias,
            },
        },
        "frecuencias_univariadas": frecuencias_univariadas,
        "heatmap_principal": heatmap_principal,
        "otros_heatmaps": otros_heatmaps,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    print(f"Frecuencias y heatmaps guardados en: {output_path}")
    print(f"Columnas univariadas: {len(frecuencias_univariadas)}")
    print(f"Heatmaps adicionales: {len(otros_heatmaps)}")


def main():
    parser = argparse.ArgumentParser(description="Prepara heatmaps y frecuencias.")
    parser.add_argument("csv", help="CSV enriquecido")
    parser.add_argument("fase0", help="fase0_output.json")
    parser.add_argument("-o", "--output", required=True, help="Ruta de salida JSON")
    args = parser.parse_args()
    preparar(args.csv, args.fase0, args.output)


if __name__ == "__main__":
    main()
