@echo off
echo ============================================
echo   LearnWise - Starting Full App
echo ============================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running!
    echo Please open Docker Desktop and wait for the engine to start.
    echo Then run this script again.
    pause
    exit /b 1
)

REM Check if test.env exists
if not exist "test.env" (
    echo [ERROR] Missing test.env file!
    echo Please get the test.env file from your friend and place it
    echo in this folder, then run this script again.
    pause
    exit /b 1
)

echo [OK] Docker is running
echo [OK] test.env found
echo.
echo Building and starting LearnWise (first run takes 3-5 minutes)...
echo.

docker compose --env-file test.env up --build

pause
