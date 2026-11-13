@echo off
setlocal
cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
    py -3 app.py
) else (
    where python >nul 2>nul
    if %errorlevel%==0 (
        python app.py
    ) else (
        echo Python 3 was not found.
        echo Install Python 3 and make sure it is added to PATH.
        pause
        exit /b 1
    )
)

if errorlevel 1 (
    echo.
    echo LocalCode closed with an error.
    pause
)
endlocal
