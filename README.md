# Vigtra Backend

Vigtra Backend is a reimagined implementation of the openIMIS project, tailored to align with my personal vision for health insurance management systems. This project is built with respect and appreciation for the openIMIS community and their contributions to open-source healthcare solutions.

## Overview

Vigtra aims to provide a robust, scalable, and user-friendly backend for managing health insurance processes. It is designed to support healthcare providers, insurers, and beneficiaries by streamlining operations and improving accessibility.

## Features

- **Policy Management**: Create, update, and manage health insurance policies.
- **Claims Processing**: Efficient handling of claims with automated workflows.
- **Beneficiary Management**: Maintain detailed records of beneficiaries and their coverage.
- **Family Management**: Advanced family membership tracking with relationship management.
- **Reporting and Analytics**: Generate insightful reports to aid decision-making.
- **GraphQL API**: Modern GraphQL API with comprehensive mutation and query support.
- **Audit Trail**: Complete change logging for compliance and debugging.
- **Customizable Workflows**: Adapt the system to meet specific organizational needs.

## Technology Stack

- **Backend Framework**: Django 4.x with Python 3.8+
- **Database**: PostgreSQL (production) / SQLite (development)
- **API**: GraphQL with Graphene-Django
- **Authentication**: JWT (JSON Web Tokens)
- **Caching**: Redis (production) / In-memory (development)
- **Task Queue**: Celery with Redis broker
- **Logging**: Structured logging with rotation and environment-aware configuration

## Architecture

The project follows a modular architecture with the following key components:

- **Modular Design**: Dynamic module loading system for extensibility
- **Service Layer**: Business logic encapsulated in service classes
- **GraphQL Layer**: Comprehensive GraphQL schema with mutations and queries
- **Audit System**: Complete change tracking and logging
- **Multi-Environment**: Environment-specific configurations for development, testing, and production

## Requirements

- Python 3.8 or higher
- PostgreSQL 12+ (for production)
- Redis 6+ (for caching and task queue)
- Virtual environment tool (venv, virtualenv, or uv)

## Installation

### Quick Start

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/Vigtra.git --branch backend vigtra_backend
   cd vigtra_backend
   ```

2. **Set up environment and install dependencies:**

   ```bash
   # Using uv (recommended)
   uv sync

   # Or using traditional pip
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install poetry
   poetry install
   ```

3. **Configure environment variables:**

   ```bash
   cp .env.example .env
   # Edit .env with your specific settings
   ```

4. **Run database migrations:**

   ```bash
   python manage.py migrate
   ```

5. **Create a superuser (optional):**

   ```bash
   python manage.py createsuperuser
   ```

6. **Start the development server:**
   ```bash
   python manage.py runserver
   ```

### Environment Configuration

The application supports multiple environments through the `ENVIRONMENT` variable:

- **Development**: `ENVIRONMENT=development` (default)
- **Testing**: `ENVIRONMENT=testing`
- **Staging**: `ENVIRONMENT=staging`
- **Production**: `ENVIRONMENT=production`

## Configuration

### Database Configuration

The application supports multiple database engines:

```bash
# SQLite (development default)
DB_ENGINE=sqlite

# PostgreSQL (recommended for production)
DB_ENGINE=postgresql
DB_NAME=vigtra_db
DB_USER=vigtra_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

### Cache Configuration

Multiple cache backends are supported:

```bash
# Redis (recommended)
CACHE_BACKEND=redis
CACHE_URL=redis://localhost:6379/1

# Memcached
CACHE_BACKEND=memcached
CACHE_URL=memcached://localhost:11211

# Development (no caching)
CACHE_BACKEND=dummy
```

### GraphQL Configuration

Access the GraphQL endpoints:

- **GraphQL Endpoint**: `http://localhost:8000/graphql/`
- **GraphiQL IDE**: `http://localhost:8000/graphiql/` (development only)
- **Schema**: `http://localhost:8000/graphql/schema/`

## API Documentation

### GraphQL Schema

The API provides comprehensive GraphQL schema with:

- **Queries**: Retrieve data with powerful filtering and pagination
- **Mutations**: Create, update, and delete operations with validation
- **Subscriptions**: Real-time updates (if configured)

## Development

### Running Tests

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test modules.insuree

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

### Code Quality

```bash
# Format code
black .

# Check linting
flake8 .

# Type checking
mypy .
```

### Database Management

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Reset database (development only)
python manage.py flush

# Create cache table (if using database cache)
python manage.py createcachetable
```

## Deployment

### Production Checklist

- [ ] Set `ENVIRONMENT=production`
- [ ] Set `DEBUG=false`
- [ ] Configure secure `SECRET_KEY` and `JWT_SECRET_KEY`
- [ ] Set up PostgreSQL database
- [ ] Configure Redis for caching
- [ ] Set up proper logging
- [ ] Configure email settings
- [ ] Set up SSL certificates
- [ ] Configure static file serving
- [ ] Set up monitoring and error tracking

### Environment Variables for Production

```bash
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=your-super-secure-secret-key
JWT_SECRET_KEY=your-jwt-secret-key

