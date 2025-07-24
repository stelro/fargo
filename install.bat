@echo off
REM fargo installer for Windows
REM Usage: install.bat [--user]

echo [install] Installing fargo for Windows...

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.7+ from https://python.org
    echo [ERROR] Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

REM Check if fargo.py exists
if not exist "fargo.py" (
    echo [ERROR] fargo.py not found in current directory
    pause
    exit /b 1
)

REM Check for --user flag
set USER_INSTALL=0
if "%1"=="--user" set USER_INSTALL=1

REM Run the Python installer
if %USER_INSTALL%==1 (
    echo [install] Installing to user directory...
    python install.py --user
) else (
    echo [install] Installing system-wide (requires Administrator)...
    python install.py
)

if errorlevel 1 (
    echo [ERROR] Installation failed
    pause
    exit /b 1
)

echo [OK] Installation completed successfully!
echo.
echo Try it out:
echo   fargo new myproject
echo   cd myproject
echo   fargo build
echo.
pause
