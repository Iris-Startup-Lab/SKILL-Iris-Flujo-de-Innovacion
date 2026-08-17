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
#   -IncludeFlujoMap  Incluye "flujo-agentes-mapa-2.html" (mapa visual ~7.3 MB)
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
            Where-Object { Test-Path -LiteralPath (Join-Path $_.FullName "AGENTE.md") } |
            ForEach-Object { "$fase/$($_.Name)" }
    }
}

if ($ListSubSkills) {
    Write-Host "Sub-skills empaquetables (-SubSkill <fase/skill>):"
    Get-SubSkills | Sort-Object | ForEach-Object { Write-Host "  $_" }
    exit 0
}

# --- Lee `name` del frontmatter YAML de un SKILL.md -----------------------
# El gestor exige que la carpeta raíz del ZIP se llame igual que este `name`.
function Get-SkillName {
    param([string]$SkillMd, [string]$Fallback)
    if (Test-Path -LiteralPath $SkillMd) {
        foreach ($linea in Get-Content -LiteralPath $SkillMd -TotalCount 20) {
            if ($linea -match '^\s*name:\s*"?([^"#]+?)"?\s*$') {
                return $Matches[1].Trim()
            }
        }
    }
    Write-Warning "No pude leer `name` del frontmatter de $SkillMd; uso '$Fallback'."
    return $Fallback
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
    if (-not (Test-Path -LiteralPath (Join-Path $srcSkill "AGENTE.md"))) {
        Write-Host "sub-skills\$rel no tiene AGENTE.md: no es una sub-skill." -ForegroundColor Red
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
    if ($IncludeFlujoMap) { $rootFiles += "flujo-agentes-mapa-2.html" }
}

# --- Nombre de la carpeta raíz del ZIP ------------------------------------
# El gestor exige UNA sola carpeta de primer nivel, llamada igual que el `name`
# del frontmatter. Con los archivos sueltos en la raíz, el ZIP se rechaza.
if ($modo -eq "sub-skill") {
    $skillName = Get-SkillName (Join-Path $srcSkill "AGENTE.md") $nombre
} else {
    $skillName = Get-SkillName (Join-Path $root "SKILL.md") "iris-flujo-de-innovacion"
}
if ($skillName -notmatch '^[a-z0-9-]+$') {
    Write-Warning ("El `name` del frontmatter es '$skillName'. El gestor solo admite " +
                   "minúsculas, números y guiones.")
}

# --- Staging --------------------------------------------------------------
$stage = Join-Path ([IO.Path]::GetTempPath()) ("iris_skill_" + [Guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $stage | Out-Null
# Todo se copia DENTRO de la carpeta raíz de la skill.
$raiz = Join-Path $stage $skillName
New-Item -ItemType Directory -Path $raiz | Out-Null

try {
    if ($modo -eq "sub-skill") {
        # La sub-skill ES la raíz del ZIP: su contenido va directo ahí.
        Copy-Tree -Src $srcSkill -Dest $raiz

        # En el repo el archivo de instrucciones se llama AGENTE.md, porque el gestor
        # exige EXACTAMENTE UN SKILL.md por ZIP y la macro ya usa ese nombre en su raíz.
        # Aquí la sub-skill sí es la skill del ZIP, así que recupera el nombre SKILL.md
        # —en el archivo y en las referencias de texto, para que el paquete sea coherente.
        $agente = Join-Path $raiz "AGENTE.md"
        if (Test-Path -LiteralPath $agente) {
            Rename-Item -LiteralPath $agente -NewName "SKILL.md"
            Get-ChildItem -LiteralPath $raiz -Recurse -File -Include *.md, *.py |
                ForEach-Object {
                    $txt = Get-Content -LiteralPath $_.FullName -Raw
                    if ($txt -match "AGENTE\.md") {
                        Set-Content -LiteralPath $_.FullName -NoNewline `
                            -Value ($txt -replace "AGENTE\.md", "SKILL.md")
                    }
                }
        }

        $srcPlantilla = Join-Path $root "_plantilla_html"
        if (-not (Test-Path -LiteralPath $srcPlantilla)) {
            throw "Falta _plantilla_html\: la sub-skill no puede generar su HTML sin ella."
        }
        # Dentro de la raíz: todo el ZIP tiene que colgar de una sola carpeta.
        Copy-Tree -Src $srcPlantilla -Dest (Join-Path $raiz "_plantilla_html")

        if ($IncludeSamples) {
            $srcSample = Join-Path (Join-Path $root "sub-skills_sample_outputs") $rel
            if (Test-Path -LiteralPath $srcSample) {
                Copy-Tree -Src $srcSample -Dest (Join-Path $raiz "sample_outputs")
            } else {
                Write-Warning "Sin muestras de diseño para $rel (sub-skills_sample_outputs\$rel)."
            }
        }
    } else {
        # Archivos raíz
        foreach ($f in $rootFiles) {
            $src = Join-Path $root $f
            if (Test-Path -LiteralPath $src) {
                Copy-Item -LiteralPath $src -Destination $raiz -Force
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
            Copy-Tree -Src $src -Dest (Join-Path $raiz $d)
        }
    }

    # --- Guardia: nombres seguros para el gestor --------------------------
    # El gestor rechaza el ZIP con «Zip file contains path with invalid characters».
    # No documenta qué acepta, así que se exige el juego conservador que sí funciona:
    # letras, dígitos, punto, guion y guion bajo. Fuera acentos, espacios y '&'.
    $malos = Get-ChildItem -LiteralPath $stage -Recurse | Where-Object {
        $_.Name -notmatch '^[A-Za-z0-9._-]+$'
    }
    if ($malos) {
        Write-Warning ("Hay $($malos.Count) nombre(s) con caracteres que el gestor puede " +
                       "rechazar ('Zip file contains path with invalid characters').")
        $malos | Select-Object -First 12 | ForEach-Object {
            $culpables = ([regex]::Matches($_.Name, '[^A-Za-z0-9._-]') |
                          ForEach-Object { $_.Value } | Select-Object -Unique) -join " "
            Write-Host ("    " + $_.FullName.Substring($stage.Length).TrimStart("\") +
                        "   <- [$culpables]") -ForegroundColor Yellow
        }
        if ($malos.Count -gt 12) { Write-Host "    ... y $($malos.Count - 12) mas" -ForegroundColor Yellow }
        Write-Host "    Renombralos a [A-Za-z0-9._-] (ver AGENTS.md 5, 'Rutas seguras')." -ForegroundColor Yellow
    }

    # --- Guardia: exactamente un SKILL.md ---------------------------------
    # El gestor responde «Zip must contain exactly one SKILL.md file» si hay más de
    # uno. Por eso las sub-skills guardan sus instrucciones en AGENTE.md.
    $skillMds = Get-ChildItem -LiteralPath $stage -Recurse -File -Filter "SKILL.md"
    if ($skillMds.Count -ne 1) {
        Write-Warning ("El ZIP lleva $($skillMds.Count) SKILL.md y el gestor exige " +
                       "exactamente 1.")
        $skillMds | ForEach-Object {
            Write-Host ("    " + $_.FullName.Substring($stage.Length).TrimStart("\")) -ForegroundColor Yellow
        }
        Write-Host "    Las sub-skills usan AGENTE.md (ver AGENTS.md 5)." -ForegroundColor Yellow
    }

    # --- Comprimir --------------------------------------------------------
    $outPath = $Output
    if (-not [IO.Path]::IsPathRooted($outPath)) { $outPath = Join-Path $root $outPath }
    if (Test-Path -LiteralPath $outPath) { Remove-Item -LiteralPath $outPath -Force }

    # NO se usa Compress-Archive: incrusta la barra invertida de Windows en el nombre
    # de cada entrada (`iris-flujo-de-innovacion\SKILL.md`). El formato ZIP exige la
    # barra normal, y un validador en Linux lee el `\` como parte del NOMBRE, no como
    # separador — de ahí el «Zip file contains path with invalid characters».
    # Con ZipArchive el nombre de cada entrada se escribe a mano, siempre con `/`.
    Add-Type -AssemblyName System.IO.Compression | Out-Null
    Add-Type -AssemblyName System.IO.Compression.FileSystem | Out-Null

    $fs = [IO.File]::Open($outPath, [IO.FileMode]::Create)
    try {
        $zip = New-Object IO.Compression.ZipArchive(
            $fs, [IO.Compression.ZipArchiveMode]::Create)
        try {
            foreach ($file in Get-ChildItem -LiteralPath $stage -Recurse -File) {
                $rel = $file.FullName.Substring($stage.Length).TrimStart("\", "/")
                $rel = $rel -replace "\\", "/"          # <- la barra correcta del ZIP
                $entry = $zip.CreateEntry(
                    $rel, [IO.Compression.CompressionLevel]::Optimal)
                $salida = $entry.Open()
                try {
                    $entrada = [IO.File]::OpenRead($file.FullName)
                    try { $entrada.CopyTo($salida) } finally { $entrada.Dispose() }
                } finally { $salida.Dispose() }
            }
        } finally { $zip.Dispose() }
    } finally { $fs.Dispose() }

    # --- Guardia: ninguna entrada con barra invertida ----------------------
    # Se relee el directorio central del ZIP escrito. Es la única comprobación que
    # no se puede falsear: `namelist()` de Python normaliza `\` a `/` en Windows y
    # daría un falso negativo.
    $bytes = [IO.File]::ReadAllBytes($outPath)
    $nEntradas = 0
    $nBackslash = 0
    for ($i = 0; $i -lt $bytes.Length - 46; $i++) {
        if ($bytes[$i] -eq 0x50 -and $bytes[$i+1] -eq 0x4B -and
            $bytes[$i+2] -eq 0x01 -and $bytes[$i+3] -eq 0x02) {
            $largo = [BitConverter]::ToUInt16($bytes, $i + 28)
            $nEntradas++
            for ($k = $i + 46; $k -lt $i + 46 + $largo; $k++) {
                if ($bytes[$k] -eq 0x5C) { $nBackslash++; break }
            }
        }
    }
    if ($nBackslash -gt 0) {
        Write-Warning ("$nBackslash de $nEntradas entradas del ZIP llevan barra " +
                       "invertida. El gestor lo rechazara con 'Zip file contains " +
                       "path with invalid characters'.")
    }

    # --- Reporte ----------------------------------------------------------
    $size = (Get-Item -LiteralPath $outPath).Length
    $mb = [math]::Round($size / 1MB, 2)
    Write-Host ""
    Write-Host "ZIP generado: $outPath ($mb MB)"
    Write-Host "  carpeta raiz del ZIP: $skillName/  (debe coincidir con el ``name`` del frontmatter)"
    if ($modo -eq "sub-skill") {
        Write-Host "  sub-skill suelta: $fase/$nombre"
        Write-Host "  contenido: $skillName/SKILL.md + $skillName/_plantilla_html/"
        Write-Host "  genera su HTML (desde $skillName/): python _plantilla_html/scripts/generar_html.py --data reporte.json --sin-flujo -o reporte.html"
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
