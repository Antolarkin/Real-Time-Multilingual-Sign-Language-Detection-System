#!/bin/bash
echo "Starting Unified Sign Language Detection API..."
echo "Using Python 3.11 from Homebrew..."

# Kill any existing process on port 8000
lsof -ti:8000 | xargs kill -9 2>/dev/null

# Clean up any previous session locks
rm -f ml/sign_language_detections.txt ml/detected_text.txt

# Run the API using the specific python interpreter that has the dependencies
/opt/homebrew/bin/python3.11 ml/api.py
