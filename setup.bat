@echo off
echo [*] Setting up the project...

:: Create and activate virtual environment
python -m venv venv


:: Upgrade pip
echo [*] Upgrading pip...
python.exe -m pip install --upgrade pip

call venv\Scripts\activate
:: Install required packages
echo [*] Installing dependencies...
pip install wmi telebot scikit-learn logging

:: Confirmation message
echo [*] Setup complete! 
echo .
echo To start open cmd as administrator, activate the virtual environment:
echo venv\Scripts\activate
echo python event_track_ai.py
echo or just open start.bat
pause
