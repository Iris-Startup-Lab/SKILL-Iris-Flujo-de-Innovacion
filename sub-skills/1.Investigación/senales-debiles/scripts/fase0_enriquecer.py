"""
fase0_enriquecer.py

Enriquecimiento determinístico del dataset cuantitativo para la skill
'senales-debiles'. Lee el CSV limpio y el fase0_output.json (roles, pregunta,
hipotesis) y produce un CSV enriquecido con columnas derivadas:

  - Normalización de espacios en columnas categóricas/texto.
  - Codificación ligera de columnas de texto según reglas semánticas.
  - Normalización de métodos de pago (si se detecta una columna de pago).
  - Flags binarios opcionales (p. ej. 'tiene_app').
  - Métricas de calidad de respuesta y advertencias.

Uso:
    python fase0_enriquecer.py <csv_limpio> <fase0_output.json> -o <csv_enriquecido> [--update-fase0]

El parámetro --update-fase0 actualiza el mismo fase0_output.json con:
  - dataset_enriquecido
  - codificacion_ligera
  - calidad_respuesta
  - advertencias (append)

Reglas de codificación:
  - Se leen de fase0_output.json['codificacion_ligera']['reglas'] si existen.
  - Si no, se usan reglas por defecto para pequeño comercio en español.
  - El usuario puede sobreescribir con --rules <json>.
"""
import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Reglas por defecto: encuestas de pequeño comercio en español.
# Cada regla es (categoría, [lista de keywords]). La primera coincidencia gana.
# ---------------------------------------------------------------------------
DEFAULT_PROBLEM_RULES = [
    ("sin_dificultad", ["ningun", "nada", "no hay", "no tiene", "gusta",
                        "no se me hace", "todo en orden", "ninguno", "ninguna",
                        "hasta ahorita nada", "no se me dificulta"]),
    ("surtido_proveedores", ["surtir", "proveed", "abasto", "central",
                              "pedido", "comprar", "abastecer"]),
    ("clientes_ventas", ["cliente", "venta", "baja", "afluencia", "llegan",
                          "atraer", "vender"]),
    ("cobro_pagos", ["cobr", "pag", "fiado", "deuda", "crédit", "credit",
                      "tarjeta", "transfer", "cambio", "terminal", "qr"]),
    ("precios_costos", ["precio", "caro", "cost", "gast", "barato",
                         "inversión", "inversion", "mayoreo"]),
    ("tiempo_horario", ["tiempo", "horario", "hora", "turno", "jornada"]),
    ("competencia", ["competencia", "compet", "oxxo", "aurrera", "seven",
                      "walmart"]),
    ("administracion", ["administr", "organiz", "control", "inventar",
                          "contab", "cuentas"]),
    ("inseguridad", ["insegur", "robo", "asalt", "delincuencia", "extorsión",
                      "ladrones"]),
    ("infraestructura", ["espacio", "local", "infraestr", "equip",
                           "mobiliario", "refri"]),
    ("no_especificado", ["no especificado", "no s", "no lo se", "no lo sé"]),
]

DEFAULT_SOLUTION_RULES = [
    ("no_especificado", ["no especificado", "no s", "no lo se", "no lo sé"]),
    ("organizacion", ["organiz", "planific", "administr", "control",
                        "contab", "cuentas"]),
    ("surtido_compras", ["surtir", "proveed", "abasto", "central",
                          "comprar", "mercancía"]),
    ("estrategia_precios", ["preci", "promoci", "ofert", "descuent",
                              "mayoreo", "abarroter"]),
    ("esfuerzo_personal", ["trabaj", "esfuer", "dedic", "empeno",
                             "esmero"]),
    ("tecnologia", ["app", "aplicaci", "tecnol", "digital", "sistema",
                     "software", "plataforma"]),
    ("medios_pago", ["transfer", "tarjeta", "pago", "cobr", "terminal",
                      "qr", "spei"]),
    ("personal", ["person", "gente", "emple", "ayudante", "familia",
                   "trabajador"]),
]

