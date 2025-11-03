#!/bin/bash

# Start script for the application

echo "Starting Code Review Assistant Agent..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Warning: .env file not found. Using default settings."
    echo "Please create a .env file based on .env.example"
fi

# Run the application
uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080} --reload
