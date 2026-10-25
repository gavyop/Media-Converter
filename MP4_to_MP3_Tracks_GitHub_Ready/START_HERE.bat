@echo off
setlocal
cd /d "%~dp0"
REM Prefer pythonw to open the GUI without a command window.
if exist "%LOCALAPPDATA%\Programs\Python\Python314\pythonw.exe" (
  start "" "%LOCALAPPDATA%\Programs\Python\Python314\pythonw.exe" "%~dp0FFmpeg_Track_Extractor.pyw"
  exit /b
)
where pyw >nul 2>nul
if %errorlevel%==0 (
  start "" pyw -3 "%~dp0FFmpeg_Track_Extractor.pyw"
  exit /b
)
where pythonw >nul 2>nul
if %errorlevel%==0 (
  start "" pythonw "%~dp0FFmpeg_Track_Extractor.pyw"
  exit /b
)
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 "%~dp0FFmpeg_Track_Extractor.pyw"
  if errorlevel 1 pause
  exit /b
)
echo ERROR: Python 3 was not found. Install Python from https://www.python.org/downloads/windows/
pause
