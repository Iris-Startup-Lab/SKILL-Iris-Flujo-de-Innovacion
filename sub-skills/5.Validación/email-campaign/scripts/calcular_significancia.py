"""
calcular_significancia.py

Calcula el tamaño de muestra mínimo para detectar diferencias estadísticamente
significativas en una tasa (open rate, CTR, conversión) con un nivel de
confianza y un poder estadístico dados.

Dos modos de cálculo:
  1. Una muestra (una tasa vs. un objetivo/umbral): detectar si la tasa
     observada difiere de la tasa base en al menos `mde`.
  2. Dos muestras (A/B entre variantes): tamaño mínimo POR variante para
     detectar una diferencia `mde` entre dos tasas.

Fórmulas:
  Una muestra:  n = (Z_alfa/2 + Z_beta)^2 * p*(1-p) / d^2
  Dos muestras: n = (Z_alfa/2 + Z_beta)^2 * [p1*(1-p1) + p2*(1-p2)] / (p1-p2)^2

Uso:
    python calcular_significancia.py --tasa-base 0.30 --mde 0.05 \
        [--n-lista 500] [-o significancia.json]
"""
import argparse
import json
import math
from statistics import NormalDist


def _z(alpha, beta):
    dist = NormalDist()
    z_alfa = dist.inv_cdf(1 - alpha / 2)  # dos colas
    z_beta = dist.inv_cdf(beta)           # poder
    return z_alfa, z_beta


def una_muestra(p, d, z_alfa, z_beta):
    n = (z_alfa + z_beta) ** 2 * p * (1 - p) / (d ** 2)
    return max(n, 1)


def dos_muestras(p1, p2, z_alfa, z_beta):
    n = (z_alfa + z_beta) ** 2 * (p1 * (1 - p1) + p2 * (1 - p2)) / ((p1 - p2) ** 2)
    return max(n, 1)


def calcular(tasa_base, mde, n_lista, confianza, poder):
    alpha = 1 - confianza
    beta = poder
    z_alfa, z_beta = _z(alpha, beta)

    p1 = min(tasa_base, 1.0)
    p2 = max(0.0, min(tasa_base + mde, 1.0)) if mde >= 0 else max(0.0, tasa_base + mde)
    p2 = min(p2, 1.0)

    resultado = {
        "parametros": {
            "tasa_base": tasa_base,
            "mde": mde,
            "tasa_objetivo": round(p2, 4),
            "confianza": confianza,
            "poder": poder,
            "n_lista": n_lista,
        },
        "una_muestra": {
            "n_minimo": math.ceil(una_muestra(p1, mde, z_alfa, z_beta)),
            "nota": "Muestra mínima para detectar que la tasa observada difiere de la base en >= mde.",
        },
        "dos_muestras": {
            "n_por_variante": math.ceil(dos_muestras(p1, p2, z_alfa, z_beta)),
            "nota": "Muestra mínima POR variante para un test A/B.",
        },
    }

    if n_lista and n_lista > 0:
        req = resultado["una_muestra"]["n_minimo"]
        resultado["advertencia_lista"] = (
            f"La lista ({n_lista}) es insuficiente para detectar una diferencia de "
            f"{mde*100:.1f}pp con {confianza*100:.0f}% de confianza y {poder*100:.0f}% "
            f"de poder: se requieren ~{req} respuestas/eventos útiles."
        ) if n_lista < req else (
            f"La lista ({n_lista}) es suficiente para detectar una diferencia de "
            f"{mde*100:.1f}pp ({req} requeridos)."
        )

    return resultado


def main(argv=None):
    parser = argparse.ArgumentParser(description="Calcula tamaño de muestra para significancia en tasas.")
    parser.add_argument("--tasa-base", type=float, required=True, help="Tasa base esperada (ej. 0.30)")
    parser.add_argument("--mde", type=float, required=True, help="Diferencia mínima detectable (ej. 0.05)")
    parser.add_argument("--n-lista", type=float, default=None, help="Tamaño de lista disponible (opcional)")
    parser.add_argument("--confianza", type=float, default=0.95, help="Nivel de confianza")
    parser.add_argument("--poder", type=float, default=0.80, help="Poder estadístico")
    parser.add_argument("-o", "--output", default="significancia.json", help="Salida JSON")
    args = parser.parse_args(argv)

    resultado = calcular(args.tasa_base, args.mde, args.n_lista, args.confianza, args.poder)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    print(json.dumps(resultado, ensure_ascii=False, indent=2))
    print(f"\nCálculo guardado en: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
