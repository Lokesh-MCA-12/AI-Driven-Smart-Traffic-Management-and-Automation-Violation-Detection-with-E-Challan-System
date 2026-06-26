@echo off
title Smart Traffic Management System - RUNNING
color 0B

echo.
echo  ============================================================
echo   AI-Driven Smart Traffic Management System
echo   Starting Dashboard Server...
echo  ============================================================
echo.

:: Check if node_modules exists
if not exist "%~dp0frontend\node_modules" (
    color 0C
    echo  [ERROR] Dependencies not installed!
    echo.
    echo  Please run INSTALL.bat first.
    echo.
    pause
    exit /b 1
)

echo  [OK] Dependencies found.
echo.
echo  Starting the dashboard...
echo.
echo  ============================================================
echo   The dashboard will open automatically in your browser.
echo.
echo   URL:  http://localhost:3000
echo.
echo   Login Credentials:
echo     Username: admin       Password: admin123
echo     Username: officer1    Password: admin123
echo     Username: officer2    Password: admin123
echo.
echo   Press Ctrl+C to stop the server.
echo  ============================================================
echo.

:: Wait 3 seconds then open browser
start "" cmd /c "timeout /t 3 /nobreak >nul && start http://localhost:3000"

:: Start the dev server
cd /d "%~dp0frontend"
call npm run dev

echo.
echo  Server stopped.
pause
