@echo off
if not exist ".venv" (
    echo Run setup.bat first.
    pause & exit /b 1
)
call .venv\Scripts\activate.bat
if exist ".env" (
    for /f "usebackq tokens=1,2 delims==" %%a in (".env") do set %%a=%%b
)
pythonw main.py
