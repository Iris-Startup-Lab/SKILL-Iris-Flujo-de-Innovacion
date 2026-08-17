"""
Verificador determinista de citas contra el corpus cualitativo.

Audita cada cita declarada en fase2_output.json y fase3_output.json contra
los archivos TXT del corpus. Busca las citas literalmente (normalizando
mayusculas, acentos y espacios) y, si no se encuentran exactas, aplica
fuzzy matching para clasificarlas.

Salidas por cita:
    ENCONTRADA             - La cita existe literalmente en el corpus.
    UBICACION_INCORRECTA   - La cita existe, pero NO en el archivo/ubicacion
                             declarado; se corrige la ubicacion (no bloquea).
    APROXIMADA             - La cita no es literal pero coincide con fuzzy
                             match >= umbral; requiere justificacion del analista.
    NO_ENCONTRADA          - La cita no aparece en ninguna parte del corpus.
                             UNICA salida que bloquea la escala de la senal.

Ademas verifica claims de ausencia (tipo "nadie menciona X" en senales y
cruces): si el termino declarado ausente SI aparece en el corpus, el claim se
marca CONTRADICCION y bloquea la escala hasta corregirse o descartarse. Si el
termino no aparece, se marca AUSENCIA_CONFIRMADA (informativo). Con --absentes
se fuerza la comprobacion de terminos especificos.

Uso:
    python verificar_citas.py fase2_output.json [fase3_output.json] \
        --corpus "carpeta_de_transcripciones" [--umbral 0.8] \
        [--absentes "comision,comisiones,costo"]
"""
import sys
import os
import re
import json
import glob
import difflib
import unicodedata


UMBRAL_DEFAULT = 0.8


def normalizar(texto):
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = texto.lower()
    texto = re.sub(r"\s+", " ", texto)
    return texto.strip()


def extraer_archivos_corpus(ruta):
    if os.path.isdir(ruta):
        return sorted(glob.glob(os.path.join(ruta, "*.txt")))
    if os.path.isfile(ruta):
        return [ruta]
    return []


def cargar_corpus_normalizado(archivos):
    corpus = {}
    for archivo in archivos:
        nombre = os.path.basename(archivo)
        with open(archivo, encoding="utf-8", errors="replace") as f:
            raw = f.read()
        corpus[nombre] = raw
        corpus[normalizar(nombre)] = raw
    return corpus


def extraer_citas_de_json(datos):
    """Extrae citas candidatas del JSON de fase 2/3."""
    citas = []
    bloques = datos.get("datos", {}).get("bloques", [])

    def recorrer(obj, senal_id):
        if isinstance(obj, dict):
            if "dato" in obj and isinstance(obj["dato"], str):
                dato = obj["dato"]
                for m in re.findall(r"['\"]([^'\"]{8,})['\"]", dato):
                    citas.append({
                        "senal_id": senal_id,
                        "cita": m,
                        "contexto": obj.get("contexto", ""),
                    })
            if "contexto" in obj and isinstance(obj["contexto"], str):
                for m in re.findall(r"['\"]([^'\"]{8,})['\"]", obj["contexto"]):
                    citas.append({
                        "senal_id": senal_id,
                        "cita": m,
                        "contexto": obj["contexto"],
                    })
            for v in obj.values():
                recorrer(v, senal_id)
        elif isinstance(obj, list):
            for item in obj:
                recorrer(item, senal_id)

    for bloque in bloques:
        for key in ("senales", "cruces"):
            for item in bloque.get(key, []):
                recorrer(item, item.get("id", "sin-id"))

    # Bitacora de ventanas (fase 2): hallazgos B1-B5 pueden citar texto
    for ventana in datos.get("datos", {}).get("bitacora_ventanas", []):
        hallazgos = ventana.get("hallazgos", {})
        for bloque_h, texto in hallazgos.items():
            if not isinstance(texto, str):
                continue
            for m in re.findall(r"['\"]([^'\"]{8,})['\"]", texto):
                citas.append({
                    "senal_id": ventana.get("ventana_id", "bitacora"),
                    "cita": m,
                    "contexto": f"{ventana.get('ventana_id')} {bloque_h}",
                })
    return citas


def archivo_declarado(contexto):
    """Intenta inferir el archivo declarado a partir del contexto o la cita."""
    m = re.search(r"([\w\-.]+\.txt)", contexto)
    if m:
        return m.group(1)
    return None


