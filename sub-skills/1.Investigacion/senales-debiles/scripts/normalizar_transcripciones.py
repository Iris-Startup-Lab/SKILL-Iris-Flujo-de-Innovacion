# -*- coding: utf-8 -*-
"""
normalizar_transcripciones.py

Normaliza transcripciones de entrevista entregadas como planilla (XLSX/DOCX)
a TXT por archivo, listos para el analisis cualitativo de la skill 'senales-debiles'.

Lee el XLSX/DOCX SIN dependencias externas (zipfile + xml.etree del stdlib), agrupa
los turnos por archivo de entrevista (columna 'archivo'), y exporta un
<entrevista>.txt por archivo, concatenando el texto de cada turno en orden con
etiqueta de hablante. Costo: calculo local, 0 tokens (CLI).

DOCX sin tabla-planilla (narrativo) se vuelca como un solo TXT
(formato 'docx_narrativo' en el manifiesto).

Rol de hablante (obligatorio):
    persona_N es una etiqueta de diarizacion, NO un rol. Dentro de cada archivo
    se infiere por contexto linguistico quien hace preguntas/solicitudes
    (-> 'entrevistador') y los demas se renombran 'entrevistado_1',
    'entrevistado_2', ... en orden de aparicion. Nunca se asume persona_N = rol.

Caso multihablante: cada entrevistado_N cuenta como poblacion distinta para la
regla 12 / blindaje transpoblacional; el manifiesto declara n_hablantes por
archivo.

Uso:
    python normalizar_transcripciones.py <planilla.xlsx|.docx> -o <dir_txt> \
        [--manifesto <json>] [--mapeo <json>]

Mapeo (opcional, lo declara Fase 0 en datos.mapeo_transcripcion):
    {
      "hoja": "Hoja1" | "1",           # nombre o indice 1-based (default: primera con datos)
      "col_archivo": "A" | "Nombre del archivo",
      "col_hablante": "C" | "Persona quien habla",
      "col_texto": "D" | "Texto",
      "col_perfil": "B" | "Perfil",    # opcional
      "col_fuente": "E" | "Fuente"     # opcional
    }
    Cada col se da por LETRA (A, B, ...) o por NOMBRE exacto de cabecera.
"""
import argparse
import json
import os
import re
import sys
import zipfile
from collections import defaultdict
from pathlib import Path
from xml.etree import ElementTree as ET

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
NS_W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def handle_ws(x):
    return re.sub(r"\s+", " ", x).strip()


def nombre_legible(celda):
    m = re.match(r"([A-Z]+)(\d+)", celda)
    if not m:
        return None
    col = 0
    for ch in m.group(1):
        col = col * 26 + (ord(ch) - ord("A") + 1)
    return col - 1, int(m.group(2)) - 1  # (col_idx, row_idx) 0-based


