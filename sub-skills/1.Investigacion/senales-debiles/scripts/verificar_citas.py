"""
Verificador determinista de citas contra el corpus cualitativo.

Audita cada cita declarada en fase2_output.json y fase3_output.json contra
los archivos TXT del corpus. Busca las citas literalmente (normalizando
mayusculas, acentos y espacios) y, si no se encuentran exactas, aplica
fuzzy matching para clasificarlas.

Rendimiento (v2): el corpus se normaliza UNA sola vez al inicio y se guarda
por archivo y por combinacion de archivos; cada cita busca primero en el
archivo declarado (si se conoce) y hace corto-circuito al encontrar una
coincidencia suficiente, sin recorrer todo el corpus para cada cita.

Salidas por cita:
    ENCONTRADA             - La cita existe literalmente en el corpus.
    ENCONTRADA_TRUNCADA    - La cita existe excepto por la elipsis (cita del
                             analista truncada con "..." o el fragmento); no
                             bloquea, avisa que la cita está en el corpus.
                             Solo se emite sin --exacto.
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
        [--absentes "comunidad,vecinos"] [--exacto]

--exacto desactiva la tolerancia a truncamiento con "..." y exige que cada
cita coincida literalmente con el corpus (busqueda estricta).
"""
import sys
import os
import re
import json
import glob
import time
import difflib
import unicodedata


UMBRAL_DEFAULT = 0.8
PASO_PROGRESO = 25  # cada N citas se imprime una linea de progreso


# Citas textuales entre comillas emparejadas. Se soportan:
#   - comillas dobles rectas: "..."
#   - comillas dobles tipograficas: "..."
#   - comillas simples tipograficas: '...'
# Se excluyen las comillas simples rectas (') porque en espanol suelen ser
# apostrofos o contracciones, no delimitadores de citas; de lo contrario el
# regex captura texto entre un cierre y una apertura de comilla simple.
RE_CITA = re.compile(
    r'"([^"]{8,})"'
    r'|\u201c([^\u201d]{8,})\u201d'
    r'|\u2018([^\u2019]{8,})\u2019'
)

# Citas inline con ancla de ubicación (contrato de Fase 2/3: ver reglas de
# fase-2-eda-cualitativo.md y fase-3-cruce.md). Dos formas soportadas:
#   A) ubicación antes de la cita:  E4/L256-292: 'al rato me asaltan'
#                                  | L92: "texto" | [min 8]: 'texto'
#   B) ubicación después de la cita: 'texto' (E4/L256) | 'texto' [L92] | 'texto' [min 8]
# La comilla simple recta ('...') solo se trata como delimitador cuando va
# precedida (forma A) o seguida (forma B) por un ancla de ubicación, para no
# confundirse con apóstrofos del español.
RE_CITA_INLINE_A = re.compile(
    r"(?P<loc>"
    r"(?:E\s*(?P<e>\d+)\s*[/:]\s*L?\s*(?P<l>\d+(?:\s*[-–]\s*\d+)?)"
    r"|L\s*(?P<ls>\d+(?:\s*[-–]\s*\d+)?)"
    r"|\[?min\s+(?P<min>\d+)\]?))"
    r"\s*[:;,)]?\s*"
    r"(?P<q>[\"'\u2018\u2019\u201c\u201d])(?P<txt>.+?)(?P=q)",
    re.DOTALL | re.IGNORECASE,
)

RE_CITA_INLINE_B = re.compile(
    r"(?P<q>[\"'\u2018\u2019\u201c\u201d])(?P<txt>.+?)(?P=q)"
    r"\s*(?P<locb>"
    r"(?:[\[(]\s*(?:min\s+)?L?\s*(?P<b1>\d+(?:\s*[-–]\s*\d+)?)\s*[)\]]"
    r"|\(\s*E\s*(?P<b2>\d+)\s*/\s*L?\s*(?P<b3>\d+(?:\s*[-–]\s*\d+)?)\s*\)))",
    re.DOTALL | re.IGNORECASE,
)


def _texto_cita(match_or_groups):
    """Extrae el texto citado de un match o de la tupla devuelta por findall."""
    if hasattr(match_or_groups, "group"):
        for i in range(1, RE_CITA.groups + 1):
            txt = match_or_groups.group(i)
            if txt is not None:
                return txt
        return None
    for txt in match_or_groups:
        if txt:
            return txt
    return None


