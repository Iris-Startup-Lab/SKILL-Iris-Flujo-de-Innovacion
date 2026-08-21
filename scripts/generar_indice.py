#!/usr/bin/env python3
"""Genera `index.html`: el tablero de navegación de un proyecto IRIS.

Lee `flujo_estado.json` + `pasos.json` y escribe un `index.html` ligero, en la misma
carpeta del proyecto, que lista los 11 pasos con su estado, su resumen y un enlace
«Abrir reporte» para los pasos completados.

Por qué existe: los reportes se enlazan entre sí con enlaces relativos (el riel del
flujo apunta a `html_1.html`, `html_4.html`, …). Esos enlaces funcionan cuando los 11
HTML se abren desde la misma carpeta **en el navegador**. En la vista previa embebida
de un gestor no hay sistema de archivos, así que un HTML no puede abrir a su vecino.
`index.html` es la puerta de entrada: se abre una sola vez y desde ahí se navega.

Es barato: NO regenera los reportes; solo lee el estado y escribe un archivo pequeño.

Uso (desde la raíz del repositorio):

    python scripts/generar_indice.py                      # estado en la raíz del repo
    python scripts/generar_indice.py --estado output/<proyecto>   # proyecto en carpeta
    python scripts/generar_indice.py --estado <ruta> -o <salida.html>
"""
import argparse
import base64
import json
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
REPO_ROOT = _HERE.parent

PASOS_JSON = REPO_ROOT / "pasos.json"
ESTADO_JSON = REPO_ROOT / "flujo_estado.json"
LOGO_DEFAULT = REPO_ROOT / "imagenes_iconos_etc" / "Logos_GS_Iris_transparent.png"

ESTADO_LABEL = {
    "completado": "Completado",
    "omitido": "Omitido",
    "pendiente": "Pendiente",
    "en_curso": "En curso",
    "fallido": "Falló",
}

CSS = """
  :root{
    --purple-900:#241B33; --purple-700:#3D2766; --purple-600:#5A3A8C; --purple-200:#D9CCEF;
    --purple-100:#EDE6F7; --purple-050:#F7F3FC;
    --gold-400:#E8B93E; --gold-600:#B8862F;
    --ink:#2A2433; --ink-soft:#5C5468; --line:#E4DCEF; --white:#fff;
    --ok:#3E8E5A; --ok-bg:#DCFCE7; --warn:#B8862F; --warn-bg:#FEF9C3;
    --bad:#B84A3D; --bad-bg:#FEE2E2;
  }
  *{box-sizing:border-box;margin:0;padding:0}
  body{font-family:'Inter',system-ui,sans-serif;background:var(--purple-050);color:var(--ink);line-height:1.5}
  a{color:var(--purple-600)}
  header{background:linear-gradient(135deg,var(--purple-900),var(--purple-700));color:#fff;padding:26px clamp(20px,4vw,56px) 30px}
  .head-row{display:flex;align-items:center;gap:16px;flex-wrap:wrap}
  .logo{background:#fff;border-radius:12px;padding:6px 12px}
  .logo img{height:44px;width:auto;display:block}
  h1{font-family:'Sora',sans-serif;font-size:clamp(1.3rem,2.6vw,1.9rem);font-weight:800;margin-top:14px}
  .sub{color:#D8CCEF;margin-top:4px;font-size:.95rem}
  .avance{margin-top:14px;display:flex;gap:10px;flex-wrap:wrap}
  .chip{background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.18);border-radius:999px;padding:5px 14px;font-size:.78rem}
  main{max-width:960px;margin:0 auto;padding:22px clamp(20px,4vw,56px) 40px}
  .paso{display:flex;gap:14px;align-items:flex-start;background:#fff;border:1px solid var(--line);border-radius:14px;padding:16px 18px;margin-bottom:12px;box-shadow:0 1px 3px rgba(42,36,51,.06)}
  .paso.actual{border-color:var(--gold-600);box-shadow:0 6px 20px rgba(61,39,102,.12)}
  .n{flex:0 0 auto;width:30px;height:30px;border-radius:999px;background:var(--purple-700);color:#fff;font-family:'Sora',sans-serif;font-weight:700;display:grid;place-items:center;font-size:.85rem}
  .paso.actual .n{background:var(--gold-400);color:var(--purple-900)}
  .info{flex:1;min-width:0}
  .info h2{font-family:'Sora',sans-serif;font-size:1rem;font-weight:700}
  .etapa{font-size:.72rem;color:var(--ink-soft);text-transform:uppercase;letter-spacing:.08em}
  .resumen{font-size:.85rem;color:var(--ink-soft);margin-top:4px}
  .col{display:flex;flex-direction:column;align-items:flex-end;gap:8px;flex:0 0 auto}
  .estado{font-size:.72rem;font-weight:700;padding:3px 12px;border-radius:999px;white-space:nowrap}
  .estado.completado{color:var(--ok);background:var(--ok-bg)}
  .estado.omitido{color:var(--ink-soft);background:var(--purple-100);text-decoration:line-through}
  .estado.pendiente{color:var(--ink-soft);background:var(--purple-100)}
  .estado.en_curso{color:var(--warn);background:var(--warn-bg)}
  .estado.fallido{color:var(--bad);background:var(--bad-bg)}
  .btn{font-size:.8rem;font-weight:600;color:#fff;background:var(--purple-600);border-radius:999px;padding:7px 16px;text-decoration:none;white-space:nowrap}
  .btn:hover{background:var(--purple-700)}
  footer{max-width:960px;margin:0 auto;padding:0 clamp(20px,4vw,56px) 40px;color:var(--ink-soft);font-size:.78rem}
  footer .box{background:#fff;border:1px solid var(--line);border-radius:12px;padding:14px 18px}
  @media (max-width:640px){ .paso{flex-wrap:wrap} .col{flex-direction:row;align-items:center;width:100%} }
"""