def buscar_cita(cita, corpus_normalizado, umbral):
    """Devuelve (estado, archivo_hallazgo, score)."""
    cita_norm = normalizar(cita)
    if not cita_norm:
        return ("NO_ENCONTRADA", None, 0.0)

    mejor = None
    mejor_score = 0.0
    mejor_nombre = None

    for nombre, raw in corpus_normalizado.items():
        raw_norm = normalizar(raw)
        if cita_norm in raw_norm:
            return ("ENCONTRADA", nombre, 1.0)
        # Fuzzy sobre ventanas de tamano del 150% de la cita
        largo = len(cita_norm)
        paso = max(largo, 40)
        for i in range(0, len(raw_norm), paso):
            ventana = raw_norm[i:i + largo + 20]
            score = difflib.SequenceMatcher(None, cita_norm, ventana).ratio()
            if score > mejor_score:
                mejor_score = score
                mejor = ventana
                mejor_nombre = nombre

    if mejor_score >= umbral:
        return ("APROXIMADA", mejor_nombre, mejor_score)
    return ("NO_ENCONTRADA", mejor_nombre, mejor_score)


RE_AUSENCIA = re.compile(
    r"(?:"
    r"(nadie|ningún|ninguna|nunca)\s+(?:entrevistado\w*\s+|comerciante\w*\s+|usuario\w*\s+)?"
    r"(mencion\w*|habla\w*|nombra\w*|toca\w*)\s+(?:de\s+|sobre\s+)?(?:la\s+|el\s+|los\s+|las\s+)?"
    r"|"
    r"no\s+(?:se\s+)?(mencion\w*|aparece\w*|habla\w*)\s+(?:de\s+|sobre\s+)?(?:la\s+|el\s+|los\s+|las\s+)?"
    r")([^.,;()\"']{2,120})",
    re.I,
)


def _terminos_de_frase(frase):
    """Extrae terminos candidatos (sustantivos de topico) de una frase."""
    terminos = []
    citados = re.findall(r"['\"]([^'\"]{2,40})['\"]", frase)
    terminos.extend(c.strip() for c in citados)
    for pre in ("entrevistado ", "entrevistados ", "ninguno de los ", "el ", "la ", "los ",
                "las ", "un ", "una "):
        if frase.lower().startswith(pre):
            frase = frase[len(pre):]
            break
    fragmento = re.split(
        r"\s+(?:o\s+(?:el\s+|la\s+)?|,|y\s+|como\s+(?:la\s+|el\s+|una\s+)?|sobre\s+)",
        frase, maxsplit=1)[0].strip()
    palabras = [p for p in re.split(r"\s+", fragmento)
                if p and len(p) >= 4 and not re.search(r"[.,;:()\"'!?]", p)]
    if palabras:
        terminos.append(" ".join(palabras[:2]))
    return [t for t in dict.fromkeys(terminos) if len(normalizar(t)) >= 4]


def extraer_claims_ausencia(datos):
    """Extrae claims de ausencia ('nadie menciona X') de senales y cruces."""
    claims = []

    def recorrer(obj, senal_id):
        if isinstance(obj, dict):
            for campo in ("dato", "contexto", "expectativa_rota", "conclusion", "sintesis"):
                texto = obj.get(campo)
                if isinstance(texto, str):
                    for m in RE_AUSENCIA.finditer(texto):
                        for termino in _terminos_de_frase(m.group(4)):
                            claims.append({
                                "senal_id": senal_id,
                                "termino": termino,
                                "claim": m.group(0),
                                "contexto": texto[:160],
                            })
            for k, v in obj.items():
                recorrer(v, senal_id)
        elif isinstance(obj, list):
            for v in obj:
                recorrer(v, senal_id)

    for bloque in datos.get("datos", {}).get("bloques", []):
        for key in ("senales", "cruces"):
            for item in bloque.get(key, []):
                recorrer(item, item.get("id", "sin-id"))
    return claims


def verificar_ausencias(archivos_json, corpus_normalizado, terminos_absentes=None):
    claims = []
    if terminos_absentes:
        for t in terminos_absentes:
            if t.strip():
                claims.append({
                    "senal_id": "[--absentes]",
                    "termino": t.strip(),
                    "claim": f"claim de ausencia forzado: {t.strip()}",
                    "contexto": "",
                })
    for json_path in archivos_json:
        with open(json_path, encoding="utf-8") as f:
            datos = json.load(f)
        claims.extend(extraer_claims_ausencia(datos))

    corpus_joined = " ".join(corpus_normalizado.values())
    corpus_norm = normalizar(corpus_joined)
    resultados = []
    vistos = set()
    for c in claims:
        t_norm = normalizar(c["termino"])
        if not t_norm or t_norm in vistos:
            continue
        vistos.add(t_norm)
        presente = t_norm in corpus_norm
        resultados.append({
            "senal_id": c["senal_id"],
            "cita": c["claim"],
            "archivo_declarado": "[claim de ausencia]",
            "estado": "CONTRADICCION" if presente else "AUSENCIA_CONFIRMADA",
            "archivo_hallazgo": "[corpus]" if presente else "[ninguno]",
            "score": 1.0,
            "contexto": c["contexto"],
        })
    return resultados


