#!/bin/bash
echo "Starting custom startup script..."

# Install dependencies if not already installed
if [ -f requirements.txt ]; then
    echo "Installing dependencies from requirements.txt..."
    pip install -r requirements.txt --no-cache-dir
else
    echo "No requirements.txt found, installing packages individually..."
    pip install flask gunicorn requests sqlalchemy psycopg2-binary python-dotenv beautifulsoup4 pypdf2 openai flask-socketio
fi

echo "Dependencies installed, starting Gunicorn..."
# Start the application
gunicorn --bind 0.0.0.0:8000 --timeout 600 --workers 1 main:app