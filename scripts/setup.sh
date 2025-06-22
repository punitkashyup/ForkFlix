#!/bin/bash

echo "Setting up ForkFlix development environment..."

echo "Installing frontend dependencies..."
cd frontend
npm install
cd ..

echo "Setting up Python virtual environment..."
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd ..

echo "Setup complete!"
echo "To start development:"
echo "1. Frontend: cd frontend && npm start"
echo "2. Backend: cd backend && source venv/bin/activate && uvicorn app.main:app --reload"