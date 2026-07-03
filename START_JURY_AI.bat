@echo off
title JURY-AI Launcher
color 0B
echo.
echo  ================================================
echo   JURY-AI ^| Legal Intelligence Platform
echo   Starting Backend + Frontend...
echo  ================================================
echo.

:: Start FastAPI Backend in a new window
start "JURY-AI Backend (FastAPI :8000)" cmd /k "cd /d C:\Users\HP\OneDrive\Desktop\JURY-AI && venv\Scripts\activate && python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload"

:: Wait 3 seconds for backend to initialize
timeout /t 3 /nobreak >nul

:: Start Next.js Frontend in a new window
start "JURY-AI Frontend (Next.js :3000)" cmd /k "cd /d C:\Users\HP\OneDrive\Desktop\JURY-AI\frontend && npm run dev"

:: Wait for frontend to boot
timeout /t 4 /nobreak >nul

:: Open browser
echo  Opening browser...
start http://localhost:3000

echo.
echo  Both servers are running!
echo  Frontend : http://localhost:3000
echo  Backend  : http://localhost:8000
echo.
echo  Close the two terminal windows to stop the servers.
pause
