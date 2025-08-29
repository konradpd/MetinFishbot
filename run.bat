@echo off
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Requesting administrative privileges...
    powershell Start-Process "%~f0" -Verb RunAs
    exit /b
)

cd /d "%~dp0"
python main.py
pause
