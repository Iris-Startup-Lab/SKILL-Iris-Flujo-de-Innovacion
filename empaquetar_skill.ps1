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
#   .\empaquetar_skill.ps1 -SubSkill "2.Descubrimiento/persona-profile"
#   .\empaquetar_skill.ps1 -ListSubSkills
#
# Opciones:
#   -SubSkill <fase/skill>  Empaqueta UNA sub-skill suelta: su carpeta +
#                           _plantilla_html/ al lado (su «Uso independiente»).
#                           Ignora las opciones de la macro.
#   -ListSubSkills    Lista las sub-skills empaquetables y termina
#   -IncludeSamples   Incluye sub-skills_sample_outputs (muestras de diseño).
#                     Con -SubSkill: solo las muestras de esa sub-skill.
#   -IncludeFlujoMap  Incluye "Flujo Agentes mapa 2.html" (mapa visual ~7.3 MB)
#   -IncludeDocx      Incluye Documentos_prompts_base_docx
#   -IncludeTemp      Incluye imagenes_master_examples_temp (screenshots)
# ============================================================================
param(
    [string]$Output = "iris-flujo-de-innovacion.zip",
    [string]$SubSkill,
    [switch]$ListSubSkills,
    [switch]$IncludeSamples,
    [switch]$IncludeFlujoMap,
    [switch]$IncludeDocx,
    [switch]$IncludeTemp
)

$ErrorActionPreference = "Stop"
$root = $PSScriptRoot
$LIMITE_MB = 30

# --- Sub-skills disponibles (fase/skill) ----------------------------------
function Get-SubSkills {
    $base = Join-Path $root "sub-skills"
    if (-not (Test-Path -LiteralPath $base)) { return @() }
    Get-ChildItem -LiteralPath $base -Directory | ForEach-Object {
        $fase = $_.Name
        Get-ChildItem -LiteralPath $_.FullName -Directory |
            Where-Object { Test-Path -LiteralPath (Join-Path $_.FullName "SKILL.md") } |
            ForEach-Object { "$fase/$($_.Name)" }
    }
}

if ($ListSubSkills) {
    Write-Host "Sub-skills empaquetables (-SubSkill <fase/skill>):"
    Get-SubSkills | Sort-Object | ForEach-Object { Write-Host "  $_" }
    exit 0
}

# --- Copia un árbol de archivos excluyendo __pycache__ y *.pyc ------------
function Copy-Tree {
    param([string]$Src, [string]$Dest)
    New-Item -ItemType Directory -Path $Dest -Force | Out-Null
    $files = Get-ChildItem -LiteralPath $Src -Recurse -File | Where-Object {
        $_.FullName -notmatch "__pycache__" -and $_.Extension -ne ".pyc"
    }
    foreach ($file in $files) {
        $rel = $file.FullName.Substring($Src.Length).TrimStart("\", "/")
        $target = Join-Path $Dest $rel
        $parent = Split-Path $target -Parent
        if (-not (Test-Path -LiteralPath $parent)) {
            New-Item -ItemType Directory -Path $parent -Force | Out-Null
        }
        Copy-Item -LiteralPath $file.FullName -Destination $target -Force
    }
}

$rootFiles = @()
$folders = @()
$modo = "macro"

if ($SubSkill) {
    # --- Modo sub-skill suelta: su carpeta + _plantilla_html/ -------------
    $modo = "sub-skill"
    $rel = $SubSkill.Trim() -replace "/", "\"
    $rel = $rel -replace "^sub-skills\\", ""
    $rel = $rel.Trim("\")
    $srcSkill = Join-Path (Join-Path $root "sub-skills") $rel

    if (-not (Test-Path -LiteralPath $srcSkill -PathType Container)) {
        Write-Host "No existe la sub-skill: sub-skills\$rel" -ForegroundColor Red
        Write-Host "Sub-skills disponibles:"
        Get-SubSkills | Sort-Object | ForEach-Object { Write-Host "  $_" }
        exit 1
    }
    if (-not (Test-Path -LiteralPath (Join-Path $srcSkill "SKILL.md"))) {
        Write-Host "sub-skills\$rel no tiene SKILL.md: no es una sub-skill." -ForegroundColor Red
        exit 1
    }

    $nombre = Split-Path $rel -Leaf
    $fase = Split-Path $rel -Parent
    if (-not $PSBoundParameters.ContainsKey("Output")) { $Output = "$nombre.zip" }

    foreach ($o in @("IncludeFlujoMap", "IncludeDocx", "IncludeTemp")) {
        if ($PSBoundParameters.ContainsKey($o)) {
            Write-Warning "-$o no aplica con -SubSkill: se ignora."
        }
    }
} else {
    # --- Modo macro: archivos raíz + carpetas del flujo -------------------
    $rootFiles = @(
        "SKILL.md",
        "pasos.json",
        "STATE.md",
        "AGENTS.md",
        "README.md",
        "flujo_agentes.md",
        "flujo_mermaid.md",
        "PLAN_CONVERSION_SKILLS.md",
        "PLAN_MEDICION_TOKENS.md",
        "_template_generador_skill.py"
    )

    $folders = @(
        "sub-skills",
        "scripts",
        "_plantilla_html",
        "Designs_files",
        "imagenes_iconos_etc",
        "Documentos_prompts_base_md"
    )

    if ($IncludeSamples)  { $folders += "sub-skills_sample_outputs" }
    if ($IncludeDocx)     { $folders += "Documentos_prompts_base_docx" }
    if ($IncludeTemp)     { $folders += "imagenes_master_examples_temp" }
    if ($IncludeFlujoMap) { $rootFiles += "Flujo Agentes mapa 2.html" }
}

# --- Staging --------------------------------------------------------------
$stage = Join-Path ([IO.Path]::GetTempPath()) ("iris_skill_" + [Guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $stage | Out-Null

try {
    if ($modo -eq "sub-skill") {
        # La sub-skill con su nombre corto, para que quede al lado de la plantilla.
        Copy-Tree -Src $srcSkill -Dest (Join-Path $stage $nombre)

        $srcPlantilla = Join-Path $root "_plantilla_html"
        if (-not (Test-Path -LiteralPath $srcPlantilla)) {
            throw "Falta _plantilla_html\: la sub-skill no puede generar su HTML sin ella."
        }
        Copy-Tree -Src $srcPlantilla -Dest (Join-Path $stage "_plantilla_html")

        if ($IncludeSamples) {
            $srcSample = Join-Path (Join-Path $root "sub-skills_sample_outputs") $rel
            if (Test-Path -LiteralPath $srcSample) {
                Copy-Tree -Src $srcSample -Dest (Join-Path $stage "sample_outputs")
            } else {
                Write-Warning "Sin muestras de diseño para $rel (sub-skills_sample_outputs\$rel)."
            }
        }
    } else {
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
            Copy-Tree -Src $src -Dest (Join-Path $stage $d)
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
    if ($modo -eq "sub-skill") {
        Write-Host "  sub-skill suelta: $fase/$nombre"
        Write-Host "  contenido: $nombre\ + _plantilla_html\"
        Write-Host "  genera su HTML con: python _plantilla_html/scripts/generar_html.py --data reporte.json --sin-flujo -o reporte.html"
    }
    if ($size -gt ($LIMITE_MB * 1MB)) {
        Write-Warning "Excede el límite de $LIMITE_MB MB de los gestores de agentes."
    } else {
        Write-Host "OK: bajo el límite de $LIMITE_MB MB."
    }
}
finally {
    if (Test-Path -LiteralPath $stage) { Remove-Item -LiteralPath $stage -Recurse -Force }
}
