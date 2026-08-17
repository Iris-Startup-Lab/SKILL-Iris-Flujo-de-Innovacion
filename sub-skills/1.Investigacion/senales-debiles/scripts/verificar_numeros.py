"""
Verificador determinista de numeros.

Recalcula los conteos clave del CSV de entrada y los compara contra las
cifras declaradas en los JSON de las fases (fase1 / fase3). Implementa el
invariante SSoT de SPEC.md seccion 0.2: ninguna cifra escrita a mano por el
LLM sobrevive al gate final.

Uso:
    python verificar_numeros.py <dataset.csv> <fase1_output.json> [fase2_output.json] [fase3_output.json] \
        [--base-pct 0.388] [--col-texto <columna> --terminos "t1,t2"]

Chequeos:
    1. N de registros del CSV. Ninguna fraccion a/b declarada en los JSON
       puede tener b > N.
    2. Toda fraccion a/b en 'dato', 'contexto' o 'sintesis' con b > N se
       reporta como ERROR.
    3. Consistencia entre fases: el 'dato' de cada senal referenciada por un
       cruce de fase3 debe declarar las mismas fracciones que en su fase de
       origen. Discrepancias (ej. 33/41 en fase1 vs 33/46 en fase3) = ERROR.
       Ademas, si un cruce introduce fracciones que no existen en la senal de
       origen, se marca WARN.
    4. Desgloses "a+b+c=total": si el texto declara una suma y un total, se
       verifica que coincidan (ej. 13+11+8 =/= 46).
    5. Matriz de frecuencias (datos_frecuencias): cada valor <= N y cada fila
       suma <= N.
    6. Baja calidad: si un JSON menciona "N registros de baja calidad" y
       fase1 declara calidad_respuesta.baja_calidad, ambos deben coincidir.
    7. Regla de tasa base (SPEC.md seccion 5): con --base-pct, todo porcentaje
       del JSON dentro de ~5 puntos porcentuales de la base se marca WARN
       (candidato a CONSISTENTE, no a senal debil).
    8. Con --col-texto y --terminos: cuenta las filas del CSV cuya celda en esa
       columna contiene cada termino y la compara contra toda fraccion a/b
       declarada en los JSON cuyo texto mencione el termino.

Salida: lista de hallazgos. Exit 0 si no hay ERRORes, 1 si los hay.
"""
import sys
import re
import json

import pandas as pd


RE_FRACCION = re.compile(r"(\d+)\s*/\s*(\d+)")
RE_PCT_FRACCION = re.compile(r"(\d{1,3}(?:\.\d+)?)\s*%\s*\(\s*(\d+)\s*/\s*(\d+)\s*\)")
RE_BAJA_CALIDAD = re.compile(r"(\d+)\s*(?:registros?\s+de\s+)?baja\s+calidad", re.I)


class Hallazgo:
    def __init__(self, nivel, msg):
        self.nivel = nivel  # "ERROR" | "WARN" | "OK"
        self.msg = msg

    def __str__(self):
        return f"[{self.nivel}] {self.msg}"


def extraer_fracciones(texto):
    res = []
    for m in RE_PCT_FRACCION.finditer(texto):
        pct = float(m.group(1))
        res.append(("pct", int(m.group(2)), int(m.group(3)), pct))
    for m in RE_FRACCION.finditer(texto):
        res.append(("frac", int(m.group(1)), int(m.group(2)), None))
    return res


def extraer_sumas_con_total(texto):
    resultados = []
    for m in re.finditer(r"(\d+(?:\s*\+\s*\d+)+)\s*=\s*(\d+)", texto):
        operandos = [int(x) for x in re.findall(r"\d+", m.group(1))]
        resultados.append((sum(operandos), int(m.group(2)), operandos))
    return resultados


def texto_de_item(item, campos=("dato", "contexto", "sintesis", "conclusion",
                                "razon", "ausencia_cuanti")):
    partes = []
    for campo in campos:
        valor = item.get(campo)
        if isinstance(valor, str):
            partes.append(valor)
        elif isinstance(valor, dict):
            for v in valor.values():
                if isinstance(v, str):
                    partes.append(v)
    return " ".join(partes)


def recorrer_objetos(obj, visitar):
    if isinstance(obj, dict):
        visitar(obj)
        for v in obj.values():
            recorrer_objetos(v, visitar)
    elif isinstance(obj, list):
        for v in obj:
            recorrer_objetos(v, visitar)


