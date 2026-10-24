@echo off
setlocal
cd /d "%~dp0"
set "CHESS_PY=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if exist "%CHESS_PY%" goto launch
set "CHESS_PY=python"
where python >nul 2>nul
if errorlevel 1 set "CHESS_PY=py"
:launch
"%CHESS_PY%" -c "import tkinter, PIL" >nul 2>nul
if errorlevel 1 goto setup
"%CHESS_PY%" app.py %*
if errorlevel 1 pause
exit /b
:setup
echo Install Python 3.10+ from python.org, then run:
echo   python -m pip install -r requirements.txt
echo   python app.py
pause
