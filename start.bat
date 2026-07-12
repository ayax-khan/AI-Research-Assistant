@echo off
where docker >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Docker not found. Please install Docker Desktop.
    pause
    exit /b 1
)

echo Starting AI Research Assistant...
echo.
docker compose up --build -d
if %ERRORLEVEL% neq 0 (
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo Frontend: http://localhost:3000
echo Backend:  http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
pause
