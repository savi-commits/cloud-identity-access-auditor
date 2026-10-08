@echo off
:: ---------------------------------------------------------------
::  run_project.bat
::  Cloud Identity and Access Auditor - one-click startup
::
::  HOW TO USE:
::    Double-click this file from anywhere.
::    The script changes to its own directory automatically,
::    so you do NOT need to be in any specific folder first.
:: ---------------------------------------------------------------

:: Move to the directory that contains this .bat file
cd /d "%~dp0"

echo.
echo  ================================================
echo   Cloud Identity and Access Auditor
echo  ================================================
echo.

:: --- Step 1: Find Python ---
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo  ERROR: Python was not found on this computer.
    echo  Please install Python 3.8+ from https://python.org
    echo  and make sure "Add to PATH" is checked during install.
    pause
    exit /b 1
)

:: --- Step 2: Activate virtual environment (if it exists) ---
if exist "venv\Scripts\activate.bat" (
    echo  [1/3] Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo  [1/3] No virtual environment found. Using system Python.
    echo        To create one: python -m venv venv
)

:: --- Step 3: Install/verify requirements ---
echo  [2/3] Checking requirements...
pip install -r requirements.txt --quiet --disable-pip-version-check
if %errorlevel% neq 0 (
    echo  WARNING: Could not install some requirements.
    echo  Try running:  pip install -r requirements.txt
    pause
    exit /b 1
)

:: --- Step 4: Open browser then start Flask ---
echo  [3/3] Starting Flask server...
echo.
echo  ------------------------------------------------
echo   Server running at: http://127.0.0.1:5000
echo   Press Ctrl+C to stop the server.
echo  ------------------------------------------------
echo.

:: Open the browser after a short delay (start is non-blocking)
timeout /t 2 /nobreak >nul
start "" "http://127.0.0.1:5000"

:: Start Flask (blocking - keeps the window open while server runs)
python app.py

:: If Flask exits or crashes, pause so the user can read the error
echo.
echo  Server stopped. Press any key to close this window.
pause >nul