def leer_xlsx(ruta):
    """Devuelve {nombre_hoja: [(row0, {col_idx: valor}), ...]}."""
    hojas = {}
    with zipfile.ZipFile(ruta) as z:
        nombres = z.namelist()
        # 1. shared strings
        shared = []
        if "xl/sharedStrings.xml" in nombres:
            root = ET.fromstring(z.read("xl/sharedStrings.xml"))
            for si in root.findall("m:si", NS):
                textos = [t.text or "" for t in si.iter("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t")]
                shared.append("".join(textos))

        # 2. workbook -> hojas (nombre, ruta de hoja) resolviendo xl/_rels/workbook.xml.rels
        REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
        rel_root = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
        rel_map = {r.get("Id"): r.get("Target") for r in rel_root}
        wb = ET.fromstring(z.read("xl/workbook.xml"))
        hojas_orden = []
        sheets_el = wb.find("m:sheets", NS)
        for sh in (sheets_el.findall("m:sheet", NS) if sheets_el is not None else []):
            name = sh.get("name")
            rid = sh.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")
            target = rel_map.get(rid)
            if not target:
                continue
            # Targets pueden ser relativos (worksheets/sheet1.xml) o absolutos
            # (/xl/worksheets/sheet1.xml). Normalizar a ruta dentro del zip.
            target_clean = target.lstrip("/")
            if target_clean.startswith("xl/"):
                path = target_clean
            else:
                path = "xl/" + target_clean
            hojas_orden.append((name, path))

        for nombre, path in hojas_orden:
            if path not in nombres:
                continue
            root = ET.fromstring(z.read(path))
            filas = []
            for row in root.iter("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row"):
                r_idx = int(row.get("r", "1")) - 1
                celdas = {}
                for c in row.findall("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c"):
                    ref = nombre_legible(c.get("r", ""))
                    if not ref:
                        continue
                    c_idx = ref[0]
                    t = c.get("t")
                    v = c.find("m:v", NS)
                    txt = ""
                    if t == "s" and v is not None:
                        txt = shared[int(v.text)]
                    elif t == "inlineStr":
                        is_ = c.find("m:is", NS)
                        if is_ is not None:
                            txt = "".join(t.text or "" for t in is_.iter("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t"))
                    elif t == "str" and v is not None:
                        txt = v.text or ""
                    elif v is not None:
                        txt = v.text or ""
                    txt = handle_ws(txt)
                    if txt:
                        celdas[c_idx] = txt
                if celdas:
                    filas.append((r_idx, celdas))
            hojas[nombre] = filas
    return hojas


def _texto_celda_docx(tc):
    """Texto completo de una celda de tabla DOCX (todos sus párrafos)."""
    return handle_ws(" ".join(t.text or "" for t in tc.iter(f"{{{NS_W}}}t")))


def leer_docx(ruta):
    """Lee tablas de un DOCX (planilla de transcripciones). Devuelve
    {nombre_hoja: [(r_idx, {col_idx: texto}), ...]} — misma estructura que
    leer_xlsx, para reutilizar resolver_columnas y el agrupado por entrevista.
    Hoja = 'Tabla N'."""
    hojas = {}
    with zipfile.ZipFile(ruta) as z:
        if "word/document.xml" not in z.namelist():
            return hojas
        root = ET.fromstring(z.read("word/document.xml"))
        tablas = root.findall(f".//{{{NS_W}}}tbl")
        for ti, tbl in enumerate(tablas, start=1):
            filas = []
            for ri, tr in enumerate(tbl.findall(f"{{{NS_W}}}tr")):
                celdas = {}
                for ci, tc in enumerate(tr.findall(f"{{{NS_W}}}tc")):
                    texto = _texto_celda_docx(tc)
                    if texto:
                        celdas[ci] = texto
                if celdas:
                    filas.append((ri, celdas))
            if filas:
                hojas[f"Tabla {ti}"] = filas
    return hojas


def leer_docx_parrafos(ruta):
    """Párrafos de texto del DOCX que NO están dentro de tablas (caso
    narrativo: un documento de transcripción, no una planilla)."""
    out = []
    with zipfile.ZipFile(ruta) as z:
        if "word/document.xml" not in z.namelist():
            return out
        root = ET.fromstring(z.read("word/document.xml"))
        parent = {}
        for el in root.iter():
            for ch in el:
                parent[ch] = el
        for p in root.iter(f"{{{NS_W}}}p"):
            cur = parent.get(p)
            en_tabla = False
            while cur is not None:
                if cur.tag == f"{{{NS_W}}}tbl":
                    en_tabla = True
                    break
                cur = parent.get(cur)
            if en_tabla:
                continue
            texto = handle_ws(" ".join(t.text or "" for t in p.iter(f"{{{NS_W}}}t")))
            if texto:
                out.append(texto)
    return out


