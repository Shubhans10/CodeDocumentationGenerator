#!/bin/bash

# Script to start the backend server for the Intelligent Code Documentation Generator

echo "Starting backend server..."

# Navigate to the backend directory
cd backend || { echo "Error: backend directory not found"; exit 1; }

# Check if virtual environment exists and activate it
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate || { echo "Error: Could not activate virtual environment"; exit 1; }
else
    echo "Warning: Virtual environment not found. You may need to create one first."
    echo "Run: python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
fi

# Check if requirements are installed
if [ -f "requirements.txt" ]; then
    echo "Checking if dependencies are installed..."
    if ! pip freeze | grep -q "fastapi"; then
        echo "Warning: Dependencies may not be installed. Installing now..."
        pip install -r requirements.txt || { echo "Error: Could not install dependencies"; exit 1; }
    fi
else
    echo "Warning: requirements.txt not found. Dependencies may not be installed."
fi

# Start the FastAPI server
echo "Starting FastAPI server with Uvicorn..."
uvicorn app.main:app --reload

# Deactivate virtual environment when the server is stopped
if [ -d "venv" ]; then
    deactivate 2>/dev/null
fi