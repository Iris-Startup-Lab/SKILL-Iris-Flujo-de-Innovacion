"""
verificar_fuentes.py — comprueba las citas de un reporte contra los documentos descargados.

Es el seguro contra cifras inventadas. El reporte cita con `[F3]` (el id que dio
`fuentes.py`); este script busca, frase por frase:

1. **Que la fuente exista.** Un `[F9]` que no está en `fuentes.json` es una cita a
   un documento que nadie descargó.
2. **Que la cifra esté en el texto.** Cada número de una frase que cita `[Fn]` tiene
   que aparecer en el texto guardado de esa fuente (se aceptan `1,234.5`, `1.234,5`
   y `1 234`). Un número seguido de `*` se declara como cálculo propio y no se busca.
3. **Que la cita textual sea literal.** Lo que va entre «», “” o "" (20+ caracteres)
   tiene que estar en la fuente; `…` o `...` separan tramos que se buscan por separado.
4. **Que el texto no se haya tocado.** El sha256 guardado al capturar tiene que coincidir.
5. **Que la fuente no sea vieja.** Más de `--max-anios` (3 por defecto) es advertencia.

Veredicto:
- `VERIFICADO` — todas las citas existen y todas las cifras y frases citadas están en su fuente.
- `PARCIAL` — las fuentes existen, pero alguna cifra o frase no aparece en la fuente citada.
- `NO VERIFICADO` — no hay bitácora, no hay ninguna cita, una cita apunta a una fuente
  inexistente o un texto guardado fue alterado.

    python _plantilla_html/scripts/verificar_fuentes.py --reporte reporte.json \
        --fuentes fuentes.json [--escribir] [--max-anios 3] [--estricto]

`--escribir` deja el resultado en el propio `reporte.json`: la lista `fuentes` con
título, medio, fecha, tipo y URL de cada fuente citada; una línea de veredicto y los
fallos en `advertencias`; y `meta.verificacion_fuentes`. Después se genera el HTML como
siempre. `--estricto` también señala cifras de 2+ dígitos que no citan nada ni llevan
`*`, `[REFERENCIA DE INDUSTRIA]` o `[no disponible]`.

Salida: 0 VERIFICADO · 2 PARCIAL · 3 NO VERIFICADO · 1 error de uso.
"""
import argparse
import hashlib
import json
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path

RE_CITA = re.compile(r"\[(F\d+(?:\s*[,;]\s*F\d+)*)\]")
RE_NUM = re.compile(r"(?<![\w.,])(\d{1,3}(?:[.,\s]\d{3})+(?:[.,]\d+)?|\d+(?:[.,]\d+)?)(\s*\*)?")
RE_FRASE = re.compile(r"(?<=[.;!?])\s+(?=[A-ZÁÉÍÓÚÑ¿¡«\"“(])|\n+")
RE_COMILLAS = re.compile(r"«([^»]{20,})»|“([^”]{20,})”|\"([^\"]{20,})\"")
MARCAS_OK = ("[REFERENCIA DE INDUSTRIA]", "[no disponible]", "[no localizable]")
CLAVES_IGNORADAS = {"flujo", "fuentes", "verificacion_fuentes", "chart", "vista_previa"}
PREFIJO_VEREDICTO = "Verificación de fuentes:"
PREFIJO_FALLO = "Fuente sin respaldo:"


def lecturas(numero):
    """Valores posibles de un número escrito con cualquiera de los dos estilos de separador."""
    n = numero.replace(" ", "").replace(" ", "")
    out = set()
    for miles, dec in ((",", "."), (".", ",")):
        if n.count(dec) > 1:
            continue
        cand = n.replace(miles, "").replace(dec, ".")
        try:
            out.add(round(float(cand), 6))
        except ValueError:
            pass
    return out


def numeros_de(texto):
    vals = set()
    for m in RE_NUM.finditer(texto):
        vals |= lecturas(m.group(1))
    return vals


