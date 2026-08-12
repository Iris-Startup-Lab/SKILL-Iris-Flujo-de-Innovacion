"""
validar_esquema.py

Validación mínima de esquema para los JSON de salida de cada fase de la skill
'senales-debiles'. No evalúa calidad de contenido, solo existencia de campos
obligatorios y coherencia básica.

Uso:
    python validar_esquema.py <faseN_output.json> [--fase fase-N]

Salida (stdout):
    JSON con verdict, errores y warnings.
"""
import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path


COMMON_TOP = ["fase", "timestamp", "pregunta_investigacion", "advertencias"]

SCHEMAS = {
    "fase-0-viabilidad": {
        "required_top": ["datos"],
        "required_datos": ["viabilidad", "pre_registro", "roles"],
        "required_arrays": ["advertencias", "hipotesis_previas"],
    },
    "fase-1-eda-cuantitativo": {
        "required_top": ["datos"],
        "required_datos": ["infraestructura", "bloques"],
        "required_arrays": ["advertencias", "datos.bloques"],
        "bloque_id_pattern": r"^B[1-7]$",
    },
    "fase-2-eda-cualitativo": {
        "required_top": ["datos"],
        "required_datos": ["bitacora_ventanas", "bloques"],
        "required_arrays": ["advertencias", "datos.bitacora_ventanas", "datos.bloques"],
        "signal_pattern": r"^SD-CUALI?-\d{3}$",
    },
    "fase-3-cruce": {
        "required_top": ["datos"],
        "required_datos": ["bloques"],
        "required_arrays": ["advertencias", "datos.bloques"],
        "cross_pattern": r"^CRUCE-\d{3}$",
    },
    "fase-4-entrega": {
        "required_top": ["mapeo_html", "validacion"],
        "required_datos": [],
        "required_arrays": ["advertencias"],
        "signal_pattern": r"^(SD-(CUANT|CUALI?|MIXTA)|CRUCE)-\d{3}$",
    },
}


def get_nested(obj, path):
    keys = path.split(".")
    cur = obj
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return None
        cur = cur[k]
    return cur


def validate_iso_timestamp(ts):
    try:
        datetime.fromisoformat(ts)
        return True
    except Exception:
        return False


def validate_file(path, expected_fase=None):
    errors = []
    warnings = []
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return {"archivo": str(path), "fase": expected_fase, "veredicto": "FALLA",
                "errores": [f"JSON invalido: {e}"], "advertencias": []}
    except FileNotFoundError:
        return {"archivo": str(path), "fase": expected_fase, "veredicto": "FALLA",
                "errores": ["Archivo no encontrado"], "advertencias": []}

    fase = data.get("fase", expected_fase)
    if not fase:
        errors.append("No se pudo determinar la fase (falta 'fase' en JSON y no se especificó --fase)")
        return {"archivo": str(path), "fase": None, "veredicto": "FALLA",
                "errores": errors, "advertencias": warnings}

    if "advertencias" in data and not isinstance(data["advertencias"], list):
        errors.append("'advertencias' debe ser una lista")

    if "timestamp" in data and not validate_iso_timestamp(data["timestamp"]):
        warnings.append("'timestamp' no está en formato ISO 8601")

    schema = SCHEMAS.get(fase)
    if not schema:
        # Validación mínima para fases desconocidas
        for key in COMMON_TOP:
            if key not in data:
                errors.append(f"Falta clave top-level '{key}'")
        warnings.append(f"No hay esquema definido para la fase '{fase}'; solo se validan claves top-level")
        return {"archivo": str(path), "fase": fase, "veredicto": "FALLA" if errors else "ADV",
                "errores": errors, "advertencias": warnings}

    # Top-level keys
    for key in COMMON_TOP + schema.get("required_top", []):
        if key not in data:
            errors.append(f"Falta clave top-level '{key}'")

    for key in schema.get("required_datos", []):
        if key not in data.get("datos", {}):
            errors.append(f"Falta datos.{key}")

    for arr_path in schema.get("required_arrays", []):
        val = get_nested(data, arr_path)
        if val is None:
            errors.append(f"Falta array '{arr_path}'")
        elif not isinstance(val, list):
            errors.append(f"'{arr_path}' debe ser una lista")

    # Validar IDs de señales/cruces
    signal_pattern = schema.get("signal_pattern")
    if signal_pattern and isinstance(get_nested(data, "datos.senales"), list):
        for s in data["datos"]["senales"]:
            sid = s.get("id") if isinstance(s, dict) else s
            if sid and not re.match(signal_pattern, sid):
                warnings.append(f"ID de señal '{sid}' no coincide con el patrón {signal_pattern}")

    if signal_pattern and isinstance(data.get("mapeo_html"), dict):
        for label, sid in data["mapeo_html"].items():
            if sid and not re.match(signal_pattern, sid):
                warnings.append(f"mapeo_html['{label}']='{sid}' no coincide con el patrón {signal_pattern}")

    cross_pattern = schema.get("cross_pattern")
    if cross_pattern and isinstance(get_nested(data, "datos.bloques"), list):
        for bloque in data["datos"]["bloques"]:
            if not isinstance(bloque, dict):
                continue
            for cruce in bloque.get("cruces", []):
                cid = cruce.get("id") if isinstance(cruce, dict) else cruce
                if cid and not re.match(cross_pattern, cid):
                    warnings.append(f"ID de cruce '{cid}' no coincide con el patrón {cross_pattern}")

    bloque_id_pattern = schema.get("bloque_id_pattern")
    if bloque_id_pattern and isinstance(get_nested(data, "datos.bloques"), list):
        for bloque in data["datos"]["bloques"]:
            bid = bloque.get("id") if isinstance(bloque, dict) else None
            if bid and not re.match(bloque_id_pattern, bid):
                warnings.append(f"ID de bloque '{bid}' no coincide con el patrón {bloque_id_pattern}")

    # Redundancia: contrato es list[dict]
    if fase in ("fase-1-eda-cuantitativo", "fase-2-eda-cualitativo", "fase-3-cruce"):
        red = data.get("redundancia")
        if red is not None:
            if isinstance(red, dict):
                warnings.append("'redundancia' debe ser una lista de objetos (list[dict]); se encontró un dict")
                red = [red]
            if isinstance(red, list):
                for i, r in enumerate(red):
                    if not isinstance(r, dict):
                        errors.append(f"'redundancia[{i}]' debe ser un objeto")
                        continue
                    for key in ("aplicada", "senal_id", "resultado"):
                        if key not in r:
                            errors.append(f"'redundancia[{i}]' falta '{key}'")
                    if r.get("absorbida_por") is not None and not isinstance(r["absorbida_por"], str):
                        errors.append(f"'redundancia[{i}].absorbida_por' debe ser string o null")
            else:
                errors.append("'redundancia' debe ser una lista de objetos")

    return {
        "archivo": str(path),
        "fase": fase,
        "veredicto": "PASA" if not errors else "FALLA",
        "errores": errors,
        "advertencias": warnings,
    }


def main():
    parser = argparse.ArgumentParser(description="Valida esquema de JSON por fase.")
    parser.add_argument("json", nargs="+", help="Archivo(s) JSON a validar")
    parser.add_argument("--fase", help="Fase esperada (si no está en el JSON)")
    args = parser.parse_args()

    resultados = []
    for path in args.json:
        resultados.append(validate_file(path, expected_fase=args.fase))

    print(json.dumps(resultados, ensure_ascii=False, indent=2))
    sys.exit(0 if all(r["veredicto"] == "PASA" for r in resultados) else 1)


if __name__ == "__main__":
    main()
