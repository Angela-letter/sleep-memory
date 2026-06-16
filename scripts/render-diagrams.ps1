# Render Sleep Memory Mermaid diagrams to PNG (zh + en)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Mmdc = "npx"
$MmdcArgs = @("--yes", "@mermaid-js/mermaid-cli")

$Chrome = "C:\Program Files\Google\Chrome\Application\chrome.exe"
if (-not (Test-Path $Chrome)) {
    $Chrome = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
}
$env:PUPPETEER_EXECUTABLE_PATH = $Chrome

function Render-Set {
    param(
        [string]$Lang,
        [string]$Config,
        [string]$OutDir
    )
    $Src = Join-Path $Root "docs\assets\mermaid\$Lang"
    New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
  foreach ($file in Get-ChildItem $Src -Filter "*.mmd") {
        $out = Join-Path $OutDir ($file.BaseName + ".png")
        Write-Host "  $($file.Name) -> $out"
        & $Mmdc @MmdcArgs -i $file.FullName -o $out -c $Config -b transparent -w 1200 -H 800 --scale 2
        if ($LASTEXITCODE -ne 0) { throw "mmdc failed: $($file.Name)" }
    }
}

Write-Host "Rendering zh diagrams..."
Render-Set -Lang "zh" -Config (Join-Path $Root "docs\assets\mermaid\config.json") -OutDir (Join-Path $Root "docs\assets\zh")

Write-Host "Rendering en diagrams..."
Render-Set -Lang "en" -Config (Join-Path $Root "docs\assets\mermaid\config-en.json") -OutDir (Join-Path $Root "docs\assets\en")

# Hero images (backward-compatible paths)
Copy-Item (Join-Path $Root "docs\assets\zh\02-layers.png") (Join-Path $Root "docs\assets\architecture.png") -Force
Copy-Item (Join-Path $Root "docs\assets\en\02-layers.png") (Join-Path $Root "docs\assets\architecture-en.png") -Force

Write-Host "Done."
