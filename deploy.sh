#!/bin/bash

# Deployment script for the Iterative Prompt Chain API server

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required but not installed. Please install Python 3 and try again."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "pip3 is required but not installed. Please install pip and try again."
    exit 1
fi

# Create a virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate the virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists, create if not
if [ ! -f .env ]; then
    echo "Creating .env file..."
    echo "# API keys" > .env
    echo "# Uncomment and add your API key below" >> .env
    echo "# ANTHROPIC_API_KEY=your_api_key_here" >> .env
    echo "# OPENAI_API_KEY=your_api_key_here" >> .env
    echo ".env file created. Please edit it to add your API key."
fi

# Ask user if they want to run the server in development or production mode
echo ""
echo "How would you like to run the server?"
echo "1. Development mode (Flask built-in server)"
echo "2. Production mode (Gunicorn)"
read -p "Enter your choice (1/2): " choice

case $choice in
    1)
        echo "Starting server in development mode..."
        python api_server.py
        ;;
    2)
        # Check if gunicorn is installed
        if ! command -v gunicorn &> /dev/null; then
            echo "Gunicorn is required for production mode but not installed."
            echo "Installing gunicorn..."
            pip install gunicorn
        fi
        
        echo "Starting server in production mode..."
        # Get port from user
        read -p "Enter port number (default: 5000): " port
        port=${port:-5000}
        
        # Start gunicorn
        gunicorn --bind 0.0.0.0:$port api_server:app
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac 