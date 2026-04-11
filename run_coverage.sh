#!/bin/bash

echo "Starting test coverage process..."

# Navigate to backend directory from the project root
PROJECT_ROOT=$(pwd)
cd "$PROJECT_ROOT/backend" || exit

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
else
    echo "Virtual environment not found in backend/venv directory!"
    exit 1
fi

# Ensure pytest and pytest-cov are installed
echo "Checking dependencies (pytest and pytest-cov)..."
pip install -q pytest pytest-cov

# Run pytest with coverage for the 'app' directory
# (assuming the main application code is inside 'backend/app/')
echo "Running tests with coverage..."
pytest --cov=app --cov-report=term-missing --cov-report=html tests/

# Deactivate the virtual environment
deactivate

echo -e "\n-----------------------------------------------"
echo "Coverage generation complete!"
echo "An HTML report has also been generated."
echo "You can view it by opening: backend/htmlcov/index.html in your browser."
echo "-----------------------------------------------"
