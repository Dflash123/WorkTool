@echo off
cd /d "%~dp0"

python --version >nul 2>&1
if errorlevel 1 (
    echo Python not found. Please install Python 3.10 or later.
    pause
    exit /b 1
)

python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    python -m pip install flask flask-wtf gspread google-auth google-auth-oauthlib pyyaml
    if errorlevel 1 (
        echo Failed to install dependencies.
        pause
        exit /b 1
    )
)

python start_app.py