def _seleccionar_hoja(hojas, mapeo):
    """Selecciona la hoja (XLSX) o tabla (DOCX) según el mapeo o la de más filas."""
    hoja_nombre = None
    hoja_sel = mapeo.get("hoja") if mapeo else None
    if hoja_sel:
        if str(hoja_sel).isdigit():
            idx = int(hoja_sel) - 1
            if 0 <= idx < len(hojas):
                hoja_nombre = list(hojas)[idx]
        elif hoja_sel in hojas:
            hoja_nombre = hoja_sel
    if hoja_nombre is None:
        hoja_nombre = max(hojas, key=lambda h: len(hojas[h]))
    return hoja_nombre


def _docx_narrativo(docx_path, out_dir, manifesto_path):
    """DOCX sin tabla-planilla: vuelca el texto completo a un TXT."""
    parrafos = leer_docx_parrafos(docx_path)
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    if not parrafos:
        raise SystemExit("Sin párrafos extraíbles en el DOCX.")
    stem = re.sub(r"\.(?:docx?|pdf|pptx?|txt)$", "", Path(docx_path).name, flags=re.I).strip()
    if not stem:
        stem = Path(docx_path).stem
    txt_name = f"{stem}.txt"
    with open(os.path.join(out_dir, txt_name), "w", encoding="utf-8") as f:
        for p in parrafos:
            f.write(f"{p}\n")
    print(f"  {txt_name}: {len(parrafos)} párrafo(s) (DOCX narrativo, sin planilla)")
    adv = ("DOCX narrativo: sin tabla-planilla de columnas; se volcó el texto completo "
           "a TXT. Si era una transcripción multi-entrevista, declarar "
           "col_archivo/col_hablante/col_texto o separar por documento.")
    manifesto = {
        "archivo_origen": os.path.basename(docx_path),
        "formato": "docx_narrativo",
        "n_parrafos": len(parrafos),
        "entrevistas": [{"archivo_txt": txt_name, "n_parrafos": len(parrafos)}],
        "advertencias": [adv],
    }
    if manifesto_path:
        with open(manifesto_path, "w", encoding="utf-8") as f:
            json.dump(manifesto, f, ensure_ascii=False, indent=2)
        print(f"Manifiesto guardado en: {manifesto_path}")
    return manifesto


def col_por_letra(letra):
    col = 0
    for ch in letra.upper():
        col = col * 26 + (ord(ch) - ord("A") + 1)
    return col - 1


def resolver_columnas(filas, mapeo):
    """Devuelve (idx_archivo, idx_hablante, idx_texto, idx_perfil, idx_fuente, header_fila).
    Con letras: header = fila 0. Con nombres: busca la fila cabecera que los contiene."""
    keys = ("col_archivo", "col_hablante", "col_texto")
    usan_letras = (
        mapeo is not None and
        all(isinstance(mapeo.get(k), str) and re.fullmatch(r"[A-Za-z]+", mapeo[k])
            for k in keys)
    )

    if usan_letras:
        def idx(k):
            return col_por_letra(mapeo.get(k, "A"))
        return (idx("col_archivo"), idx("col_hablante"), idx("col_texto"),
                idx("col_perfil") if mapeo.get("col_perfil") else None,
                idx("col_fuente") if mapeo.get("col_fuente") else None, 0)

    # Por nombre de cabecera: buscar la primera fila que contenga 2+ nombres objetivo.
    metas = {
        "col_archivo": ["nombre del archivo", "archivo"],
        "col_hablante": ["persona quien habla", "quien habla", "hablante"],
        "col_texto": ["texto", "texto de la transcripcion", "transcripcion"],
        "col_perfil": ["perfil"],
        "col_fuente": ["fuente"],
    }
    header_idx = None
    pos = {}
    for r_idx, celdas in filas:
        norm = {c: re.sub(r"[^a-z0-9 ]", "", v.lower()) for c, v in celdas.items()}
        matched = 0
        for c, v in norm.items():
            for key, tokens in metas.items():
                if key not in pos and any(t in v for t in tokens):
                    pos[key] = c
                    matched += 1
        if matched >= 2:
            header_idx = r_idx
            for k in ("col_archivo", "col_hablante", "col_texto"):
                if k not in pos:
                    pos[k] = None
            break
    if header_idx is None:
        raise SystemExit("No se pudo localizar la fila de cabecera. Usa --mapeo con letras o nombres exactos.")
    return (pos["col_archivo"], pos["col_hablante"], pos["col_texto"],
            pos.get("col_perfil"), pos.get("col_fuente"), header_idx)


