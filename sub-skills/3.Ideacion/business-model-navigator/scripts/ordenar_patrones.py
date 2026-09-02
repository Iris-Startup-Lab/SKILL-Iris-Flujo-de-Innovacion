"""
ordenar_patrones.py

Aplica el orden de priorización y el desempate del Business Model Navigator sobre los
candidatos que el agente ya evaluó, de forma determinista.

Por qué existe: las reglas de la skill fijan un orden exacto —1º alineación con la
hipótesis, y para desempatar: fuerza de evidencia, menor costo, menor tiempo de
configuración, menor tiempo de ejecución— y ese orden lo aplicaba el LLM de cabeza sobre
cuatro indicadores por candidato. Con 5 candidatos y 4 criterios encadenados es fácil que
el orden entregado no sea el que las reglas dictan, y nadie lo nota.

Sobre la otra mitad del problema: el `catalogo-patrones.md` **no trae** los indicadores
numéricos, así que hoy los estima el agente. Enriquecer el catálogo con cifras inventadas
está prohibido por la regla de integridad del repositorio (§4 de `AGENTS.md`: nunca inventar
datos). Así que la solución es la otra: los indicadores siguen siendo del agente, se
declaran como estimación, y **el orden que sale de ellos lo calcula este script**, que no
se equivoca al encadenar cuatro criterios y deja por escrito cuál decidió cada empate.

Convención de los indicadores (1 a 5), la misma del AGENTE.md:

    costo, configuracion, ejecucion  →  1 = el más bajo / rápido, 5 = el más alto / lento
    evidencia                        →  1 = anecdótica, 5 = casos documentados y replicados
    alineacion                       →  1 = tangencial, 5 = resuelve la hipótesis de lleno

Orden resultante: alineación ↓ · evidencia ↓ · costo ↑ · configuración ↑ · ejecución ↑

Uso:
    python ordenar_patrones.py --plantilla > candidatos.json
    python ordenar_patrones.py --datos candidatos.json [--top 5] [-o orden.json]

Códigos de salida: 0 ok · 1 error de archivo/uso · 2 entrada inválida.
"""
import argparse
import json
import sys

# (clave, etiqueta, ascendente) — ascendente=True significa «menor es mejor».
CRITERIOS = [
    ("alineacion", "Alineación con la hipótesis", False),
    ("evidencia", "Fuerza de evidencia", False),
    ("costo", "Costo", True),
    ("configuracion", "Tiempo de configuración", True),
    ("ejecucion", "Tiempo de ejecución", True),
]
CLAVES = [c[0] for c in CRITERIOS]
ETIQUETAS = {c[0]: c[1] for c in CRITERIOS}
ASCENDENTE = {c[0]: c[2] for c in CRITERIOS}
TOP_DEFECTO = 5


class EntradaInvalida(Exception):
    pass


def _texto(v):
    return isinstance(v, str) and v.strip() != ""


def plantilla():
    return {
        "hipotesis": "La hipótesis que el usuario quiere validar",
        "exclusiones": ["Patterns o experimentos que el usuario pidió evitar"],
        "candidatos": [
            {
                "nombre": "NOMBRE EXACTO DEL PATTERN, tal como está en el catálogo",
                "alineacion": 4,
                "evidencia": 4,
                "costo": 2,
                "configuracion": 2,
                "ejecucion": 3,
                "origen_indicadores": "estimación del analista | catálogo | caso documentado",
                "fuera_de_catalogo": False,
            }
        ],
    }


def _validar(c, pos):
    if not isinstance(c, dict):
        raise EntradaInvalida(f"candidatos[{pos}] no es un objeto")
    nombre = c.get("nombre")
    if not _texto(nombre):
        raise EntradaInvalida(f"candidatos[{pos}].nombre está vacío")
    valores = {}
    faltan = []
    for clave in CLAVES:
        v = c.get(clave)
        if v is None:
            faltan.append(clave)
            continue
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            raise EntradaInvalida(
                f"«{nombre}».{clave} debe ser un número de 1 a 5, no {v!r}")
        if not 1 <= v <= 5:
            raise EntradaInvalida(f"«{nombre}».{clave} = {v} está fuera del rango 1-5")
        valores[clave] = float(v)
    if "alineacion" in faltan:
        raise EntradaInvalida(
            f"«{nombre}» no declara `alineacion`. Es la prioridad absoluta de las reglas: "
            f"sin ella no hay orden que calcular.")
    return {
        "nombre": nombre.strip(),
        "indicadores": valores,
        "sin_declarar": faltan,
        "origen_indicadores": c.get("origen_indicadores") or "[no disponible]",
        "fuera_de_catalogo": bool(c.get("fuera_de_catalogo")),
    }