DEFAULT_GIRO_RULES = [
    ("abarrotes_tienda", ["abarrot", "tienda", "tiendita", "miscelán",
                            "miscelan", "minisuper", "super", "abarrotera"]),
    ("alimentos_bebidas", ["comida", "aliment", "restaur", "taco", "fonda",
                             "cocina", "torta", "antoj", "bebida", "cremería",
                             "panadería", "carnicería", "lonja"]),
    ("ropa_calzado", ["ropa", "textil", "boutique", "zapato", "calzado",
                       "paca"]),
    ("papeleria_merceria", ["papelería", "papeler", "merceria"]),
    ("farmacia", ["farm", "medic"]),
    ("estetica_belleza", ["estética", "estetica", "belleza", "salon",
                            "peluq", " SPA", "spa"]),
    ("no_especificado", ["no especificado", "no s", "no lo se", "no lo sé"]),
]

PAYMENT_KEYWORDS = ["efectivo", "tarjeta", "transfer", "digital", "qr",
                    "spei", "vales"]

APP_BANK_KEYWORDS = ["app", "aplicación", "banco", "bbva", "banamex",
                     "santander", "bancomer", "azteca", "clip",
                     "mercado pago", "baz", "banorte", "bancoppel",
                     "hsbc", "t-conecta", "bimbo"]


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------
def normalize_whitespace(val):
    if pd.isna(val):
        return val
    return re.sub(r"\s+", " ", str(val).strip())


def categorize_text(val, rules):
    """Aplica reglas de keyword a un valor de texto."""
    if pd.isna(val):
        return np.nan
    v = str(val).lower()
    for cat, keywords in rules:
        if any(kw in v for kw in keywords):
            return cat
    return "otro"


def normalize_payment(val):
    """Normaliza una cadena de método de pago a categorías estándar."""
    if pd.isna(val):
        return np.nan
    v = str(val).lower()
    has_cash = "efectivo" in v or "cash" in v
    has_digital = any(k in v for k in ["tarjeta", "transfer", "digital",
                                         "qr", "spei"])
    if has_cash and has_digital:
        return "efectivo_digital"
    if has_digital:
        return "solo_digital"
    if has_cash:
        return "solo_efectivo"
    return "otro"


def looks_like_payment_column(series, threshold=0.30):
    """Heurística: ¿esta serie parece una columna de métodos de pago?"""
    non_null = series.dropna().astype(str).str.lower()
    if len(non_null) == 0:
        return False
    hits = non_null.apply(lambda x: any(k in x for k in PAYMENT_KEYWORDS))
    return hits.mean() >= threshold


def looks_like_appbank_column(series, threshold=0.30):
    """Heurística: ¿esta serie parece contener nombres de apps/bancos?"""
    non_null = series.dropna().astype(str).str.lower()
    if len(non_null) == 0:
        return False
    hits = non_null.apply(lambda x: any(k in x for k in APP_BANK_KEYWORDS))
    return hits.mean() >= threshold


def object_columns(df):
    """Devuelve columnas de texto (object/string) sin warnings de pandas."""
    return [c for c in df.columns if df[c].dtype.name in ("object", "string")]


def build_quality_report(df):
    """Construye métricas de calidad de respuesta."""
    total = len(df)
    # Respuestas abiertas monosílabas / genéricas en columnas de texto
    generic = ["no", "nada", "ninguno", "na", ".", "-", "--", "...", "x"]
    baja_calidad = 0
    for col in object_columns(df):
        for val in df[col].dropna().astype(str).str.strip().str.lower():
            if len(val) <= 2 or val in generic:
                baja_calidad += 1
    # Duplicados exactos
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
        # Evitar advertencias duplicadas para columnas derivadas
        if col.endswith("_Cat") or col == "tiene_app":
            continue
        pct = df[col].isna().mean()
        if pct >= threshold:
            advs.append(f"{col}: {df[col].isna().sum()}/{len(df)} "
                        f"({pct*100:.1f}%) valores faltantes.")
    return advs