RE_INTERROGATIVO = re.compile(
    r"(?:^|\s)(?:qué|que|cómo|como|cuándo|cuan?do|dónde|donde|por qué|porque|porqué"
    r"|cuánto|cuan?to|cuál|cual|quién|quien|cúal|cuáles|cuàl|cuàles)\b|"
    r"(\?|¿)|(?:cuéntame|cuentame|platíca|platica|explícame|explicame|me podrías|"
    r"me podrias|me puede decir|dígame|digame|a ver|o sea que)", re.I)


def inferir_roles(turnos_por_label):
    """Heurística de rol: el hablante con mas preguntas/ratio y turnos cortos
    es el 'entrevistador'. Nunca se asume persona_N = rol."""
    labels = list(turnos_por_label)
    if not labels:
        return {}
    datos = {}
    for lab, textos in turnos_por_label.items():
        n_preg = sum(1 for t in textos if RE_INTERROGATIVO.search(t))
        palabras = [len(t.split()) for t in textos]
        media = (sum(palabras) / len(palabras)) if palabras else 0
        ratio = n_preg / max(len(textos), 1)
        score = ratio + (0.6 if n_preg >= 2 else 0) + (0.4 if media < 16 else 0)
        datos[lab] = {"n": len(textos), "n_preguntas": n_preg, "media_palabras": media,
                      "score": score}
    el = max(labels, key=lambda l: datos[l]["score"])
    es_entrevistador = datos[el]["n_preguntas"] >= 1 and datos[el]["score"] > 0 or (
        len(labels) == 1 and datos[el]["n_preguntas"] >= 1)
    roles = {}
    entrevistados = []
    for lab in labels:
        if lab == el and (es_entrevistador or datos[lab]["n_preguntas"] >= 1):
            roles[lab] = "entrevistador"
        else:
            entrevistados.append(lab)
    for i, lab in enumerate(sorted(entrevistados, key=lambda l: datos[l]["n"], reverse=True), start=1):
        roles[lab] = f"entrevistado_{i}"
    return roles


