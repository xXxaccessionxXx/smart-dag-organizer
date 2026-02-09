@echo off
echo ===================================================
echo      Smart DAG Organizer - Builder Tool
echo ===================================================
echo.
echo This script will rebuild the executable from the source code.
echo.

:: Check for PyInstaller
python -c "import PyInstaller" >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] PyInstaller not found. Installing...
    pip install pyinstaller
    if %errorlevel% neq 0 (
        echo [x] Failed to install PyInstaller.
        pause
        exit /b %errorlevel%
    )
)

:: Run Build
echo [*] Building Application...
pyinstaller main.spec

if %errorlevel% neq 0 (
    echo [x] Build Failed! Check the error messages above.
    pause
    exit /b %errorlevel%
)

echo.
echo [V] Build Successful!
echo     Executable is located in: dist\SmartDAGOrganizer\SmartDAGOrganizer.exe
echo.
pause
