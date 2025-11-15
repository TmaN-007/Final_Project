#!/bin/bash
# Script to completely restart the Flask server with fresh Python cache

echo "Stopping all Flask servers..."
pkill -9 -f "python.*run.py"
sleep 2

echo "Cleaning Python cache..."
cd "/Users/hii/Desktop/AiDD Final Project/Final_Project"
find . -type d -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null

echo "Starting fresh server on port 5002..."
export PYTHONDONTWRITEBYTECODE=1
export FLASK_RUN_PORT=5002
python3 run.py
