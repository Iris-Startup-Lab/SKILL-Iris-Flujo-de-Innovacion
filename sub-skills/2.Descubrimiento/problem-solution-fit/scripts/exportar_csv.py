"""
exportar_csv.py

Convierte el análisis de Problem-Solution Fit a un CSV listo para descargar o
integrar en Google Sheets/Excel.

Entrada: JSON. Tres formatos aceptados:
  1) `reporte.json` del reporte HTML: se leen los bloques
     `secciones[].items[].psf` y las filas se derivan de ahí aplicando el mapeo
     de `references/analisis-psf.md`. Una fila por problema; los campos del
     análisis (patrones, JTBD, Blue Ocean) se repiten en cada fila del mismo
     análisis. Es el modo recomendado: los datos se escriben una sola vez.
  2) Lista directa de objetos ya con nombres de columna:
     [ {"problema": "...", ...}, ... ]
  3) Objeto con "filas" y, opcionalmente, "columnas" (orden de columnas).

Columnas en modo `psf`:
  persona, n, problema, contexto, frecuencia, impacto,
  satisfaccion_solucion_actual, costo_tiempo_horas_semana,
  costo_dinero_usd_mes, solucion_actual, solucion_cubre, ajustes_sugeridos,
  patrones_tendencias, jtbd, oportunidad_blue_ocean

Regla de integridad: los costos deben venir del input como citas explícitas,
[ESTIMACIÓN] o N/D. Este script NO calcula ni inventa valores; solo exporta.

Uso:
    python exportar_csv.py reporte.json -o problem_solution_fit.csv
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

_COLUMNAS_PSF = [
    "persona",
    "n",
    "problema",
    "contexto",
    "frecuencia",
    "impacto",
    "satisfaccion_solucion_actual",
    "costo_tiempo_horas_semana",
    "costo_dinero_usd_mes",
    "solucion_actual",
    "solucion_cubre",
    "ajustes_sugeridos",
    "patrones_tendencias",
    "jtbd",
    "oportunidad_blue_ocean",
]

# Campo de `psf.problemas[]` -> columna del CSV (references/analisis-psf.md).
_MAPEO_PROBLEMA = {
    "n": "n",
    "problema": "problema",
    "contexto": "contexto",
    "frecuencia": "frecuencia",
    "importancia": "impacto",
    "satisfaccion": "satisfaccion_solucion_actual",
    "costo_tiempo": "costo_tiempo_horas_semana",
    "costo_dinero": "costo_dinero_usd_mes",
    "solucion_actual": "solucion_actual",
    "cubre": "solucion_cubre",
    "ajustes": "ajustes_sugeridos",
}

# Campo del análisis -> columna del CSV. Se repite en cada fila del análisis.
_MAPEO_ANALISIS = {
    "patrones": "patrones_tendencias",
    "jtbd": "jtbd",
    "blue_ocean": "oportunidad_blue_ocean",
}

_SEPARADOR_LISTA = " · "


def _valor(dato):
    """Aplana el dato a algo que quepa en una celda, sin inventar nada."""
    if dato is None:
        return ""
    if isinstance(dato, (list, tuple)):
        return _SEPARADOR_LISTA.join(str(x).strip() for x in dato if str(x).strip())
    return dato


def _bloques_psf(data):
    """Devuelve [(titulo_item, bloque_psf)] de un reporte.json o de {'psf': ...}."""
    bloques = []
    if isinstance(data.get("psf"), dict):
        bloques.append((data.get("titulo", ""), data["psf"]))
    for seccion in data.get("secciones") or []:
        if not isinstance(seccion, dict):
            continue
        for item in seccion.get("items") or []:
            if isinstance(item, dict) and isinstance(item.get("psf"), dict):
                bloques.append((item.get("titulo", ""), item["psf"]))
    return bloques


def _filas_desde_psf(bloques):
    filas = []
    for titulo, psf in bloques:
        persona = psf.get("persona") or titulo or ""
        analisis = {
            columna: _valor(psf.get(campo))
            for campo, columna in _MAPEO_ANALISIS.items()
        }
        problemas = psf.get("problemas") or []
        if not problemas:
            print(
                f"Aviso: el bloque psf de «{persona or 'sin título'}» no trae "
                f"problemas; no genera filas.",
                file=sys.stderr,
            )
        for posicion, problema in enumerate(problemas, 1):
            if not isinstance(problema, dict):
                continue
            fila = {"persona": persona}
            for campo, columna in _MAPEO_PROBLEMA.items():
                fila[columna] = _valor(problema.get(campo))
            # `n` es opcional en el bloque: si falta, se numera por posición
            # (el problema 2 de la tabla es el punto 2 de la matriz).
            if fila["n"] == "":
                fila["n"] = posicion
            fila.update(analisis)
            filas.append(fila)
    return filas


def _cargar_filas(input_path):
    with open(input_path, encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        return data, None

    if isinstance(data, dict):
        # Entrada histórica: filas ya con nombres de columna.
        if isinstance(data.get("filas"), list):
            return data["filas"], data.get("columnas")

        bloques = _bloques_psf(data)
        if bloques:
            return _filas_desde_psf(bloques), _COLUMNAS_PSF

        if "secciones" in data:
            raise ValueError(
                "el reporte.json no trae ningún item con bloque 'psf'. "
                "Revisa references/analisis-psf.md: el bloque va dentro de "
                "secciones[].items[]."
            )

    raise ValueError(
        "JSON no reconocido: se espera un reporte.json con bloques 'psf', "
        "una lista de objetos o {'filas': [...]}"
    )


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
    parser.add_argument("json", help="reporte.json (bloques psf) o JSON de filas")
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
