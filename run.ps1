# 1. Check/Start Docker Desktop
Write-Host "===================================================" -ForegroundColor Magenta
Write-Host "             Starting Quiz App Services            " -ForegroundColor Magenta
Write-Host "===================================================" -ForegroundColor Magenta
Write-Host ""

Write-Host "[1/4] Checking Docker daemon status..." -ForegroundColor Cyan
$dockerRunning = docker info 2>$null
if ($null -eq $dockerRunning) {
    Write-Host "[!] Docker is not running. Starting Docker Desktop..." -ForegroundColor Yellow
    Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    Write-Host "[*] Waiting for Docker daemon to initialize..." -ForegroundColor Yellow
    while ($null -eq (docker info 2>$null)) {
        Start-Sleep -Seconds 3
    }
    Write-Host "[+] Docker daemon started successfully!" -ForegroundColor Green
} else {
    Write-Host "[+] Docker daemon is already running." -ForegroundColor Green
}

# 2. Start Piston Sandbox
Write-Host ""
Write-Host "[2/4] Starting Piston Code Sandbox container..." -ForegroundColor Cyan
docker compose up -d piston

# 3. Start Flask Backend in Background
Write-Host ""
Write-Host "[3/4] Starting Flask Backend (in background window)..." -ForegroundColor Cyan
Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", "cd backend; .\venv\Scripts\python.exe app.py" -WindowStyle Minimized

# 4. Start Vite Frontend in Foreground
Write-Host ""
Write-Host "[4/4] Starting Vite Frontend in this window..." -ForegroundColor Cyan
cd frontend
npm.cmd run dev
