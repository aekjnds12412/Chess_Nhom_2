@echo off
chcp 65001 >nul
cd /d "%~dp0.."
set "CHESS_PY=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if exist "%CHESS_PY%" goto launch
set "CHESS_PY=python"
where python >nul 2>nul
if errorlevel 1 set "CHESS_PY=py"
:launch
"%CHESS_PY%" tools\view_db.py
echo.
pause
