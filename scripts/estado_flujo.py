"""
estado_flujo.py — máquina de estados del flujo de innovación IRIS.

Mantiene `flujo_estado.json` (fuente de verdad del avance de un proyecto) y
genera `STATE.md` como vista humana. La macro-skill nunca edita el estado a
mano: lo hace con este script, para que el histórico sea siempre parseable y
el contexto que viaja a cada HTML sea idéntico paso a paso.

La definición del flujo (qué pasos existen, qué skills invoca cada uno, qué se
puede omitir) vive en `pasos.json` y este script solo la lee.

Uso típico de la macro-skill:

    python scripts/estado_flujo.py init --proyecto "Huertos urbanos MX" \
        --objetivo "Validar demanda" --audiencia "Familias urbanas 28-45"

    python scripts/estado_flujo.py mostrar --paso html_1
    python scripts/estado_flujo.py iniciar --paso html_1
    python scripts/estado_flujo.py decision --paso html_1 \
        --nodo "¿Cómo quieres iniciar?" --opcion "Estado actual"
    python scripts/estado_flujo.py completar --paso html_1 \
        --skills 1.Investigacion/benchmark-mercado \
        --resumen "TAM MX 4.2 mil M* y 3 huecos de oferta" \
        --veredicto perseverar --outputs html_1.html --datos reporte.json

Cerrar un paso registra dos cosas distintas y las dos viajan al siguiente:
`--resumen` (una línea: el índice de lo que pasó) y `--datos` (el `reporte.json`
del paso: la estructura que el paso siguiente lee para heredar sus bloques en
lugar de reteclearlos desde el resumen).

    python scripts/estado_flujo.py omitir --paso html_2 \
        --motivo "El usuario ya tiene 12 entrevistas hechas"

`iniciar` y `completar` comprueban los `predecesores` del paso: avisan si alguno
sigue abierto (pendiente / en curso) y **bloquean** si ese predecesor no es
omitible, con `--forzar` como escape. Cerrar un paso omitiéndolo o marcándolo
fallido no depende de sus predecesores: no consume su input.

Las dos barreras que hacen cumplir el flujo, no solo describirlo:

- `decision` **rechaza** un nodo que no esté en `pasos.json` y una opción que no
  esté en su catálogo, y exige el `minimo` de los nodos `multiple`. En un nodo
  `multiple` se repite `--opcion` una vez por elección.
- `completar` **se niega** a cerrar un paso con nodos de decisión sin responder:
  si el paso pregunta algo, ese algo lo decide el usuario. `--forzar` cierra igual
  y lo deja anotado en el histórico.

    python scripts/estado_flujo.py verificar     # ¿se respetó el flujo? (exit 2 si no)

    python scripts/estado_flujo.py contexto --paso html_4 -o contexto.json
    python scripts/estado_flujo.py render          # reescribe STATE.md

Códigos de salida: 0 ok · 1 error de uso/archivo · 2 regla del flujo violada.
"""
import argparse
import json
import sys
import unicodedata
from datetime import datetime
from pathlib import Path

# En Windows la consola es cp1252 y caracteres como → (U+2192) rompen el print.
# Se escribe UTF-8 a stdout/stderr para que el output no dependa del code page.
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass

_HERE = Path(__file__).resolve().parent
REPO_ROOT = _HERE.parent

PASOS_JSON = REPO_ROOT / "pasos.json"
ESTADO_JSON = REPO_ROOT / "flujo_estado.json"
STATE_MD = REPO_ROOT / "STATE.md"

ESTADOS = ["pendiente", "en_curso", "completado", "omitido", "fallido"]
VEREDICTOS = ["perseverar", "pivotear", "descartar"]

ICONO = {
    "completado": "[x]",
    "omitido": "[-]",
    "en_curso": "[>]",
    "fallido": "[!]",
    "pendiente": "[ ]",
}


class ReglaDelFlujo(Exception):
    """Se intentó una transición que el flujo no permite."""


ABIERTOS = ("pendiente", "en_curso")

# Nota que viaja a todos los reportes cuando el usuario elige simular. La escribe el
# flujo, no las skills: así la marca no depende de que nadie se acuerde de ponerla.
NOTA_SIMULACION = (
    "Las entrevistas y encuestas de este proyecto son SIMULADAS: las respuestas las "
    "generó un simulador a partir de prevalencias declaradas, no provienen de usuarios "
    "reales. Lo que se lee aquí es un ensayo del instrumento y de cómo se leerían los "
    "resultados, no evidencia de campo."
)


# --------------------------------------------------------------------------- #
# Carga
# --------------------------------------------------------------------------- #

def cargar_pasos(ruta=None):
    ruta = Path(ruta) if ruta else PASOS_JSON
    if not ruta.is_file():
        raise FileNotFoundError(f"No encuentro la definición del flujo: {ruta}")
    return json.loads(ruta.read_text(encoding="utf-8"))


def cargar_estado(ruta=None):
    ruta = Path(ruta) if ruta else ESTADO_JSON
    if not ruta.is_file():
        raise FileNotFoundError(
            f"No encuentro {ruta.name}. Inicia el proyecto con:\n"
            f"    python scripts/estado_flujo.py init --proyecto \"<nombre>\""
        )
    return json.loads(ruta.read_text(encoding="utf-8"))


