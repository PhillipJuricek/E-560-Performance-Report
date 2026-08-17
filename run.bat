@echo off
setlocal

echo ============================================
echo  E-560 M-Exchanger Performance Report
echo ============================================
echo.

where py >nul 2>nul
if %errorlevel%==0 (
    set "PY_LAUNCHER=py -3.13"
) else (
    where python >nul 2>nul
    if %errorlevel%==0 (
        set "PY_LAUNCHER=python"
    ) else (
        echo [ERROR] Python was not found.
        echo Install Python 3.13 from https://www.python.org/downloads/
        echo Make sure to tick "Add python.exe to PATH" during install.
        pause
        exit /b 1
    )
)

if not exist ".venv\Scripts\python.exe" (
    echo Creating virtual environment...
    %PY_LAUNCHER% -m venv .venv
    if errorlevel 1 (
        echo [ERROR] Could not create the virtual environment.
        pause
        exit /b 1
    )
)

call ".venv\Scripts\activate.bat"

echo Checking dependencies...
python -c "import streamlit" 2>nul
if errorlevel 1 (
    echo Installing dependencies from requirements.txt...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] pip install failed. Check your internet / proxy, then re-run.
        pause
        exit /b 1
    )
)

echo.
echo Starting the app... your browser will open at http://localhost:8501
echo Close this window to stop the app.
echo.
streamlit run app_streamlit.py
pause
