# Сборка диплома одной командой.
# Использование: .\compile.ps1
#
# Делает: pdflatex -> bibtex -> pdflatex -> pdflatex,
# чтобы корректно собрались список литературы и все перекрёстные ссылки.

$ErrorActionPreference = 'Stop'

$miktex = 'C:\Users\denis\AppData\Local\Programs\MiKTeX\miktex\bin\x64'
if (-not (Test-Path "$miktex\pdflatex.exe")) {
    Write-Error "pdflatex.exe not found at $miktex. Установлен ли MiKTeX?"
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

Invoke-Step 'pdflatex pass 1' { pdflatex -interaction=nonstopmode -halt-on-error "$jobname.tex" | Out-Null }
Invoke-Step 'bibtex'          { bibtex "$jobname"                                                | Out-Null }
Invoke-Step 'pdflatex pass 2' { pdflatex -interaction=nonstopmode -halt-on-error "$jobname.tex" | Out-Null }
Invoke-Step 'pdflatex pass 3' { pdflatex -interaction=nonstopmode -halt-on-error "$jobname.tex" | Out-Null }

$pdf = Get-Item "$jobname.pdf"
$kb = [math]::Round($pdf.Length / 1KB, 1)
Write-Host ""
Write-Host "OK: $($pdf.FullName)  ($kb KB)"