def cargar_pasos(ruta=None):
    ruta = Path(ruta) if ruta else PASOS_JSON
    if not ruta.is_file():
        raise FileNotFoundError(f"No encuentro la definición del flujo: {ruta}")
    return json.loads(ruta.read_text(encoding="utf-8"))


def cargar_estado(ruta=None):
    ruta = Path(ruta) if ruta else ESTADO_JSON
    if not ruta.is_file():
        raise FileNotFoundError(f"No encuentro {ruta}. Inicia el proyecto primero.")
    return json.loads(ruta.read_text(encoding="utf-8"))


def logo_data_uri():
    if LOGO_DEFAULT.is_file():
        data = base64.b64encode(LOGO_DEFAULT.read_bytes()).decode("ascii")
        return f"data:image/png;base64,{data}"
    return None


def esc(texto):
    return (
        str(texto if texto is not None else "")
        .replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    )


def construir_indice(estado, pasos):
    titulos = {p["id"]: p for p in pasos["pasos"]}
    proyecto = estado.get("proyecto") or "Proyecto IRIS"
    comp = sum(1 for p in estado["pasos"] if p["estado"] == "completado")
    omit = sum(1 for p in estado["pasos"] if p["estado"] == "omitido")
    total = len(estado["pasos"])
    actual = estado.get("paso_actual")

    filas = []
    for p in estado["pasos"]:
        d = titulos.get(p["id"], {})
        estado_txt = ESTADO_LABEL.get(p["estado"], p["estado"])
        es_actual = p["id"] == actual
        if es_actual:
            estado_txt = "Este reporte" if p["estado"] == "en_curso" else "Actual"
        resumen = p.get("resumen") or ""
        if p["estado"] == "omitido":
            resumen = f"Omitido — {p.get('motivo','')}"
            if p.get("impacto"):
                resumen += f" · Impacto: {p['impacto']}"
        elif p["estado"] == "fallido":
            resumen = f"Falló — {p.get('motivo','')}"

        enlace = ""
        if p["estado"] == "completado" and p.get("outputs"):
            archivo = p["outputs"][0]
            enlace = f'<a class="btn" href="{esc(archivo)}" target="_blank" rel="noopener">Abrir reporte</a>'

        filas.append(
            f'<div class="paso{(" actual" if es_actual else "")}">'
            f'<span class="n">{d.get("orden", "?")}</span>'
            f'<div class="info"><h2>{esc(p["titulo"])}</h2>'
            f'<div class="etapa">{esc(d.get("etapa", p.get("etapa", "")))} · {esc(p["id"])}</div>'
            + (f'<p class="resumen">{esc(resumen)}</p>' if resumen else "")
            + f'</div>'
            f'<div class="col"><span class="estado {esc(p["estado"])}">{esc(estado_txt)}</span>{enlace}</div>'
            f'</div>'
        )
    return proyecto, comp, omit, total, "\n".join(filas)


def generar(estado_path, output_path, pasos_path=None):
    pasos = cargar_pasos(pasos_path)
    estado = cargar_estado(estado_path)
    proyecto, comp, omit, total, filas = construir_indice(estado, pasos)

    uri = logo_data_uri()
    logo = f'<span class="logo"><img alt="IRIS" src="{uri}"></span>' if uri else ""

    avance = f"<div class='avance'>"
    avance += f"<span class='chip'>{comp} completado{'s' if comp != 1 else ''}</span>"
    avance += f"<span class='chip'>{omit} omitido{'s' if omit != 1 else ''}</span>"
    avance += f"<span class='chip'>{total} pasos</span></div>"

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>IRIS — {esc(proyecto)}</title>
<link href="https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>
<header>
  <div class="head-row">{logo}<span class="chip" style="background:transparent;border:none;font-family:Sora;font-weight:700">IRIS — Flujo de Innovación</span></div>
  <h1>{esc(proyecto)}</h1>
  <p class="sub">Tablero de navegación · abre cada reporte con el botón «Abrir reporte».</p>
  {avance}
</header>
<main>{filas}</main>
<footer><div class="box">
  <b>Para navegar entre reportes:</b> mantén todos los HTML de este proyecto en esta misma
  carpeta y abre <code>index.html</code> con el navegador (doble clic). Los enlaces del
  riel dentro de cada reporte también funcionan desde aquí. En una vista previa embebida
  (sin sistema de archivos) los enlaces entre archivos no se pueden resolver.
</div></footer>
</body>
</html>
"""
    out = Path(output_path) if output_path else Path(estado_path).resolve().parent / "index.html"
    out.write_text(html, encoding="utf-8")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="Genera index.html: tablero de navegación del proyecto IRIS.")
    ap.add_argument("--estado", default=None, help="Ruta de flujo_estado.json")
    ap.add_argument("--pasos", default=None, help="Ruta de pasos.json")
    ap.add_argument("-o", "--output", default=None, help="Ruta de salida (default: index.html junto al estado)")
    args = ap.parse_args(argv)

    try:
        out = generar(args.estado, args.output, args.pasos)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    print(f"Tablero de navegación escrito en {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