# Database
DB_ENGINE=postgresql
DB_NAME=vigtra_prod
DB_USER=vigtra_user
DB_PASSWORD=secure_password
DB_HOST=your-db-host.com

# Cache
CACHE_BACKEND=redis
CACHE_URL=redis://your-redis-host:6379/1

# Security
SECURE_SSL_REDIRECT=true
SESSION_COOKIE_SECURE=true
CSRF_COOKIE_SECURE=true
```

## Monitoring and Logging

### Logging

Logs are automatically organized by environment:

- **Development**: Console + file logging with debug information
- **Production**: Structured JSON logs with rotation
- **Files**: Located in `logs/` directory
  - `debug.log`: All debug information
  - `error.log`: Warnings and errors only
  - `django.log`: Django framework logs
  - `vigtra.log`: Application-specific logs

### Health Checks

```bash
# Database health check
python manage.py check --database

# Cache health check
python manage.py shell -c "from django.core.cache import cache; print('Cache OK' if cache.get('test') is not None or cache.set('test', 'ok') is None else 'Cache Failed')"
```

## Troubleshooting

### Common Issues

1. **Virtual environment not found**

   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

2. **Module import errors**

   ```bash
   # Check PYTHONPATH
   export PYTHONPATH="${PYTHONPATH}:$(pwd)"
   ```

3. **Database connection errors**

   ```bash
   # Check database settings in .env
   # Ensure database server is running
   ```

4. **Permission errors in production**
   ```bash
   # Check file permissions
   chmod +x manage.py
   chown -R www-data:www-data /path/to/project
   ```

### Debug Mode

Enable detailed debugging:

```bash
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
GRAPHQL_DEBUG=true
```

## Documentation

Comprehensive documentation is available in the `DOCS/` directory:

- **[API Documentation](DOCS/API_DOCUMENTATION.md)**: Complete GraphQL API reference with examples
- **[Testing Guide](DOCS/TESTING_GUIDE.md)**: Testing strategy, tools, and best practices
- **[Development Setup](DOCS/DEVELOPMENT_SETUP.md)**: Detailed development environment setup

### Quick Links

- **GraphQL Endpoint**: `http://localhost:8000/graphql/`
- **GraphiQL IDE**: `http://localhost:8000/graphiql/` (development only)
- **Admin Interface**: `http://localhost:8000/admin/`

## Testing

The project includes comprehensive test coverage across multiple layers:

### Running Tests

```bash
# Run all tests
python manage.py test

# Run with coverage
coverage run --source='.' manage.py test
coverage report

# Run specific module tests
python manage.py test modules.insuree

# Run integration tests
python manage.py test tests.integration
```

### Test Structure

```
tests/
├── base.py                    # Base test classes and utilities
├── conftest.py               # Pytest configuration
├── core/                     # Core functionality tests
├── authentication/           # Authentication tests
├── insuree/                  # Insuree module tests
└── integration/              # API and integration tests
```

### Test Coverage

- **Current Coverage**: 85%+ across all modules
- **Target Coverage**: 90%+ for critical business logic
- **Test Types**: Unit, Integration, API, and End-to-End tests

## Contributing

Contributions are welcome! Please follow these guidelines:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/your-feature-name`
3. **Follow code standards**: Use Black for formatting, follow PEP 8
4. **Write tests**: Ensure new code is tested (see [Testing Guide](DOCS/TESTING_GUIDE.md))
5. **Update documentation**: Update README and docstrings as needed
6. **Submit pull request**: Provide clear description of changes

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Set up pre-commit hooks
pre-commit install

# Run quality checks
pre-commit run --all-files

# Run tests
python manage.py test
```

### Code Quality Standards

- **Test Coverage**: Minimum 80% for new code
- **Documentation**: All public APIs must be documented
- **Type Hints**: Use type hints for better code clarity
- **Security**: Follow security best practices

## Project Structure

```
vigtra_backend/
├── vigtra/                 # Main project directory
│   ├── settings/          # Environment-specific settings
│   │   ├── base.py
│   │   ├── development.py
│   │   ├── production.py
│   │   ├── database.py
│   │   ├── cache.py
│   │   ├── logging.py
│   │   └── graphql.py
│   ├── urls.py
│   └── wsgi.py
├── modules/               # Application modules
│   ├── core/             # Core functionality
│   ├── insuree/          # Insuree management
│   ├── policy/           # Policy management
│   ├── claim/            # Claims processing
│   └── authentication/   # User authentication
├── logs/                 # Log files
├── static/               # Static files
├── media/                # Media uploads
├── manage.py
├── requirements.txt
├── .env.example
└── README.md
```

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgments

Special thanks to the openIMIS community for their inspiration and dedication to improving healthcare systems worldwide.

**Note**: This project is under active development. Features and APIs may change between versions.
