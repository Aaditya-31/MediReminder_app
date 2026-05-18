# MediReminder — Appointment Reminder Agent Startup Script (Windows PowerShell)

Write-Host ""
Write-Host "  ███████╗██╗  ██╗ ██████╗ ██████╗ ███████╗" -ForegroundColor Cyan
Write-Host "  ██╔════╝██║ ██╔╝██╔═══██╗██╔══██╗██╔════╝" -ForegroundColor Cyan
Write-Host "  ███████╗█████╔╝ ██║   ██║██████╔╝█████╗  " -ForegroundColor Cyan
Write-Host "  ╚════██║██╔═██╗ ██║   ██║██╔══██╗██╔══╝  " -ForegroundColor Cyan
Write-Host "  ███████║██║  ██╗╚██████╔╝██║  ██║███████╗" -ForegroundColor Cyan
Write-Host "  ╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Appointment Reminder Agent — Intelligence Platform" -ForegroundColor DarkCyan
Write-Host ""

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendDir = Join-Path $root "backend"
$frontendDir = Join-Path $root "frontend"

# ── Refresh PATH from Registry (Dynamic Environment Reload) ───────────────────
$machinePath = [System.Environment]::GetEnvironmentVariable("Path", "Machine")
$userPath = [System.Environment]::GetEnvironmentVariable("Path", "User")
$env:Path = "$machinePath;$userPath"

# ── Auto-Detect Python in Default AppData Location ────────────────────────────
$defaultPythonDir = Join-Path $env:LocalAppData "Programs\Python\Python311"
if (Test-Path (Join-Path $defaultPythonDir "python.exe")) {
    $env:Path = "$defaultPythonDir;$(Join-Path $defaultPythonDir 'Scripts');$env:Path"
}

# ── Backend Setup ──────────────────────────────────────────────────────────────
Write-Host "[1/3] Setting up Python backend..." -ForegroundColor Yellow

$venvPath = Join-Path $backendDir "venv"
if (-not (Test-Path $venvPath)) {
    Write-Host "  Creating virtual environment..." -ForegroundColor DarkYellow
    python -m venv $venvPath
}

$pipPath = Join-Path $venvPath "Scripts\pip.exe"
Write-Host "  Installing backend dependencies..." -ForegroundColor DarkYellow
& $pipPath install -r (Join-Path $backendDir "requirements.txt") -q

Write-Host "[2/3] Starting FastAPI backend on http://localhost:8000 ..." -ForegroundColor Yellow
$backendJob = Start-Job -ScriptBlock {
    param($dir, $venv)
    Set-Location $dir
    $uvicornPath = Join-Path $venv "Scripts\uvicorn.exe"
    & $uvicornPath main:app --reload --port 8000
} -ArgumentList $backendDir, $venvPath

Start-Sleep -Seconds 3

# ── Frontend Setup ─────────────────────────────────────────────────────────────
Write-Host "[3/3] Setting up React frontend..." -ForegroundColor Yellow
$nodeModulesPath = Join-Path $frontendDir "node_modules"
if (-not (Test-Path $nodeModulesPath)) {
    Write-Host "  Installing frontend dependencies (this may take a minute)..." -ForegroundColor DarkYellow
    Start-Process -FilePath "npm.cmd" -ArgumentList "install" -WorkingDirectory $frontendDir -NoNewWindow -Wait
}

Write-Host "  Starting React frontend on http://localhost:5173 ..." -ForegroundColor Yellow
$frontendJob = Start-Job -ScriptBlock {
    param($dir)
    Set-Location $dir
    npm.cmd run dev
} -ArgumentList $frontendDir

Write-Host ""
Write-Host "  ✅ Both servers started!" -ForegroundColor Green
Write-Host "  → Frontend : http://localhost:5173" -ForegroundColor Cyan
Write-Host "  → Backend  : http://localhost:8000" -ForegroundColor Cyan
Write-Host "  → API Docs : http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Press Ctrl+C to stop both servers." -ForegroundColor DarkGray
Write-Host ""

try {
    while ($true) {
        $backendJob | Receive-Job
        $frontendJob | Receive-Job
        Start-Sleep -Seconds 2
    }
} finally {
    Write-Host "Shutting down..." -ForegroundColor Red
    Stop-Job $backendJob, $frontendJob
    Remove-Job $backendJob, $frontendJob
}
