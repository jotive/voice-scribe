@echo off
echo ============================================
echo  voice-scribe setup
echo ============================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Install Python 3.11 or 3.12.
    pause & exit /b 1
)

:: Create venv
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

echo Activating venv...
call .venv\Scripts\activate.bat

echo Installing dependencies...
pip install --upgrade pip -q
pip install -r requirements.txt -q

echo.
echo Installing PyTorch with CUDA 12.x (for GTX 1050 Ti)...
pip install torch --index-url https://download.pytorch.org/whl/cu121 -q

echo.
echo Checking hardware...
python check_hardware.py

echo.
echo ============================================
echo  Setup complete. Run: run.bat
echo ============================================
pause
