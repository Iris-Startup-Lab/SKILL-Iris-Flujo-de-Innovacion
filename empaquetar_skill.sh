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
#   --flujo            Mapa visual "Flujo Agentes mapa 2.html" (~7.3 MB)
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
    [ -f "$d/SKILL.md" ] || continue
    echo "  ${d#"$ROOT/sub-skills/"}"
  done
}

if [ "$LIST_SUB_SKILLS" = "1" ]; then
  echo "Sub-skills empaquetables (--sub-skill <fase/skill>):"
  listar_sub_skills
  exit 0
fi

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
  if [ ! -f "$SRC_SKILL/SKILL.md" ]; then
    echo "sub-skills/$REL no tiene SKILL.md: no es una sub-skill." >&2
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
  )

  FOLDERS=(
    "sub-skills" "scripts" "_plantilla_html" "Designs_files"
    "imagenes_iconos_etc" "Documentos_prompts_base_md"
  )

  [ "$INCLUDE_SAMPLES" = "1" ] && FOLDERS+=("sub-skills_sample_outputs")
  [ "$INCLUDE_DOCX"   = "1" ] && FOLDERS+=("Documentos_prompts_base_docx")
  [ "$INCLUDE_TEMP"   = "1" ] && FOLDERS+=("imagenes_master_examples_temp")
  [ "$INCLUDE_FLUJO"  = "1" ] && ROOT_FILES+=("Flujo Agentes mapa 2.html")
fi

STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT

if [ "$MODO" = "sub-skill" ]; then
  # La sub-skill con su nombre corto, para que quede al lado de la plantilla.
  copiar_arbol "$SRC_SKILL" "$STAGE/$NOMBRE"

  if [ ! -d "$ROOT/_plantilla_html" ]; then
    echo "Falta _plantilla_html/: la sub-skill no puede generar su HTML sin ella." >&2
    exit 1
  fi
  copiar_arbol "$ROOT/_plantilla_html" "$STAGE/_plantilla_html"

  if [ "$INCLUDE_SAMPLES" = "1" ]; then
    if [ -d "$ROOT/sub-skills_sample_outputs/$REL" ]; then
      copiar_arbol "$ROOT/sub-skills_sample_outputs/$REL" "$STAGE/sample_outputs"
    else
      echo "Aviso: sin muestras de diseño para $REL." >&2
    fi
  fi
else
  # --- Copiar archivos raíz -----------------------------------------------
  for f in "${ROOT_FILES[@]}"; do
    if [ -f "$ROOT/$f" ]; then cp "$ROOT/$f" "$STAGE/"; fi
  done

  # --- Copiar carpetas (excluye __pycache__ y *.pyc) ----------------------
  for d in "${FOLDERS[@]}"; do
    [ -d "$ROOT/$d" ] || continue
    copiar_arbol "$ROOT/$d" "$STAGE/$d"
  done
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

SIZE=$(stat -c%s "$OUT_ABS" 2>/dev/null || stat -f%z "$OUT_ABS")
MB=$(awk "BEGIN{printf \"%.2f\", $SIZE/1048576}")
echo ""
echo "ZIP generado: $OUT_ABS ($MB MB)"
if [ "$MODO" = "sub-skill" ]; then
  echo "  sub-skill suelta: $FASE/$NOMBRE"
  echo "  contenido: $NOMBRE/ + _plantilla_html/"
  echo "  genera su HTML con: python _plantilla_html/scripts/generar_html.py --data reporte.json --sin-flujo -o reporte.html"
fi
if awk "BEGIN{exit !($SIZE > $LIMITE_MB*1048576)}"; then
  echo "ADVERTENCIA: excede el límite de $LIMITE_MB MB."
else
  echo "OK: bajo el límite de $LIMITE_MB MB."
fi
