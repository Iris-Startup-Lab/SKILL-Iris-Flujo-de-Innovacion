"""
run_gate.py

Orquestador completo del gate de calidad para una ejecución de la skill
'senales-debiles'. Ejecuta de forma determinista todos los verificadores
obligatorios del skill:

  1. validar_esquema.py sobre cada faseN_output.json.
  2. verificar_trazabilidad.py sobre los 5 JSON + reporte HTML.
  3. validar_reporte.py sobre el HTML + fase1-4.
  4. verificar_citas.py sobre fase2/fase3 contra el corpus de transcripciones.
  5. verificar_numeros.py sobre el dataset CSV + fase1-3.

Genera un gate_report.json con veredicto global, errores y warnings por
verificador.

Progreso y fail-closed:
  - Imprime una linea de progreso antes y despues de cada verificador.
  - Cada verificador tiene timeout propio; si se excede, el check se marca
    PENDIENTE en lugar de colgar el orquestador indefinidamente.
  - Al terminar, reescribe el bloque "validacion" de fase4_output.json con la
    salida real del orquestador (y lo escribe a gate_report.json). Si un check
    no llega a PASA/ADV, ese campo queda false. Esto impide que un LLM
    estampe a mano flags de validacion sin un gate real.

Uso:
    python run_gate.py <directorio_proyecto> -o <gate_report.json> \
        [--corpus <carpeta_txt>] [--dataset <dataset.csv>] \
        [--base-pct 0.388] [--absentes "term1,term2"] \
        [--timeout 120]

El directorio debe contener:
    fase0_output.json ... fase4_output.json
    reporte_ejecutivo.html (o fase4_output.html)

Si no se pasa --corpus, se usa el directorio del proyecto (busca *.txt).
Si no se pasa --dataset, se lee la ruta desde fase0_output.json.
"""
import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path


FASES = ["fase0_output.json", "fase1_output.json", "fase2_output.json",
         "fase3_output.json", "fase4_output.json"]

HTML_CANDIDATES = ["reporte_ejecutivo.html", "fase4_output.html", "index.html"]

TIMEOUT_DEFAULT = 120  # segundos por verificador


def find_script(name):
    """Localiza el script en el mismo directorio de run_gate.py."""
    return str(Path(__file__).with_name(name).resolve())


def run_python(script, args, timeout):
    """Ejecuta un script Python con timeout y devuelve (returncode, stdout,
    stderr) o (None, '', 'timeout') si excede el limite."""
    cmd = [sys.executable, script] + [str(a) for a in args]
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              encoding="utf-8", errors="replace", env=env,
                              timeout=timeout)
        return proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired:
        return None, "", f"timeout de {timeout}s excedido"


def veredicto_por_rc(rc, adv_rc=None):
    """Mapea return code a PASA/ADV/FALLA/PENDIENTE."""
    if rc is None:
        return "PENDIENTE"
    if rc == 0:
        return "PASA"
    if adv_rc is not None and rc == adv_rc:
        return "ADV"
    return "FALLA"


def detectar_dataset(project, fase0_path):
    """Busca el CSV de referencia. Prioriza el CSV enriquecido (es el que
    consume fase1_analisis.py y el que verifica el SSoT), luego el crudo
    declarado en fase0 y por último cualquier *.csv del directorio."""
    try:
        with open(fase0_path, encoding="utf-8-sig") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return None

    cuanti = data.get("datos", {}).get("viabilidad", {}).get("datos_cuantitativos", {})
    if not cuanti.get("disponible"):
        return None

    enriquecido = data.get("datos", {}).get("dataset_enriquecido", {}).get("path")
    candidatos = [enriquecido, cuanti.get("archivo")]
    for key in candidatos:
        if key:
            p = project / key
            if p.exists():
                return p

    csvs = sorted(project.glob("*.csv"))
    return csvs[0] if csvs else None


def detectar_corpus(project):
    """Busca una carpeta con archivos .txt."""
    if list(project.glob("*.txt")):
        return project
    for sub in sorted(project.iterdir()):
        if sub.is_dir() and list(sub.glob("*.txt")):
            return sub
    return None


def resumen_estados(check):
    """Deriva un resumen corto por check."""
    v = check.get("veredicto")
    stdout = check.get("stdout") or []
    lineas = [l for l in stdout if l.strip() and "Resumen:" in l]
    if lineas:
        return f"{v} | {lineas[-1].strip()}"
    return v


