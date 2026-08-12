#!/usr/bin/env bash
# ============================================================================
# empaquetar_skill.sh
# Empaqueta la skill "iris-flujo-de-innovacion" en un ZIP con los documentos
# necesarios para ejecutarla, bajo el límite de 30 MB de los gestores de agentes.
#
# Uso:
#   ./empaquetar_skill.sh
#   ./empaquetar_skill.sh -o mi_skill.zip --samples --flujo
#
# Requiere la utilidad `zip` (instala con: apt install zip / brew install zip).
# Si no hay `zip`, usa `tar -czf` como respaldo (salida .tar.gz).
# ============================================================================
set -euo pipefail

OUTPUT="iris-flujo-de-innovacion.zip"
INCLUDE_SAMPLES=0
INCLUDE_FLUJO=0
INCLUDE_DOCX=0
INCLUDE_TEMP=0
LIMITE_MB=30

while [[ $# -gt 0 ]]; do
  case "$1" in
    -o|--output) OUTPUT="$2"; shift 2 ;;
    --samples) INCLUDE_SAMPLES=1; shift ;;
    --flujo)   INCLUDE_FLUJO=1; shift ;;
    --docx)    INCLUDE_DOCX=1; shift ;;
    --temp)    INCLUDE_TEMP=1; shift ;;
    *) echo "Opción desconocida: $1" >&2; exit 1 ;;
  esac
done

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT

# --- Archivos raíz necesarios ---------------------------------------------
ROOT_FILES=(
  "SKILL.md" "pasos.json" "STATE.md" "AGENTS.md" "README.md"
  "flujo_agentes.md" "flujo_mermaid.md"
  "PLAN_CONVERSION_SKILLS.md" "_template_generador_skill.py"
)

# --- Carpetas necesarias --------------------------------------------------
FOLDERS=(
  "sub-skills" "scripts" "_plantilla_html" "Designs_files"
  "imagenes_iconos_etc" "Documentos_prompts_base_md"
)

[ "$INCLUDE_SAMPLES" = "1" ] && FOLDERS+=("sub-skills_sample_outputs")
[ "$INCLUDE_DOCX"   = "1" ] && FOLDERS+=("Documentos_prompts_base_docx")
[ "$INCLUDE_TEMP"   = "1" ] && FOLDERS+=("imagenes_master_examples_temp")
[ "$INCLUDE_FLUJO"  = "1" ] && ROOT_FILES+=("Flujo Agentes mapa 2.html")

# --- Copiar archivos raíz -------------------------------------------------
for f in "${ROOT_FILES[@]}"; do
  if [ -f "$ROOT/$f" ]; then cp "$ROOT/$f" "$STAGE/"; fi
done

# --- Copiar carpetas (excluye __pycache__ y *.pyc) ------------------------
for d in "${FOLDERS[@]}"; do
  [ -d "$ROOT/$d" ] || continue
  mkdir -p "$STAGE/$d"
  # rsync si está disponible, si no find+cp
  if command -v rsync >/dev/null 2>&1; then
    rsync -a --exclude '__pycache__/' --exclude '*.pyc' "$ROOT/$d/" "$STAGE/$d/"
  else
    (cd "$ROOT/$d" && find . -type f ! -path '*__pycache__*' ! -name '*.pyc' -exec sh -c '
      for src; do dst="$1/$src"; mkdir -p "$(dirname "$dst")"; cp "$src" "$dst"; done
    ' sh "$STAGE/$d" {} +)
  fi
done

# --- Comprimir ------------------------------------------------------------
OUT_ABS="$OUTPUT"
[[ "$OUT_ABS" = /* ]] || OUT_ABS="$ROOT/$OUTPUT"
rm -f "$OUT_ABS"

if command -v zip >/dev/null 2>&1; then
  (cd "$STAGE" && zip -qr "$OUT_ABS" .)
else
  echo "Aviso: 'zip' no disponible, generando .tar.gz como respaldo." >&2
  tar -C "$STAGE" -czf "${OUT_ABS%.zip}.tar.gz" .
  OUT_ABS="${OUT_ABS%.zip}.tar.gz"
fi

SIZE=$(stat -c%s "$OUT_ABS" 2>/dev/null || stat -f%z "$OUT_ABS")
MB=$(awk "BEGIN{printf \"%.2f\", $SIZE/1048576}")
echo ""
echo "ZIP generado: $OUT_ABS ($MB MB)"
if awk "BEGIN{exit !($SIZE > $LIMITE_MB*1048576)}"; then
  echo "ADVERTENCIA: excede el límite de $LIMITE_MB MB."
else
  echo "OK: bajo el límite de $LIMITE_MB MB."
fi
