"""
calcular_muestra.py

Calcula el tamaño de muestra estadísticamente significativo para una encuesta
de descubrimiento (Discovery Survey), junto con la muestra ajustada a población
finita y el número de envíos requeridos según la tasa de respuesta esperada.

Fórmulas:
    n     = (Z^2 * p * (1 - p)) / e^2          (población infinita/grande)
    n_aj  = n / (1 + (n - 1) / N)              (ajuste por población finita)
    envíos = n_aj / tasa_respuesta

Uso:
    python calcular_muestra.py --N 10000 --confianza 0.95 --error 0.05 \
        --tasa-respuesta 0.20 [--p 0.5] [-o muestra.json]
"""
import argparse
import json
import math

# Valores Z por nivel de confianza común.
VALORES_Z = {
    0.80: 1.2816,
    0.85: 1.4395,
    0.90: 1.6449,
    0.95: 1.9600,
    0.98: 2.3263,
    0.99: 2.5758,
}


def valor_z(confianza):
    clave = min(VALORES_Z, key=lambda c: abs(c - confianza))
    return VALORES_Z[clave], clave


def calcular(N, confianza, error, tasa_respuesta, p=0.5):
    Z, nivel = valor_z(confianza)
    n = (Z ** 2 * p * (1 - p)) / (error ** 2)

    if N and N > 0:
        n_aj = n / (1 + (n - 1) / N)
    else:
        n_aj = n  # población infinita

    envios = n_aj / tasa_respuesta if tasa_respuesta and tasa_respuesta > 0 else None

    return {
        "formulas": {
            "n": "n = (Z^2 * p * (1 - p)) / e^2",
            "n_aj": "n_aj = n / (1 + (n - 1) / N)",
            "envios": "envios = n_aj / tasa_respuesta",
        },
        "parametros": {
            "N": N,
            "confianza": confianza,
            "nivel_z": nivel,
            "Z": Z,
            "p": p,
            "margen_error": error,
            "tasa_respuesta": tasa_respuesta,
        },
        "resultados": {
            "n": round(n, 2),
            "n_aj": round(n_aj, 2),
            "envios_requeridos": round(envios, 0) if envios is not None else None,
        },
        "interpretacion": (
            f"Con un nivel de confianza del {int(nivel * 100)}% (Z={Z}) y un margen de "
            f"error de {error * 100:.0f}%, se requieren {math.ceil(n_aj)} respuestas útiles. "
            f"Con una tasa de respuesta esperada del {tasa_respuesta * 100:.0f}%, deben "
            f"enviarse ~{math.ceil(envios)} invitaciones."
        ) if envios is not None else (
            f"Con un nivel de confianza del {int(nivel * 100)}% (Z={Z}) y un margen de "
            f"error de {error * 100:.0f}%, se requieren {math.ceil(n_aj)} respuestas útiles."
        ),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Calcula tamaño de muestra para encuesta.")
    parser.add_argument("--N", type=float, default=None, help="Tamaño de la población (vacío = infinita)")
    parser.add_argument("--confianza", type=float, default=0.95, help="Nivel de confianza (0.80-0.99)")
    parser.add_argument("--error", type=float, default=0.05, help="Margen de error en proporción (ej. 0.05)")
    parser.add_argument("--tasa-respuesta", type=float, default=None, help="Tasa de respuesta esperada (ej. 0.20)")
    parser.add_argument("--p", type=float, default=0.5, help="Proporción estimada (default 0.5, conservador)")
    parser.add_argument("-o", "--output", default="muestra.json", help="Ruta de salida JSON")
    args = parser.parse_args(argv)

    resultado = calcular(args.N, args.confianza, args.error, args.tasa_respuesta, args.p)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    print(json.dumps(resultado["resultados"], ensure_ascii=False, indent=2))
    print(f"\nCálculo guardado en: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
