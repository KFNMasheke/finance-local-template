@echo off
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (py -3 -m pip install "pypdf>=5,<7") else (python -m pip install "pypdf>=5,<7")
pause
