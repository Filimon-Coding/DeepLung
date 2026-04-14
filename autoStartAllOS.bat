@echo off
REM autoStartAllOS.bat — Windows
REM Run from anywhere; paths are resolved relative to this script's location.

setlocal enabledelayedexpansion

REM ── Resolve project root ──────────────────────────────────────────────────────
set "BASE_DIR=%~dp0"
REM Strip trailing backslash
if "%BASE_DIR:~-1%"=="\" set "BASE_DIR=%BASE_DIR:~0,-1%"

REM ── Free ports ────────────────────────────────────────────────────────────────
echo Freeing ports 5056, 8001, 5173...

for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr /r ":5056 "') do (
    taskkill /PID %%a /F 2>nul
)
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr /r ":8001 "') do (
    taskkill /PID %%a /F 2>nul
)
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr /r ":5173 "') do (
    taskkill /PID %%a /F 2>nul
)

REM ── Services ──────────────────────────────────────────────────────────────────

REM .NET backend
start "DeepLungCTApi (.NET)" cmd /k ^
    "cd /d "%BASE_DIR%\backEnd\DeepLungCTApi" && echo >>> In %CD% && dotnet run"

REM Python inference service
start "inferenceService (FastAPI)" cmd /k ^
    "cd /d "%BASE_DIR%\backEnd\inferenceService" && echo >>> In %CD% && .venv\Scripts\activate && uvicorn app:app --host 127.0.0.1 --port 8001 --reload"

REM React frontend
start "frontEnd (Vite)" cmd /k ^
    "cd /d "%BASE_DIR%\frontEnd" && echo >>> In %CD% && npm run dev"

echo All services started!
endlocal