def plano(s):
    s = unicodedata.normalize("NFKD", s.lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[^\w\s]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def cadenas(obj, ruta="", clave=None):
    """(ruta, texto) de cada cadena del reporte, saltando el contexto del flujo."""
    if clave in CLAVES_IGNORADAS:
        return
    if isinstance(obj, str):
        yield ruta, obj
    elif isinstance(obj, dict):
        for k, v in obj.items():
            yield from cadenas(v, f"{ruta}.{k}" if ruta else k, k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from cadenas(v, f"{ruta}[{i}]", None)


def cargar_fuentes(ruta):
    base = Path(ruta).resolve().parent
    bit = json.loads(Path(ruta).read_text(encoding="utf-8"))
    fuentes, alteradas = {}, []
    for f in bit.get("fuentes", []):
        p = base / f["archivo_texto"]
        texto = p.read_text(encoding="utf-8") if p.exists() else None
        if texto is None or hashlib.sha256(texto.encode("utf-8")).hexdigest() != f.get("sha256"):
            alteradas.append(f["id"])
            texto = texto or ""
        fuentes[f["id"]] = {**f, "_texto": texto, "_plano": plano(texto),
                            "_numeros": numeros_de(texto)}
    return fuentes, alteradas


def verificar(reporte, fuentes, max_anios=3, estricto=False):
    citadas, fallos, inexistentes, sin_cita = set(), [], set(), []
    n_cifras = n_frases = 0
    for ruta, texto in cadenas(reporte):
        for frase in RE_FRASE.split(texto):
            ids = [i.strip() for g in RE_CITA.findall(frase) for i in re.split(r"[,;]", g)]
            limpia = RE_CITA.sub(" ", frase)
            if not ids:
                if estricto and not any(m in frase for m in MARCAS_OK):
                    for m in RE_NUM.finditer(limpia):
                        if not m.group(2) and len(re.sub(r"\D", "", m.group(1))) >= 2:
                            sin_cita.append(f"{ruta}: «{frase.strip()[:120]}»")
                            break
                continue
            presentes = [i for i in ids if i in fuentes]
            inexistentes |= {i for i in ids if i not in fuentes}
            citadas |= set(presentes)
            if not presentes:
                continue
            nums_fuente = set().union(*(fuentes[i]["_numeros"] for i in presentes))
            for m in RE_NUM.finditer(limpia):
                if m.group(2):          # «12.5*»: cálculo propio declarado
                    continue
                vals = lecturas(m.group(1))
                if vals and max(vals) < 10 and "." not in m.group(1) and "," not in m.group(1):
                    continue            # enteros de un dígito: conteos y ordinales
                n_cifras += 1
                if not vals & nums_fuente:
                    fallos.append(f"{PREFIJO_FALLO} la cifra «{m.group(1)}» no aparece en "
                                  f"{', '.join(presentes)} ({ruta}).")
            for g in RE_COMILLAS.findall(limpia):
                cita = next(x for x in g if x)
                for tramo in re.split(r"…|\.\.\.", cita):
                    t = plano(tramo)
                    if len(t) < 12:
                        continue
                    n_frases += 1
                    if not any(t in fuentes[i]["_plano"] for i in presentes):
                        fallos.append(f"{PREFIJO_FALLO} la frase «{tramo.strip()[:80]}» no está "
                                      f"literal en {', '.join(presentes)} ({ruta}).")

    viejas = []
    hoy = date.today()
    for i in sorted(citadas, key=lambda x: int(x[1:])):
        fp = fuentes[i].get("fecha_publicacion") or ""
        try:
            anios = (hoy - date.fromisoformat(fp[:10])).days / 365.25
        except ValueError:
            continue
        if anios > max_anios:
            viejas.append(f"{i} se publicó hace {anios:.1f} años ({fp[:10]}): úsala como "
                          "contexto, no como dato actual.")
    return citadas, sorted(inexistentes), fallos, viejas, sin_cita, n_cifras, n_frases


def linea_fuente(f):
    partes = [f"[{f['id']}] {f['titulo']}"]
    if f.get("medio"):
        partes.append(f["medio"])
    partes.append(f"publicada {f['fecha_publicacion']}" if f.get("fecha_publicacion")
                  else "sin fecha de publicación")
    partes.append(f"consultada {f['fecha_consulta']}")
    partes.append({"oficial": "fuente oficial", "medio": "medio de comunicación",
                   "consultora": "consultora", "academica": "académica", "empresa": "empresa",
                   "propia": "material propio", "otro": "otra fuente"}.get(f["tipo"], f["tipo"]))
    if f.get("capturado_por") == "herramienta_web":
        partes.append("texto obtenido con la búsqueda web de la herramienta")
    s = " — ".join(partes[:2]) + " · " + " · ".join(partes[2:])
    return s + (f" · {f['url']}" if f.get("url") else "")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--reporte", required=True)
    ap.add_argument("--fuentes", default="fuentes.json")
    ap.add_argument("--max-anios", type=float, default=3)
    ap.add_argument("--escribir", action="store_true")
    ap.add_argument("--estricto", action="store_true")
    a = ap.parse_args(argv)

    reporte = json.loads(Path(a.reporte).read_text(encoding="utf-8"))
    if Path(a.fuentes).exists():
        fuentes, alteradas = cargar_fuentes(a.fuentes)
    else:
        fuentes, alteradas = {}, []
    citadas, inexistentes, fallos, viejas, sin_cita, n_cif, n_fra = verificar(
        reporte, fuentes, a.max_anios, a.estricto)

    motivos = []
    if not fuentes:
        motivos.append("no hay bitácora de fuentes (fuentes.json)")
    if not citadas and not inexistentes:
        motivos.append("el reporte no cita ninguna fuente con [Fn]")
    if inexistentes:
        motivos.append("cita fuentes que no están en la bitácora: " + ", ".join(inexistentes))
    alt = sorted(set(alteradas) & citadas)
    if alt:
        motivos.append("el texto guardado de " + ", ".join(alt) + " no coincide con el capturado")
    estado = "NO VERIFICADO" if motivos else ("PARCIAL" if fallos else "VERIFICADO")

    resumen = (f"{estado} — fuentes citadas: {len(citadas)}; comprobadas contra el texto "
               f"descargado: {n_cif} cifras y {n_fra} frases; sin respaldo: {len(fallos)}.")
    if motivos:
        resumen += " Motivo: " + "; ".join(motivos) + "."
    resultado = {"estado": estado, "resumen": resumen, "fuentes_citadas": sorted(citadas),
                 "fallos": fallos, "fuentes_antiguas": viejas, "cifras_sin_cita": sin_cita}
    print(json.dumps(resultado, ensure_ascii=False, indent=2))

    if a.escribir:
        adv = [x for x in reporte.get("advertencias", [])
               if not str(x).startswith((PREFIJO_VEREDICTO, PREFIJO_FALLO))]
        adv.insert(0, f"{PREFIJO_VEREDICTO} {resumen}")
        adv += fallos + [f"Fuente antigua: {v}" for v in viejas]
        adv += [f"{PREFIJO_FALLO} cifra sin cita ni marca en {s}" for s in sin_cita]
        reporte["advertencias"] = adv
        previas = [x for x in reporte.get("fuentes", []) if not re.match(r"\[F\d+\]", str(x))]
        reporte["fuentes"] = [linea_fuente(fuentes[i])
                              for i in sorted(citadas, key=lambda x: int(x[1:]))] + previas
        reporte.setdefault("meta", {})["verificacion_fuentes"] = {
            k: resultado[k] for k in ("estado", "resumen", "fuentes_citadas")}
        Path(a.reporte).write_text(json.dumps(reporte, ensure_ascii=False, indent=2),
                                   encoding="utf-8")
    return {"VERIFICADO": 0, "PARCIAL": 2, "NO VERIFICADO": 3}[estado]


if __name__ == "__main__":
    sys.exit(main())
