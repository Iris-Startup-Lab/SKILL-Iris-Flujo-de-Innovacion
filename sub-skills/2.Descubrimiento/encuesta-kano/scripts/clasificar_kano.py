"""
clasificar_kano.py

Clasifica respuestas de una encuesta tipo Kano (pregunta funcional × pregunta
disfuncional) en las categorías M/O/A/I/R/Q, según la tabla de clasificación
Kano, y genera un conteo por categoría.

Entrada: CSV con columnas:
  - feature (nombre de la característica)
  - funcional (respuesta a "si la característica estuviera presente")
  - disfuncional (respuesta a "si la característica NO estuviera presente")
  - importancia (opcional)

Opciones de respuesta reconocidas (flexible, minúsculas, sin tildes):
  - like      -> "Me gusta que sea así"
  - expect    -> "Espero que sea así"
  - neutral   -> "Indiferente"
  - tolerate  -> "Lo tolero"
  - dislike   -> "No me gusta"

Leyenda de salida: M = Must-be · O = Unidimensional · A = Atractivo ·
I = Indiferente · R = Inverso · Q = Cuestionable.

Uso:
    python clasificar_kano.py respuestas.csv -o clasificacion.csv
"""
import argparse
import csv
import json
import sys

# Matriz de clasificación: (funcional, disfuncional) -> categoría
# Orden de ejes: like, expect, neutral, tolerate, dislike
_MATRIZ = {
    ("like", "like"): "Q",
    ("like", "expect"): "A",
    ("like", "neutral"): "A",
    ("like", "tolerate"): "A",
    ("like", "dislike"): "O",
    ("expect", "like"): "R",
    ("expect", "expect"): "I",
    ("expect", "neutral"): "I",
    ("expect", "tolerate"): "I",
    ("expect", "dislike"): "M",
    ("neutral", "like"): "R",
    ("neutral", "expect"): "R",
    ("neutral", "neutral"): "I",
    ("neutral", "tolerate"): "I",
    ("neutral", "dislike"): "M",
    ("tolerate", "like"): "R",
    ("tolerate", "expect"): "R",
    ("tolerate", "neutral"): "I",
    ("tolerate", "tolerate"): "I",
    ("tolerate", "dislike"): "M",
    ("dislike", "like"): "Q",
    ("dislike", "expect"): "R",
    ("dislike", "neutral"): "R",
    ("dislike", "tolerate"): "R",
    ("dislike", "dislike"): "Q",
}

_CATEGORIAS = {
    "M": "Must-be / Obligatorio",
    "O": "Unidimensional / Rendimiento",
    "A": "Atractivo",
    "I": "Indiferente",
    "R": "Inverso",
    "Q": "Cuestionable",
}


def normalizar(texto):
    t = (texto or "").strip().lower()
    t = t.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
    if "no me gusta" in t or t == "dislike":
        return "dislike"
    if "me gusta" in t or t == "like":
        return "like"
    if "espero" in t:
        return "expect"
    if "indiferente" in t:
        return "neutral"
    if "tolero" in t:
        return "tolerate"
    return None


def clasificar(fila, col_func, col_disf):
    f = normalizar(fila.get(col_func))
    d = normalizar(fila.get(col_disf))
    if f is None or d is None:
        return None, f, d
    return _MATRIZ.get((f, d)), f, d


def procesar(input_path, output_path):
    rows = []
    with open(input_path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        campos = reader.fieldnames or []
        col_feature = "feature" if "feature" in campos else (campos[0] if campos else "feature")
        col_func = "funcional" if "funcional" in campos else (campos[1] if len(campos) > 1 else "funcional")
        col_disf = "disfuncional" if "disfuncional" in campos else (campos[2] if len(campos) > 2 else "disfuncional")
        for fila in reader:
            cat, f, d = clasificar(fila, col_func, col_disf)
            rows.append({
                "feature": fila.get(col_feature, ""),
                "funcional": fila.get(col_func, ""),
                "disfuncional": fila.get(col_disf, ""),
                "categoria": cat or "",
                "categoria_nombre": _CATEGORIAS.get(cat, "") if cat else "",
                "importancia": fila.get("importancia", "") if "importancia" in campos else "",
            })

    conteo = {c: 0 for c in _CATEGORIAS}
    for r in rows:
        if r["categoria"] in conteo:
            conteo[r["categoria"]] += 1

    # CSV de salida
    with open(output_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["feature", "funcional", "disfuncional", "categoria", "categoria_nombre", "importancia"])
        for r in rows:
            writer.writerow([
                r["feature"], r["funcional"], r["disfuncional"],
                r["categoria"], r["categoria_nombre"], r["importancia"],
            ])

    resumen = {
        "n_total": len(rows),
        "conteo_por_categoria": conteo,
        "categorias": _CATEGORIAS,
    }
    return resumen


def main(argv=None):
    parser = argparse.ArgumentParser(description="Clasifica respuestas Kano en M/O/A/I/R/Q.")
    parser.add_argument("csv", help="CSV de respuestas (feature, funcional, disfuncional[, importancia])")
    parser.add_argument("-o", "--output", default="clasificacion_kano.csv", help="CSV de salida")
    args = parser.parse_args(argv)

    try:
        resumen = procesar(args.csv, args.output)
    except FileNotFoundError:
        print(f"Error: no se encontró '{args.csv}'", file=sys.stderr)
        return 1

    print(json.dumps(resumen, ensure_ascii=False, indent=2))
    print(f"\nClasificación guardada en: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
