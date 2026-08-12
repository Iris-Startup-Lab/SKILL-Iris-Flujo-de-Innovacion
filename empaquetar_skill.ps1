# ============================================================================
# empaquetar_skill.ps1
# Empaqueta la skill "iris-flujo-de-innovacion" en un ZIP con los documentos
# necesarios para ejecutarla, manteniéndose bajo el límite de 30 MB de los
# gestores de agentes.
#
# Uso:
#   .\empaquetar_skill.ps1
#   .\empaquetar_skill.ps1 -Output "mi_skill.zip"
#   .\empaquetar_skill.ps1 -IncludeSamples -IncludeFlujoMap
#
# Opciones:
#   -IncludeSamples   Incluye sub-skills_sample_outputs (muestras de diseño)
#   -IncludeFlujoMap  Incluye "Flujo Agentes mapa 2.html" (mapa visual ~7.3 MB)
#   -IncludeDocx      Incluye Documentos_prompts_base_docx
#   -IncludeTemp      Incluye imagenes_master_examples_temp (screenshots)
# ============================================================================
param(
    [string]$Output = "iris-flujo-de-innovacion.zip",
    [switch]$IncludeSamples,
    [switch]$IncludeFlujoMap,
    [switch]$IncludeDocx,
    [switch]$IncludeTemp
)

$ErrorActionPreference = "Stop"
$root = $PSScriptRoot
$LIMITE_MB = 30

# --- Archivos raíz necesarios ---------------------------------------------
$rootFiles = @(
    "SKILL.md",
    "pasos.json",
    "STATE.md",
    "AGENTS.md",
    "README.md",
    "flujo_agentes.md",
    "flujo_mermaid.md",
    "PLAN_CONVERSION_SKILLS.md",
    "_template_generador_skill.py"
)

# --- Carpetas necesarias --------------------------------------------------
$folders = @(
    "sub-skills",
    "scripts",
    "_plantilla_html",
    "Designs_files",
    "imagenes_iconos_etc",
    "Documentos_prompts_base_md"
)

# --- Opcionales -----------------------------------------------------------
if ($IncludeSamples) { $folders += "sub-skills_sample_outputs" }
if ($IncludeDocx)   { $folders += "Documentos_prompts_base_docx" }
if ($IncludeTemp)   { $folders += "imagenes_master_examples_temp" }
if ($IncludeFlujoMap) { $rootFiles += "Flujo Agentes mapa 2.html" }

# --- Staging --------------------------------------------------------------
$stage = Join-Path ([IO.Path]::GetTempPath()) ("iris_skill_" + [Guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $stage | Out-Null

try {
    # Archivos raíz
    foreach ($f in $rootFiles) {
        $src = Join-Path $root $f
        if (Test-Path -LiteralPath $src) {
            Copy-Item -LiteralPath $src -Destination $stage -Force
        } else {
            Write-Warning "Omitido (no existe): $f"
        }
    }

    # Carpetas, excluyendo __pycache__ y *.pyc
    foreach ($d in $folders) {
        $src = Join-Path $root $d
        if (-not (Test-Path -LiteralPath $src)) {
            Write-Warning "Omitida (no existe): $d"
            continue
        }
        $dest = Join-Path $stage $d
        New-Item -ItemType Directory -Path $dest -Force | Out-Null
        $files = Get-ChildItem -LiteralPath $src -Recurse -File | Where-Object {
            $_.FullName -notmatch "__pycache__" -and $_.Extension -ne ".pyc"
        }
        foreach ($file in $files) {
            $rel = $file.FullName.Substring($src.Length).TrimStart("\", "/")
            $target = Join-Path $dest $rel
            $parent = Split-Path $target -Parent
            if (-not (Test-Path -LiteralPath $parent)) {
                New-Item -ItemType Directory -Path $parent -Force | Out-Null
            }
            Copy-Item -LiteralPath $file.FullName -Destination $target -Force
        }
    }

    # --- Comprimir --------------------------------------------------------
    $outPath = $Output
    if (-not [IO.Path]::IsPathRooted($outPath)) { $outPath = Join-Path $root $outPath }
    if (Test-Path -LiteralPath $outPath) { Remove-Item -LiteralPath $outPath -Force }

    Compress-Archive -Path (Join-Path $stage "*") -DestinationPath $outPath -CompressionLevel Optimal

    # --- Reporte ----------------------------------------------------------
    $size = (Get-Item -LiteralPath $outPath).Length
    $mb = [math]::Round($size / 1MB, 2)
    Write-Host ""
    Write-Host "ZIP generado: $outPath ($mb MB)"
    if ($size -gt ($LIMITE_MB * 1MB)) {
        Write-Warning "Excede el límite de $LIMITE_MB MB de los gestores de agentes."
    } else {
        Write-Host "OK: bajo el límite de $LIMITE_MB MB."
    }
}
finally {
    if (Test-Path -LiteralPath $stage) { Remove-Item -LiteralPath $stage -Recurse -Force }
}
