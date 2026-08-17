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

Uso:
    python run_gate.py <directorio_proyecto> -o <gate_report.json> \
        [--corpus <carpeta_txt>] [--dataset <dataset.csv>] \
        [--base-pct 0.388] [--absentes "term1,term2"]

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
from pathlib import Path


FASES = ["fase0_output.json", "fase1_output.json", "fase2_output.json",
         "fase3_output.json", "fase4_output.json"]

HTML_CANDIDATES = ["reporte_ejecutivo.html", "fase4_output.html", "index.html"]


def find_script(name):
    """Localiza el script en el mismo directorio de run_gate.py."""
    return str(Path(__file__).with_name(name).resolve())


def run_python(script, args):
    """Ejecuta un script Python y devuelve (returncode, stdout, stderr)."""
    cmd = [sys.executable, script] + [str(a) for a in args]
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                          errors="replace", env=env)
    return proc.returncode, proc.stdout, proc.stderr


def veredicto_por_rc(rc, adv_rc=None):
    """Mapea return code a PASA/ADV/FALLA."""
    if rc == 0:
        return "PASA"
    if adv_rc is not None and rc == adv_rc:
        return "ADV"
    return "FALLA"


def detectar_dataset(project, fase0_path):
    """Busca el CSV original en fase0_output.json o en el directorio."""
    try:
        with open(fase0_path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return None

    cuanti = data.get("datos", {}).get("viabilidad", {}).get("datos_cuantitativos", {})
    if not cuanti.get("disponible"):
        return None

    for key in (cuanti.get("archivo"),
                data.get("datos", {}).get("dataset_enriquecido", {}).get("path")):
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


def gate(project_dir, output_path, corpus_dir=None, dataset_path=None,
         base_pct=None, absentes=None):
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
    }

    # 1. Esquema
    schema_script = find_script("validar_esquema.py")
    rc, out, err = run_python(schema_script, fase_paths)
    try:
        schema_results = json.loads(out) if out.strip() else []
    except json.JSONDecodeError:
        schema_results = [{"error": "Salida no es JSON", "stdout": out, "stderr": err}]
    schema_ok = all(r.get("veredicto") == "PASA" for r in schema_results) and rc == 0
    report["checks"]["esquema"] = {
        "veredicto": "PASA" if schema_ok else "FALLA",
        "detalle": schema_results,
        "stderr": err if err else None,
    }

    # 2. Trazabilidad
    traz_script = find_script("verificar_trazabilidad.py")
    args = fase_paths + ([html_path] if html_path else [])
    rc, out, err = run_python(traz_script, args)
    report["checks"]["trazabilidad"] = {
        "veredicto": veredicto_por_rc(rc),
        "stdout": out.strip().splitlines() if out else [],
        "stderr": err.strip().splitlines() if err else [],
    }

    # 3. Reporte
    rep_script = find_script("validar_reporte.py")
    if html_path:
        # validar_reporte.py espera: html fase1 fase2 fase3 [fase4]
        args = [html_path] + fase_paths[1:]
    else:
        args = []
    rc, out, err = run_python(rep_script, args)
    report["checks"]["reporte"] = {
        "veredicto": veredicto_por_rc(rc),
        "stdout": out.strip().splitlines() if out else [],
        "stderr": err.strip().splitlines() if err else [],
    }

    # 4. Citas (fase2 y fase3 contra corpus)
    if corpus and corpus.exists() and (fase_paths[2].exists() or fase_paths[3].exists()):
        cita_script = find_script("verificar_citas.py")
        args = [fase_paths[2], fase_paths[3], "--corpus", corpus]
        if absentes:
            args += ["--absentes", absentes]
        rc, out, err = run_python(cita_script, args)
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

    # 5. Números (dataset + fase1-3)
    if dataset and dataset.exists() and fase_paths[1].exists():
        num_script = find_script("verificar_numeros.py")
        args = [dataset, fase_paths[1], fase_paths[2], fase_paths[3]]
        if base_pct is not None:
            args += ["--base-pct", base_pct]
        rc, out, err = run_python(num_script, args)
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

    # Veredicto global
    if any(v["veredicto"] == "FALLA" for v in report["checks"].values()):
        report["veredicto"] = "FALLA"
    elif any(v["veredicto"] == "ADV" for v in report["checks"].values()):
        report["veredicto"] = "ADV"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    out_json = json.dumps(report, ensure_ascii=False, indent=2)
    sys.stdout.buffer.write(out_json.encode("utf-8"))
    sys.stdout.buffer.write(b"\n\n")
    sys.stdout.buffer.write(f"Gate report guardado en: {output_path}\n".encode("utf-8"))
    sys.exit(0 if report["veredicto"] == "PASA" else 1)


def main():
    parser = argparse.ArgumentParser(description="Ejecuta el gate de calidad completo.")
    parser.add_argument("project_dir", help="Directorio con JSON de fases y HTML")
    parser.add_argument("-o", "--output", required=True, help="Ruta del gate_report.json")
    parser.add_argument("--corpus", help="Carpeta con transcripciones .txt (default: directorio del proyecto)")
    parser.add_argument("--dataset", help="CSV del dataset cuantitativo (default: ruta en fase0_output.json)")
    parser.add_argument("--base-pct", help="Porcentaje base para verificar_numeros (ej. 0.388)")
    parser.add_argument("--absentes", help="Términos para claims de ausencia en verificar_citas (ej. 'comision,comisiones')")
    args = parser.parse_args()
    gate(args.project_dir, args.output, corpus_dir=args.corpus, dataset_path=args.dataset,
         base_pct=args.base_pct, absentes=args.absentes)


if __name__ == "__main__":
    main()