def extraer_citas_inline(texto):
    """Extrae citas con ancla de ubicación de un texto en prosa (contrato de
    Fase 2/3). Devuelve lista de dicts {cita, entrevista, linea, ubicacion}.
    Rechaza capturas donde el texto citado contiene el mismo carácter
    delimitador (cita anidada / comilla sin cerrar) — artefacto tipo
    'ganancias'. Sí menciona 'generar historial crediticio' (L120)."""
    citas = []
    for m in RE_CITA_INLINE_A.finditer(texto):
        txt = m.group("txt")
        if m.group("q") in txt:
            continue
        entrevista = int(m.group("e")) if m.group("e") else None
        linea = m.group("l") or m.group("ls")
        citas.append({
            "cita": txt.strip(),
            "entrevista": entrevista,
            "linea": linea,
            "ubicacion": m.group("loc").strip(),
        })
    for m in RE_CITA_INLINE_B.finditer(texto):
        txt = m.group("txt")
        if m.group("q") in txt:
            continue
        entrevista = int(m.group("b2")) if m.group("b2") else None
        linea = m.group("b1") or m.group("b3")
        citas.append({
            "cita": txt.strip(),
            "entrevista": entrevista,
            "linea": linea,
            "ubicacion": m.group("locb").strip(),
        })
    return citas


RE_CITA_SIMPLE_SIN_ANCLA = re.compile(r"'([^']{8,})'")


def _detectar_sin_ancla(texto):
    """Citas entre comillas simples rectas SIN ancla de ubicación cercana.

    RE_CITA excluye las simples rectas y el parser inline exige ancla: estas
    citas quedarían invisibles a la verificación. Se extraen igual (verificación
    global verbatim) pero se marcan como SIN_ANCLA para que el analista sepa
    que no tienen ubicación declarada (contrato de Fase 2/3)."""
    out = []
    for m in RE_CITA_SIMPLE_SIN_ANCLA.finditer(texto):
        span = m.group(1).strip()
        if len(span) < 8 or (len(span) < 12 and " " not in span):
            continue
        if span.lstrip().startswith((".", ",", ":", ";")):
            continue
        if re.search(r"\bL?\s*\d+\s*:|min\s*\d+", span):
            continue
        antes = texto[max(0, m.start() - 25):m.start()]
        despues = texto[m.end():m.end() + 25]
        if re.search(r"[Ee]\s*\d+\s*[/:]\s*L\s*\d+|L\s*\d+|\[?min\s+\d+\]?",
                     antes + " | " + despues):
            continue  # tiene ancla cercana: ya la maneja el parser inline
        out.append(span)
    return out


def normalizar(texto):
    """Normaliza mayusculas, acentos, diacriticos, espacios multiples y
    comillas tipograficas curvas (' ' ' ') a rectas."""
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = "".join({"\u201c": '"', "\u201d": '"',
                     "\u2018": "'", "\u2019": "'"}.get(c, c) for c in texto)
    texto = texto.lower()
    texto = re.sub(r"\s+", " ", texto)
    return texto.strip()


# --- Validación de paráfrasis anclada (contrato de Fase 2/3) ---
# Cuando una cita NO se encuentra verbatim, el verificador intenta validarla
# como paráfrasis fiel contra la ventana DECLARADA (archivo + líneas). La
# cobertura léxica es un pre-filtro determinista: separa "obvio bien" de
# "obvio mal"; el tramo intermedio requiere confirmación (humana o LLM-judge).
# Nota: la cobertura NO prueba la fidelidad semántica (una paráfrasis fiel
# puede tener cobertura baja y una vaga cobertura alta); por eso las bandas
# media/baja derivan a un lector, no se auto-aprueban.
PARAFRASIS_MARGEN_LINEAS = 2
MIN_COV_PARAFRASIS_OK = 0.6
MIN_COV_PARAFRASIS_APROX = 0.35

_STOPW_ES = set("""de la el en y a los las un una que para con por no si se su al del lo
como pero mas ya eso esa ese esto esta este muy bien nada todo toda me te mi mis tu tus nos
os les sus el ella ellos ellas uno unas unos tan cual cuales cuanto cuando donde mientras
mediante durante entre sobre tras hacia contra desde hasta segun tambien porque por que""".split())