# Mapeo campo->check: cada punto del checklist de validacion que respalda un
# verificador concreto. Un punto solo puede quedar true si su check es PASA/ADV.
CAMPO_A_CHECK = {
    "ejecutada": "esquema",
    "estructura_2_secciones": "reporte",
    "senales_en_rango": "reporte",
    "decisiones_en_rango": "reporte",
    "badges_ausentes": "reporte",
    "numeracion_correcta": "reporte",
    "decisiones_referencian_senales": "reporte",
    "tono_exploratorio": "reporte",
    "sin_temporalidad": "reporte",
    "ancla_declarada": "reporte",
    "fallback_respetado": "reporte",
    "design_system_aplicado": "reporte",
    "graficas_en_tarjetas": "reporte",
    "heatmap_svg_presente": "reporte",
    "footer_sin_trazabilidad": "reporte",
    "sin_ids_tecnicos": "reporte",
    "citas_verificadas": "citas",
    "filtro_pertinencia_aplicado": "reporte",
    "silencio_de_instrumento_a_footer": "reporte",
    "exclusion_clasificacion_respetada": "esquema",
    "senales_escalan_correctas": "trazabilidad",
}


def aplicar_fail_closed(report, fase4_path):
    """Reescribe el bloque 'validacion' de fase4_output.json segun la salida
    real del orquestador (invariante 0.4 reforzado).

    Regla: ningun campo del checklist queda 'true' si su verificador de
    soporte no es PASA/ADV. El gate es la unica fuente que estampa true;
    si el orquestador no corrio, los campos quedan false."""
    checks = report["checks"]
    estados = {k: checks.get(k, {}).get("veredicto") for k in
               ("esquema", "trazabilidad", "reporte", "citas", "numeros")}
    ok_check = {k: (v in ("PASA", "ADV")) for k, v in estados.items()}

    try:
        with open(fase4_path, encoding="utf-8-sig") as f:
            fase4 = json.load(f)
    except (OSError, json.JSONDecodeError):
        report["fase4_validacion_no_escrita"] = (
            "fase4_output.json no existe o no es JSON valido")
        return report

    # Rebuild total (regla 17 / invariante 0.4): el bloque 'validacion' se
    # reconstruye desde cero con la salida real del gate. Nunca se heredan
    # claves escritas por el LLM (incluidas las que no estan en CAMPO_A_CHECK).
    validacion_prev = fase4.get("validacion")
    si_no_habia = not isinstance(validacion_prev, dict) or not validacion_prev
    validacion = {}

    # 1. Cada campo mapeado hereda el veredicto de su check (nunca true sin check).
    for campo, check in CAMPO_A_CHECK.items():
        validacion[campo] = ok_check[check]

    # 2. Verificadores a nivel de check (nombres tecnicos estables).
    for check, ok in ok_check.items():
        validacion[f"gate_{check}"] = ok

    # 3. Marcadores de autoridad del gate.
    # 'ejecutada' refleja que el gate corrio realmente; el resultado del gate
    # viaja en 'gate_veredicto' (PASA/ADV/FALLA/PENDIENTE).
    validacion["ejecutada"] = True
    validacion["gate_corrio"] = True
    validacion["gate_veredicto"] = report["veredicto"]

    # 4. Puntos fallidos: lista con los checks que no pasaron (vacia si todos pasan).
    fallidos = [k for k, v in estados.items() if v not in ("PASA", "ADV")]
    validacion["puntos_fallidos"] = fallidos if fallidos else []

    fase4["validacion"] = validacion
    if si_no_habia:
        report["fase4_validacion_creada"] = (
            "fase4_output.json no tenia bloque 'validacion' poblado; el gate lo creo")
    else:
        report["fase4_validacion_reconstruida"] = (
            "fase4_output.json traia un bloque 'validacion' pre-existente; se descarto "
            "y se reconstruyo desde la salida real del gate (regla 17)")
    with open(fase4_path, "w", encoding="utf-8") as f:
        json.dump(fase4, f, ensure_ascii=False, indent=2)
    report["fase4_validacion_no_escrita"] = None
    report["validacion_aplicada"] = validacion
    return report