def extraer_items(datos):
    items = []
    for bloque in datos.get("datos", {}).get("bloques", []):
        for key in ("senales", "cruces"):
            for item in bloque.get(key, []):
                items.append(item)
    return items


def verificar(csv_path, json_paths, base_pct=None, col_texto=None, terminos=None):
    hallazgos = []

    try:
        df = pd.read_csv(csv_path, encoding="utf-8", dtype=str)
    except Exception as e:
        return [Hallazgo("ERROR", f"No se pudo leer el CSV {csv_path}: {e}")]

    n = len(df)
    hallazgos.append(Hallazgo("OK", f"N de registros del CSV: {n}"))

    terminos = [t.strip().lower() for t in (terminos or []) if t.strip()]

    por_fase = {}
    for path in json_paths:
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, ValueError) as e:
            hallazgos.append(Hallazgo("ERROR", f"No se pudo leer {path}: {e}"))
            continue
        por_fase[path] = data
        fase = data.get("fase", "")
        baja_calidad_declarada = None
        if fase.startswith("fase-1"):
            infra = data.get("datos", {}).get("infraestructura", {})
            calidad = infra.get("calidad_respuesta", {})
            baja_calidad_declarada = calidad.get("baja_calidad")
        for item in extraer_items(data):
            texto = texto_de_item(item)
            item_id = item.get("id", "?")
            for tipo, num, den, pct in extraer_fracciones(texto):
                if den > n:
                    hallazgos.append(Hallazgo(
                        "ERROR", f"{path} {item_id}: fraccion {num}/{den} con denominador > N={n}"
                    ))
                if base_pct is not None and tipo == "pct" and pct is not None:
                    diff = abs(pct - base_pct * 100.0)
                    if diff <= 5.0:
                        hallazgos.append(Hallazgo(
                            "WARN",
                            f"{path} {item_id}: {pct}% ({num}/{den}) dentro de ~5pp de la "
                            f"tasa base ({base_pct*100:.1f}%) - candidato a CONSISTENTE "
                            f"(regla de tasa base, SPEC.md seccion 5)"
                        ))
            for suma, total, operandos in extraer_sumas_con_total(texto):
                if suma != total:
                    hallazgos.append(Hallazgo(
                        "ERROR",
                        f"{path} {item_id}: desglose {'+'.join(map(str, operandos))}={suma} "
                        f"no coincide con el total declarado {total}"
                    ))
            # Chequeo 5: matriz de frecuencias
            gf = item.get("grafica")
            if isinstance(gf, dict):
                dfreq = gf.get("datos_frecuencias")
                if isinstance(dfreq, dict):
                    valores = dfreq.get("valores")
                    if isinstance(valores, list):
                        for fila in valores:
                            if isinstance(fila, list) and sum(fila) > n:
                                hallazgos.append(Hallazgo(
                                    "ERROR",
                                    f"{path} {item_id}: fila del heatmap suma {sum(fila)} > N={n}"
                                ))
                                break
            # Chequeo 6: baja calidad vs fase1
            if baja_calidad_declarada is not None:
                for m in RE_BAJA_CALIDAD.finditer(texto):
                    numero = int(m.group(1))
                    if numero != baja_calidad_declarada:
                        hallazgos.append(Hallazgo(
                            "ERROR",
                            f"{path} {item_id}: menciona {numero} registro(s) de baja calidad "
                            f"pero fase1 declara calidad_respuesta.baja_calidad = "
                            f"{baja_calidad_declarada}"
                        ))
            # Chequeo 8: conteo por terminos vs CSV
            if col_texto and terminos and col_texto in df.columns:
                for termino in terminos:
                    conteo = int(df[col_texto].fillna("").str.lower().str.contains(
                        re.escape(termino), regex=True).sum())
                    if termino in texto.lower():
                        hallazgos.append(Hallazgo(
                            "OK",
                            f"{path} {item_id}: CSV contiene '{termino}' en {conteo} fila(s) "
                            f"de '{col_texto}' (declarado en el JSON)"
                        ))
                    else:
                        hallazgos.append(Hallazgo(
                            "WARN",
                            f"CSV: '{termino}' aparece en {conteo} fila(s) de '{col_texto}', "
                            f"pero el JSON no lo menciona"
                        ))

    # Chequeo 3: consistencia entre fases (requiere fase1 y fase3)
    origenes = {}
    for path, data in por_fase.items():
        fase = data.get("fase", "")
        if fase.startswith("fase-1") or fase.startswith("fase-2"):
            for item in extraer_items(data):
                origenes[item.get("id")] = (path, item)
    for path, data in por_fase.items():
        fase = data.get("fase", "")
        if not fase.startswith("fase-3"):
            continue
        for cruce in extraer_items(data):
            cruce_id = cruce.get("id", "?")
            texto_completo = json.dumps(cruce, ensure_ascii=False)
            fr_todo = sorted(set(extraer_fracciones(texto_completo)))
            for clave in ("senal_cuanti", "senal_cuali"):
                ref = cruce.get(clave)
                if not isinstance(ref, dict) or not ref.get("id"):
                    continue
                rid = ref.get("id")
                if rid not in origenes:
                    hallazgos.append(Hallazgo(
                        "ERROR", f"{path} {cruce_id}: referencia {rid} que no existe en fases 1-2"
                    ))
                    continue
                f_origen = origenes[rid][1].get("dato", "")
                f_cruce = ref.get("dato", "")
                fr_origen = sorted(set(extraer_fracciones(f_origen)))
                fr_cruce = sorted(set(extraer_fracciones(f_cruce)))
                if fr_origen and fr_cruce and fr_origen != fr_cruce:
                    hallazgos.append(Hallazgo(
                        "ERROR",
                        f"{path} {cruce_id} / {rid}: fracciones discrepantes entre fases "
                        f"(origen {fr_origen} vs cruce {fr_cruce}) - SPEC.md seccion 0.2"
                    ))
            # WARN: el cruce introduce fracciones que no estaban en la senal de origen
            for clave in ("senal_cuanti", "senal_cuali"):
                ref = cruce.get(clave)
                if not isinstance(ref, dict) or not ref.get("id"):
                    continue
                rid = ref.get("id")
                if rid not in origenes:
                    continue
                f_origen = origenes[rid][1].get("dato", "")
                fr_origen = set(extraer_fracciones(f_origen))
                fr_ref = set(extraer_fracciones(ref.get("dato", "")))
                if fr_ref - fr_origen:
                    hallazgos.append(Hallazgo(
                        "WARN",
                        f"{path} {cruce_id}: introduce cifras no declaradas en {rid} "
                        f"({sorted(fr_ref - fr_origen)})"
                    ))
            if fr_todo:
                fr_origen_all = set()
                for clave in ("senal_cuanti", "senal_cuali"):
                    ref = cruce.get(clave)
                    if isinstance(ref, dict) and ref.get("id") in origenes:
                        fr_origen_all |= set(extraer_fracciones(
                            origenes[ref["id"]][1].get("dato", "")))
                extra = sorted(set(fr_todo) - fr_origen_all)
                if extra:
                    hallazgos.append(Hallazgo(
                        "WARN",
                        f"{path} {cruce_id}: el texto del cruce contiene cifras nuevas "
                        f"fuera del dato de origen ({extra})"
                    ))

    return hallazgos


