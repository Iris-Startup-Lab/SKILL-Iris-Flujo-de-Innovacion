#!/usr/bin/env bash
# ============================================================================
# empaquetar_skill.sh
# Empaqueta la skill "iris-flujo-de-innovacion" en un ZIP con los documentos
# necesarios para ejecutarla, bajo el límite de 30 MB de los gestores de agentes.
#
# Uso:
#   ./empaquetar_skill.sh
#   ./empaquetar_skill.sh -o mi_skill.zip --samples --flujo
#   ./empaquetar_skill.sh --sub-skill "2.Descubrimiento/persona-profile"
#   ./empaquetar_skill.sh --list-sub-skills
#
# Opciones:
#   --sub-skill <fase/skill>  Empaqueta UNA sub-skill suelta: su carpeta +
#                             _plantilla_html/ al lado (su «Uso independiente»).
#                             Ignora las opciones de la macro.
#   --list-sub-skills  Lista las sub-skills empaquetables y termina
#   --samples          Muestras de diseño. Con --sub-skill: solo las suyas.
#   --flujo            Mapa visual "flujo-agentes-mapa-2.html" (~7.3 MB)
#   --docx             Documentos_prompts_base_docx
#   --temp             imagenes_master_examples_temp (screenshots)
#
# Requiere la utilidad `zip` (instala con: apt install zip / brew install zip).
# Si no hay `zip`, usa `tar -czf` como respaldo (salida .tar.gz).
# ============================================================================
set -euo pipefail

OUTPUT=""
SUB_SKILL=""
LIST_SUB_SKILLS=0
INCLUDE_SAMPLES=0
INCLUDE_FLUJO=0
INCLUDE_DOCX=0
INCLUDE_TEMP=0
LIMITE_MB=30

while [[ $# -gt 0 ]]; do
  case "$1" in
    -o|--output) OUTPUT="$2"; shift 2 ;;
    --sub-skill) SUB_SKILL="$2"; shift 2 ;;
    --list-sub-skills) LIST_SUB_SKILLS=1; shift ;;
    --samples) INCLUDE_SAMPLES=1; shift ;;
    --flujo)   INCLUDE_FLUJO=1; shift ;;
    --docx)    INCLUDE_DOCX=1; shift ;;
    --temp)    INCLUDE_TEMP=1; shift ;;
    *) echo "Opción desconocida: $1" >&2; exit 1 ;;
  esac
done

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# --- Sub-skills disponibles (fase/skill) ----------------------------------
listar_sub_skills() {
  [ -d "$ROOT/sub-skills" ] || return 0
  find "$ROOT/sub-skills" -mindepth 2 -maxdepth 2 -type d | sort | while read -r d; do
    [ -f "$d/AGENTE.md" ] || continue
    echo "  ${d#"$ROOT/sub-skills/"}"
  done
}

if [ "$LIST_SUB_SKILLS" = "1" ]; then
  echo "Sub-skills empaquetables (--sub-skill <fase/skill>):"
  listar_sub_skills
  exit 0
fi

# --- Lee `name` del frontmatter YAML de un SKILL.md -----------------------
# El gestor exige que la carpeta raíz del ZIP se llame igual que este `name`.
leer_skill_name() {
  local skill_md="$1" fallback="$2" n=""
  # Un solo awk, sin pipes: con `set -o pipefail`, un `head` que cierra la tubería
  # manda SIGPIPE al proceso anterior y abortaría el script en silencio.
  if [ -f "$skill_md" ]; then
    n="$(awk 'NR<=20 && /^[[:space:]]*name:[[:space:]]*/ {
                sub(/^[[:space:]]*name:[[:space:]]*/, "")
                sub(/[[:space:]]*$/, "")
                gsub(/^"|"$/, "")
                print; exit
              }' "$skill_md")"
  fi
  if [ -z "$n" ]; then
    echo "Aviso: no pude leer 'name' del frontmatter de $skill_md; uso '$fallback'." >&2
    n="$fallback"
  fi
  printf '%s' "$n"
}

