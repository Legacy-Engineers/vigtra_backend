# Development Setup Guide

## Prerequisites

- Python 3.13 or higher
- PostgreSQL 12+ (for production-like development)
- Redis 6+ (for caching and task queue)
- Git
- Virtual environment tool (venv, virtualenv, or uv)

## Quick Setup

### 1. Clone and Setup

```bash
git clone https://github.com/yourusername/Vigtra.git --branch backend vigtra_backend
cd vigtra_backend

# Using uv (recommended)
uv sync

# Or using traditional pip
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Configuration

```bash
cp .env.example .env
# Edit .env with your specific settings
```

### 3. Database Setup

```bash
# Create database (PostgreSQL)
createdb vigtra_dev

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### 4. Start Development Server

```bash
python manage.py runserver
```

## Testing Setup

### Running Tests

```bash
# Run all tests
python manage.py test

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html

# Run specific module tests
python manage.py test modules.insuree
```

### Test Database

Tests use SQLite in-memory database by default for speed. To test with PostgreSQL:

```bash
export ENVIRONMENT=testing
export DB_ENGINE=postgresql
export DB_NAME=vigtra_test
python manage.py test
```

## Development Tools

### Code Quality

```bash
# Format code
black .

# Check linting
flake8 .

# Type checking
mypy .

# Import sorting
isort .
```

### Pre-commit Hooks

```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

## API Development

### GraphQL

- **Endpoint**: `http://localhost:8000/graphql/`
- **GraphiQL IDE**: `http://localhost:8000/graphiql/`
- **Schema**: `http://localhost:8000/graphql/schema/`

### Testing API

```bash
# Test GraphQL endpoint
curl -X POST http://localhost:8000/graphql/ \
  -H "Content-Type: application/json" \
  -d '{"query": "{ currentUser { id username } }"}'
```

## Documentation

- **API Documentation**: [DOCS/API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- **Testing Guide**: [DOCS/TESTING_GUIDE.md](TESTING_GUIDE.md)
- **Deployment Guide**: [DEPLOYMENT_CHECKLIST.md](../DEPLOYMENT_CHECKLIST.md)