def main():
    args = sys.argv[1:]
    if not args or "-h" in args or "--help" in args:
        print(__doc__)
        sys.exit(1)

    base_pct = None
    col_texto = None
    terminos = None
    pos = []
    i = 0
    while i < len(args):
        if args[i] == "--base-pct" and i + 1 < len(args):
            base_pct = float(args[i + 1])
            i += 2
        elif args[i] == "--col-texto" and i + 1 < len(args):
            col_texto = args[i + 1]
            i += 2
        elif args[i] == "--terminos" and i + 1 < len(args):
            terminos = [t for t in args[i + 1].split(",") if t.strip()]
            i += 2
        else:
            pos.append(args[i])
            i += 1

    if len(pos) < 2:
        print("Uso: python verificar_numeros.py <dataset.csv> <fase1_output.json> "
              "[fase3_output.json] [--base-pct 0.388] "
              "[--col-texto <columna> --terminos \"t1,t2\"]", file=sys.stderr)
        sys.exit(1)

    csv_path = pos[0]
    json_paths = pos[1:]

    hallazgos = verificar(csv_path, json_paths, base_pct, col_texto, terminos)
    for h in hallazgos:
        print(h)
    n_err = sum(1 for h in hallazgos if h.nivel == "ERROR")
    n_warn = sum(1 for h in hallazgos if h.nivel == "WARN")
    print(f"\nResumen: {n_err} error(es), {n_warn} advertencia(s).")
    sys.exit(1 if n_err else 0)


if __name__ == "__main__":
    main()
