#!/bin/bash

# Forbes Marshall - Quick Start Script
# This script starts both the frontend and backend

echo "Starting Forbes Marshall Employee Management System..."
echo ""
echo "IMPORTANT: Oracle Database must be set up before running this application!"
echo "Please ensure:"
echo "1. Oracle Database is installed and running"
echo "2. Database user 'forbes_app' is created with proper permissions"
echo "3. .env file is configured in backend/ directory"
echo ""
echo "See ORACLE_MIGRATION.md for detailed setup instructions."
echo ""

# Check if .env file exists
if [ ! -f "backend/.env" ]; then
    echo "Warning: .env file not found in backend/ directory"
    echo "Please create it with Oracle database configuration"
    echo "See backend/.env.example for template"
    read -p "Press Enter to continue anyway..."
fi

# Start backend in background
echo "Starting Flask backend on http://localhost:5000..."
cd backend
python app.py &
BACKEND_PID=$!
echo "Backend started with PID: $BACKEND_PID"
sleep 2

# Start frontend
echo ""
echo "Starting React frontend on http://localhost:3000..."
cd ..
npm start

# Cleanup on exit
trap "kill $BACKEND_PID" EXIT
