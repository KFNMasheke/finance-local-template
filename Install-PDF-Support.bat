@echo off
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
 ".venv\Scripts\python.exe" -m pip install -r requirements-pdf.txt
) else (
 echo Run Start-Finance.bat first. It sets up PDF support automatically.
)
pause