def gate(project_dir, output_path, corpus_dir=None, dataset_path=None,
         base_pct=None, absentes=None, timeout=TIMEOUT_DEFAULT, juicio_path=None):
    project = Path(project_dir)
    if not project.is_dir():
        raise SystemExit(f"No es un directorio: {project_dir}")

    fase_paths = [project / f for f in FASES]
    missing = [p.name for p in fase_paths if not p.exists()]
    if missing:
        raise SystemExit(f"Faltan archivos de fase: {missing}")

    html_path = None
    for cand in HTML_CANDIDATES:
        p = project / cand
        if p.exists():
            html_path = p
            break

    # Detectar corpus y dataset si no se proporcionaron
    corpus = Path(corpus_dir) if corpus_dir else detectar_corpus(project)
    dataset = Path(dataset_path) if dataset_path else detectar_dataset(project, fase_paths[0])

    report = {
        "directorio": str(project.resolve()),
        "html": str(html_path.resolve()) if html_path else None,
        "corpus": str(corpus.resolve()) if corpus else None,
        "dataset": str(dataset.resolve()) if dataset else None,
        "checks": {},
        "veredicto": "PASA",
        "generado_por": "run_gate.py",
    }

    print(f"[gate] Iniciando {len(FASES)} fases + verificadores. "
          f"Timeout por verificador: {timeout}s")

    # 1. Esquema
    print("[gate] 1/5 validar_esquema.py ...")
    t0 = time.time()
    schema_script = find_script("validar_esquema.py")
    rc, out, err = run_python(schema_script, fase_paths, timeout)
    try:
        schema_results = json.loads(out) if out.strip() else []
    except json.JSONDecodeError:
        schema_results = [{"error": "Salida no es JSON", "stdout": out, "stderr": err}]
    schema_ok = all(r.get("veredicto") == "PASA" for r in schema_results) and rc == 0
    report["checks"]["esquema"] = {
        "veredicto": "PASA" if schema_ok else ("PENDIENTE" if rc is None else "FALLA"),
        "detalle": schema_results,
        "stderr": err if err else None,
    }
    print(f"[gate] 1/5 -> {report['checks']['esquema']['veredicto']} "
          f"({time.time()-t0:.1f}s)")
    del schema_results

    # 2. Trazabilidad
    print("[gate] 2/5 verificar_trazabilidad.py ...")
    t0 = time.time()
    traz_script = find_script("verificar_trazabilidad.py")
    args = fase_paths + ([html_path] if html_path else [])
    rc, out, err = run_python(traz_script, args, timeout)
    report["checks"]["trazabilidad"] = {
        "veredicto": veredicto_por_rc(rc),
        "stdout": out.strip().splitlines() if out else [],
        "stderr": err.strip().splitlines() if err else [],
    }
    print(f"[gate] 2/5 -> {report['checks']['trazabilidad']['veredicto']} "
          f"({time.time()-t0:.1f}s)")
    del rc, out, err, args

    # 3. Reporte (solo aplica si el HTML existe; sin reporte el check es "no aplica")
    print("[gate] 3/5 validar_reporte.py ...")
    t0 = time.time()
    rep_script = find_script("validar_reporte.py")
    rc, out, err = None, "", ""
    if html_path:
        # validar_reporte.py espera: html fase1 fase2 fase3 [fase4]
        args = [html_path] + fase_paths[1:]
        rc, out, err = run_python(rep_script, args, timeout)
        report["checks"]["reporte"] = {
            "veredicto": veredicto_por_rc(rc),
            "stdout": out.strip().splitlines() if out else [],
            "stderr": err.strip().splitlines() if err else [],
        }
    else:
        report["checks"]["reporte"] = {
            "veredicto": "ADV",
            "motivo": "No se generó reporte_ejecutivo.html (ninguna señal escala; ver SPEC.md sección 10)",
            "stdout": [],
            "stderr": [],
        }
    print(f"[gate] 3/5 -> {report['checks']['reporte']['veredicto']} "
          f"({time.time()-t0:.1f}s)")

    # 4. Citas (fase2 y fase3 contra corpus)
    print("[gate] 4/5 verificar_citas.py ...")
    t0 = time.time()
    rc, out, err = None, "", ""
    if corpus and corpus.exists() and (fase_paths[2].exists() or fase_paths[3].exists()):
        cita_script = find_script("verificar_citas.py")
        args = [fase_paths[2], fase_paths[3], "--corpus", corpus]
        if absentes:
            args += ["--absentes", absentes]
        if juicio_path:
            args += ["--juicio", juicio_path]
        rc, out, err = run_python(cita_script, args, timeout)
        report["checks"]["citas"] = {
            "veredicto": veredicto_por_rc(rc, adv_rc=2),
            "stdout": out.strip().splitlines() if out else [],
            "stderr": err.strip().splitlines() if err else [],
        }
    else:
        report["checks"]["citas"] = {
            "veredicto": "ADV",
            "motivo": "No se encontró corpus de transcripciones (*.txt) o faltan fase2/fase3",
            "stdout": [],
            "stderr": [],
        }
    print(f"[gate] 4/5 -> {report['checks']['citas']['veredicto']} "
          f"({time.time()-t0:.1f}s)")

    # 5. Números (dataset + fase1-3)
    print("[gate] 5/5 verificar_numeros.py ...")
    t0 = time.time()
    rc, out, err = None, "", ""
    if dataset and dataset.exists() and fase_paths[1].exists():
        num_script = find_script("verificar_numeros.py")
        args = [dataset, fase_paths[1], fase_paths[2], fase_paths[3]]
        if base_pct is not None:
            args += ["--base-pct", base_pct]
        rc, out, err = run_python(num_script, args, timeout)
        report["checks"]["numeros"] = {
            "veredicto": veredicto_por_rc(rc),
            "stdout": out.strip().splitlines() if out else [],
            "stderr": err.strip().splitlines() if err else [],
        }
    else:
        report["checks"]["numeros"] = {
            "veredicto": "ADV",
            "motivo": "No se encontró dataset CSV o falta fase1",
            "stdout": [],
            "stderr": [],
        }
    print(f"[gate] 5/5 -> {report['checks']['numeros']['veredicto']} "
          f"({time.time()-t0:.1f}s)")

    # Veredicto global
    veredictos = [v["veredicto"] for v in report["checks"].values()]
    if any(v == "FALLA" for v in veredictos):
        report["veredicto"] = "FALLA"
    elif any(v == "PENDIENTE" for v in veredictos):
        report["veredicto"] = "PENDIENTE"
    elif any(v == "ADV" for v in veredictos):
        report["veredicto"] = "ADV"

    print(f"[gate] Veredicto: {report['veredicto']}")
    for nombre, check in report["checks"].items():
        print(f"[gate]   {nombre}: {resumen_estados(check)}")

    # Fail-closed: reescribir bloque validacion de fase4_output.json
    report = aplicar_fail_closed(report, fase_paths[4])
    if report.get("fase4_validacion_no_escrita"):
        print(f"[gate] AVISO: {report['fase4_validacion_no_escrita']}")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    out_json = json.dumps(report, ensure_ascii=False, indent=2)
    sys.stdout.buffer.write(out_json.encode("utf-8"))
    sys.stdout.buffer.write(b"\n\n")
    sys.stdout.buffer.write(f"Gate report guardado en: {output_path}\n".encode("utf-8"))
    sys.exit(0 if report["veredicto"] == "PASA" else (1 if report["veredicto"] == "FALLA" else 2))