def _tokens_contenido(texto):
    """Tokens de contenido (sin stopwords, len>=4) en orden, sin duplicados."""
    out = []
    vistos = set()
    for w in re.findall(r"[a-z0-9]+", normalizar(texto)):
        if w in _STOPW_ES or len(w) < 4:
            continue
        if w.isdigit() and len(w) < 3:
            continue
        if w not in vistos:
            vistos.add(w)
            out.append(w)
    return out


def _rango_lineas(linea_str):
    m = re.search(r"(\d+)\s*[-–]\s*(\d+)", linea_str or "")
    if m:
        return int(m.group(1)), int(m.group(2))
    m = re.search(r"(\d+)", linea_str or "")
    if m:
        return int(m.group(1)), int(m.group(1))
    return None


def _ventana_de_corpus(corpus_archivo, linea_str, margen=PARAFRASIS_MARGEN_LINEAS):
    """Ventana (líneas declaradas ± margen) del archivo del corpus, o None."""
    rng = _rango_lineas(linea_str)
    if not rng:
        return None
    lineas = (corpus_archivo or {}).get("crudo", "").splitlines()
    if not lineas:
        return None
    ini, fin = rng
    ini = max(1, ini - margen)
    fin = min(len(lineas), fin + margen)
    return "\n".join(lineas[ini - 1:fin])


def _cobertura(cita, ventana):
    """Cobertura de tokens de contenido de la cita en la ventana.
    Match por CONTENCION de palabra (tok == w, o una es prefijo de la otra),
    NO por prefijo de 5 chars: este ultimo produce falsos positivos de raiz
    ('control' vs 'contraluz'). El coste es algun falso negativo de morfologia
    ('tengo' vs 'tengamos') que cae a la banda de confirmacion, nunca a una
    auto-aprobacion."""

    def _match(tok, w):
        return tok == w or tok.startswith(w) or w.startswith(tok)

    p = _tokens_contenido(cita)
    if not p:
        return 0.0
    w = _tokens_contenido(ventana)
    coinciden = sum(1 for tok in p if any(_match(tok, ww) for ww in w))
    return coinciden / len(p)


def _numeros(texto):
    return set(re.findall(r"\d+(?:[.,]\d+)?", texto))


def evaluar_parafrasis(cita, ventana):
    """Veredicto determinista de paráfrasis anclada.
    Devuelve (estado, score):
      PARAFRASIS_VALIDADA | PARAFRASIS_APROXIMADA | PARAFRASIS_NO_SOPORTADA
    """
    if not ventana:
        return ("PARAFRASIS_NO_SOPORTADA", 0.0)
    cov = _cobertura(cita, ventana)
    faltantes = sorted(_numeros(cita) - _numeros(ventana))
    if cov >= MIN_COV_PARAFRASIS_OK and not faltantes:
        return ("PARAFRASIS_VALIDADA", cov)
    if cov >= MIN_COV_PARAFRASIS_APROX and not faltantes:
        return ("PARAFRASIS_APROXIMADA", cov)
    return ("PARAFRASIS_NO_SOPORTADA", cov)


def extraer_archivos_corpus(ruta):
    if os.path.isdir(ruta):
        return sorted(glob.glob(os.path.join(ruta, "*.txt")))
    if os.path.isfile(ruta):
        return [ruta]
    return []


def cargar_corpus_normalizado(archivos):
    """Normaliza cada archivo UNA vez. Devuelve:
        corpus[txt]      -> texto crudo (para busqueda exacta de fragmentos)
        corpus_norm[txt] -> texto normalizado (para busqueda normalizada)
    """
    corpus = {}
    for archivo in archivos:
        nombre = os.path.basename(archivo)
        with open(archivo, encoding="utf-8-sig", errors="replace") as f:
            raw = f.read()
        corpus[nombre] = {
            "crudo": raw,
            "norm": normalizar(raw),
        }
    return corpus