# --- Copia un árbol excluyendo __pycache__ y *.pyc ------------------------
copiar_arbol() {
  local src="$1" dest="$2"
  mkdir -p "$dest"
  if command -v rsync >/dev/null 2>&1; then
    rsync -a --exclude '__pycache__/' --exclude '*.pyc' "$src/" "$dest/"
  else
    # `shift` saca el destino de los posicionales: sin él, el `for` lo trataría
    # como un archivo más y cp protestaría por recibir un directorio.
    (cd "$src" && find . -type f ! -path '*__pycache__*' ! -name '*.pyc' -exec sh -c '
      base="$1"; shift
      for f; do dst="$base/$f"; mkdir -p "$(dirname "$dst")"; cp "$f" "$dst"; done
    ' sh "$dest" {} +)
  fi
}

MODO="macro"
ROOT_FILES=()
FOLDERS=()

if [ -n "$SUB_SKILL" ]; then
  # --- Modo sub-skill suelta: su carpeta + _plantilla_html/ ---------------
  MODO="sub-skill"
  REL="${SUB_SKILL#sub-skills/}"
  REL="${REL%/}"
  SRC_SKILL="$ROOT/sub-skills/$REL"

  if [ ! -d "$SRC_SKILL" ]; then
    echo "No existe la sub-skill: sub-skills/$REL" >&2
    echo "Sub-skills disponibles:" >&2
    listar_sub_skills >&2
    exit 1
  fi
  if [ ! -f "$SRC_SKILL/AGENTE.md" ]; then
    echo "sub-skills/$REL no tiene AGENTE.md: no es una sub-skill." >&2
    exit 1
  fi

  NOMBRE="$(basename "$REL")"
  FASE="$(dirname "$REL")"
  [ -n "$OUTPUT" ] || OUTPUT="$NOMBRE.zip"

  for par in "--flujo:$INCLUDE_FLUJO" "--docx:$INCLUDE_DOCX" "--temp:$INCLUDE_TEMP"; do
    if [ "${par#*:}" = "1" ]; then
      echo "Aviso: ${par%%:*} no aplica con --sub-skill: se ignora." >&2
    fi
  done
else
  # --- Modo macro: archivos raíz + carpetas del flujo --------------------
  [ -n "$OUTPUT" ] || OUTPUT="iris-flujo-de-innovacion.zip"

  ROOT_FILES=(
    "SKILL.md" "pasos.json" "STATE.md" "AGENTS.md" "README.md"
    "flujo_agentes.md" "flujo_mermaid.md"
    "PLAN_CONVERSION_SKILLS.md" "PLAN_MEDICION_TOKENS.md"
    "_template_generador_skill.py"
    "CLAUDE.md" "actualizar_claude.ps1" "actualizar_claude.sh"
  )

  FOLDERS=(
    "sub-skills" "scripts" "_plantilla_html" "Designs_files"
    "imagenes_iconos_etc" "Documentos_prompts_base_md"
  )

  [ "$INCLUDE_SAMPLES" = "1" ] && FOLDERS+=("sub-skills_sample_outputs")
  [ "$INCLUDE_DOCX"   = "1" ] && FOLDERS+=("Documentos_prompts_base_docx")
  [ "$INCLUDE_TEMP"   = "1" ] && FOLDERS+=("imagenes_master_examples_temp")
  [ "$INCLUDE_FLUJO"  = "1" ] && ROOT_FILES+=("flujo-agentes-mapa-2.html")
fi

# --- Nombre de la carpeta raíz del ZIP ------------------------------------
# El gestor exige UNA sola carpeta de primer nivel, llamada igual que el `name`
# del frontmatter. Con los archivos sueltos en la raíz, el ZIP se rechaza.
if [ "$MODO" = "sub-skill" ]; then
  SKILL_NAME="$(leer_skill_name "$SRC_SKILL/AGENTE.md" "$NOMBRE")"
else
  SKILL_NAME="$(leer_skill_name "$ROOT/SKILL.md" "iris-flujo-de-innovacion")"
fi
case "$SKILL_NAME" in
  *[!a-z0-9-]*) echo "Aviso: el 'name' del frontmatter es '$SKILL_NAME'. El gestor solo admite minúsculas, números y guiones." >&2 ;;
