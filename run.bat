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
    echo Node.js was not found. It is required by LocalCode for JavaScript submissions and building the editor.
    echo Install Node.js LTS from https://nodejs.org/ and run this file again.
    pause
    exit /b 1
)

if not exist "webui\dist\app.js" (
    echo First-time setup: downloading and building the CodeMirror 6 editor...
    pushd webui
    call npm install --no-audit --no-fund
    if errorlevel 1 (
        echo Failed to install CodeMirror dependencies. Check your internet connection and try again.
        popd
        pause
        exit /b 1
    )
    call npm run build
    if errorlevel 1 (
        echo Failed to build the CodeMirror editor.
        popd
        pause
        exit /b 1
    )
    if not exist "dist\app.js" (
        echo Build completed but webui\dist\app.js was not created.
        popd
        pause
        exit /b 1
    )
    popd
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
