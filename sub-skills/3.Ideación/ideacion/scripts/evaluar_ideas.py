"""
evaluar_ideas.py

Calcula el score de ideas generadas en la skill `ideacion` a partir de tres
dimensiones (Novedad, Utilidad, Factibilidad, escala 1-10), genera el promedio
(o promedio ponderado si se definen pesos) y produce un ranking y una tabla de
evaluación.

Entrada: JSON con {"ideas": [...], "pesos": {"novedad": ..., "utilidad": ..., "factibilidad": ...}}
Cada idea:
  {"nombre": "...", "metodologia": "...", "novedad": 8, "utilidad": 7, "factibilidad": 6}

Salida: JSON con ranking, promedios y veredicto sugerido por idea.

Uso:
    python evaluar_ideas.py ideas.json -o evaluacion.json
"""
import argparse
import json
import sys

_PESOS_DEFAULT = {"novedad": 1.0, "utilidad": 1.0, "factibilidad": 1.0}
_DIMENSIONES = ("novedad", "utilidad", "factibilidad")


def evaluar(ideas, pesos):
    pesos = {k: pesos.get(k, _PESOS_DEFAULT[k]) for k in _DIMENSIONES}
    total_peso = sum(pesos.values()) or 1.0

    resultados = []
    for idea in ideas:
        score = 0.0
        faltante = False
        for dim in _DIMENSIONES:
            v = idea.get(dim)
            if v is None or not isinstance(v, (int, float)):
                faltante = True
                continue
            score += float(v) * pesos[dim]
        promedio = round(score / total_peso, 2) if not faltante else None
        resultados.append({
            "nombre": idea.get("nombre", ""),
            "metodologia": idea.get("metodologia", ""),
            "novedad": idea.get("novedad"),
            "utilidad": idea.get("utilidad"),
            "factibilidad": idea.get("factibilidad"),
            "promedio": promedio,
            "veredicto": (
                "PRIORIZAR" if promedio is not None and promedio >= 7.5
                else "EVALUAR" if promedio is not None and promedio >= 6
                else "DESCARTAR" if promedio is not None
                else "INCOMPLETO"
            ),
        })

    resultados.sort(key=lambda r: (r["promedio"] if r["promedio"] is not None else -1), reverse=True)
    return {"pesos": pesos, "ranking": resultados}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Evalúa ideas (Novedad/Utilidad/Factibilidad).")
    parser.add_argument("json", help="JSON con ideas y pesos opcionales")
    parser.add_argument("-o", "--output", default="evaluacion_ideas.json", help="Salida JSON")
    args = parser.parse_args(argv)

    try:
        with open(args.json, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: no se encontró '{args.json}'", file=sys.stderr)
        return 1

    ideas = data.get("ideas", data if isinstance(data, list) else [])
    pesos = data.get("pesos", {}) if isinstance(data, dict) else {}

    resultado = evaluar(ideas, pesos)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    print(json.dumps(resultado, ensure_ascii=False, indent=2))
    print(f"\nEvaluación guardada en: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
