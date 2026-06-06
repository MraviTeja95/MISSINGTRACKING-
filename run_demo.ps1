param(
    [string]$PythonExe = "py -3.11"
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$appRoot = Join-Path $projectRoot "missing_tracker"
$venvPath = Join-Path $projectRoot ".venv-demo"
$venvPython = Join-Path $venvPath "Scripts\\python.exe"
$requirementsPath = Join-Path $appRoot "requirements-demo.txt"

if (-not (Test-Path $requirementsPath)) {
    throw "Missing demo requirements file at $requirementsPath"
}

if (-not (Test-Path $venvPython)) {
    Write-Host "Creating fresh demo virtual environment..."

    if ($PythonExe -eq "py -3.11") {
        & py -3.11 -m venv $venvPath
    } else {
        & $PythonExe -m venv $venvPath
    }
}

Write-Host "Installing demo dependencies..."
& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -r $requirementsPath

Write-Host "Starting TraceNet demo on http://localhost:5000 ..."
Push-Location $appRoot
try {
    & $venvPython app.py
} finally {
    Pop-Location
}