esac

STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT
# Todo se copia DENTRO de la carpeta raíz de la skill.
RAIZ="$STAGE/$SKILL_NAME"
mkdir -p "$RAIZ"

if [ "$MODO" = "sub-skill" ]; then
  # La sub-skill ES la raíz del ZIP: su contenido va directo ahí.
  copiar_arbol "$SRC_SKILL" "$RAIZ"

  # En el repo el archivo de instrucciones se llama AGENTE.md, porque el gestor exige
  # EXACTAMENTE UN SKILL.md por ZIP y la macro ya usa ese nombre en su raíz. Aquí la
  # sub-skill sí es la skill del ZIP, así que recupera el nombre SKILL.md —en el
  # archivo y en las referencias de texto, para que el paquete sea coherente.
  if [ -f "$RAIZ/AGENTE.md" ]; then
    mv "$RAIZ/AGENTE.md" "$RAIZ/SKILL.md"
    find "$RAIZ" -type f \( -name '*.md' -o -name '*.py' \) \
      -exec sed -i 's|AGENTE\.md|SKILL.md|g' {} +
  fi

  if [ ! -d "$ROOT/_plantilla_html" ]; then
    echo "Falta _plantilla_html/: la sub-skill no puede generar su HTML sin ella." >&2
    exit 1
  fi
  # Dentro de la raíz: todo el ZIP tiene que colgar de una sola carpeta.
  copiar_arbol "$ROOT/_plantilla_html" "$RAIZ/_plantilla_html"

  if [ "$INCLUDE_SAMPLES" = "1" ]; then
    if [ -d "$ROOT/sub-skills_sample_outputs/$REL" ]; then
      copiar_arbol "$ROOT/sub-skills_sample_outputs/$REL" "$RAIZ/sample_outputs"
    else
      echo "Aviso: sin muestras de diseño para $REL." >&2
    fi
  fi
else
  # --- Copiar archivos raíz -----------------------------------------------
  for f in "${ROOT_FILES[@]}"; do
    if [ -f "$ROOT/$f" ]; then cp "$ROOT/$f" "$RAIZ/"; fi
  done

  # --- Copiar carpetas (excluye __pycache__ y *.pyc) ----------------------
  for d in "${FOLDERS[@]}"; do
    [ -d "$ROOT/$d" ] || continue
    copiar_arbol "$ROOT/$d" "$RAIZ/$d"
  done
fi

# --- Guardia: nombres seguros para el gestor ------------------------------
# El gestor rechaza el ZIP con «Zip file contains path with invalid characters».
# No documenta qué acepta, así que se exige el juego conservador que sí funciona:
# letras, dígitos, punto, guion y guion bajo. Fuera acentos, espacios y '&'.
# El basename se saca con sed, no con `-exec basename`: un proceso por archivo
# hacía que el empaquetado de la macro tardara minutos.
# El `|| true` es obligatorio: sin coincidencias grep sale con 1 y, con
# `set -e -o pipefail`, abortaría el script justo cuando todo está bien.
MALOS="$(cd "$STAGE" && LC_ALL=C find . -mindepth 1 | sed 's|.*/||' \
         | LC_ALL=C grep -v '^[A-Za-z0-9._-]*$' | sort -u || true)"
if [ -n "$MALOS" ]; then
  N=$(printf '%s\n' "$MALOS" | wc -l)
  echo "AVISO: hay $N nombre(s) con caracteres que el gestor puede rechazar" >&2
  echo "       ('Zip file contains path with invalid characters')." >&2
  printf '%s\n' "$MALOS" | head -12 | sed 's|^|    |' >&2
  echo "    Renómbralos a [A-Za-z0-9._-] (ver AGENTS.md §5, «Rutas seguras»)." >&2
fi

