@echo off
setlocal

:: Check if Python is installed
where python >nul 2>nul
if %errorlevel% equ 0 (
    echo Python is already installed.
    exit /b
)

:: Define Python version and URL
set PYTHON_VERSION=3.11.4
set PYTHON_INSTALLER=python-%PYTHON_VERSION%-amd64.exe
set PYTHON_URL=https://www.python.org/ftp/python/%PYTHON_VERSION%/%PYTHON_INSTALLER%

:: Download Python installer
if not exist %PYTHON_INSTALLER% (
    echo Downloading Python %PYTHON_VERSION%...
    powershell -Command "Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%PYTHON_INSTALLER%'"
)

:: Install Python silently
if exist %PYTHON_INSTALLER% (
    echo Installing Python...
    start /wait %PYTHON_INSTALLER% /quiet InstallAllUsers=1 PrependPath=1
    echo Python installation completed.
    del %PYTHON_INSTALLER%
) else (
    echo Failed to download Python installer.
)

endlocal
