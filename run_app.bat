@echo off
echo ITAM Mentors Service Runner
echo.
echo Choose how to run the application:
echo 1. Run with Docker (requires Docker Desktop)
echo 2. Run with SQLite (no Docker required)
echo.

set /p choice="Enter your choice (1 or 2): "

if "%choice%"=="1" (
    echo.
    echo Starting with Docker...
    echo.
    powershell -ExecutionPolicy Bypass -File .\start_docker.ps1
) else if "%choice%"=="2" (
    echo.
    echo Starting with SQLite...
    echo.
    call .\myenv\Scripts\activate
    python run_with_sqlite.py
) else (
    echo.
    echo Invalid choice. Please run again and select 1 or 2.
    echo.
    pause
    exit /b 1
)

pause 