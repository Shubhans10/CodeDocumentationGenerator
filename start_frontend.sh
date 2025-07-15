#!/bin/bash

# Script to start the frontend server for the Intelligent Code Documentation Generator

echo "Starting frontend server..."

# Navigate to the frontend directory
cd frontend || { echo "Error: frontend directory not found"; exit 1; }

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install || { echo "Error: Could not install dependencies"; exit 1; }
fi

# Start the React development server
echo "Starting React development server..."
npm start

# The script will continue running until the server is stopped with Ctrl+C