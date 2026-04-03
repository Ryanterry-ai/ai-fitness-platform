@echo off
REM Website Cloner AI System - Run Script for Windows

echo Starting Website Cloner AI System...
echo.

cd /d "%~dp0"

echo Installing dependencies...
pip install -r requirements.txt

if %ERRORLEVEL% NEQ 0 (
    echo Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Starting server on http://localhost:10000
echo.
echo Access the application:
echo   - Main App: http://localhost:10000
echo   - Admin Panel: http://localhost:10000/admin
echo   - API Docs: http://localhost:10000/docs
echo.
echo Default login: admin@admin.com / admin123
echo.

python -m uvicorn backend.app:app --reload --host 0.0.0.0 --port 10000

pause
