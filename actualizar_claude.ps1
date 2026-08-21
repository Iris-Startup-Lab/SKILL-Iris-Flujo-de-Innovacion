# ============================================================================
# actualizar_claude.ps1
# Clona/sincroniza AGENTS.md a CLAUDE.md a demanda para compatibilidad
# con Claude Code, Claude Desktop y otros entornos que leen CLAUDE.md.
#
# Uso:
#   .\actualizar_claude.ps1
# ============================================================================
[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}
$root = $PSScriptRoot

$src = Join-Path $root "AGENTS.md"
$dest = Join-Path $root "CLAUDE.md"

if (-not (Test-Path -LiteralPath $src)) {
    Write-Error "No se encontro el archivo origen: $src"
    exit 1
}

try {
    # Copia exacta en binario para preservar codificacion UTF-8 e integridad
    [System.IO.File]::Copy($src, $dest, $true)
    $srcInfo = Get-Item -LiteralPath $src
    $destInfo = Get-Item -LiteralPath $dest
    x|
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host " Sincronizacion de AGENTS.md -> CLAUDE.md exitosa" -ForegroundColor Green
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host " Origen  : $($srcInfo.Name) ($($srcInfo.Length) bytes, modificado $($srcInfo.LastWriteTime))" -ForegroundColor Gray
    Write-Host " Destino : $($destInfo.Name) ($($destInfo.Length) bytes)" -ForegroundColor Gray
    Write-Host " Entorno : Listo para Claude Code / Claude Desktop / Antigravity" -ForegroundColor Yellow
    Write-Host "============================================================" -ForegroundColor Cyan
} catch {
    Write-Error "Error al copiar AGENTS.md a CLAUDE.md: $_"
    exit 1
}