def guardar_estado(estado, ruta=None):
    ruta = Path(ruta) if ruta else ESTADO_JSON
    estado["actualizado"] = datetime.now().isoformat(timespec="seconds")
    ruta.write_text(
        json.dumps(estado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def def_paso(pasos, paso_id):
    for p in pasos["pasos"]:
        if p["id"] == paso_id:
            return p
    validos = ", ".join(p["id"] for p in pasos["pasos"])
    raise ReglaDelFlujo(f"Paso desconocido: {paso_id}. Válidos: {validos}")


def estado_paso(estado, paso_id):
    for p in estado["pasos"]:
        if p["id"] == paso_id:
            return p
    raise ReglaDelFlujo(f"El paso {paso_id} no está en flujo_estado.json")


# --------------------------------------------------------------------------- #
# Decisiones: catálogo, condiciones y qué falta responder
#
# Aquí vive la parte del flujo que antes solo estaba escrita en prosa: qué nodos
# tiene un paso, qué opciones son legítimas y cuándo un nodo aplica. El script lo
# comprueba porque un documento no puede: si el catálogo solo vive en `pasos.json`
# y nadie lo verifica, una opción inventada o un nodo sin responder pasan sin ruido
# y el proyecto avanza con un hueco que nadie declaró.
# --------------------------------------------------------------------------- #

def _norm(texto):
    """Normaliza un texto para comparar nodos y opciones.

    Sin mayúsculas, sin acentos y con cualquier guion largo reducido a `-`. La
    comparación tiene que ser tolerante con la tipografía y estricta con el
    contenido: «No — simulación» y «No - simulacion» son la misma opción, y
    rechazarla por el guion sería un falso positivo molesto e inútil.
    """
    t = unicodedata.normalize("NFKD", str(texto or "").strip().lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    for guion in ("—", "–", "−"):
        t = t.replace(guion, "-")
    return " ".join(t.split())


def _elegidas(dec):
    """Las opciones de una decisión registrada, siempre como lista.

    Los nodos `multiple` guardan `opciones: [...]`; los antiguos y los `unica`
    guardan un solo `opcion`. Se lee de las dos formas para no romper proyectos
    ya empezados.
    """
    if isinstance(dec.get("opciones"), list) and dec["opciones"]:
        return list(dec["opciones"])
    return [dec.get("opcion", "")]


def decision_registrada(estado, paso_id, nombre_nodo):
    """La decisión ya registrada para ese nodo del paso, o None."""
    for dec in estado.get("decisiones", []):
        if dec.get("paso") == paso_id and _norm(dec.get("nodo")) == _norm(nombre_nodo):
            return dec
    return None


def buscar_nodo(definicion, nombre):
    """El nodo de decisión del paso cuyo texto coincide con `nombre`, o None."""
    for nodo in definicion.get("decisiones", []):
        if _norm(nodo["nodo"]) == _norm(nombre):
            return nodo
    return None


def opciones_declaradas(nodo, estado, pasos, paso_id):
    """Las opciones válidas del nodo, o None si `pasos.json` no las conoce.

    `opciones_desde` significa exactamente eso: el catálogo no está en el archivo.
    O sale de otro nodo del mismo paso (las palancas de la ambición elegida), o lo
    produce el propio paso (las ideas del paso 8). El primer caso se resuelve; el
    segundo no tiene catálogo posible y el script no se inventa uno.
    """
    if nodo.get("opciones"):
        return [o["opcion"] for o in nodo["opciones"]]

    origen = str(nodo.get("opciones_desde") or "")
    if "." not in origen:
        return None

    nodo_origen, campo = origen.split(".", 1)
    definicion = def_paso(pasos, paso_id)
    previo = buscar_nodo(definicion, nodo_origen)
    dec = decision_registrada(estado, paso_id, nodo_origen)
    if previo is None or dec is None:
        return None                       # todavía no se sabe: el nodo previo está sin responder

    valores = []
    for elegida in _elegidas(dec):
        for opcion in previo.get("opciones", []):
            if _norm(opcion["opcion"]) == _norm(elegida):
                valores.extend(opcion.get(campo, []))
    return valores or None


def origen_sin_responder(nodo, estado, paso_id):
    """Si el catálogo del nodo sale de OTRO nodo que aún no se respondió, devuelve su nombre.

    `opciones_desde: "Ambición estratégica.palancas"` significa que las opciones válidas
    dependen de una decisión previa. Registrar ese nodo antes es elegir una palanca sin
    saber de qué ambición: no hay catálogo contra el que comprobar nada, y aceptarlo
    en silencio es justo el agujero por el que se cuela una opción inventada.

    Un `opciones_desde` sin punto («las ideas generadas en este paso») no depende de
    ningún nodo: ahí el texto libre es lo correcto y esto devuelve None.
    """
    origen = str(nodo.get("opciones_desde") or "")
    if "." not in origen:
        return None
    nodo_origen = origen.split(".", 1)[0]
    if decision_registrada(estado, paso_id, nodo_origen) is None:
        return nodo_origen
    return None


def nodo_aplica(nodo, estado, paso_id):
    """¿Hay que preguntar este nodo en este proyecto?

    Devuelve `(aplica, comprobable)`. Un `solo_si` estructurado
    (`{nodo, opcion}` o `{nodo, incluye}`) se evalúa. En texto libre no se puede,
    así que el nodo se da por aplicable y se marca como no comprobable: la barrera
    no debe bloquear por una condición que el script no entiende.
    """
    cond = nodo.get("solo_si")
    if not cond:
        return True, True
    if not isinstance(cond, dict):
        return True, False

    ref = None
    for dec in estado.get("decisiones", []):
        if _norm(dec.get("nodo")) == _norm(cond.get("nodo")):
            ref = dec
            break
    if ref is None:
        # El nodo del que depende no se ha respondido: por ahora no aplica.
        return False, True

    elegidas = [_norm(x) for x in _elegidas(ref)]
    if cond.get("opcion") is not None:
        return _norm(cond["opcion"]) in elegidas, True
    if cond.get("incluye") is not None:
        return _norm(cond["incluye"]) in elegidas, True
    return True, False


def decisiones_sin_resolver(estado, definicion):
    """Decisiones del paso que impiden cerrarlo: `[(nodo, motivo)]`.

    Solo cuenta lo que el script puede afirmar: nodos que aplican y no tienen
    respuesta, y nodos `multiple` con menos opciones elegidas que su `minimo`.
    """
    faltan = []
    for nodo in definicion.get("decisiones", []):
        aplica, _ = nodo_aplica(nodo, estado, definicion["id"])
        if not aplica:
            continue
        dec = decision_registrada(estado, definicion["id"], nodo["nodo"])
        if dec is None:
            faltan.append((nodo, "sin responder"))
            continue
        minimo = nodo.get("minimo")
        if minimo:
            n = len([x for x in _elegidas(dec) if str(x).strip()])
            if n < minimo:
                faltan.append((
                    nodo,
                    f"se registraron {n} opciones y el mínimo de este nodo es {minimo}",
                ))
    return faltan


# --------------------------------------------------------------------------- #
# init
# --------------------------------------------------------------------------- #

def cmd_init(args):
    pasos = cargar_pasos(args.pasos)
    destino = Path(args.estado) if args.estado else ESTADO_JSON

    if destino.is_file() and not args.forzar:
        estado = json.loads(destino.read_text(encoding="utf-8"))
        print(
            f"Ya existe {destino.name} para el proyecto «{estado.get('proyecto')}».\n"
            "Continúa ese proyecto, o usa --forzar para empezar de cero "
            "(se pierde el histórico)."
        )
        return 2

    ahora = datetime.now().isoformat(timespec="seconds")
    ruta_minima = args.ruta == "minima"

    estado = {
        "version": 1,
        "proyecto": args.proyecto,
        "objetivo": args.objetivo or "",
        "audiencia": args.audiencia or "",
        "creado": ahora,
        "actualizado": ahora,
        "ruta": args.ruta,
        "paso_actual": None,
        "pasos": [],
        "decisiones": [],
    }

    for p in pasos["pasos"]:
        entrada = {
            "id": p["id"],
            "titulo": p["titulo"],
            "etapa": p["etapa"],
            "estado": "pendiente",
            "skills": [],
            "outputs": [],
            "resumen": "",
            "veredicto": None,
        }
        if ruta_minima and not p.get("en_ruta_minima"):
            if p.get("omitible"):
                entrada["estado"] = "omitido"
                entrada["motivo"] = "Ruta mínima: paso fuera del recorrido express"
                entrada["impacto"] = p.get("si_omitido", "")
        estado["pasos"].append(entrada)

    primero = next(
        (p["id"] for p in estado["pasos"] if p["estado"] == "pendiente"), None
    )
    estado["paso_actual"] = primero

    guardar_estado(estado, destino)
    render_state_md(estado, pasos, destino)

    # Los pasos se anuncian por su título: un `html_7` no le dice nada al usuario.
    titulos = {p["id"]: p["titulo"] for p in pasos["pasos"]}
    print(f"Proyecto «{args.proyecto}» iniciado en {destino.name}.")
    if ruta_minima:
        omitidos = [p["id"] for p in estado["pasos"] if p["estado"] == "omitido"]
        print("  Ruta mínima ("
              + f"{len(pasos['ruta_minima'])} pasos): "
              + " → ".join(titulos[i] for i in pasos["ruta_minima"]))
        print(f"  Omitidos de entrada ({len(omitidos)}): "
              + ", ".join(f"{titulos[i]} ({i})" for i in omitidos))
    print(f"  Primer paso: {titulos.get(primero, '')} ({primero})")
    print(f"  STATE.md actualizado.")
    return 0


# --------------------------------------------------------------------------- #
# Transiciones
# --------------------------------------------------------------------------- #

def predecesores_abiertos(estado, pasos, definicion):
    """Predecesores del paso que siguen sin resolverse.

    `predecesores` en `pasos.json` son los pasos de los que este hereda, y son
    alternativos entre sí (html_7 puede venir de html_6, de html_5 o de html_4).
    Por eso la regla no es «todos cerrados»: un paso está resuelto si se completó,
    se omitió o falló. Lo que rompe el hilo es dejarlo *abierto*, porque entonces
    nadie declaró su impacto y el paso siguiente hereda un hueco en silencio.

    Devuelve [(id, entrada_de_estado, definicion)] de los que siguen abiertos.
    """
    abiertos = []
    for pid in definicion.get("predecesores", []):
        entrada = next((p for p in estado["pasos"] if p["id"] == pid), None)
        if entrada is None:
            continue
        if entrada["estado"] in ABIERTOS:
            abiertos.append((pid, entrada, def_paso(pasos, pid)))
    return abiertos


def _revisar_predecesores(args, estado, pasos, definicion, entrada):
    """Avisa —o bloquea— si el paso avanza con predecesores abiertos.

    Avisa por defecto; bloquea solo si el predecesor abierto no es omitible, con
    `--forzar` como escape, igual que la regla de los pasos `omitible: false`.
    """
    abiertos = predecesores_abiertos(estado, pasos, definicion)
    if not abiertos:
        return

    duros = [x for x in abiertos if not x[2].get("omitible", True)]
    blandos = [x for x in abiertos if x not in duros]

    if duros and not args.forzar:
        detalle = "\n".join(
            f"  - {pid} ({d['titulo']}): {e['estado']} · no es omitible — "
            f"{d.get('razon_no_omitible', 'dependencia dura del flujo')}"
            for pid, e, d in duros
        )
        raise ReglaDelFlujo(
            f"{args.paso} ({definicion['titulo']}) hereda de pasos que no se pueden "
            f"saltar y siguen abiertos:\n{detalle}\n"
            f"  Ciérralos antes ({', '.join(pid for pid, _, _ in duros)}), o usa "
            f"--forzar: el salto queda registrado en el histórico."
        )

    if duros:
        entrada["predecesores_saltados"] = [pid for pid, _, _ in duros]
        print(
            "Aviso: --forzar salta predecesores no omitibles: "
            + ", ".join(f"{pid} ({e['estado']})" for pid, e, _ in duros)
            + ". Este paso trabaja sin su input: márcalo en `advertencias` del reporte.",
            file=sys.stderr,
        )

    if blandos:
        print(
            f"Aviso: {args.paso} avanza con predecesores todavía abiertos: "
            + ", ".join(f"{pid} ({e['estado']})" for pid, e, _ in blandos)
            + ". Si el usuario no los va a ejecutar, ciérralos con "
            "`omitir --motivo \"…\"` para que su impacto quede declarado.",
            file=sys.stderr,
        )


def _revisar_decisiones(args, estado, definicion, entrada):
    """Bloquea el cierre de un paso con decisiones del usuario sin registrar.

    No es burocracia: cada nodo de `pasos.json` es una elección que le toca al
    usuario. Si el paso se cierra sin ella, alguien decidió en su nombre —casi
    siempre el agente, ejecutando lo que le pareció— y eso no queda en ninguna
    parte. `--forzar` deja seguir, pero lo anota.
    """
    faltan = decisiones_sin_resolver(estado, definicion)
    if not faltan:
        return

    detalle = "\n".join(
        f"  - «{nodo['nodo']}» ({nodo.get('tipo', 'unica')}): {motivo}"
        + (f"\n      {nodo['descripcion']}" if nodo.get("descripcion") else "")
        for nodo, motivo in faltan
    )
    if not args.forzar:
        raise ReglaDelFlujo(
            f"{args.paso} ({definicion['titulo']}) no se puede cerrar: hay decisiones "
            f"del usuario sin registrar.\n{detalle}\n"
            f"  Pregúntaselas y regístralas:\n"
            f"    python scripts/estado_flujo.py decision --paso {args.paso} "
            f"--nodo \"<nodo>\" --opcion \"<opción>\"\n"
            f"  Si el usuario no quiere este paso, omítelo con su motivo en vez de "
            f"cerrarlo sin decisión. --forzar cierra igual y lo deja anotado."
        )

    entrada["decisiones_sin_registrar"] = [nodo["nodo"] for nodo, _ in faltan]
    print(
        "Aviso: --forzar cierra el paso con decisiones sin registrar: "
        + ", ".join(f"«{nodo['nodo']}»" for nodo, _ in faltan)
        + ". Nadie sabrá qué eligió el usuario ahí: decláralo en `advertencias`.",
        file=sys.stderr,
    )


def _transicion(args, nuevo_estado):
    pasos = cargar_pasos(args.pasos)
    estado = cargar_estado(args.estado)
    definicion = def_paso(pasos, args.paso)
    entrada = estado_paso(estado, args.paso)

    if nuevo_estado == "omitido" and not definicion.get("omitible", True):
        if not args.forzar:
            raise ReglaDelFlujo(
                f"{args.paso} ({definicion['titulo']}) no se puede omitir.\n"
                f"  Motivo: {definicion.get('razon_no_omitible', 'dependencia dura del flujo')}\n"
                f"  Si el usuario insiste, repite con --forzar y quedará registrado como "
                f"omisión forzada."
            )
        entrada["omision_forzada"] = True

    # Avanzar (iniciar/completar) exige que lo que este paso hereda esté resuelto.
    # Omitir o fallar un paso no depende de sus predecesores: no consume su input.
    if nuevo_estado in ("en_curso", "completado"):
        _revisar_predecesores(args, estado, pasos, definicion, entrada)

    # Cerrar un paso exige haber preguntado lo que el paso pregunta. Es la barrera
    # que impide el fallo más común del flujo: ejecutar las sub-skills eligiendo por
    # el usuario y cerrar el paso como si él hubiera decidido.
    if nuevo_estado == "completado":
        _revisar_decisiones(args, estado, definicion, entrada)

    entrada["estado"] = nuevo_estado
    entrada["cerrado"] = datetime.now().isoformat(timespec="seconds")

    if nuevo_estado == "completado":
        entrada["skills"] = args.skills or []
        entrada["outputs"] = args.outputs or []
        entrada["resumen"] = args.resumen or ""
        # `datos` es el reporte.json del paso: lo que los pasos siguientes leen para
        # heredar la estructura (persona, psf, items…) y no reteclearla del resumen.
        entrada["datos"] = getattr(args, "datos", None) or ""
        if args.veredicto:
            entrada["veredicto"] = args.veredicto
        # Los outputs viven junto al estado del proyecto, no en la raíz del repo.
        base = Path(args.estado).resolve().parent if args.estado else REPO_ROOT
        declarados = list(args.outputs or [])
        if entrada["datos"]:
            declarados.append(entrada["datos"])
        faltantes = [
            f for f in declarados
            if not (base / f).is_file() and not Path(f).is_file()
        ]
        if faltantes:
            print(
                "Aviso: estos archivos no existen en disco todavía: "
                + ", ".join(faltantes),
                file=sys.stderr,
            )
        if not entrada["resumen"]:
            print(
                "Aviso: paso cerrado sin --resumen. Es lo único que los pasos "
                "siguientes ven de este en su contexto: sin él, la cadena pierde "
                "el hilo en silencio.",
                file=sys.stderr,
            )
        if not entrada["datos"]:
            print(
                "Aviso: paso cerrado sin --datos <reporte.json>. Los pasos "
                "siguientes solo heredarán el resumen, no los datos estructurados.",
                file=sys.stderr,
            )
    elif nuevo_estado in ("omitido", "fallido"):
        entrada["motivo"] = args.motivo or ""
        # Un paso no omitible no declara `si_omitido`: su impacto es exactamente la
        # razón por la que no debía omitirse.
        entrada["impacto"] = definicion.get("si_omitido") or definicion.get(
            "razon_no_omitible", ""
        )

    # Avanza el puntero al primer paso no cerrado.
    pendiente = next(
        (p["id"] for p in estado["pasos"] if p["estado"] in ("pendiente", "en_curso")),
        None,
    )
    estado["paso_actual"] = pendiente

    guardar_estado(estado, args.estado)
    render_state_md(estado, pasos, args.estado)

    # Se nombra el paso, no solo su id: es lo que se le traslada al usuario.
    total = len(estado["pasos"])
    print(f"Paso {definicion.get('orden')} de {total} — {definicion['titulo']}"
          f" → {nuevo_estado}  ({args.paso})")
    if nuevo_estado == "omitido":
        print(f"  Impacto declarado: {entrada['impacto'] or '(sin impacto declarado)'}")
    if pendiente:
        sig = def_paso(pasos, pendiente)
        print(f"  Siguiente: paso {sig.get('orden')} de {total} — {sig['titulo']}"
              f" ({pendiente})")
    else:
        print("  Siguiente: flujo completo")
    return 0


def cmd_iniciar(args):
    return _transicion(args, "en_curso")


def cmd_completar(args):
    return _transicion(args, "completado")


def cmd_omitir(args):
    return _transicion(args, "omitido")


def cmd_fallar(args):
    return _transicion(args, "fallido")


def cmd_decision(args):
    """Registra la elección de un nodo, comprobándola contra `pasos.json`.

    Tres cosas se verifican antes de escribir: que el nodo exista en el paso, que
    el tipo permita el número de opciones y que cada opción esté en el catálogo.
    `--forzar` es el escape para el único caso legítimo —una opción propuesta por
    el agente en un nodo con `permite_propuestas`— y deja rastro en el histórico.
    """
    pasos = cargar_pasos(args.pasos)
    estado = cargar_estado(args.estado)
    definicion = def_paso(pasos, args.paso)

    elegidas = [x for x in (args.opcion or []) if str(x).strip()]
    if not elegidas:
        raise ReglaDelFlujo("--opcion no puede ir vacío: registra lo que eligió el usuario.")

    nodo = buscar_nodo(definicion, args.nodo)
    if nodo is None:
        declarados = [n["nodo"] for n in definicion.get("decisiones", [])]
        detalle = (
            "\n".join(f"    · {n}" for n in declarados)
            if declarados
            else "    (este paso no tiene ningún nodo de decisión)"
        )
        if not args.forzar:
            raise ReglaDelFlujo(
                f"«{args.nodo}» no es un nodo de decisión de {args.paso} "
                f"({definicion['titulo']}). Los nodos de este paso son:\n{detalle}\n"
                f"  Usa el texto exacto de `pasos.json`. Si de verdad hace falta un nodo "
                f"nuevo, repite con --forzar y quedará marcado como fuera del flujo."
            )
        print(
            f"Aviso: «{args.nodo}» no está en pasos.json. Se registra como nodo fuera "
            f"del flujo; el flujo no lo tendrá en cuenta en ningún paso posterior.",
            file=sys.stderr,
        )

    nombre_nodo = nodo["nodo"] if nodo else args.nodo
    tipo = (nodo or {}).get("tipo", "unica")

    if nodo and tipo != "multiple" and len(elegidas) > 1:
        raise ReglaDelFlujo(
            f"«{nombre_nodo}» es de tipo {tipo}: admite una sola opción y llegaron "
            f"{len(elegidas)} ({', '.join(elegidas)}).\n"
            f"  Si el usuario eligió varias cosas, es que es el nodo equivocado: revisa "
            f"`mostrar --paso {args.paso}`."
        )

    # Un nodo condicional no se responde hasta saber si aplica. Registrarlo antes deja
    # en el histórico una decisión de un nodo que quizá el usuario nunca debió ver.
    if nodo and isinstance(nodo.get("solo_si"), dict):
        aplica, _ = nodo_aplica(nodo, estado, args.paso)
        if not aplica and not args.forzar:
            cond = nodo["solo_si"]
            fuente = cond.get("nodo", "")
            previa = next((d for d in estado.get("decisiones", [])
                           if _norm(d.get("nodo")) == _norm(fuente)), None)
            requisito = (f"= «{cond['opcion']}»" if cond.get("opcion")
                         else f"incluya «{cond.get('incluye')}»")
            if previa is None:
                motivo = (f"«{fuente}» todavía no se ha registrado, así que no se sabe si "
                          f"este nodo aplica.\n  Pregunta «{fuente}» primero")
            else:
                motivo = (f"este nodo solo aplica si «{fuente}» {requisito}, y quedó "
                          f"registrado como «{previa.get('opcion')}».\n"
                          f"  No hay que preguntárselo al usuario")
            raise ReglaDelFlujo(
                f"«{nombre_nodo}» es una decisión condicional: {motivo}."
            )

    # Un nodo cuyo catálogo depende de otro no se puede responder antes que él.
    pendiente = origen_sin_responder(nodo, estado, args.paso) if nodo else None
    if pendiente and not args.forzar:
        raise ReglaDelFlujo(
            f"«{nombre_nodo}» no se puede responder todavía: sus opciones salen de "
            f"«{pendiente}», que sigue sin registrar.\n"
            f"  Pregunta «{pendiente}» primero; después «{nombre_nodo}» ya tendrá "
            f"opciones concretas que ofrecer al usuario.\n"
            f"  El orden de los nodos en `pasos.json` es el orden en que se preguntan."
        )

    catalogo = opciones_declaradas(nodo, estado, pasos, args.paso) if nodo else None
    canonicas, fuera = [], []
    for elegida in elegidas:
        if catalogo is None:
            canonicas.append(elegida)          # nodo sin catálogo: el texto lo pone el paso
            continue
        match = next((c for c in catalogo if _norm(c) == _norm(elegida)), None)
        if match is None:
            fuera.append(elegida)
        else:
            canonicas.append(match)            # se guarda el texto de pasos.json, no el reescrito

    if fuera:
        propuestas_ok = bool((nodo or {}).get("permite_propuestas", {}).get("permitido")) \
            if isinstance((nodo or {}).get("permite_propuestas"), dict) \
            else bool((nodo or {}).get("permite_propuestas"))
        lista = "\n".join(f"    · {c}" for c in (catalogo or []))
        if not args.forzar:
            extra = (
                "  Este nodo admite propuestas del agente: si es una opción nueva y el "
                "usuario la eligió a conciencia, repite con --forzar y quedará marcada "
                "como propuesta en el histórico y en el reporte."
                if propuestas_ok else
                "  No inventes opciones ni reescribas las declaradas: preséntalas como "
                "están. Si aun así hay que registrarla, usa --forzar y quedará marcada "
                "como fuera del catálogo."
            )
            raise ReglaDelFlujo(
                f"Opción no declarada en «{nombre_nodo}» de {args.paso}: "
                f"{', '.join(fuera)}\n  Opciones válidas:\n{lista}\n{extra}"
            )
        canonicas.extend(fuera)
        etiqueta = "propuesta del agente" if propuestas_ok else "FUERA del catálogo"
        print(
            f"Aviso: {', '.join(fuera)} se registra como {etiqueta} en «{nombre_nodo}». "
            f"Decláralo así ante el usuario y en `advertencias` del reporte.",
            file=sys.stderr,
        )

    minimo = (nodo or {}).get("minimo")
    if minimo and len(canonicas) < minimo:
        raise ReglaDelFlujo(
            f"«{nombre_nodo}» exige elegir al menos {minimo} "
            f"{'opción' if minimo == 1 else 'opciones'} y llegaron {len(canonicas)}.\n"
            f"  Si el usuario no quiere ninguna, lo que corresponde es omitir el paso "
            f"({args.paso}) con su motivo, no cerrarlo sin decisión."
        )

    registro = {
        "paso": args.paso,
        "nodo": nombre_nodo,
        # `opcion` sigue siendo el texto plano de siempre (un solo valor queda idéntico
        # al formato anterior); `opciones` es la lista, que es lo que se puede comprobar.
        "opcion": " + ".join(canonicas),
        "opciones": canonicas,
        "registrado": datetime.now().isoformat(timespec="seconds"),
    }
    if fuera:
        registro["fuera_de_catalogo"] = fuera
        # `propuesta_agente` solo si el nodo las admite. Si no, es una opción fuera del
        # catálogo: las dos cosas quedan registradas, pero no son lo mismo y el reporte
        # no debe presentar como propuesta legítima algo que el flujo no contemplaba.
        registro["propuesta_agente"] = bool(propuestas_ok)

    estado["decisiones"] = [
        d
        for d in estado["decisiones"]
        if not (d["paso"] == args.paso and _norm(d["nodo"]) == _norm(nombre_nodo))
    ]
    estado["decisiones"].append(registro)
    guardar_estado(estado, args.estado)
    render_state_md(estado, pasos, args.estado)
    print(f"Decisión registrada · {args.paso} · {nombre_nodo} → {registro['opcion']}")

    # Lo que queda por preguntar en este paso: evita cerrarlo a medias.
    faltan = decisiones_sin_resolver(estado, definicion)
    if faltan:
        print("  Todavía sin responder en este paso: "
              + ", ".join(f"«{n['nodo']}»" for n, _ in faltan))
    return 0


# --------------------------------------------------------------------------- #
# Bloque de contexto que viaja a cada HTML
# --------------------------------------------------------------------------- #

def detectar_simulacion(estado, pasos):
    """¿Está activa la simulación de entrevistas/encuestas en este proyecto?

    No se busca por texto. Una opción de `pasos.json` marcada `marca_simulacion: true`
    enciende la marca en cuanto queda registrada como decisión, y desde ahí viaja a
    todos los reportes posteriores.
    """
    for dec in estado.get("decisiones", []):
        try:
            definicion = def_paso(pasos, dec.get("paso"))
        except ReglaDelFlujo:
            continue
        for nodo in definicion.get("decisiones", []):
            if _norm(nodo.get("nodo")) != _norm(dec.get("nodo")):
                continue
            # En un nodo `multiple` la marca la enciende cualquiera de las elegidas.
            elegidas = [_norm(x) for x in _elegidas(dec)]
            for opcion in nodo.get("opciones", []):
                if (_norm(opcion.get("opcion")) in elegidas
                        and opcion.get("marca_simulacion")):
                    return {
                        "activo": True,
                        "desde": dec.get("paso", ""),
                        "nodo": dec.get("nodo", ""),
                        "opcion": dec.get("opcion", ""),
                        "registrado": dec.get("registrado", ""),
                        "nota": NOTA_SIMULACION,
                    }
    return {"activo": False}


def construir_bloque_flujo(estado, pasos, paso_id):
    """Devuelve el bloque `flujo` de REPORT_DATA para `paso_id`.

    Es el contexto completo del flujo: dónde está este reporte dentro de los
    11 pasos, qué se decidió antes, qué se omitió y con qué consecuencia.
    """
    definicion = def_paso(pasos, paso_id)
    actual = estado_paso(estado, paso_id)

    ruta = []
    for p in estado["pasos"]:
        d = def_paso(pasos, p["id"])
        item = {
            "id": p["id"],
            "titulo": p["titulo"],
            "etapa": p["etapa"],
            "estado": "actual" if p["id"] == paso_id else p["estado"],
            "objetivo": d.get("objetivo", ""),
        }
        if p.get("resumen"):
            item["resumen"] = p["resumen"]
        if p.get("outputs"):
            item["archivo"] = p["outputs"][0]     # el que enlaza el riel del flujo
            item["archivos"] = p["outputs"]       # todos: el resto también es herencia
        if p.get("datos"):
            item["datos"] = p["datos"]            # reporte.json: los datos estructurados
        if p.get("veredicto"):
            item["veredicto"] = p["veredicto"]
        if p.get("skills"):
            item["skills"] = p["skills"]
        if p["estado"] == "omitido":
            item["motivo"] = p.get("motivo", "")
            item["impacto"] = p.get("impacto", "")
        ruta.append(item)

    omitidos = [
        {
            "id": p["id"],
            "titulo": p["titulo"],
            "motivo": p.get("motivo", ""),
            "impacto": p.get("impacto", ""),
            "forzada": bool(p.get("omision_forzada")),
        }
        for p in estado["pasos"]
        if p["estado"] == "omitido"
    ]

    completados = [p for p in estado["pasos"] if p["estado"] == "completado"]

    # Siguiente paso del flujo (para el cierre del reporte): el primero que sigue
    # abierto, distinto del paso que se está renderizando. Sigue el orden de pasos.json.
    siguiente_paso = None
    for p in estado["pasos"]:
        if p["id"] == paso_id:
            continue
        if p["estado"] in ABIERTOS:
            d_sig = def_paso(pasos, p["id"])
            siguiente_paso = {
                "id": p["id"],
                "titulo": p["titulo"],
                "etapa": p["etapa"],
                "orden": d_sig.get("orden"),
                "objetivo": d_sig.get("objetivo", ""),
            }
            break

    return {
        "proyecto": estado.get("proyecto", ""),
        "objetivo_proyecto": estado.get("objetivo", ""),
        "audiencia": estado.get("audiencia", ""),
        "paso_actual": paso_id,
        "paso_titulo": definicion["titulo"],
        "paso_objetivo": definicion.get("objetivo", ""),
        "paso_orden": definicion.get("orden"),
        "total_pasos": len(estado["pasos"]),
        "avance": {
            "completados": len(completados),
            "omitidos": len(omitidos),
            "pendientes": sum(
                1 for p in estado["pasos"] if p["estado"] == "pendiente"
            ),
        },
        "predecesores": definicion.get("predecesores", []),
        "simulacion": detectar_simulacion(estado, pasos),
        "skills_del_paso": actual.get("skills", []),
        "ruta": ruta,
        "decisiones": estado.get("decisiones", []),
        "omitidos": omitidos,
        "siguiente_paso": siguiente_paso,
    }


def cmd_contexto(args):
    """Imprime el *contenido* del bloque `flujo` (sin la clave que lo envuelve).

    Es para inspeccionar qué hereda un paso; quien lo inyecta en el reporte es
    `generar_html.py --estado --paso`, no este comando.
    """
    pasos = cargar_pasos(args.pasos)
    estado = cargar_estado(args.estado)
    bloque = construir_bloque_flujo(estado, pasos, args.paso)
    texto = json.dumps(bloque, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(texto + "\n", encoding="utf-8")
        print(f"Contenido del bloque `flujo` escrito en {args.output}")
    else:
        print(texto)
    return 0


# --------------------------------------------------------------------------- #
# mostrar — briefing del paso para la macro-skill
# --------------------------------------------------------------------------- #

def cmd_mostrar(args):
    pasos = cargar_pasos(args.pasos)
    estado = cargar_estado(args.estado)

    if not args.paso:
        paso_id = estado.get("paso_actual")
        if not paso_id:
            print("El flujo está completo: no queda ningún paso pendiente.")
            return 0
    else:
        paso_id = args.paso

    d = def_paso(pasos, paso_id)
    e = estado_paso(estado, paso_id)

    # El encabezado trae ya la frase que se le dice al usuario («Paso 4 de 11 —
    # Persona Profile»); `html_N` va aparte, porque es el nombre del archivo de
    # entrega, no el del paso.
    print(f"# Paso {d.get('orden')} de {len(estado['pasos'])} — {d['titulo']}"
          f"  ({d['etapa']})")
    print(f"Id interno: {paso_id} · entrega: {d['entrega']}")
    print(f"Proyecto: {estado.get('proyecto')}")
    print(f"Objetivo del paso: {d.get('objetivo','')}")
    print(f"Estado actual: {e['estado']}")
    print()

    print("## Histórico relevante (predecesores)")
    if not d["predecesores"]:
        print("- (es el primer paso del flujo)")
    for pid in d["predecesores"]:
        pe = estado_paso(estado, pid)
        linea = f"- {ICONO[pe['estado']]} {pid} {pe['titulo']}: {pe['estado']}"
        if pe.get("resumen"):
            linea += f" — {pe['resumen']}"
        if pe["estado"] == "omitido":
            linea += f" — IMPACTO: {pe.get('impacto','')}"
        print(linea)
        # De dónde leer sus datos: el resumen es el índice, no el contenido.
        outs = pe.get("outputs") or []
        if pe.get("datos"):
            print(f"    datos estructurados: {pe['datos']}")
        elif outs:
            print(f"    datos embebidos en {outs[0]} (window.REPORT_DATA)")
        if len(outs) > 1:
            print(f"    otros archivos: {', '.join(outs[1:])}")
    abiertos = predecesores_abiertos(estado, pasos, d)
    if abiertos:
        duros = [pid for pid, _, pd in abiertos if not pd.get("omitible", True)]
        print(
            "- ATENCIÓN: estos predecesores siguen abiertos: "
            + ", ".join(f"{pid} ({pe['estado']})" for pid, pe, _ in abiertos)
        )
        if duros:
            print(
                f"    {', '.join(duros)} no es omitible: hay que cerrarlo antes de "
                f"avanzar con {paso_id} (o forzarlo y declararlo)."
            )
        else:
            print(
                "    ninguno es obligatorio; si el usuario no los va a ejecutar, "
                "omítelos con su motivo para que el impacto quede declarado."
            )
    print()

    if estado.get("decisiones"):
        print("## Decisiones ya tomadas (no volver a preguntar)")
        for dec in estado["decisiones"]:
            print(f"- [{dec['paso']}] {dec['nodo']} → {dec['opcion']}")
        print()

    omitidos = [p for p in estado["pasos"] if p["estado"] == "omitido"]
    if omitidos:
        print("## Pasos omitidos (usar supuestos marcados * donde falte su input)")
        for p in omitidos:
            print(f"- {p['id']} {p['titulo']}: {p.get('impacto','')}")
        print()

    print("## Decisiones a presentar en este paso")
    if not d["decisiones"]:
        print("- (ninguna: este paso no tiene nodo de decisión)")
    for dec in d["decisiones"]:
        aplica, comprobable = nodo_aplica(dec, estado, paso_id)
        registrada = decision_registrada(estado, paso_id, dec["nodo"])

        espera = origen_sin_responder(dec, estado, paso_id)
        if registrada is not None:
            marca = "RESPONDIDA → «" + registrada.get("opcion", "") + "»"
        elif not aplica:
            marca = "no aplica por ahora (depende de otra decisión)"
        elif espera:
            marca = f"PENDIENTE — pregunta «{espera}» primero: de ahí salen sus opciones"
        else:
            marca = "PENDIENTE — hay que preguntarla antes de cerrar el paso"
        print(f"- {dec['nodo']} ({dec['tipo']}) · {marca}")

        if dec.get("descripcion"):
            print(f"    cómo presentarla: {dec['descripcion']}")
        if dec.get("minimo"):
            print(f"    hay que elegir al menos {dec['minimo']} "
                  f"{'opción' if dec['minimo'] == 1 else 'opciones'}; "
                  f"si el usuario no quiere ninguna, se omite el paso")
        if dec.get("ofrecer_todos"):
            print("    ofrece «todos» como atajo, pero PREGUNTA antes de ejecutar nada")
        if dec.get("solo_si"):
            cond = dec["solo_si"]
            texto = (f"«{cond.get('nodo')}» "
                     + (f"= «{cond['opcion']}»" if cond.get("opcion")
                        else f"incluye «{cond.get('incluye')}»")
                     ) if isinstance(cond, dict) else str(cond)
            print(f"    solo si: {texto}"
                  + ("" if comprobable else "  (condición en texto: la juzgas tú)"))
        if dec.get("opciones_desde"):
            resueltas = opciones_declaradas(dec, estado, pasos, paso_id)
            if resueltas:
                print(f"    opciones desde {dec['opciones_desde']} → "
                      + ", ".join(resueltas))
            else:
                print(f"    opciones desde: {dec['opciones_desde']} "
                      f"(no están en pasos.json: salen del nodo previo o de este paso)")

        for o in dec.get("opciones", []):
            extra = ""
            if o.get("agente"):
                extra += f"  [agente: {o['agente']}]"
            if o.get("skills"):
                extra += "  → " + ", ".join(o["skills"])
            if o.get("palancas"):
                extra += "  → palancas: " + ", ".join(o["palancas"])
            if o.get("marca_simulacion"):
                extra += "  [enciende la marca de datos simulados]"
            if o.get("requiere_propuesta"):
                extra += "  [el contenido lo propone el agente y lo aprueba el usuario]"
            print(f"    · {o['opcion']}{extra}")
            if o.get("efecto"):
                print(f"        efecto: {o['efecto']}")

        if dec.get("glosario"):
            print("    explica estos términos al presentarlos (no esperes a que pregunte):")
            for termino, explicacion in dec["glosario"].items():
                print(f"        {termino}: {explicacion}")
        if dec.get("permite_propuestas"):
            pp = dec["permite_propuestas"]
            if isinstance(pp, dict):
                print(f"    propuestas del agente: {pp.get('regla','')}")
                if pp.get("prohibido"):
                    print(f"    PROHIBIDO: {pp['prohibido']}")
            else:
                print("    puedes AÑADIR opciones marcadas como propuesta; nunca quitar "
                      "ni reescribir las declaradas")
        if dec.get("auto_si"):
            print(
                f"    auto: si {dec['auto_si']['condicion']} → "
                f"«{dec['auto_si']['opcion']}» — infórmalo al usuario en vez de "
                f"preguntarlo, y regístralo igual"
            )

    faltan = decisiones_sin_resolver(estado, d)
    if faltan:
        print()
        print("- BARRERA: este paso no se puede cerrar hasta registrar "
              + ", ".join(f"«{n['nodo']}»" for n, _ in faltan))
    print()

    # Lo que las decisiones ya registradas eligieron: son las que se ejecutan, no
    # todas las del catálogo. La decisión puede venir de otro paso (así se enlaza
    # «elegir agentes» con «ejecutarlos»), por eso se recorre el histórico entero.
    elegidas_por_decision = []
    for dec in estado.get("decisiones", []):
        try:
            dsel = def_paso(pasos, dec.get("paso"))
        except ReglaDelFlujo:
            continue
        nodo = buscar_nodo(dsel, dec.get("nodo"))
        if not nodo:
            continue
        marcadas = [_norm(x) for x in _elegidas(dec)]
        for o in nodo.get("opciones", []):
            if _norm(o.get("opcion")) in marcadas:
                for s in o.get("skills", []):
                    if s in d["skills_posibles"] and s not in elegidas_por_decision:
                        elegidas_por_decision.append(s)

    simulacion = detectar_simulacion(estado, pasos)
    simuladores = d.get("simuladores") or {}
    if simulacion["activo"]:
        print("## SIMULACIÓN ACTIVA")
        print(f"- Decidido en {simulacion['desde']}: «{simulacion['nodo']}» → "
              f"«{simulacion['opcion']}»")
        print(f"- {NOTA_SIMULACION}")
        print("- Todo reporte de aquí en adelante sale marcado SIMULADO: lo hace el "
              "generador, no hace falta pedirlo.")
        # Solo los simuladores de las skills elegidas: listar los cuatro cuando el
        # usuario pidió dos invita a ejecutar lo que nadie pidió.
        pertinentes = {k: v for k, v in simuladores.items()
                       if not elegidas_por_decision or k in elegidas_por_decision}
        if pertinentes:
            print("- Simuladores a usar en este paso (generan el CSV que analiza la skill):")
            for skill, sim in pertinentes.items():
                print(f"    {skill} → sub-skills/{sim}/SIMULADOR.md")
        print()

    print("## Sub-skills invocables en este paso")
    for s in d["skills_posibles"]:
        linea = f"- sub-skills/{s}/AGENTE.md"
        if elegidas_por_decision:
            linea += ("  [ELEGIDA por el usuario]" if s in elegidas_por_decision
                      else "  (no elegida: no la ejecutes)")
        if simulacion["activo"] and s in simuladores:
            linea += f"  (datos simulados: sub-skills/{simuladores[s]}/SIMULADOR.md)"
        print(linea)
    if not elegidas_por_decision and d["skills_posibles"] and d["decisiones"]:
        print("- (ninguna elegida todavía: la decisión de este paso dice cuáles corren)")
    if d.get("cadenas"):
        for cadena in d["cadenas"]:
            print("- cadena obligatoria: " + " → ".join(cadena))
    if d.get("paralelo"):
        print("- (se ejecutan en paralelo y se consolidan en un solo HTML)")
    print()

    print("## Omisión")
    if d.get("omitible"):
        print(f"- Se puede omitir. Si se omite: {d.get('si_omitido','')}")
    else:
        print(f"- NO se puede omitir. {d.get('razon_no_omitible','')}")
    print()
    print(f"## Entrega esperada\n- {d['entrega']} (validado por el generador)")
    return 0


# --------------------------------------------------------------------------- #
# rutas — los dos recorridos, con nombres, para presentarlos al usuario
# --------------------------------------------------------------------------- #

def cmd_verificar(args):
    """Audita el proyecto contra `pasos.json`: ¿se respetó el flujo?

    Se ejecuta al final (o cuando algo huele raro) y responde una sola pregunta:
    qué se cerró sin preguntar lo que había que preguntar. Devuelve 2 si encuentra
    algo, para que se pueda usar como comprobación automática.
    """
    pasos = cargar_pasos(args.pasos)
    estado = cargar_estado(args.estado)

    hallazgos = []
    ids_validos = {p["id"] for p in pasos["pasos"]}

    for entrada in estado["pasos"]:
        definicion = def_paso(pasos, entrada["id"])
        etiqueta = f"paso {definicion.get('orden')} ({entrada['id']}) {definicion['titulo']}"

        if entrada["estado"] == "completado":
            for nodo, motivo in decisiones_sin_resolver(estado, definicion):
                hallazgos.append(
                    f"{etiqueta}: cerrado sin la decisión «{nodo['nodo']}» ({motivo})"
                )
            if not entrada.get("resumen"):
                hallazgos.append(f"{etiqueta}: cerrado sin resumen para el paso siguiente")
            if not entrada.get("datos"):
                hallazgos.append(f"{etiqueta}: cerrado sin --datos (el siguiente paso "
                                 f"solo hereda el resumen)")
            if not entrada.get("outputs"):
                hallazgos.append(f"{etiqueta}: cerrado sin declarar su entrega "
                                 f"({definicion['entrega']})")
            if entrada.get("decisiones_sin_registrar"):
                hallazgos.append(
                    f"{etiqueta}: cerrado con --forzar dejando sin registrar "
                    + ", ".join(f"«{n}»" for n in entrada["decisiones_sin_registrar"])
                )
        if entrada.get("predecesores_saltados"):
            hallazgos.append(
                f"{etiqueta}: saltó con --forzar los predecesores "
                + ", ".join(entrada["predecesores_saltados"])
            )
        if entrada["estado"] == "omitido" and not entrada.get("motivo"):
            hallazgos.append(f"{etiqueta}: omitido sin motivo declarado")

    # Decisiones que no corresponden a ningún nodo del flujo: o el nodo se registró
    # con otro texto, o se inventó. En los dos casos el flujo no las verá.
    for dec in estado.get("decisiones", []):
        if dec.get("paso") not in ids_validos:
            hallazgos.append(f"decisión en un paso inexistente: {dec.get('paso')}")
            continue
        definicion = def_paso(pasos, dec["paso"])
        if buscar_nodo(definicion, dec.get("nodo")) is None:
            hallazgos.append(
                f"paso {definicion.get('orden')} ({dec['paso']}): la decisión "
                f"«{dec.get('nodo')}» no es un nodo de pasos.json — el flujo la ignora"
            )
        if dec.get("fuera_de_catalogo"):
            que = ("propuesta del agente" if dec.get("propuesta_agente")
                   else "opción fuera del catálogo")
            hallazgos.append(
                f"paso {definicion.get('orden')} ({dec['paso']}): «{dec.get('nodo')}» "
                f"se registró con una {que} ({', '.join(dec['fuera_de_catalogo'])}) — "
                f"debe estar declarada en `advertencias` del reporte"
            )
            continue

        # Una respuesta puede quedar obsoleta sin que nadie la toque: si el nodo del que
        # salían sus opciones se cambió después, la palanca elegida ya no pertenece a la
        # ambición vigente. Nada lo detectaría, porque en su momento fue válida.
        nodo = buscar_nodo(definicion, dec.get("nodo"))

        # Decisión registrada en un nodo que no aplica: se le preguntó al usuario algo
        # que su recorrido no incluía, o la condición cambió después.
        if nodo and isinstance(nodo.get("solo_si"), dict):
            aplica, _ = nodo_aplica(nodo, estado, dec["paso"])
            if not aplica:
                cond = nodo["solo_si"]
                hallazgos.append(
                    f"paso {definicion.get('orden')} ({dec['paso']}): «{dec['nodo']}» está "
                    f"registrada pero no aplica — depende de «{cond.get('nodo')}», que quedó "
                    f"con otro valor. O se preguntó de más, o la condición cambió después"
                )
                continue

        if nodo and "." in str(nodo.get("opciones_desde") or ""):
            fuente = str(nodo["opciones_desde"]).split(".", 1)[0]
            origen = decision_registrada(estado, dec["paso"], fuente)
            etiqueta = f"paso {definicion.get('orden')} ({dec['paso']}): «{dec['nodo']}»"

            # Se responde antes que el nodo del que salen sus opciones: la respuesta no
            # se eligió de ningún catálogo.
            if origen is None:
                hallazgos.append(
                    f"{etiqueta} está respondida pero «{fuente}», de donde salen sus "
                    f"opciones, no. La respuesta no salió de ningún catálogo"
                )
            # Registrada ANTES que su fuente: en su momento fue válida, pero la decisión
            # de la que dependía cambió después. Nada más lo detectaría.
            elif dec.get("registrado", "") < origen.get("registrado", ""):
                hallazgos.append(
                    f"{etiqueta} se registró ANTES que «{fuente}», que cambió después: "
                    f"la opción elegida pertenecía a otro valor. Hay que volver a preguntarla"
                )
            else:
                catalogo = opciones_declaradas(nodo, estado, pasos, dec["paso"])
                if catalogo is None:
                    hallazgos.append(
                        f"{etiqueta} no se puede comprobar: «{fuente}» se resolvió con una "
                        f"opción fuera del catálogo, así que no declara opciones para este nodo"
                    )
                else:
                    huerfanas = [o for o in _elegidas(dec)
                                 if not any(_norm(c) == _norm(o) for c in catalogo)]
                    if huerfanas:
                        hallazgos.append(
                            f"{etiqueta} → {', '.join(huerfanas)} no está entre las opciones "
                            f"que ofrece «{fuente}» con su valor actual"
                        )

    print(f"# Verificación del flujo — {estado.get('proyecto','(sin nombre)')}")
    cerrados = sum(1 for p in estado["pasos"] if p["estado"] == "completado")
    omitidos = sum(1 for p in estado["pasos"] if p["estado"] == "omitido")
    print(f"Pasos completados: {cerrados} · omitidos: {omitidos} · "
          f"decisiones registradas: {len(estado.get('decisiones', []))}")
    print()
    if not hallazgos:
        print("Sin hallazgos: cada paso cerrado registró sus decisiones, su resumen y "
              "sus datos, y todas las decisiones corresponden a nodos del flujo.")
        return 0
    print(f"{len(hallazgos)} hallazgos:")
    for h in hallazgos:
        print(f"- {h}")
    print()
    print("Ninguno se arregla editando el estado a mano: se corrige registrando la "
          "decisión que falta o volviendo a cerrar el paso con lo que le falte.")
    return 2


def cmd_rutas(args):
    """Imprime los dos recorridos con el título de cada paso.

    Existe para que la macro no tenga que enumerar los pasos de memoria ni
    presentarlos como `html_N`, que al usuario no le dice nada. Sale de
    `pasos.json`, así que no se puede desincronizar del flujo real.
    """
    pasos = cargar_pasos(args.pasos)
    todos = pasos["pasos"]
    minima_ids = pasos["ruta_minima"]
    minima = [p for p in todos if p["id"] in minima_ids]
    saltados = [p for p in todos if p["id"] not in minima_ids]

    def linea(i, p):
        return f"{i}. {p['titulo']} ({p['etapa']}) · {p['id']}"

    print(f"# Recorridos disponibles\n")
    print(f"## Ruta completa — {len(todos)} pasos")
    print("El proceso íntegro, de la investigación al experimento.\n")
    for i, p in enumerate(todos, 1):
        print(linea(i, p))

    print(f"\n## Ruta mínima — {len(minima)} pasos")
    print("De la investigación al experimento, sin las etapas intermedias.\n")
    for i, p in enumerate(minima, 1):
        print(linea(i, p))

    print(f"\n### Lo que la ruta mínima se salta ({len(saltados)} pasos)")
    for p in saltados:
        print(f"- {p['titulo']} ({p['id']}): {p.get('si_omitido', '')}")

    print(
        "\nLa ruta mínima se elige con `init --ruta minima`; esos pasos quedan "
        "omitidos de entrada y su impacto se declara en todos los reportes."
    )
    return 0


# --------------------------------------------------------------------------- #
# render — STATE.md como vista humana
# --------------------------------------------------------------------------- #

def render_state_md(estado, pasos, estado_path=None):
    destino = STATE_MD
    if estado_path:
        destino = Path(estado_path).resolve().parent / "STATE.md"

    L = []
    L.append("# STATE — Flujo de Innovación IRIS")
    L.append("")
    L.append(
        "> Vista humana **generada** desde `flujo_estado.json`. No la edites a mano: "
        "se reescribe en cada paso. Para cambiar el estado usa "
        "`python scripts/estado_flujo.py <comando>`."
    )
    L.append("")
    L.append(f"- proyecto: {estado.get('proyecto') or '(sin iniciar)'}")
    if estado.get("objetivo"):
        L.append(f"- objetivo: {estado['objetivo']}")
    if estado.get("audiencia"):
        L.append(f"- audiencia: {estado['audiencia']}")
    L.append(f"- ruta: {estado.get('ruta', 'completa')}")
    L.append(f"- paso_actual: {estado.get('paso_actual') or 'flujo completo'}")
    L.append(f"- actualizado: {estado.get('actualizado','')}")
    L.append("")

    comp = sum(1 for p in estado["pasos"] if p["estado"] == "completado")
    omit = sum(1 for p in estado["pasos"] if p["estado"] == "omitido")
    total = len(estado["pasos"])
    L.append(f"**Avance:** {comp} completados · {omit} omitidos · {total} pasos.")
    L.append("")

    simulacion = detectar_simulacion(estado, pasos)
    if simulacion["activo"]:
        L.append(
            f"> ## ⚠ DATOS SIMULADOS\n>\n> {NOTA_SIMULACION}\n>\n> Decidido en "
            f"`{simulacion['desde']}`: «{simulacion['nodo']}» → "
            f"«{simulacion['opcion']}». Todos los reportes de este proyecto salen "
            f"marcados."
        )
        L.append("")

    L.append("## Ruta")
    L.append("")
    L.append("| | Paso | Etapa | Estado | Resumen / motivo |")
    L.append("| --- | --- | --- | --- | --- |")
    for p in estado["pasos"]:
        nota = p.get("resumen") or ""
        if p["estado"] == "omitido":
            nota = f"omitido: {p.get('motivo','')}"
        elif p["estado"] == "fallido":
            nota = f"falló: {p.get('motivo','')}"
        nota = nota.replace("|", "\\|")
        L.append(
            f"| {ICONO[p['estado']]} | `{p['id']}` {p['titulo']} | {p['etapa']} "
            f"| {p['estado']} | {nota} |"
        )
    L.append("")

    L.append("## Decisiones")
    L.append("")
    if estado.get("decisiones"):
        for d in estado["decisiones"]:
            linea = f"- `{d['paso']}` **{d['nodo']}** → {d['opcion']}"
            if d.get("fuera_de_catalogo"):
                # Se anota en la vista humana porque es lo único del histórico que no
                # sale de `pasos.json`: quien lea el estado tiene que poder distinguirlo.
                # Y se distingue una propuesta legítima (el nodo las admite) de una
                # opción que el flujo no contemplaba.
                que = ("propuesta del agente" if d.get("propuesta_agente")
                       else "FUERA del catálogo del flujo")
                # Si todo lo elegido está fuera del catálogo, enumerarlo detrás de la
                # opción es repetir lo mismo dos veces.
                fuera = d["fuera_de_catalogo"]
                detalle = "" if len(fuera) == len(_elegidas(d)) else ": " + ", ".join(fuera)
                linea += f" — _{que}{detalle}_"
            L.append(linea)
    else:
        L.append("_(ninguna registrada todavía)_")
    L.append("")

    L.append("## Historial")
    L.append("")
    hechos = [
        p for p in estado["pasos"] if p["estado"] in ("completado", "fallido")
    ]
    if hechos:
        for p in hechos:
            skills = ", ".join(p.get("skills", [])) or "—"
            outs = ", ".join(p.get("outputs", [])) or "—"
            L.append(f"- **`{p['id']}`** {p['titulo']}")
            L.append(f"  - skills: {skills}")
            L.append(f"  - resumen: {p.get('resumen') or '—'}")
            L.append(f"  - veredicto: {p.get('veredicto') or '—'}")
            L.append(f"  - outputs: {outs}")
            L.append(f"  - datos (reporte.json): {p.get('datos') or '—'}")
            if p.get("predecesores_saltados"):
                L.append(
                    "  - **predecesores saltados con `--forzar`:** "
                    + ", ".join(p["predecesores_saltados"])
                )
    else:
        L.append("_(sin pasos ejecutados todavía)_")
    L.append("")

    omitidos = [p for p in estado["pasos"] if p["estado"] == "omitido"]
    L.append("## Pasos omitidos y su impacto")
    L.append("")
    if omitidos:
        for p in omitidos:
            forzada = " **(omisión forzada)**" if p.get("omision_forzada") else ""
            L.append(f"- **`{p['id']}`** {p['titulo']}{forzada}")
            L.append(f"  - motivo: {p.get('motivo') or '—'}")
            L.append(f"  - impacto: {p.get('impacto') or '—'}")
    else:
        L.append("_(ninguno)_")
    L.append("")

    L.append("## Siguiente paso")
    L.append("")
    siguiente = estado.get("paso_actual")
    if siguiente:
        d = def_paso(pasos, siguiente)
        L.append(f"- `{siguiente}` — {d['titulo']} ({d['etapa']})")
        L.append(f"- objetivo: {d.get('objetivo','')}")
        L.append(
            f"- sub-skills: "
            + ", ".join(f"`sub-skills/{s}`" for s in d["skills_posibles"])
        )
    else:
        L.append("- Flujo completo.")
    L.append("")

    destino.write_text("\n".join(L), encoding="utf-8")
    return destino


def cmd_render(args):
    pasos = cargar_pasos(args.pasos)
    estado = cargar_estado(args.estado)
    destino = render_state_md(estado, pasos, args.estado)
    print(f"STATE.md regenerado: {destino}")
    return 0


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def _comunes(sp):
    sp.add_argument("--estado", default=None, help="Ruta de flujo_estado.json")
    sp.add_argument("--pasos", default=None, help="Ruta de pasos.json")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Máquina de estados del flujo de innovación IRIS."
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("init", help="Crea flujo_estado.json para un proyecto nuevo")
    p.add_argument("--proyecto", required=True)
    p.add_argument("--objetivo", default=None)
    p.add_argument("--audiencia", default=None)
    p.add_argument(
        "--ruta",
        choices=["completa", "minima"],
        default="completa",
        help="minima = solo los 5 pasos de ruta_minima; el resto queda omitido",
    )
    p.add_argument("--forzar", action="store_true", help="Sobreescribe un estado existente")
    _comunes(p)
    p.set_defaults(func=cmd_init)

    p = sub.add_parser("rutas",
                       help="Los dos recorridos con el título de cada paso "
                            "(para presentarlos al usuario al arrancar)")
    _comunes(p)
    p.set_defaults(func=cmd_rutas)

    p = sub.add_parser("mostrar", help="Briefing del paso: histórico, decisiones y skills")
    p.add_argument("--paso", default=None, help="Por defecto, el paso_actual")
    _comunes(p)
    p.set_defaults(func=cmd_mostrar)

    p = sub.add_parser("iniciar", help="Marca un paso como en_curso")
    p.add_argument("--paso", required=True)
    p.add_argument("--forzar", action="store_true",
                   help="Avanzar con predecesores no omitibles todavía abiertos")
    _comunes(p)
    p.set_defaults(func=cmd_iniciar, skills=None, outputs=None, resumen=None,
                   veredicto=None, motivo=None)

    p = sub.add_parser("completar", help="Marca un paso como completado")
    p.add_argument("--paso", required=True)
    p.add_argument("--skills", nargs="*", default=[], help="Rutas de sub-skills usadas")
    p.add_argument("--outputs", nargs="*", default=[], help="Archivos generados")
    p.add_argument("--datos", default=None,
                   help="reporte.json del paso: los datos estructurados que heredan "
                        "los pasos siguientes")
    p.add_argument("--resumen", default="", help="Una línea: qué se aprendió")
    p.add_argument("--veredicto", choices=VEREDICTOS, default=None)
    p.add_argument("--forzar", action="store_true",
                   help="Cerrar con predecesores no omitibles todavía abiertos")
    _comunes(p)
    p.set_defaults(func=cmd_completar, motivo=None)

    p = sub.add_parser("omitir", help="Marca un paso como omitido por decisión del usuario")
    p.add_argument("--paso", required=True)
    p.add_argument("--motivo", required=True, help="Por qué lo omite el usuario")
    p.add_argument("--forzar", action="store_true",
                   help="Omitir un paso marcado como no omitible")
    _comunes(p)
    p.set_defaults(func=cmd_omitir, skills=None, outputs=None, resumen=None,
                   veredicto=None)

    p = sub.add_parser("fallar", help="Marca un paso como fallido")
    p.add_argument("--paso", required=True)
    p.add_argument("--motivo", required=True)
    _comunes(p)
    p.set_defaults(func=cmd_fallar, skills=None, outputs=None, resumen=None,
                   veredicto=None, forzar=False)

    p = sub.add_parser("decision", help="Registra la elección de un nodo de decisión")
    p.add_argument("--paso", required=True)
    p.add_argument("--nodo", required=True,
                   help="Texto exacto del nodo en pasos.json")
    p.add_argument("--opcion", required=True, action="append",
                   help="Opción elegida, tal como está en pasos.json. Se repite en los "
                        "nodos `multiple`: --opcion A --opcion B")
    p.add_argument("--forzar", action="store_true",
                   help="Registrar una opción o un nodo que no están en pasos.json "
                        "(queda marcado como propuesta / fuera del catálogo)")
    _comunes(p)
    p.set_defaults(func=cmd_decision)

    p = sub.add_parser("verificar",
                       help="Audita el proyecto contra pasos.json: qué se cerró sin "
                            "preguntar lo que había que preguntar")
    _comunes(p)
    p.set_defaults(func=cmd_verificar)

    p = sub.add_parser("contexto",
                       help="Inspecciona qué hereda un paso (contenido del bloque `flujo`)")
    p.add_argument("--paso", required=True)
    p.add_argument("-o", "--output", default=None)
    _comunes(p)
    p.set_defaults(func=cmd_contexto)

    p = sub.add_parser("render", help="Regenera STATE.md desde flujo_estado.json")
    _comunes(p)
    p.set_defaults(func=cmd_render)

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except ReglaDelFlujo as exc:
        print(f"Regla del flujo: {exc}", file=sys.stderr)
        return 2
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"Error: JSON inválido — {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
