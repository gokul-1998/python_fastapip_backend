#!/bin/bash

# Exit on any error
set -e

# Check if virtual environment exists, if not create it
if [ ! -d "env" ]; then
    echo "Creating virtual environment..."
    python3 -m venv env
fi

# Activate virtual environment
source env/bin/activate

# Upgrade pip to the latest version
pip install --upgrade pip

# Install requirements if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "Installing requirements..."
    pip install -r requirements.txt
else
    # Install common FastAPI dependencies if no requirements file
    echo "No requirements.txt found. Installing default dependencies..."
    pip install fastapi uvicorn sqlalchemy pydantic
fi

# Run database migrations or create tables (if applicable)
python3 -c "from app import Base, engine; Base.metadata.create_all(bind=engine)"

# Run the FastAPI application using uvicorn
echo "Starting the application..."
uvicorn app:app --host 0.0.0.0 --port 8000 --reload

# Deactivate virtual environment when done
deactivate