# --- Guardia: exactamente un SKILL.md -------------------------------------
# El gestor responde «Zip must contain exactly one SKILL.md file» si hay más de uno.
# Por eso las sub-skills guardan sus instrucciones en AGENTE.md.
N_SKILL=$(find "$STAGE" -type f -name 'SKILL.md' | wc -l)
if [ "$N_SKILL" -ne 1 ]; then
  echo "AVISO: el ZIP lleva $N_SKILL SKILL.md y el gestor exige exactamente 1." >&2
  find "$STAGE" -type f -name 'SKILL.md' | sed "s|^$STAGE/|    |" >&2
  echo "    Las sub-skills usan AGENTE.md (ver AGENTS.md §5)." >&2
fi

# --- Comprimir ------------------------------------------------------------
OUT_ABS="$OUTPUT"
# Absoluta en POSIX (/...) o en Windows (C:\... / C:/...), por si corre en Git Bash.
if [[ "$OUT_ABS" != /* && ! "$OUT_ABS" =~ ^[A-Za-z]:[\\/] ]]; then
  OUT_ABS="$ROOT/$OUTPUT"
fi
rm -f "$OUT_ABS"

if command -v zip >/dev/null 2>&1; then
  (cd "$STAGE" && zip -qr "$OUT_ABS" .)
else
  echo "Aviso: 'zip' no disponible, generando .tar.gz como respaldo." >&2
  # A stdout y redirigido: así tar no interpreta la ruta (un `C:` lo leería como host).
  OUT_ABS="${OUT_ABS%.zip}.tar.gz"
  tar -C "$STAGE" -czf - . > "$OUT_ABS"
fi

# --- Guardia: ninguna entrada con barra invertida --------------------------
# `zip` y `tar` en POSIX escriben la barra correcta, pero se comprueba igual: es el
# fallo que rechazó el paquete y no se ve en las herramientas que normalizan rutas.
if command -v python3 >/dev/null 2>&1 || command -v python >/dev/null 2>&1; then
  PY="$(command -v python3 || command -v python)"
  "$PY" - "$OUT_ABS" <<'PYEOF' || true
import struct, sys
datos = open(sys.argv[1], "rb").read()
FIRMA, pos, n, malos = b"PK\x01\x02", 0, 0, 0
pos = datos.find(FIRMA)
while pos != -1:
    largo = struct.unpack_from("<H", datos, pos + 28)[0]
    extra = struct.unpack_from("<H", datos, pos + 30)[0]
    coment = struct.unpack_from("<H", datos, pos + 32)[0]
    n += 1
    if b"\x5c" in datos[pos + 46: pos + 46 + largo]:
        malos += 1
    pos = datos.find(FIRMA, pos + 46 + largo + extra + coment)
if malos:
    print(f"AVISO: {malos} de {n} entradas del ZIP llevan barra invertida. El gestor "
          f"lo rechazara con 'Zip file contains path with invalid characters'.",
          file=sys.stderr)
PYEOF
fi

SIZE=$(stat -c%s "$OUT_ABS" 2>/dev/null || stat -f%z "$OUT_ABS")
MB=$(awk "BEGIN{printf \"%.2f\", $SIZE/1048576}")
echo ""
echo "ZIP generado: $OUT_ABS ($MB MB)"
echo "  carpeta raiz del ZIP: $SKILL_NAME/  (debe coincidir con el 'name' del frontmatter)"
if [ "$MODO" = "sub-skill" ]; then
  echo "  sub-skill suelta: $FASE/$NOMBRE"
  echo "  contenido: $SKILL_NAME/SKILL.md + $SKILL_NAME/_plantilla_html/"
  echo "  genera su HTML (desde $SKILL_NAME/): python _plantilla_html/scripts/generar_html.py --data reporte.json --sin-flujo -o reporte.html"
fi
if awk "BEGIN{exit !($SIZE > $LIMITE_MB*1048576)}"; then
  echo "ADVERTENCIA: excede el límite de $LIMITE_MB MB."
else
  echo "OK: bajo el límite de $LIMITE_MB MB."
fi
