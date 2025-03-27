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
pip install wmi 
echo wmi installed \n
pip install telebot 
echo telebot installed \n
pip install scikit-learn
echo sckikit installed \n
pip install logging
echo logging installed \n

:: Confirmation message
echo [*] Setup complete! 
echo .
echo To start open cmd as administrator, activate the virtual environment:
echo venv\Scripts\activate
echo python event_track_ai.py
echo or just open start.bat
pause