def extraer_citas_de_json(datos):
    """Extrae citas candidatas del JSON de fase 2/3."""
    citas = []
    bloques = datos.get("datos", {}).get("bloques", [])
    vistos = set()

    def agregar(senal_id, cita, contexto, entrevista=None, linea=None,
                ubicacion="", archivo_ventana=None, sin_ancla=False):
        key = (senal_id, cita)
        if key in vistos:
            return
        vistos.add(key)
        citas.append({
            "senal_id": senal_id,
            "cita": cita,
            "contexto": contexto,
            "entrevista": entrevista,
            "linea": linea,
            "ubicacion": ubicacion,
            "archivo_ventana": archivo_ventana,
            "sin_ancla": sin_ancla,
        })

    def recorrer(obj, senal_id):
        if isinstance(obj, dict):
            if "dato" in obj and isinstance(obj["dato"], str):
                dato = obj["dato"]
                contexto = obj.get("contexto", "")
                for m in RE_CITA.findall(dato):
                    texto = _texto_cita(m)
                    if texto:
                        agregar(senal_id, texto, contexto)
                for inline in extraer_citas_inline(dato):
                    agregar(senal_id, inline["cita"], contexto,
                            inline["entrevista"], inline["linea"], inline["ubicacion"])
                for sp in _detectar_sin_ancla(dato):
                    agregar(senal_id, sp, contexto, sin_ancla=True)
            if "contexto" in obj and isinstance(obj["contexto"], str):
                ctx = obj["contexto"]
                for m in RE_CITA.findall(ctx):
                    texto = _texto_cita(m)
                    if texto:
                        agregar(senal_id, texto, ctx)
            for v in obj.values():
                recorrer(v, senal_id)
        elif isinstance(obj, list):
            for item in obj:
                recorrer(item, senal_id)

    for bloque in bloques:
        for key in ("senales", "cruces"):
            for item in bloque.get(key, []):
                recorrer(item, item.get("id", "sin-id"))

    # Bitacora de ventanas (fase 2): hallazgos B1-B6 pueden citar texto
    for ventana in datos.get("datos", {}).get("bitacora_ventanas", []):
        hallazgos = ventana.get("hallazgos", {})
        ventana_id = ventana.get("ventana_id", "bitacora")
        archivo_ventana = ventana.get("archivo")
        for bloque_h, texto in hallazgos.items():
            if not isinstance(texto, str):
                continue
            for m in RE_CITA.findall(texto):
                texto_cita = _texto_cita(m)
                if texto_cita:
                    agregar(ventana_id, texto_cita, f"{ventana_id} {bloque_h}",
                            archivo_ventana=archivo_ventana)
            for inline in extraer_citas_inline(texto):
                agregar(ventana_id, inline["cita"], f"{ventana_id} {bloque_h}",
                        inline["entrevista"], inline["linea"], inline["ubicacion"],
                        archivo_ventana)
            for sp in _detectar_sin_ancla(texto):
                agregar(ventana_id, sp, f"{ventana_id} {bloque_h}",
                        archivo_ventana=archivo_ventana, sin_ancla=True)
    return citas


def archivo_de_interview(entrevista, corpus):
    """Mapea un ID de entrevista (E4) al archivo .txt del corpus, si existe."""
    if not entrevista:
        return None
    pat = re.compile(rf"entrevista\s*{entrevista}\.txt", re.IGNORECASE)
    for nombre in corpus:
        if pat.search(nombre):
            return nombre
    return None


def archivo_declarado(contexto):
    """Intenta inferir el archivo declarado a partir del contexto o la cita."""
    m = re.search(r"([\w\-.]+\.txt)", contexto)
    if m:
        return m.group(1)
    return None


def _buscar_en_texto(txt_norm, cita_norm):
    """Busqueda de subcadena normalizada en un texto ya normalizado."""
    return cita_norm in txt_norm


def _buscar_fragmentos_truncada(cita_norm, corpus):
    """Busca una cita truncada con elipsis en un texto YA normalizado.

    Elimina los marcadores '...' y comprueba que los fragmentos resultantes
    aparezcan en orden dentro de algun archivo del corpus. Devuelve True si
    todos aparecen.
    """
    fragmentos = [f.strip() for f in re.split(r"(?:\.\.\.|\u2026|\.\s*\.\s*\.)", cita_norm) if f.strip()]
    fragmentos = [f for f in fragmentos if len(f) >= 4]
    if not fragmentos:
        return False
    for nombre, info in corpus.items():
        resto = info["norm"]
        ok = True
        for frag in fragmentos:
            idx = resto.find(frag)
            if idx == -1:
                ok = False
                break
            resto = resto[idx + len(frag):]
        if ok:
            return True
    return False


