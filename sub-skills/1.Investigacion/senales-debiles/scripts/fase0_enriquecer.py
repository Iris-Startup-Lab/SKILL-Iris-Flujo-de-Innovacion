"""
fase0_enriquecer.py

Enriquecimiento determinístico del dataset cuantitativo para la skill
'senales-debiles'. Lee el CSV limpio y el fase0_output.json (roles, pregunta,
hipotesis) y produce un CSV enriquecido con columnas derivadas:

  - Normalización de espacios en columnas categóricas/texto.
  - Codificación ligera de columnas de texto SEGÚN reglas semánticas declaradas.
  - Detección de variables binarias (0/1, Sí/No, verdadero/falso, etc.).
  - Métricas de calidad de respuesta y advertencias.

Este script NO aplica reglas de dominio por defecto: la codificación ligera
depende de las reglas que la Fase 0 declare (o de --rules). Si una columna
temática no tiene reglas, se advierte y se preserva el valor original
(passthrough) en lugar de inventar categorías de un dominio ajeno.

Uso:
    python fase0_enriquecer.py <csv_limpio> <fase0_output.json> -o <csv_enriquecido> [--update-fase0]

El parámetro --update-fase0 actualiza el mismo fase0_output.json con:
  - dataset_enriquecido (incluye variables_binarias)
  - codificacion_ligera (resultados; conserva reglas)
  - calidad_respuesta
  - advertencias (append)

Reglas de codificación (estructura JSON):
  {
    "problem":   [["categoria_1", ["keyword1", ...]], ...],
    "solution":  [["categoria_1", ["keyword1", ...]], ...],
    "segment":   [["categoria_1", ["keyword1", ...]], ...]
  }
  Se leen, en orden de prioridad:
  1. --rules <json> (explícito de línea de comandos)
  2. fase0_output.json['datos']['codificacion_ligera']['reglas']
  3. sin reglas: no se codifica; passthrough + advertencia.
"""
import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------
def normalize_whitespace(val):
    if pd.isna(val):
        return val
    return re.sub(r"\s+", " ", str(val).strip())


def categorize_text(val, rules):
    """Aplica reglas de keyword a un valor de texto. La primera coincidencia
    gana; si ninguna coincide devuelve 'otro'."""
    if pd.isna(val):
        return np.nan
    v = str(val).lower()
    for cat, keywords in rules:
        if any(kw in v for kw in keywords):
            return cat
    return "otro"


BINARIO_STR = {
    "1": 1, "0": 0, "1.0": 1, "0.0": 0,
    "true": 1, "false": 0, "verdadero": 1, "falso": 0,
    "si": 1, "sí": 1, "no": 0, "s": 1, "n": 0, "y": 1,
}


def es_binaria(series):
    """True si la serie es binaria: valores no nulos ⊆ {0,1} numéricos o
    pares booleanos típicos (Sí/No, verdadero/falso, s/n, y/n)."""
    s = series.dropna()
    if len(s) == 0:
        return False
    valores = set(s.astype(str).str.strip().str.lower())
    if valores.issubset({"0", "1", "0.0", "1.0"}):
        return True
    return valores.issubset(BINARIO_STR)


def coerce_binaria(series):
    """Devuelve una serie numérica 0/1 si la columna es binaria; si la
    columna ya es numérica 0/1 la devuelve tal cual; si un valor cae en
    BINARIO_STR lo convierte; si algo no es binario devuelve None."""
    s = series.dropna()
    if len(s) == 0:
        return None
    valores = set(s.astype(str).str.strip().str.lower())
    if not valores.issubset(BINARIO_STR):
        return None
    return s.map(lambda x: BINARIO_STR[str(x).strip().lower()])


def object_columns(df):
    """Devuelve columnas de texto (object/string) sin warnings de pandas."""
    return [c for c in df.columns if df[c].dtype.name in ("object", "string")]


def build_quality_report(df):
    """Construye métricas de calidad de respuesta."""
    total = len(df)
    generic = ["no", "nada", "ninguno", "na", ".", "-", "--", "...", "x"]
    baja_calidad = 0
    for col in object_columns(df):
        for val in df[col].dropna().astype(str).str.strip().str.lower():
            if len(val) <= 2 or val in generic:
                baja_calidad += 1
    dupes = df.duplicated().sum()
    return {
        "baja_calidad": int(baja_calidad),
        "total_marcados": int(baja_calidad),
        "duplicados_exactos": int(dupes),
        "nota": (f"{baja_calidad} respuestas cortas/genéricas detectadas; "
                 f"{dupes} duplicados exactos.")
    }


def missingness_advertencias(df, threshold=0.40):
    """Genera advertencias para columnas con alta tasa de missingness."""
    advs = []
    for col in df.columns:
        if col.endswith("_Cat"):
            continue
        pct = df[col].isna().mean()
        if pct >= threshold:
            advs.append(f"{col}: {df[col].isna().sum()}/{len(df)} "
                        f"({pct*100:.1f}%) valores faltantes.")
    return advs