def normalizar(input_path, out_dir, mapeo=None, manifesto_path=None):
    ext = Path(input_path).suffix.lower()
    if ext == ".xlsx":
        hojas = leer_xlsx(input_path)
        if not hojas:
            raise SystemExit("Sin hojas con datos en el XLSX.")
        hoja_nombre = _seleccionar_hoja(hojas, mapeo)
        filas = hojas[hoja_nombre]
    elif ext == ".docx":
        hojas = leer_docx(input_path)
        filas = None
        hoja_nombre = None
        for nombre, filas_tabla in hojas.items():
            try:
                resolver_columnas(filas_tabla, mapeo or {})
            except SystemExit:
                continue
            filas = filas_tabla
            hoja_nombre = nombre
            break
        if filas is None:
            return _docx_narrativo(input_path, out_dir, manifesto_path)
    else:
        raise SystemExit(f"Formato no soportado para transcripciones: {ext} "
                         f"(usar .xlsx o .docx)")

    (i_arch, i_habl, i_txt, i_perf, i_fuente, header_idx) = resolver_columnas(filas, mapeo or {})

    if i_arch is None or i_habl is None or i_txt is None:
        raise SystemExit("Mapeo incompleto: faltan columnas de archivo, hablante o texto.")

    # Agrupar turnos por archivo (col A). Filas sin archivo heredan el anterior.
    grupos = defaultdict(list)
    continua = []
    for r_idx, celdas in filas:
        if r_idx <= header_idx:
            continue
        arch = celdas.get(i_arch)
        if not arch:
            if grupos:
                grupos[list(grupos)[-1]].append((i_habl, i_txt, r_idx, celdas))
            else:
                continua.append((i_habl, i_txt, r_idx, celdas))
            continue
        grupos[arch].append((i_habl, i_txt, r_idx, celdas))

    Path(out_dir).mkdir(parents=True, exist_ok=True)
    if continua:
        grupos.setdefault("transcripcion_sin_archivo.txt", []).extend(continua)

    entrevistas = []
    n_turnos = 0
    for arch in sorted(grupos):
        turnos = grupos[arch]
        n_turnos += len(turnos)
        mapa_roles = defaultdict(list)
        for i_h, i_t, r_idx, celdas in turnos:
            hab = celdas.get(i_h) or "[sin hablante]"
            texto = celdas.get(i_t, "")
            if not texto:
                continue
            mapa_roles[hab].append(texto)
        roles = inferir_roles(mapa_roles)

        # Nombre del archivo TXT: quitar la extension del audio/original.
        stem = re.sub(r"\.(?:m4a|mp3|wav|ogg|amr|mp4|aac|flac|wma|docx?|xlsx?|txt)$", "",
                      arch.strip(), flags=re.I).strip()
        if not stem:
            stem = arch.strip()
        txt_name = f"{stem}.txt"
        with open(os.path.join(out_dir, txt_name), "w", encoding="utf-8") as f:
            for i_h, i_t, r_idx, celdas in turnos:
                hab = celdas.get(i_h) or "[sin hablante]"
                texto = celdas.get(i_t, "")
                if not texto:
                    continue
                rol = roles.get(hab, "entrevistado")
                f.write(f"[{rol}] {texto}\n")
        entrevistas.append({
            "archivo_origen": arch.strip(),
            "archivo_txt": txt_name,
            "n_turnos": len(turnos),
            "n_hablantes": len(mapa_roles),
            "roles_por_etiqueta": roles,
            "n_entrevistados": sum(1 for r in roles.values() if r.startswith("entrevistado")),
        })
        print(f"  {txt_name}: {len(turnos)} turnos, {len(mapa_roles)} hablante(s), "
              f"roles={roles}")

    adv = ("rol_hablante inferido por heurística lingüística, no por etiqueta del "
           "transcriptor (persona_N); cada entrevistado_N cuenta como población "
           "distinta para la regla 12 / blindaje transpoblacional")
    manifesto = {
        "archivo_origen": os.path.basename(input_path),
        "hoja": hoja_nombre,
        "mapeo_transcripcion": mapeo or {},
        "formato_linea": "[rol_hablante] texto",
        "n_entrevistas": len(entrevistas),
        "n_turnos": n_turnos,
        "entrevistas": entrevistas,
        "advertencias": [adv],
    }
    if manifesto_path:
        with open(manifesto_path, "w", encoding="utf-8") as f:
            json.dump(manifesto, f, ensure_ascii=False, indent=2)
        print(f"Manifiesto guardado en: {manifesto_path}")
    print(f"Total: {len(entrevistas)} entrevistas, {n_turnos} turnos en {out_dir}")
    return manifesto


def main():
    # Robustez de consola: reconfigure stdout/stderr para no crashear al
    # imprimir no-ASCII en consolas cp1252 (UnicodeEncodeError con \u0301 etc.).
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(
        description="Normaliza transcripciones (XLSX/DOCX planilla o DOCX narrativo) a TXT por entrevista.")
    ap.add_argument("input", help="Archivo de transcripciones: XLSX o DOCX")
    ap.add_argument("-o", "--output", required=True, help="Directorio de salida para los TXT")
    ap.add_argument("--manifesto", help="JSON de manifiesto (roles, conteos)")
    ap.add_argument("--mapeo", help="JSON con mapeo_transcripcion (letras o nombres de cabecera)")
    args = ap.parse_args()
    mapeo = None
    if args.mapeo:
        with open(args.mapeo, encoding="utf-8-sig") as f:
            mapeo = json.load(f)
    normalizar(args.input, args.output, mapeo=mapeo, manifesto_path=args.manifesto)


if __name__ == "__main__":
    main()
