"""
exportar_csv.py

Convierte el análisis de Problem-Solution Fit (JSON estructurado) a un CSV
listo para descargar o integrar en Google Sheets/Excel.

Entrada: JSON con una lista de registros. Dos formatos aceptados:
  1) Lista directa de objetos:  [ {"problema": "...", ...}, ... ]
  2) Objeto con "filas" y, opcionalmente, "columnas" (orden de columnas).

Columnas estándar (Problem-Solution Fit):
  problema, contexto, impacto (1-5), satisfaccion_solucion_actual (1-5),
  costo_tiempo_horas_semana, costo_dinero_usd_mes, solucion_cubre,
  ajustes_sugeridos, patrones_tendencias, jtbd, oportunidad_blue_ocean

Regla de integridad: los costos deben venir del input como citas explícitas,
[ESTIMACIÓN] o N/D. Este script NO calcula ni inventa valores; solo exporta.

Uso:
    python exportar_csv.py analisis.json -o problem_solution_fit.csv
"""
import argparse
import csv
import json
import sys

_COLUMNAS_ESTANDAR = [
    "problema",
    "contexto",
    "impacto",
    "satisfaccion_solucion_actual",
    "costo_tiempo_horas_semana",
    "costo_dinero_usd_mes",
    "solucion_cubre",
    "ajustes_sugeridos",
    "patrones_tendencias",
    "jtbd",
    "oportunidad_blue_ocean",
]


def _cargar_filas(input_path):
    with open(input_path, encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        return data, None
    if isinstance(data, dict) and isinstance(data.get("filas"), list):
        return data["filas"], data.get("columnas")
    raise ValueError("JSON no reconocido: debe ser una lista de objetos o {'filas': [...]}")


def exportar(input_path, output_path):
    filas, columnas = _cargar_filas(input_path)
    if not filas:
        print("Aviso: no hay registros para exportar.", file=sys.stderr)
        return 0

    columnas = columnas or _COLUMNAS_ESTANDAR
    # Añadir claves presentes en las filas que no estén en el esquema.
    extras = []
    for fila in filas:
        for k in fila.keys():
            if k not in columnas and k not in extras:
                extras.append(k)
    columnas = columnas + extras

    with open(output_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columnas, extrasaction="ignore")
        writer.writeheader()
        for fila in filas:
            writer.writerow(fila)

    print(f"CSV exportado en: {output_path} ({len(filas)} registros)")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description="Exporta análisis Problem-Solution Fit a CSV.")
    parser.add_argument("json", help="JSON del análisis")
    parser.add_argument("-o", "--output", default="problem_solution_fit.csv", help="CSV de salida")
    args = parser.parse_args(argv)

    try:
        return exportar(args.json, args.output)
    except FileNotFoundError:
        print(f"Error: no se encontró '{args.json}'", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
