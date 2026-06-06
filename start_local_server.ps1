$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$appDir = Join-Path $projectRoot "missing_tracker"
$py = "C:\Users\BAVAN KUMAR\AppData\Local\Programs\Python\Python312\python.exe"

if (-not (Test-Path $py)) {
    throw "Python runtime not found at $py"
}

Set-Location $appDir
& $py -c "from app import create_app; app = create_app(); app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)"
