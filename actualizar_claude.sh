#!/usr/bin/env bash
# ============================================================================
# actualizar_claude.sh
# Clona/sincroniza AGENTS.md a CLAUDE.md a demanda para compatibilidad
# con Claude Code, Claude Desktop y otros entornos que leen CLAUDE.md.
#
# Uso:
#   ./actualizar_claude.sh
# ============================================================================
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="$ROOT/AGENTS.md"
DEST="$ROOT/CLAUDE.md"

if [ ! -f "$SRC" ]; then
  echo "Error: No se encontró el archivo origen: $SRC" >&2
  exit 1
fi

cp "$SRC" "$DEST"
echo "============================================================"
echo " Sincronización de AGENTS.md -> CLAUDE.md exitosa"
echo " Origen  : AGENTS.md ($(wc -c < "$SRC") bytes)"
echo " Destino : CLAUDE.md ($(wc -c < "$DEST") bytes)"
echo " Entorno : Listo para Claude Code / Claude Desktop / Antigravity"
echo "============================================================"
