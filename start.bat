@echo off
echo Starting Forbes Marshall Employee Management System...
echo.
echo IMPORTANT: Oracle Database must be set up before running this application!
echo Please ensure:
echo 1. Oracle Database is installed and running
echo 2. Database user 'forbes_app' is created with proper permissions
echo 3. .env file is configured in backend/ directory
echo.
echo See ORACLE_MIGRATION.md for detailed setup instructions.
echo.
pause

REM Check if backend/requirements.txt exists
if not exist "backend\requirements.txt" (
    echo Error: backend folder not found
    exit /b 1
)

REM Check if .env file exists
if not exist "backend\.env" (
    echo Warning: .env file not found in backend/ directory
    echo Please create it with Oracle database configuration
    echo See backend/.env.example for template
    pause
)

REM Install backend dependencies if not already installed
echo Checking Python dependencies...
cd backend
pip install -r requirements.txt > nul 2>&1

REM Start backend in a new window
echo Starting Flask backend on http://localhost:5000...
start cmd /k python app.py
timeout /t 2 /nobreak

REM Start frontend
cd ..
echo.
echo Starting React frontend on http://localhost:3000...
echo Browser will open automatically
npm start
