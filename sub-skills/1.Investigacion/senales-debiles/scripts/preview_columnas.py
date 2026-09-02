"""
preview_columnas.py

Vuelca un diccionario de datos compacto de un CSV para que el agente proponga
el mapeo de columnas a roles (Paso 1 de Fase 0) sin leer el archivo completo.

Por cada columna imprime: nombre | tipo | n (no nulos) | cardinalidad | muestras
(3-5 valores truncados a ~40 caracteres) y marca las que parecen binarias o
fechas. El script SOLO describe: no sugiere roles (el mapeo semantico lo decide
el LLM).

Uso:
    python preview_columnas.py datos.csv [-o preview.txt]

Si se omite -o, la salida va a stdout.
"""
import argparse
import sys

import pandas as pd


BINARIO = {
    "0", "1", "0.0", "1.0", "true", "false", "verdadero", "falso",
    "si", "sí", "no", "s", "n", "y",
}

MAX_MUESTRA = 40
N_MUESTRAS = 5


def es_binaria(series):
    valores = set(series.dropna().astype(str).str.strip().str.lower())
    if not valores:
        return False
    return valores.issubset(BINARIO)


def es_fecha(series):
    if pd.api.types.is_datetime64_any_dtype(series):
        return True
    if series.dtype.name not in ("object", "string", "str"):
        return False
    muestra = series.dropna().head(10)
    if muestra.empty:
        return False
    try:
        conv = pd.to_datetime(muestra, errors="coerce", format="mixed")
        return float(conv.notna().mean()) >= 0.8
    except Exception:
        return False


def tipo_legible(series):
    if series.dtype.name in ("object", "string", "str"):
        return "texto"
    return str(series.dtype)


def muestras(series):
    valores = series.dropna().astype(str).str.strip()
    unicos = []
    vistos = set()
    for v in valores:
        if v not in vistos:
            vistos.add(v)
            unicos.append(v)
        if len(unicos) >= N_MUESTRAS:
            break
    out = []
    for v in unicos:
        if len(v) > MAX_MUESTRA:
            v = v[:MAX_MUESTRA] + "..."
        out.append('"' + v + '"')
    return out


def preview(csv_path, output=None):
    df = pd.read_csv(csv_path, encoding="utf-8-sig")
    lineas = [f"# {csv_path} | filas={len(df)} | columnas={len(df.columns)}"]
    for col in df.columns:
        s = df[col]
        n = int(s.notna().sum())
        uniq = int(s.nunique(dropna=True))
        marcas = []
        if es_binaria(s):
            marcas.append("binaria")
        if es_fecha(s):
            marcas.append("fecha")
        fila = f"{col} | {tipo_legible(s)} | n={n} | unicos={uniq}"
        if marcas:
            fila += f" | [{', '.join(marcas)}]"
        ms = muestras(s)
        if ms:
            fila += " | " + ", ".join(ms)
        lineas.append(fila)
    texto = "\n".join(lineas) + "\n"
    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(texto)
        print(f"Vista previa guardada en: {output}")
    else:
        sys.stdout.buffer.write(texto.encode("utf-8"))
        sys.stdout.buffer.flush()


def main():
    parser = argparse.ArgumentParser(
        description="Vuelca un diccionario de datos compacto de un CSV.")
    parser.add_argument("csv", help="CSV de entrada")
    parser.add_argument("-o", "--output", default=None,
                        help="Archivo de salida (default: stdout)")
    args = parser.parse_args()
    preview(args.csv, args.output)


if __name__ == "__main__":
    main()