def buscar_cita(cita, corpus, umbral, exacto=False,
                archivo_declarado=None, nombre_normalizado=None):
    """Devuelve (estado, archivo_hallazgo, score).

    Con exacto=True se exige coincidencia literal; sin elipsis no cambia nada.
    Con exacto=False, una cita con '...' que solo falla por el truncamiento se
    reporta como ENCONTRADA_TRUNCADA (la cita existe en el corpus).
    Mantiene como referencia la ubicacion declarada para detectar
    UBICACION_INCORRECTA.
    """
    cita_norm = normalizar(cita)
    if not cita_norm:
        return ("NO_ENCONTRADA", None, 0.0)

    def _exacto(o_inf):
        return _buscar_en_texto(o_inf["norm"], cita_norm)

    # Bloque 1: busqueda exacta normalizada, primero en el archivo declarado.
    if archivo_declarado and archivo_declarado in corpus:
        info = corpus[archivo_declarado]
        if _exacto(info):
            return ("ENCONTRADA", archivo_declarado, 1.0)
    elif nombre_normalizado and nombre_normalizado in corpus:
        info = corpus[nombre_normalizado]
        if _exacto(info):
            return ("ENCONTRADA", nombre_normalizado, 1.0)

    for nombre, info in corpus.items():
        if archivo_declarado and nombre == archivo_declarado:
            continue  # ya se probo el declarado; no duplicar recorridos
        if _exacto(info):
            return ("ENCONTRADA", nombre, 1.0)

    # Bloque 2: truncamiento con elipsis (mantener orden de aparicion).
    # Reconoce '...', elipsis Unicode '...' y puntos separados '. . .'.
    if not exacto and ("\u2026" in cita_norm or re.search(r"\.\s*\.\s*\.", cita_norm)):
        if _buscar_fragmentos_truncada(cita_norm, corpus):
            return ("ENCONTRADA_TRUNCADA", "[truncada]", 1.0)

    # Bloque 3: fuzzy sobre ventanas, con corto-circuito al alcanzar el umbral.
    # Con --exacto no se rescata nada: se exige coincidencia literal y la cita
    # termina NO_ENCONTRADA (la unica salida que bloquea la escala).
    if not exacto:
        mejor_score = 0.0
        mejor_nombre = None
        mejor_ventana = None
        largo = len(cita_norm)
        paso = max(largo, 40)

        def _fuzzy_sobre(nombre, info):
            nonlocal mejor_score, mejor_nombre, mejor_ventana
            raw_norm = info["norm"]
            for i in range(0, len(raw_norm), paso):
                ventana = raw_norm[i:i + largo + 20]
                score = difflib.SequenceMatcher(None, cita_norm, ventana).ratio()
                if score >= umbral:
                    mejor_score = score
                    mejor_nombre = nombre
                    mejor_ventana = ventana
                    return True  # corto-circuito: suficiente para clasificar
                if score > mejor_score:
                    mejor_score = score
                    mejor_nombre = nombre
                    mejor_ventana = ventana
            return False

        # Primero en el declarado (el mas probable), luego en el resto.
        orden = []
        if archivo_declarado and archivo_declarado in corpus:
            orden.append(archivo_declarado)
        if nombre_normalizado and nombre_normalizado not in orden and nombre_normalizado in corpus:
            orden.append(nombre_normalizado)
        orden += [n for n in corpus if n not in orden]

        for nombre in orden:
            if _fuzzy_sobre(nombre, corpus[nombre]):
                break

        if mejor_score >= umbral:
            return ("APROXIMADA", mejor_nombre, mejor_score)
    return ("NO_ENCONTRADA", None, 0.0)


