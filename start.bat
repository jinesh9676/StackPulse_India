@echo off
cd /d "%~dp0"
where python >nul 2>&1
if errorlevel 1 (
  winget install --id Python.Python.3.13 -e --accept-package-agreements --accept-source-agreements
  echo Reopen CMD after installation and run start.bat again.
  exit /b
)
python app.py
