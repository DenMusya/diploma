# Сборка диплома (XeLaTeX — Times New Roman, совместимость с ЛК МФТИ).
# Использование: .\compile.ps1
#
# xelatex -> bibtex -> xelatex -> xelatex

$ErrorActionPreference = 'Stop'

$Engine = 'xelatex'
$miktex = 'C:\Users\denis\AppData\Local\Programs\MiKTeX\miktex\bin\x64'
if (-not (Test-Path "$miktex\$Engine.exe")) {
    Write-Error "$Engine.exe not found at $miktex. Установлен ли MiKTeX?"
    exit 1
}
$env:PATH = "$miktex;$env:PATH"

$jobname = 'main'

function Invoke-Step {
    param([string]$Name, [scriptblock]$Block)
    Write-Host ""
    Write-Host "==> $Name"
    & $Block
    if ($LASTEXITCODE -ne 0) {
        Write-Error "$Name failed with exit code $LASTEXITCODE. См. main.log."
        exit $LASTEXITCODE
    }
}

function Invoke-XeLaTeX {
    $prev = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        & $Engine -interaction=nonstopmode -halt-on-error "$jobname.tex" *> $null
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    } finally {
        $ErrorActionPreference = $prev
    }
}

Invoke-Step "xelatex pass 1" { Invoke-XeLaTeX }
Invoke-Step 'bibtex' {
    $prev = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try { bibtex "$jobname" *> $null } finally { $ErrorActionPreference = $prev }
}
Invoke-Step "xelatex pass 2" { Invoke-XeLaTeX }
Invoke-Step "xelatex pass 3" { Invoke-XeLaTeX }

$pdf = Get-Item "$jobname.pdf"
$kb = [math]::Round($pdf.Length / 1KB, 1)
Write-Host ""
Write-Host "OK: $($pdf.FullName)  ($kb KB)"
