#!/bin/bash

# Vigtra Backend Development Launch Script
# Simple script with comprehensive error handling

set -e # Exit immediately if a command exits with a non-zero status

# Colors for better output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored messages
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Error handler function
error_exit() {
    print_error "$1"
    exit 1
}

# Cleanup function
cleanup() {
    if [ $? -ne 0 ]; then
        print_error "Script failed. Check the errors above."
    fi
}

# Set trap for cleanup
trap cleanup EXIT

print_info "Starting Vigtra Backend Development Server..."

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    error_exit "manage.py not found. Please run this script from the project root directory."
fi

# Check if virtual environment directory exists
if [ ! -d ".venv" ]; then
    print_warning "Virtual environment not found at ./.venv"
    print_info "Creating virtual environment..."

    python3 -m venv .venv || error_exit "Failed to create virtual environment"
    print_success "Virtual environment created"
fi

# Check if activation script exists
if [ ! -f ".venv/bin/activate" ]; then
    error_exit "Virtual environment activation script not found at .venv/bin/activate"
fi

# Activate virtual environment
print_info "Activating virtual environment..."
source .venv/bin/activate || error_exit "Failed to activate virtual environment"

# Verify virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    error_exit "Virtual environment not properly activated"
fi

print_success "Virtual environment activated: $(basename $VIRTUAL_ENV)"

# Check if Python is available
if ! command -v python &>/dev/null; then
    error_exit "Python not found in virtual environment"
fi

# Check Python version
python_version=$(python --version 2>&1)
print_info "Using $python_version"

# Install/update dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    print_info "Installing/updating dependencies..."
    pip install -r requirements.txt || error_exit "Failed to install dependencies"
    print_success "Dependencies installed"
elif [ -f "pyproject.toml" ]; then
    print_info "Installing/updating dependencies with uv..."
    if command -v uv &>/dev/null; then
        uv sync || error_exit "Failed to sync dependencies with uv"
    else
        print_warning "uv not found, falling back to pip"
        pip install -e . || error_exit "Failed to install project with pip"
    fi
    print_success "Dependencies installed"
else
    print_warning "No requirements.txt or pyproject.toml found"
fi

# Check for .env file
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        print_warning ".env file not found. Copying from .env.example"
        cp .env.example .env || error_exit "Failed to copy .env.example"
        print_warning "Please edit .env file with your configuration"
    else
        print_warning "No .env file found. Using default settings"
    fi
else
    print_success "Environment configuration found"
fi

# Check Django configuration
print_info "Checking Django configuration..."
python manage.py check || error_exit "Django configuration check failed"
print_success "Django configuration is valid"

# Check for pending migrations
print_info "Checking for database migrations..."
if python manage.py showmigrations --plan 2>/dev/null | grep -q "\[ \]"; then
    print_warning "Pending migrations detected"
    read -p "Apply migrations now? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Applying migrations..."
        python manage.py migrate || error_exit "Migration failed"
        print_success "Migrations applied"
    else
        print_warning "Skipping migrations. Server may not work correctly."
    fi
else
    print_success "Database is up to date"
fi

# Get server host and port from environment or use defaults
HOST=${HOST:-127.0.0.1}
PORT=${PORT:-8000}

print_info "Starting development server on http://$HOST:$PORT"
print_info "Press Ctrl+C to stop the server"
echo

# Start the development server
python manage.py runserver $HOST:$PORT || error_exit "Failed to start development server"
