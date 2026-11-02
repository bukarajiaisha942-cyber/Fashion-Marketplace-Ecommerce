@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Creating the Python virtual environment...
    py -3 -m venv .venv
    if errorlevel 1 (
        echo.
        echo Could not create the virtual environment.
        echo Make sure Python 3.10 or newer is installed and added to PATH.
        pause
        exit /b 1
    )
)
echo Installing/updating project requirements...
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo Dependency installation failed. Check your internet connection.
    pause
    exit /b 1
)
echo.
echo Starting Aji Fashion Marketplace on this computer...
echo Close this window to stop the application.
echo.
.venv\Scripts\python.exe app.py
pause