def verificar(archivos_json, ruta_corpus, umbral, terminos_absentes=None):
    archivos_txt = extraer_archivos_corpus(ruta_corpus)
    if not archivos_txt:
        return [{"error": f"No se encontraron .txt en {ruta_corpus}"}]

    corpus = cargar_corpus_normalizado(archivos_txt)
    resultados = []
    n_no_encontradas = 0

    for json_path in archivos_json:
        with open(json_path, encoding="utf-8") as f:
            datos = json.load(f)
        citas = extraer_citas_de_json(datos)

        for item in citas:
            archivo_decl = archivo_declarado(item["contexto"])
            estado, archivo_hallazgo, score = buscar_cita(item["cita"], corpus, umbral)

            if estado == "ENCONTRADA" and archivo_decl:
                # La cita se encontro, pero hay que verificar si es en el archivo declarado
                nombre_normalizado = normalizar(archivo_decl)
                if archivo_hallazgo not in (archivo_decl, nombre_normalizado):
                    estado = "UBICACION_INCORRECTA"

            if estado == "NO_ENCONTRADA":
                n_no_encontradas += 1

            resultados.append({
                "senal_id": item["senal_id"],
                "cita": item["cita"],
                "archivo_declarado": archivo_decl or "[no declarado]",
                "estado": estado,
                "archivo_hallazgo": archivo_hallazgo or "[ninguno]",
                "score": round(score, 3) if estado in ("APROXIMADA", "NO_ENCONTRADA") else 1.0,
                "contexto": item["contexto"],
            })

    resultados.extend(verificar_ausencias(archivos_json, corpus, terminos_absentes))
    return resultados, n_no_encontradas


def main():
    args = sys.argv[1:]
    if not args or "-h" in args or "--help" in args:
        print(__doc__)
        sys.exit(1)

    umbral = UMBRAL_DEFAULT
    ruta_corpus = "."
    archivos_json = []
    terminos_absentes = []

    i = 0
    while i < len(args):
        if args[i] == "--corpus" and i + 1 < len(args):
            ruta_corpus = args[i + 1]
            i += 2
        elif args[i] == "--umbral" and i + 1 < len(args):
            umbral = float(args[i + 1])
            i += 2
        elif args[i] == "--absentes" and i + 1 < len(args):
            terminos_absentes = [t.strip() for t in args[i + 1].split(",") if t.strip()]
            i += 2
        else:
            archivos_json.append(args[i])
            i += 1

    resultados, n_no_encontradas = verificar(
        archivos_json, ruta_corpus, umbral, terminos_absentes)

    for r in resultados:
        if "error" in r:
            print(f"[ERROR] {r['error']}")
            continue
        print(f"[{r['estado']}] {r['senal_id']} :: {r['cita'][:80]}... "
              f"(declarado: {r['archivo_declarado']} | hallado: {r['archivo_hallazgo']} | score: {r['score']})")

    n_encontradas = sum(1 for r in resultados if r.get("estado") == "ENCONTRADA")
    n_aprox = sum(1 for r in resultados if r.get("estado") == "APROXIMADA")
    n_ubic = sum(1 for r in resultados if r.get("estado") == "UBICACION_INCORRECTA")
    n_contradiccion = sum(1 for r in resultados if r.get("estado") == "CONTRADICCION")
    n_ausencia_ok = sum(1 for r in resultados if r.get("estado") == "AUSENCIA_CONFIRMADA")

    print(f"\nResumen: {n_encontradas} ENCONTRADA(s), {n_aprox} APROXIMADA(s), "
          f"{n_ubic} UBICACION_INCORRECTA(s), {n_no_encontradas} NO_ENCONTRADA(s), "
          f"{n_contradiccion} CONTRADICCION(es), {n_ausencia_ok} AUSENCIA_CONFIRMADA(s).")

    if n_no_encontradas:
        print("Las senales con citas NO_ENCONTRADA no escalan a Fase 4 hasta corregirse.")
        sys.exit(1)
    if n_contradiccion:
        print("Claims de ausencia CONTRADICCION: el termino declarado ausente SI aparece "
              "en el corpus. Corregir o descartar la senal antes de escalar.")
        sys.exit(1)
    if n_aprox:
        print("Citas APROXIMADAS: el analista debe justificar la desviacion o corregir la cita.")
        sys.exit(2)
    print("Verificacion de citas completada.")
    sys.exit(0)


if __name__ == "__main__":
    main()
