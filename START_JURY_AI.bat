@echo off
title JURY-AI Launcher
color 0B
echo.
echo  ================================================
echo   JURY-AI ^| Legal Intelligence Platform
echo   Starting Backend + Frontend...
echo  ================================================
echo.

:: Get directory where this bat file is located
set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"

:: Start FastAPI Backend in a new window
start "JURY-AI Backend (FastAPI :8000)" cmd /k "cd /d "%PROJECT_ROOT%" && call venv\Scripts\activate.bat && python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000"

:: Wait 3 seconds for backend to initialize
timeout /t 3 /nobreak >nul

:: Start Next.js Frontend in a new window
start "JURY-AI Frontend (Next.js :3000)" cmd /k "cd /d "%PROJECT_ROOT%frontend" && npm run dev"

:: Wait 4 seconds for frontend to boot
timeout /t 4 /nobreak >nul

:: Open browser
echo  Opening browser...
start http://localhost:3000

echo.
echo  Both servers are running!
echo  Frontend : http://localhost:3000
echo  Backend  : http://localhost:8000
echo.
echo  Close the terminal windows when you want to stop the servers.
echo.
pause