def _clave_orden(c):
    """Clave de ordenación. Un indicador sin declarar se ordena al final de su nivel:
    no se le inventa un valor medio, porque eso lo colaría por delante de candidatos
    peor evaluados pero sí medidos."""
    partes = []
    for clave in CLAVES:
        v = c["indicadores"].get(clave)
        if v is None:
            # 1 en el flag = «sin dato», y va después de los que tienen dato.
            partes.append((1, 0.0))
        else:
            partes.append((0, v if ASCENDENTE[clave] else -v))
    return tuple(partes) + (c["nombre"],)


def _decidio_el_orden(a, b):
    """Cuál de los criterios separó a dos candidatos consecutivos."""
    for clave in CLAVES:
        va, vb = a["indicadores"].get(clave), b["indicadores"].get(clave)
        if va is None or vb is None:
            if va != vb:
                return (f"{ETIQUETAS[clave]} (uno de los dos no la declara, y un "
                        f"indicador sin dato no adelanta a uno medido)")
            continue
        if va != vb:
            direccion = "menor" if ASCENDENTE[clave] else "mayor"
            return f"{ETIQUETAS[clave]} ({direccion}: {va:g} contra {vb:g})"
    return ("ninguno: los cinco indicadores son idénticos, así que el orden entre estos "
            "dos es alfabético y no significa nada")


def calcular(datos, top=TOP_DEFECTO):
    candidatos = datos.get("candidatos")
    if not isinstance(candidatos, list) or not candidatos:
        raise EntradaInvalida("`candidatos` debe ser una lista con al menos un pattern")
    exclusiones = datos.get("exclusiones") or []
    if not isinstance(exclusiones, list):
        raise EntradaInvalida("`exclusiones` debe ser una lista de textos")

    evaluados = [_validar(c, i) for i, c in enumerate(candidatos)]

    # Las exclusiones son del usuario: se descartan por completo, no se penalizan.
    excl_norm = {str(e).strip().lower() for e in exclusiones if _texto(str(e))}
    descartados = [c for c in evaluados if c["nombre"].lower() in excl_norm]
    vivos = [c for c in evaluados if c["nombre"].lower() not in excl_norm]
    if not vivos:
        raise EntradaInvalida(
            "las exclusiones del usuario descartan todos los candidatos: hacen falta "
            "otros patterns antes de poder ordenar")

    ordenados = sorted(vivos, key=_clave_orden)
    for i, c in enumerate(ordenados, 1):
        c["posicion"] = i
        c["desempate_frente_al_anterior"] = (
            None if i == 1 else _decidio_el_orden(ordenados[i - 2], c))

    resultado = {
        "script": "ordenar_patrones.py",
        "hipotesis": datos.get("hipotesis") or "[no disponible]",
        "parametros": {
            "orden_de_criterios": [
                f"{ETIQUETAS[k]} ({'menor es mejor' if ASCENDENTE[k] else 'mayor es mejor'})"
                for k in CLAVES
            ],
            "escala": "1 a 5. costo/configuracion/ejecucion: 1 = el más bajo. "
                      "evidencia/alineacion: 5 = la más fuerte.",
            "top": top,
            "exclusiones_aplicadas": sorted(excl_norm),
        },
        "resultados": {
            "recomendados": ordenados[:top],
            "resto": ordenados[top:],
            "descartados_por_exclusion": [c["nombre"] for c in descartados],
        },
    }
    resultado["advertencias"] = _advertencias(resultado, ordenados)
    resultado["tabla"] = _tabla(resultado)
    return resultado


