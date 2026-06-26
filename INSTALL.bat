@echo off
title Smart Traffic Management System - INSTALLER
color 0A

echo.
echo  ============================================================
echo   AI-Driven Smart Traffic Management System
echo   Automated Violation Detection with E-Challan System
echo  ============================================================
echo.
echo   This will install all required dependencies.
echo   Make sure Node.js (v18+) is installed on this computer.
echo.
echo  ============================================================
echo.

:: Check if Node.js is installed
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    color 0C
    echo  [ERROR] Node.js is NOT installed!
    echo.
    echo  Please download and install Node.js from:
    echo  https://nodejs.org/en/download/
    echo.
    echo  After installing Node.js, run this file again.
    echo.
    pause
    exit /b 1
)

:: Show Node.js version
echo  [OK] Node.js found:
node --version
echo.

:: Show npm version
echo  [OK] npm found:
call npm --version
echo.

echo  ============================================================
echo   Step 1: Installing Frontend Dependencies...
echo  ============================================================
echo.

cd /d "%~dp0frontend"

if not exist "package.json" (
    color 0C
    echo  [ERROR] package.json not found in frontend folder!
    echo  Make sure you extracted the project correctly.
    pause
    exit /b 1
)

call npm install

if %ERRORLEVEL% NEQ 0 (
    color 0C
    echo.
    echo  [ERROR] Frontend installation failed!
    echo  Please check your internet connection and try again.
    pause
    exit /b 1
)

echo.
echo  [OK] Frontend dependencies installed successfully!
echo.

echo  ============================================================
echo   Step 2: Checking Python (Optional - for AI Service)
echo  ============================================================
echo.

where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo  [OK] Python found:
    python --version
    echo.
    echo  To install backend dependencies, run:
    echo  cd backend ^&^& pip install -r requirements.txt
    echo  cd ai_service ^&^& pip install -r requirements.txt
) else (
    echo  [INFO] Python not found. That's OK!
    echo  The Simulator Mode runs entirely in the browser.
    echo  Python is only needed for the real-time AI backend.
)

echo.
echo  ============================================================
echo.
color 0A
echo   INSTALLATION COMPLETE!
echo.
echo   To start the application, double-click: RUN.bat
echo.
echo  ============================================================
echo.
pause