# ---------------------------------------------------------------------------
# Función principal
# ---------------------------------------------------------------------------
def enriquecer(csv_path, fase0_path, output_csv, update_fase0=False,
               rules_path=None):
    df = pd.read_csv(csv_path, encoding="utf-8")
    n_original = len(df)

    with open(fase0_path, encoding="utf-8") as f:
        fase0 = json.load(f)

    roles = fase0.get("datos", {}).get("roles", {})
    notas = fase0.get("datos", {}).get("notas_semanticas", {})

    # Cargar reglas personalizadas si existen
    custom_rules = None
    if rules_path:
        with open(rules_path, encoding="utf-8") as f:
            custom_rules = json.load(f)

    problem_rules = custom_rules.get("problem", DEFAULT_PROBLEM_RULES) if custom_rules else DEFAULT_PROBLEM_RULES
    solution_rules = custom_rules.get("solution", DEFAULT_SOLUTION_RULES) if custom_rules else DEFAULT_SOLUTION_RULES
    giro_rules = custom_rules.get("giro", DEFAULT_GIRO_RULES) if custom_rules else DEFAULT_GIRO_RULES

    codificacion_ligera = {}
    columnas_nuevas = []

    # Normalizar espacios en columnas de texto
    text_cols = object_columns(df)
    for col in text_cols:
        df[col] = df[col].apply(normalize_whitespace)

    # Detectar columnas que contienen nombres de apps/bancos (no son temáticas)
    appbank_cols = set()
    for role_key in ("categoria_problema", "categoria_solucion", "segmento_perfil"):
        for col in roles.get(role_key, []):
            if col in df.columns and looks_like_appbank_column(df[col]):
                appbank_cols.add(col)

    # Derivar flag tiene_app si aplica
    if appbank_cols and "tiene_app" not in df.columns:
        df["tiene_app"] = df[list(appbank_cols)[0]].notna()
        columnas_nuevas.append("tiene_app")

    # Codificación ligera según roles
    for col in roles.get("categoria_problema", []):
        if col not in df.columns or col in appbank_cols:
            continue
        new_col = f"{col}_Cat"
        df[new_col] = df[col].apply(lambda x: categorize_text(x, problem_rules))
        columnas_nuevas.append(new_col)
        codificacion_ligera[new_col] = {
            "variable_original": col,
            "criterio": "reglas semánticas por keyword",
            "categorias": df[new_col].value_counts().to_dict(),
        }

    for col in roles.get("categoria_solucion", []):
        if col not in df.columns or col in appbank_cols:
            continue
        new_col = f"{col}_Cat"
        df[new_col] = df[col].apply(lambda x: categorize_text(x, solution_rules))
        columnas_nuevas.append(new_col)
        codificacion_ligera[new_col] = {
            "variable_original": col,
            "criterio": "reglas semánticas por keyword",
            "categorias": df[new_col].value_counts().to_dict(),
        }

    # Segmento/perfil: intentar normalizar métodos de pago y giros
    for col in roles.get("segmento_perfil", []):
        if col not in df.columns or col in appbank_cols:
            continue
        if looks_like_payment_column(df[col]):
            new_col = f"{col}_Cat"
            df[new_col] = df[col].apply(normalize_payment)
            columnas_nuevas.append(new_col)
            codificacion_ligera[new_col] = {
                "variable_original": col,
                "criterio": "normalización de método de pago",
                "categorias": df[new_col].value_counts().to_dict(),
            }
        # Giro: si el nombre de columna sugiere giro o los valores parecen giros
        if "giro" in col.lower() or "negocio" in col.lower() or "tipo" in col.lower():
            new_col = f"{col}_Cat"
            df[new_col] = df[col].apply(lambda x: categorize_text(x, giro_rules))
            columnas_nuevas.append(new_col)
            codificacion_ligera[new_col] = {
                "variable_original": col,
                "criterio": "reglas semánticas por keyword (giro)",
                "categorias": df[new_col].value_counts().to_dict(),
            }

    # Calidad de respuesta
    calidad = build_quality_report(df)
    advertencias = missingness_advertencias(df)
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
            "columnas_originales": list(df.columns[:len(df.columns) - len(columnas_nuevas)]),
            "columnas_nuevas": columnas_nuevas,
        }
        fase0["datos"]["codificacion_ligera"] = codificacion_ligera
        fase0["datos"]["calidad_respuesta"] = calidad
        fase0["advertencias"] = fase0.get("advertencias", []) + advertencias
        with open(fase0_path, "w", encoding="utf-8") as f:
            json.dump(fase0, f, ensure_ascii=False, indent=2)

    # Resumen en consola
    print(f"CSV enriquecido guardado en: {output_csv}")
    print(f"Registros: {len(df)} | Columnas nuevas: {len(columnas_nuevas)}")
    for c in columnas_nuevas:
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
