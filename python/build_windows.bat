@echo off
setlocal
cd /d "%~dp0"

echo [1/2] Checking requirements and installing PyInstaller...
python -m pip install --upgrade pip pyinstaller
if errorlevel 1 goto :error

echo.
echo [2/2] Building standalone executable with PyInstaller...
pyinstaller --noconfirm --onefile --windowed --name PseudoSudoku main.py
if errorlevel 1 goto :error

echo.
echo ========================================================
echo  Build successful! Standalone executable generated at:
echo  %~dp0dist\PseudoSudoku.exe
echo ========================================================
echo.
pause
exit /b 0

:error
echo.
echo Build failed. Please verify that Python 3.8+ and pip are installed and available in PATH.
pause
exit /b 1