# ---------------------------------------------------------------------------
# Codificación ligera (solo por reglas declaradas; nunca reglas de dominio)
# ---------------------------------------------------------------------------
def codificar_columna(df, col, col_key, reglas, advertencias, columnas_nuevas,
                      codificacion_ligera, procesadas):
    """Crea {col}_Cat según las reglas declaradas para el rol. Sin reglas:
    passthrough del valor original y advertencia (nunca categorías de un
    dominio ajeno)."""
    new_col = f"{col}_Cat"
    if new_col in procesadas or col not in df.columns:
        return
    procesadas.add(new_col)
    rules = reglas.get(col_key)
    if rules:
        df[new_col] = df[col].apply(lambda x: categorize_text(x, rules))
        criterio = "reglas semánticas por keyword (declaradas)"
    else:
        cardinalidad = df[col].dropna().nunique()
        if cardinalidad <= 25:
            df[new_col] = df[col].astype("string")
            criterio = ("sin reglas declaradas: passthrough del valor original "
                        "(revisar en Fase 0 con codificacion_ligera.reglas)")
        else:
            df[new_col] = df[col].apply(lambda x: np.nan if pd.isna(x) else "otro")
            criterio = ("sin reglas declaradas y cardinalidad alta: valor propio "
                        "no aplicable, marcado 'otro' (declarar reglas en Fase 0)")
        advertencias.append(
            f"{col}: sin reglas de codificación declaradas en "
            "codificacion_ligera.reglas; columna generada sin categorización "
            "semántica. Revisa y declara reglas en Fase 0."
        )
    columnas_nuevas.append(new_col)
    codificacion_ligera[new_col] = {
        "variable_original": col,
        "criterio": criterio,
        "categorias": df[new_col].value_counts().to_dict(),
    }


# ---------------------------------------------------------------------------
# Función principal
# ---------------------------------------------------------------------------
def enriquecer(csv_path, fase0_path, output_csv, update_fase0=False,
               rules_path=None):
    df = pd.read_csv(csv_path, encoding="utf-8-sig")
    n_original = len(df)

    with open(fase0_path, encoding="utf-8-sig") as f:
        fase0 = json.load(f)

    roles = fase0.get("datos", {}).get("roles", {})

    # Reglas: --rules primero, luego las declaradas en Fase 0.
    reglas = {}
    if rules_path:
        with open(rules_path, encoding="utf-8-sig") as f:
            reglas = json.load(f)
    cod_fase0 = fase0.get("datos", {}).get("codificacion_ligera", {})
    if isinstance(cod_fase0, dict) and isinstance(cod_fase0.get("reglas"), dict):
        reglas = dict(cod_fase0["reglas"], **reglas if rules_path else {})

    columnas_nuevas = []
    codificacion_ligera = {}
    advertencias = []

    # Normalizar espacios en columnas de texto
    for col in object_columns(df):
        df[col] = df[col].apply(normalize_whitespace)

    # Variables binarias (0/1, Sí/No, verdadero/falso) sobre columnas originales
    binarias = [c for c in df.columns if es_binaria(df[c])]

    # Codificación ligera según roles
    procesadas = set()
    for col in roles.get("categoria_problema", []):
        codificar_columna(df, col, "problem", reglas, advertencias,
                          columnas_nuevas, codificacion_ligera, procesadas)

    for col in roles.get("categoria_solucion", []):
        codificar_columna(df, col, "solution", reglas, advertencias,
                          columnas_nuevas, codificacion_ligera, procesadas)

    for col in roles.get("segmento_perfil", []):
        codificar_columna(df, col, "segment", reglas, advertencias,
                          columnas_nuevas, codificacion_ligera, procesadas)

    # Calidad de respuesta
    calidad = build_quality_report(df)
    advertencias += missingness_advertencias(df)
    if calidad["duplicados_exactos"]:
        advertencias.append(
            f"{calidad['duplicados_exactos']} registros duplicados exactos."
        )

    # Guardar CSV enriquecido
    df.to_csv(output_csv, index=False, encoding="utf-8")

    # Actualizar fase0_output.json si se solicita
    if update_fase0:
        fase0.setdefault("datos", {})
        fase0["datos"]["dataset_enriquecido"] = {
            "path": str(Path(output_csv).name),
            "n_registros_original": n_original,
            "n_registros_final": len(df),
            "columnas_originales": [
                c for c in df.columns if c not in columnas_nuevas
            ],
            "columnas_nuevas": columnas_nuevas,
            "variables_binarias": binarias,
        }
        cod_out = fase0["datos"].get("codificacion_ligera", {})
        if not isinstance(cod_out, dict):
            cod_out = {}
        cod_out.update(codificacion_ligera)
        fase0["datos"]["codificacion_ligera"] = cod_out
        fase0["datos"]["calidad_respuesta"] = calidad
        fase0["advertencias"] = fase0.get("advertencias", []) + advertencias
        with open(fase0_path, "w", encoding="utf-8") as f:
            json.dump(fase0, f, ensure_ascii=False, indent=2)

    # Resumen en consola
    print(f"CSV enriquecido guardado en: {output_csv}")
    print(f"Registros: {len(df)} | Columnas nuevas: {len(columnas_nuevas)}")
    for c in columnas_nuevas:
        print(f"  - {c}")
    print(f"Variables binarias detectadas: {len(binarias)}")
    for c in binarias:
        print(f"  - {c}")
    if update_fase0:
        print(f"fase0_output.json actualizado: {fase0_path}")
    if advertencias:
        print("Advertencias generadas:")
        for a in advertencias:
            print(f"  - {a}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Enriquecimiento determinístico del dataset cuantitativo.")
    parser.add_argument("csv", help="CSV limpio de entrada")
    parser.add_argument("fase0", help="fase0_output.json con roles mapeados")
    parser.add_argument("-o", "--output", required=True,
                        help="Ruta del CSV enriquecido de salida")
    parser.add_argument("--update-fase0", action="store_true",
                        help="Actualizar fase0_output.json con resultados")
    parser.add_argument("--rules", default=None,
                        help="JSON con reglas personalizadas de codificación")
    args = parser.parse_args()

    enriquecer(args.csv, args.fase0, args.output,
               update_fase0=args.update_fase0, rules_path=args.rules)


if __name__ == "__main__":
    main()
