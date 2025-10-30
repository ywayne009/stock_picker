@echo off
echo Setting up Stock Picker Backend...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed. Please install Python 3.11 or higher.
    exit /b 1
)

REM Create virtual environment
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created
) else (
    echo Virtual environment already exists
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Backend setup complete!
echo.
echo To activate the virtual environment, run:
echo   venv\Scripts\activate
echo.
echo To start the development server, run:
echo   uvicorn app.main:app --reload
echo.
pause
