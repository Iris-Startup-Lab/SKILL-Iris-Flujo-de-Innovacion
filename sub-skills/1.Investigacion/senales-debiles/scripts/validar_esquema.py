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
from invariante_clasificacion import verificar_invariante
from invariante_clasificacion import items_de_fase


COMMON_TOP = ["fase", "timestamp", "pregunta_investigacion", "advertencias"]

# Conjunto de claves que run_gate.py escribe en 'validacion' de fase4_output.json
# (regla 17 / invariante 0.4). Cualquier otra clave escrita por el LLM se marca.
_VALIDACION_GATE_KEYS = {
    "estructura_2_secciones", "senales_en_rango", "decisiones_en_rango",
    "badges_ausentes", "numeracion_correcta", "decisiones_referencian_senales",
    "tono_exploratorio", "sin_temporalidad", "ancla_declarada",
    "fallback_respetado", "design_system_aplicado", "graficas_en_tarjetas",
    "heatmap_svg_presente", "footer_sin_trazabilidad", "sin_ids_tecnicos",
    "citas_verificadas", "filtro_pertinencia_aplicado",
    "silencio_de_instrumento_a_footer", "exclusion_clasificacion_respetada",
    "senales_escalan_correctas",
    "ejecutada", "gate_corrio", "gate_veredicto", "puntos_fallidos", "n_senales",
    "gate_esquema", "gate_trazabilidad", "gate_reporte", "gate_citas", "gate_numeros",
}

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
        with open(path, encoding="utf-8-sig") as f:
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

    # Poblaciones de Fase 0: {universo: {nombre, n}}; legacy => {universo: "nombre"}.
    if fase == "fase-0-viabilidad":
        pobl = data.get("datos", {}).get("poblaciones")
        if pobl is not None:
            items = pobl.items() if isinstance(pobl, dict) else enumerate(pobl)
            for universo, valor in items:
                if isinstance(valor, dict):
                    if not isinstance(valor.get("nombre"), str):
                        errors.append(f"datos.poblaciones[{universo}].nombre debe ser string")
                    n = valor.get("n")
                    if n is not None and (not isinstance(n, int) or n <= 0):
                        errors.append(f"datos.poblaciones[{universo}].n debe ser int > 0")
                    if n is None:
                        warnings.append(f"datos.poblaciones[{universo}] sin 'n': el piso "
                                        f"adaptativo por población usará 30 fijo")
                elif not isinstance(valor, str):
                    errors.append(f"datos.poblaciones[{universo}] debe ser objeto "
                                  f"{{'nombre', 'n'}} o string (nombre legado)")
                else:
                    warnings.append(f"datos.poblaciones[{universo}] en formato string: "
                                    f"declare {{'nombre', 'n'}} para el piso por población")

    # Señales de Fases 1/2: 'poblacion' y 'n' estructurados para el piso por población.
    if fase in ("fase-1-eda-cuantitativo", "fase-2-eda-cualitativo"):
        for bloque in data.get("datos", {}).get("bloques", []):
            if not isinstance(bloque, dict):
                continue
            for s in bloque.get("senales", []):
                sid = s.get("id", "?") if isinstance(s, dict) else "?"
                if not isinstance(s, dict):
                    continue
                if "poblacion" in s and not isinstance(s["poblacion"], str):
                    errors.append(f"señal {sid}: 'poblacion' debe ser string")
                if "n" in s and (not isinstance(s["n"], int) or s["n"] <= 0):
                    errors.append(f"señal {sid}: 'n' debe ser int > 0")
                if s.get("poblacion") is None:
                    warnings.append(f"señal {sid}: sin 'poblacion' (declárela para el "
                                    f"piso por población en cruces transpoblacionales)")
                if s.get("n") is None:
                    warnings.append(f"señal {sid}: sin 'n' estructurado (la convergencia "
                                    f"usará la extracción por heurística)")

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

    # Gate intermedio: invariante de clasificación (Filtro 2 de AGENTE.md).
    # Misma implementación que el gate final (validar_reporte.py) vía
    # invariante_clasificacion.py; aquí se aplica al cierre de Fases 1-3 para
    # detener el pipeline antes de que el error se propague al reporte HTML.
    if fase in ("fase-1-eda-cuantitativo", "fase-2-eda-cualitativo", "fase-3-cruce"):
        for nivel, msg in verificar_invariante(data, str(path)):
            if nivel == "ERROR":
                errors.append(msg)
            else:
                warnings.append(msg)

        # Calibración por ancla (SPEC sección 5): cap de sorpresa.
        # Regla de cierre (AGENTE.md regla 13): reclasificación auditable.
        for item in items_de_fase(data):
            iid = item.get("id", "?")
            ancla = item.get("ancla")
            sorpresa = item.get("sorpresa")
            clasif = item.get("clasificacion_hipotesis_previa")
            if ancla == "expectativa_inferida" and sorpresa == "Alta":
                errors.append(
                    f"{iid}: ancla 'expectativa_inferida' con sorpresa 'Alta' "
                    f"— cap Media (SPEC sección 5)")
            if clasif == "señal débil" and ancla == "hipotesis_usuario":
                mn = item.get("mecanismo_nuevo")
                if not (isinstance(mn, str) and mn.strip()):
                    errors.append(
                        f"{iid}: clasificada 'señal débil' con ancla 'hipotesis_usuario' "
                        f"requiere campo 'mecanismo_nuevo' (regla de cierre de AGENTE.md regla 13)")

    # Coherencia de cruces transpoblacionales (Fase 3): la justificación no puede
    # contradecir la naturaleza declarada (blindaje de fase-3-cruce.md).
    if fase == "fase-3-cruce":
        for bloque in data.get("datos", {}).get("bloques", []):
            if not isinstance(bloque, dict):
                continue
            for cruce in bloque.get("cruces", []):
                if not isinstance(cruce, dict):
                    continue
                cid = cruce.get("id", "?")
                nat = cruce.get("naturaleza_cruce")
                jsev = cruce.get("justificacion_severidad") or ""
                motivo = cruce.get("motivo_no_escala") or ""
                if nat == "extrapolacion":
                    if re.search(r"por\s+naturaleza\s+convergencia", jsev, re.I):
                        errors.append(
                            f"{cid}: naturaleza 'extrapolacion' pero justificacion_severidad "
                            f"justifica por 'naturaleza convergencia' (incoherencia)")
                    if re.search(r"\bconvergencia\b", motivo, re.I):
                        warnings.append(
                            f"{cid}: naturaleza 'extrapolacion' pero motivo_no_escala "
                            f"menciona 'convergencia' (verificar coherencia)")
                elif nat == "convergencia":
                    if re.search(r"por\s+naturaleza\s+extrapolacion", jsev, re.I):
                        errors.append(
                            f"{cid}: naturaleza 'convergencia' pero justificacion_severidad "
                            f"justifica por 'naturaleza extrapolacion' (incoherencia)")

    # Fase 4: 'validacion' no debe llegar con claves que no escribe el gate
    # (regla 17 / invariante 0.4). run_gate.py lo reconstruye desde cero, pero
    # se avisa para que el LLM no pre-popule el bloque.
    if fase == "fase-4-entrega":
        val = data.get("validacion")
        if isinstance(val, dict) and val:
            extra = sorted(k for k in val if k not in _VALIDACION_GATE_KEYS)
            if extra:
                warnings.append(
                    f"'validacion' trae claves fuera del conjunto que escribe run_gate.py: "
                    f"{extra} (regla 17; el gate las descartará al reconstruir)")

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