def main():
    parser = argparse.ArgumentParser(description="Ejecuta el gate de calidad completo.")
    parser.add_argument("project_dir", help="Directorio con JSON de fases y HTML")
    parser.add_argument("-o", "--output", required=True, help="Ruta del gate_report.json")
    parser.add_argument("--corpus", help="Carpeta con transcripciones .txt (default: directorio del proyecto)")
    parser.add_argument("--dataset", help="CSV del dataset cuantitativo (default: ruta en fase0_output.json)")
    parser.add_argument("--base-pct", help="Porcentaje base para verificar_numeros (ej. 0.388)")
    parser.add_argument("--absentes", help="Términos para claims de ausencia en verificar_citas (ej. 'comunidad,vecinos')")
    parser.add_argument("--juicio", help="Veredictos de LLM-judge para citas de paráfrasis (verificar_citas --juicio)")
    parser.add_argument("--timeout", type=int, default=TIMEOUT_DEFAULT,
                        help=f"Segundos máximos por verificador (default: {TIMEOUT_DEFAULT})")
    args = parser.parse_args()
    gate(args.project_dir, args.output, corpus_dir=args.corpus, dataset_path=args.dataset,
         base_pct=args.base_pct, absentes=args.absentes, timeout=args.timeout,
         juicio_path=args.juicio)


if __name__ == "__main__":
    main()
