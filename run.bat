@echo off
setlocal
cd /d "%~dp0"
title LocalCode Setup and Launcher

where py >nul 2>nul
if %errorlevel%==0 (
    set "PYTHON_CMD=py -3"
) else (
    where python >nul 2>nul
    if %errorlevel%==0 (
        set "PYTHON_CMD=python"
    ) else (
        echo Python 3 was not found. Install Python 3 and add it to PATH.
        pause
        exit /b 1
    )
)

where node >nul 2>nul
if errorlevel 1 (
    echo WARNING: Node.js was not found. Python and C++ will work, but JavaScript submissions need Node.js.
    echo Install Node.js LTS from https://nodejs.org/ if you want JavaScript support.
    echo.
)

%PYTHON_CMD% -c "import webview" >nul 2>nul
if errorlevel 1 (
    echo Installing LocalCode desktop webview dependency...
    %PYTHON_CMD% -m pip install -r requirements.txt
    if errorlevel 1 (
        echo Could not install pywebview. Check your internet connection and Python installation.
        pause
        exit /b 1
    )
)

%PYTHON_CMD% app.py
if errorlevel 1 (
    echo.
    echo LocalCode closed with an error.
    pause
)
endlocal