RE_AUSENCIA = re.compile(
    r"(?:"
    r"(nadie|ningún|ninguna|nunca)\s+(?:entrevistado\w*\s+|usuario\w*\s+|participante\w*\s+)?"
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


def verificar_ausencias(archivos_json, corpus, terminos_absentes=None):
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
        with open(json_path, encoding="utf-8-sig") as f:
            datos = json.load(f)
        claims.extend(extraer_claims_ausencia(datos))

    corpus_norm = " ".join(info["norm"] for info in corpus.values())
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


def verificar(archivos_json, ruta_corpus, umbral, terminos_absentes=None, exacto=False):
    archivos_txt = extraer_archivos_corpus(ruta_corpus)
    if not archivos_txt:
        return [{"error": f"No se encontraron .txt en {ruta_corpus}"}], 0

    t0 = time.time()
    print(f"Corpus: {len(archivos_txt)} archivo(s). Normalizando...")
    corpus = cargar_corpus_normalizado(archivos_txt)
    print(f"Corpus normalizado en {time.time()-t0:.1f}s.")

    resultados = []
    n_no_encontradas = 0
    n_items = 0

    for json_path in archivos_json:
        with open(json_path, encoding="utf-8-sig") as f:
            datos = json.load(f)
        citas = extraer_citas_de_json(datos)

        for idx, item in enumerate(citas, start=1):
            archivo_decl = archivo_declarado(item["contexto"])
            if not archivo_decl and item.get("archivo_ventana"):
                archivo_decl = item["archivo_ventana"]
            entrevista = item.get("entrevista")
            if not entrevista:
                m_e = re.search(r"[Ee]\s*(\d+)", item.get("senal_id") or "")
                if m_e:
                    entrevista = int(m_e.group(1))
            if not archivo_decl and entrevista:
                archivo_decl = archivo_de_interview(entrevista, corpus)
            nombre_norm = normalizar(archivo_decl) if archivo_decl else None
            estado, archivo_hallazgo, score = buscar_cita(
                item["cita"], corpus, umbral, exacto=exacto,
                archivo_declarado=archivo_decl,
                nombre_normalizado=nombre_norm)

            # Citas SIN_ANCLA: entre comillas simples sin ancla de ubicación.
            # Son INFORMATIVAS (el analista debe anclarlas), NUNCA bloquean, y no
            # disparan paráfrasis (sin ubicación no hay ventana que anclar).
            # Se reporta si el contenido es verbatim para dar contexto.
            ventana_par = None
            if item.get("sin_ancla"):
                contenido_ok = estado in ("ENCONTRADA", "ENCONTRADA_TRUNCADA",
                                          "UBICACION_INCORRECTA", "APROXIMADA")
                estado = "SIN_ANCLA"
                archivo_hallazgo = archivo_hallazgo or "[ninguno]"
                score = 1.0 if contenido_ok else 0.0
                resultados.append({
                    "senal_id": item["senal_id"],
                    "cita": item["cita"],
                    "archivo_declarado": "[sin ancla]",
                    "estado": estado,
                    "archivo_hallazgo": archivo_hallazgo,
                    "score": score,
                    "contexto": item["contexto"],
                    "ubicacion": "[sin ancla]",
                    "ventana_parafrasis": None,
                    "sin_ancla": True,
                    "contenido_verbatim": contenido_ok,
                })
                continue

            # Si no es verbatim, intentar paráfrasis anclada contra la ventana
            # declarada (archivo + líneas). Solo la cobertura alta auto-aprueba;
            # las bandas media/baja derivan a confirmación (agente LLM-juez).
            if (estado == "NO_ENCONTRADA" and archivo_decl
                    and archivo_decl in corpus and item.get("linea")):
                ventana_par = _ventana_de_corpus(corpus[archivo_decl], item["linea"])
                if ventana_par:
                    estado, score = evaluar_parafrasis(item["cita"], ventana_par)
                    archivo_hallazgo = archivo_decl

            if estado == "ENCONTRADA" and archivo_decl:
                # La cita se encontro, pero hay que verificar si es en el archivo declarado.
                # Comparar con normalizacion (evita falsos UBICACION_INCORRECTA por
                # descomposicion Unicode del nombre, p. ej. "José" vs "Jose\u0301").
                if normalizar(archivo_hallazgo) != nombre_norm:
                    estado = "UBICACION_INCORRECTA"

            if estado in ("NO_ENCONTRADA", "PARAFRASIS_NO_SOPORTADA"):
                n_no_encontradas += 1

            resultados.append({
                "senal_id": item["senal_id"],
                "cita": item["cita"],
                "archivo_declarado": archivo_decl or "[no declarado]",
                "estado": estado,
                "archivo_hallazgo": archivo_hallazgo or "[ninguno]",
                "score": round(score, 3) if estado in (
                    "APROXIMADA", "NO_ENCONTRADA",
                    "PARAFRASIS_APROXIMADA", "PARAFRASIS_NO_SOPORTADA") else 1.0,
                "contexto": item["contexto"],
                "ubicacion": item.get("ubicacion") or "",
                "ventana_parafrasis": ventana_par,
                "sin_ancla": False,
            })

            if idx % PASO_PROGRESO == 0:
                print(f"  citas procesadas: {idx}/{len(citas)} "
                      f"({time.time()-t0:.1f}s)")

        n_items += len(citas)

    resultados.extend(verificar_ausencias(archivos_json, corpus, terminos_absentes))
    print(f"Verificacion terminada: {n_items} citas + {len(resultados)-n_items} claims de ausencia "
          f"en {time.time()-t0:.1f}s totales.")
    return resultados, n_no_encontradas


def main():
    args = sys.argv[1:]
    if "-h" in args or "--help" in args:
        print(__doc__)
        sys.exit(0)          # la ayuda pedida no es un error
    if not args:
        print(__doc__, file=sys.stderr)
        sys.exit(1)

    umbral = UMBRAL_DEFAULT
    ruta_corpus = "."
    archivos_json = []
    terminos_absentes = []
    exacto = False
    llm_judge_out = None
    juicio_path = None

    i = 0
    while i < len(args):
        if args[i] == "--exacto":
            exacto = True
            i += 1
        elif args[i] == "--corpus" and i + 1 < len(args):
            ruta_corpus = args[i + 1]
            i += 2
        elif args[i] == "--umbral" and i + 1 < len(args):
            umbral = float(args[i + 1])
            i += 2
        elif args[i] == "--absentes" and i + 1 < len(args):
            terminos_absentes = [t.strip() for t in args[i + 1].split(",") if t.strip()]
            i += 2
        elif args[i] == "--llm-judge" and i + 1 < len(args):
            llm_judge_out = args[i + 1]
            i += 2
        elif args[i] == "--juicio" and i + 1 < len(args):
            juicio_path = args[i + 1]
            i += 2
        else:
            archivos_json.append(args[i])
            i += 1

    resultados, _ = verificar(
        archivos_json, ruta_corpus, umbral, terminos_absentes, exacto)
    if resultados and "error" in resultados[0]:
        print(f"[ERROR] {resultados[0]['error']}")
        sys.exit(1)

    # LLM-judge: aplicar veredictos externos a citas en banda ambigua.
    if juicio_path:
        try:
            with open(juicio_path, encoding="utf-8-sig") as f:
                juicios = json.load(f)
        except (OSError, ValueError) as e:
            print(f"[ERROR] No se pudo leer --juicio {juicio_path}: {e}")
            sys.exit(1)
        items_juicio = juicios.get("items", juicios) if isinstance(juicios, dict) else juicios
        for j in items_juicio:
            if not isinstance(j, dict):
                continue
            v = str(j.get("veredicto", "")).upper()
            for r in resultados:
                if (r["senal_id"] == j.get("senal_id") and r["cita"] == j.get("cita")
                        and r.get("estado") in ("PARAFRASIS_JUICIO_PENDIENTE",
                                                "PARAFRASIS_APROXIMADA",
                                                "PARAFRASIS_NO_SOPORTADA")):
                    r["estado"] = ("PARAFRASIS_VALIDADA" if "VALIDADA" in v
                                   else "PARAFRASIS_NO_SOPORTADA")

    # Emitir solicitud de juicio para citas ambiguas (no auto-resueltas).
    if llm_judge_out:
        requests = []
        for r in resultados:
            if (r.get("estado") in ("PARAFRASIS_APROXIMADA", "PARAFRASIS_NO_SOPORTADA")
                    and r.get("ventana_parafrasis")):
                r["estado"] = "PARAFRASIS_JUICIO_PENDIENTE"
                requests.append({
                    "senal_id": r["senal_id"],
                    "cita": r["cita"],
                    "ubicacion": r.get("ubicacion") or r.get("archivo_declarado"),
                    "ventana": r.get("ventana_parafrasis"),
                })
        with open(llm_judge_out, "w", encoding="utf-8") as f:
            json.dump({
                "instruccion": "Para cada item, responde {\"veredicto\": "
                               "\"VALIDADA\"|\"NO_SOPORTADA\", \"razon\": \"...\"} "
                               "segun si la ventana real respalda la cita/parafrasis.",
                "items": requests,
            }, f, ensure_ascii=False, indent=2)
        print(f"[LLM-JUDGE] {len(requests)} cita(s) pendientes de juicio -> {llm_judge_out}")

    for r in resultados:
        ancla_note = " | SIN_ANCLA" if r.get("sin_ancla") else ""
        ub = f" | ubicacion: {r.get('ubicacion')}" if r.get("ubicacion") else ""
        print(f"[{r['estado']}] {r['senal_id']} :: {r['cita'][:80]}... "
              f"(declarado: {r['archivo_declarado']} | hallado: {r['archivo_hallazgo']} | score: {r['score']}){ub}{ancla_note}")
        if (r.get("ventana_parafrasis")
                and r.get("estado") in ("PARAFRASIS_APROXIMADA",
                                        "PARAFRASIS_NO_SOPORTADA",
                                        "PARAFRASIS_JUICIO_PENDIENTE")):
            for ln in r["ventana_parafrasis"].splitlines()[:8]:
                print(f"        | {ln[:140]}")

    n_no_encontradas = sum(1 for r in resultados
                           if r.get("estado") in ("NO_ENCONTRADA", "PARAFRASIS_NO_SOPORTADA"))
    n_encontradas = sum(1 for r in resultados if r.get("estado") == "ENCONTRADA")
    n_truncadas = sum(1 for r in resultados if r.get("estado") == "ENCONTRADA_TRUNCADA")
    n_aprox = sum(1 for r in resultados
                  if r.get("estado") in ("APROXIMADA", "PARAFRASIS_APROXIMADA"))
    n_par_ok = sum(1 for r in resultados if r.get("estado") == "PARAFRASIS_VALIDADA")
    n_par_pend = sum(1 for r in resultados if r.get("estado") == "PARAFRASIS_JUICIO_PENDIENTE")
    n_ubic = sum(1 for r in resultados if r.get("estado") == "UBICACION_INCORRECTA")
    n_contradiccion = sum(1 for r in resultados if r.get("estado") == "CONTRADICCION")
    n_ausencia_ok = sum(1 for r in resultados if r.get("estado") == "AUSENCIA_CONFIRMADA")
    n_sin_ancla = sum(1 for r in resultados if r.get("sin_ancla"))

    print(f"\nResumen: {n_encontradas} ENCONTRADA(s), {n_truncadas} ENCONTRADA_TRUNCADA(s), "
          f"{n_aprox} APROXIMADA(s), {n_par_ok} PARAFRASIS_VALIDADA(s), "
          f"{n_par_pend} PARAFRASIS_JUICIO_PENDIENTE(s), "
          f"{n_ubic} UBICACION_INCORRECTA(s), "
          f"{n_no_encontradas} NO_ENCONTRADA/NO_SOPORTADA(s), "
          f"{n_contradiccion} CONTRADICCION(es), {n_ausencia_ok} AUSENCIA_CONFIRMADA(s), "
          f"{n_sin_ancla} SIN_ANCLA(s).")

    if n_sin_ancla:
        print(f"Citas SIN_ANCLA: {n_sin_ancla} cita(s) entre comillas simples sin ancla de "
              f"ubicación (contrato Fase 2/3). Se verificaron por contenido, pero no hay "
              f"ubicación declarada para anclar; el analista debe anclarlas (E<ID>/L<ini>) o "
              f"descartarlas.")

    if n_no_encontradas:
        print("Las senales con citas NO_ENCONTRADA o PARAFRASIS_NO_SOPORTADA no escalan "
              "a Fase 4 hasta corregirse o validarse.")
        sys.exit(1)
    if n_contradiccion:
        print("Claims de ausencia CONTRADICCION: el termino declarado ausente SI aparece "
              "en el corpus. Corregir o descartar la senal antes de escalar.")
        sys.exit(1)
    if n_aprox or n_par_pend:
        print("Citas APROXIMADAS o PARAFRASIS pendientes de juicio: el analista debe "
              "confirmar contra la ventana (o resolver con --juicio).")
        sys.exit(2)
    if n_truncadas:
        print("Citas ENCONTRADA_TRUNCADA: la cita exacta con elipsis no existe, pero el "
              "fragmento citado si aparece en el corpus. Revisar que la elipsis respete "
              "el sentido original.")
    print("Verificacion de citas completada.")
    sys.exit(0)


if __name__ == "__main__":
    main()
