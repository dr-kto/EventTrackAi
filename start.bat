@echo off
:: Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Requesting administrator privileges...
    powershell -Command "Start-Process cmd -ArgumentList '/c \"%~f0\"' -Verb RunAs"
    exit /b
)

echo [*] Running script as administrator...

:: Navigate to the script directory
cd /d %~dp0

:: Activate virtual environment
call venv\Scripts\activate

:: Run the Python script
python event_track_ai.py

:: Pause to keep the window open
pause
