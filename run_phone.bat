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
echo ============================================================
echo   AJI FASHION MARKETPLACE - PHONE ACCESS
echo ============================================================
echo.
echo Your computer IPv4 addresses are:
ipconfig | findstr /R /C:"IPv4 Address" /C:"IPv4" 
echo.
echo Keep this window open.
echo On your phone, connect to the SAME Wi-Fi as this computer.
echo Then open Chrome and enter:
echo.
echo     http://YOUR-COMPUTER-IP:8550
echo.
echo Example: http://192.168.1.5:8550
echo.
echo Starting the web server on port 8550...
echo ============================================================
.venv\Scripts\python.exe -m flet run --web --host "*" --port 8550 app.py
pause
