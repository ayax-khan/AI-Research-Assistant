param(
    [switch]$Detached
)

$ErrorActionPreference = "Stop"

# Check Docker
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "Docker not found. Please install Docker Desktop." -ForegroundColor Red
    exit 1
}

# Check Docker is running
try {
    docker info | Out-Null
} catch {
    Write-Host "Docker daemon is not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

Write-Host "Starting AI Research Assistant..." -ForegroundColor Cyan

if ($Detached) {
    docker compose up --build -d
    Write-Host "`nFrontend: http://localhost:3000" -ForegroundColor Green
    Write-Host "Backend:  http://localhost:8000" -ForegroundColor Green
    Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Green
} else {
    docker compose up --build
}
