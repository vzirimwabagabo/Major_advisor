@echo off
REM USIU-Africa Major Advisor Launcher
cd /d "%~dp0"
echo ===================================================
echo   Starting USIU-Africa Major Advisor Server
echo ===================================================
echo.

REM Try direct Python 3.12 path first, then fallback to python in PATH
if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" run_waitress.py
) else (
    python run_waitress.py
)

pause