def _advertencias(r, ordenados):
    adv = [
        "Los indicadores no salen del catálogo: los estima el analista. El script aplica el "
        "orden de las reglas sobre esos números, no los valida. Decláralos como estimación en "
        "el reporte.",
    ]
    sin_datos = [f"{c['nombre']} (falta: {', '.join(c['sin_declarar'])})"
                 for c in ordenados if c["sin_declarar"]]
    if sin_datos:
        adv.append(
            f"Candidatos con indicadores sin declarar: {'; '.join(sin_datos)}. Van al final "
            f"de su nivel a propósito: un indicador ausente no debe adelantar a uno medido. "
            f"Si el catálogo no da el dato, dilo con «Datos de indicadores no disponibles en "
            f"la fuente» en vez de estimar un valor medio.")
    fuera = [c["nombre"] for c in ordenados if c["fuera_de_catalogo"]]
    if fuera:
        adv.append(
            f"Fuera del catálogo: {', '.join(fuera)}. Márcalos `[FUERA DE CATÁLOGO]` en la "
            f"entrega; compiten en el mismo orden pero no tienen el respaldo del catálogo.")
    empatados = [c["nombre"] for c in ordenados
                 if c.get("desempate_frente_al_anterior")
                 and c["desempate_frente_al_anterior"].startswith("ninguno")]
    if empatados:
        adv.append(
            f"Empate total en los cinco indicadores: {', '.join(empatados)}. El orden entre "
            f"ellos es alfabético y no significa nada; para decidir hace falta un criterio "
            f"que hoy no está declarado.")
    if len(r["resultados"]["recomendados"]) < r["parametros"]["top"]:
        adv.append(
            f"Solo hay {len(r['resultados']['recomendados'])} candidatos para un top de "
            f"{r['parametros']['top']}. Dilo en la entrega en vez de rellenar con patterns "
            f"que no encajan con la hipótesis.")
    return adv


def _tabla(r):
    filas = []
    for c in r["resultados"]["recomendados"]:
        ind = c["indicadores"]
        filas.append([
            str(c["posicion"]),
            c["nombre"] + (" [FUERA DE CATÁLOGO]" if c["fuera_de_catalogo"] else ""),
            *[(f"{ind[k]:g}" if k in ind else "n/d") for k in CLAVES],
            c["desempate_frente_al_anterior"] or "es el primero",
        ])
    return {
        "titulo": "Patterns recomendados, en el orden que dictan las reglas",
        "columnas": ["#", "Pattern", "Alineación", "Evidencia", "Costo", "Config.",
                     "Ejecución", "Qué lo separó del anterior"],
        "filas": filas,
        "nota": ("Orden: alineación con la hipótesis (mayor primero) y, para desempatar, "
                 "fuerza de evidencia (mayor), costo (menor), configuración (menor) y "
                 "ejecución (menor). `n/d` = el indicador no está declarado; esos candidatos "
                 "van al final de su nivel."),
    }


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Ordena los patterns del Business Model Navigator con el desempate "
                    "exacto de las reglas.")
    ap.add_argument("--datos", help="JSON con los candidatos y sus indicadores")
    ap.add_argument("--plantilla", action="store_true",
                    help="Imprime el esqueleto de entrada y termina")
    ap.add_argument("--top", type=int, default=TOP_DEFECTO,
                    help=f"Cuántos recomendar (por omisión {TOP_DEFECTO})")
    ap.add_argument("-o", "--output", default="orden_patrones.json")
    args = ap.parse_args(argv)

    if args.plantilla:
        print(json.dumps(plantilla(), ensure_ascii=False, indent=2))
        return 0
    if not args.datos:
        ap.error("hace falta --datos (o --plantilla para ver el esqueleto)")
    if args.top < 1:
        ap.error("--top tiene que ser al menos 1")

    try:
        datos = json.loads(open(args.datos, encoding="utf-8").read())
    except FileNotFoundError:
        print(f"Error: no encuentro {args.datos}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"Error: {args.datos} no es JSON válido — {exc}", file=sys.stderr)
        return 1

    try:
        r = calcular(datos, args.top)
    except EntradaInvalida as exc:
        print(f"Entrada inválida: {exc}", file=sys.stderr)
        return 2

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(r, f, ensure_ascii=False, indent=2)

    for c in r["resultados"]["recomendados"]:
        print(f"{c['posicion']}. {c['nombre']}")
        if c["desempate_frente_al_anterior"]:
            print(f"     lo separó del anterior: {c['desempate_frente_al_anterior']}")
    if r["resultados"]["descartados_por_exclusion"]:
        print(f"\nDescartados por exclusión del usuario: "
              f"{', '.join(r['resultados']['descartados_por_exclusion'])}")
    for a in r["advertencias"][1:]:
        print(f"\n[AVISO] {a}")
    print(f"\nOrden guardado en: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
