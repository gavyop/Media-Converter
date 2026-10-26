@echo off
cd /d "%~dp0"
where py >nul 2>&1
if not errorlevel 1 (
    py -3 "%~dp0media_converter.pyw"
    if not errorlevel 1 exit /b 0
)
where python >nul 2>&1
if not errorlevel 1 (
    python "%~dp0media_converter.pyw"
    if not errorlevel 1 exit /b 0
)
echo.
echo Could not start the Media Converter.
echo Install Python 3 from https://www.python.org/downloads/windows/
echo Ensure Python includes Tkinter.
pause
