# Vigtra Backend Testing Guide

## Overview

This guide covers the testing strategy, tools, and best practices for the Vigtra Backend project. Our testing approach ensures code quality, reliability, and maintainability.

## Table of Contents

- [Testing Philosophy](#testing-philosophy)
- [Testing Structure](#testing-structure)
- [Test Types](#test-types)
- [Running Tests](#running-tests)
- [Writing Tests](#writing-tests)
- [Test Coverage](#test-coverage)
- [Best Practices](#best-practices)
- [Continuous Integration](#continuous-integration)

## Testing Philosophy

We follow a comprehensive testing approach with multiple layers:

1. **Unit Tests**: Test individual components in isolation
2. **Integration Tests**: Test component interactions
3. **API Tests**: Test GraphQL and REST endpoints
4. **End-to-End Tests**: Test complete user workflows

### Testing Pyramid

```
    /\
   /  \     E2E Tests (Few, High Value)
  /____\
 /      \   Integration Tests (Some, Medium Value)
/________\
|        |  Unit Tests (Many, Fast, Low Cost)
|________|
```

## Testing Structure

### Directory Organization

```
vigtra_backend/
├── tests/                      # Test root directory
│   ├── __init__.py
│   ├── base.py                 # Base test classes and utilities
│   ├── conftest.py            # Pytest configuration
│   ├── core/                  # Core functionality tests
│   │   ├── test_models.py
│   │   ├── test_services.py
│   │   └── test_utils.py
│   ├── authentication/        # Authentication tests
│   │   ├── test_models.py
│   │   ├── test_services.py
│   │   └── test_views.py
│   ├── insuree/              # Insuree module tests
│   │   ├── test_models.py
│   │   ├── test_family_models.py
│   │   └── test_services.py
│   └── integration/          # Integration tests
│       └── test_api_endpoints.py
└── modules/                   # Application modules
    └── [module]/
        └── tests.py           # Module-specific tests
```

### Base Test Classes

We provide several base test classes for different testing scenarios:

- `BaseTestCase`: Basic test utilities
- `BaseModelTestCase`: Model testing utilities
- `BaseServiceTestCase`: Service testing utilities
- `BaseAPITestCase`: API testing utilities
- `BaseTransactionTestCase`: Transaction testing utilities

## Test Types

### Unit Tests

Test individual functions, methods, and classes in isolation.

```python
from tests.base import BaseModelTestCase
from modules.insuree.models import Insuree

class InsureeModelTest(BaseModelTestCase):
    def test_insuree_creation(self):
        """Test creating an insuree."""
        insuree = Insuree.objects.create(
            chf_id='12345',
            last_name='Doe',
            other_names='John',
            audit_user=self.test_user
        )
        
        self.assertEqual(insuree.chf_id, '12345')
        self.assertEqual(insuree.last_name, 'Doe')
        self.assertIsNotNone(insuree.uuid)
```

### Service Tests

Test business logic and service layer functionality.

```python
from tests.base import BaseServiceTestCase
from modules.authentication.services import AuthService

class AuthServiceTest(BaseServiceTestCase):
    def test_create_user_success(self):
        """Test successful user creation."""
        user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        
        response = self.auth_service.create(user_data)
        
        self.assertServiceResponse(response, success=True)
        self.assertIn('data', response)
```

### API Tests

Test GraphQL queries, mutations, and REST endpoints.

```python
from tests.base import BaseAPITestCase

class GraphQLAPITest(BaseAPITestCase):
    def test_get_current_user(self):
        """Test current user query."""
        query = """
        query {
            currentUser {
                id
                username
                email
            }
        }
        """
        
        response = self.graphql_query(query, user=self.test_user)
        
        self.assertGraphQLResponse(response, data_keys=['currentUser'])
        self.assertEqual(
            response['data']['currentUser']['username'],
            self.test_user.username
        )
```

### Integration Tests

Test interactions between multiple components.

```python
from tests.base import BaseAPITestCase

class InsureeIntegrationTest(BaseAPITestCase):
    def test_create_insuree_with_family(self):
        """Test creating insuree and adding to family."""
        # Create family
        family_data = self.generate_family_data()
        family = Family.objects.create(**family_data)
        
        # Create insuree
        insuree_data = self.generate_insuree_data()
        insuree = Insuree.objects.create(**insuree_data)
        
        # Add to family
        membership = FamilyMembership.objects.create(
            family=family,
            insuree=insuree,
            is_head=True
        )
        
        # Verify integration
        self.assertEqual(membership.family, family)
        self.assertEqual(membership.insuree, insuree)
        self.assertTrue(membership.is_head)
```

## Running Tests

### Command Line

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test modules.insuree

# Run specific test class
python manage.py test tests.core.test_models.ChangeLogModelTest

# Run specific test method
python manage.py test tests.core.test_models.ChangeLogModelTest.test_change_log_creation

# Run tests with coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Generate HTML report

# Run tests in parallel
python manage.py test --parallel

# Run tests with verbose output
python manage.py test --verbosity=2
```

### Using Pytest (Alternative)

```bash
# Install pytest-django
pip install pytest-django

# Run all tests
pytest

# Run specific tests
pytest tests/core/test_models.py

# Run with coverage
pytest --cov=modules --cov-report=html

# Run with specific markers
pytest -m "unit"
pytest -m "integration"

# Run failed tests only
pytest --lf
```

### Environment Variables

Set these environment variables for testing:

```bash
export ENVIRONMENT=testing
export DEBUG=true
export DB_ENGINE=sqlite
export CACHE_BACKEND=dummy
```

## Writing Tests

### Test Naming Conventions

- Test files: `test_*.py`
- Test classes: `*Test` (e.g., `InsureeModelTest`)
- Test methods: `test_*` (e.g., `test_create_insuree`)

### Test Documentation

Each test should have a clear docstring explaining what it tests:

```python
def test_insuree_unique_chf_id(self):
    """Test that CHF ID must be unique across all insurees."""
    # Test implementation
```

### Test Data Generation

Use the `TestDataMixin` for generating test data:

```python
class MyTest(BaseTestCase, TestDataMixin):
    def test_with_generated_data(self):
        insuree_data = self.generate_insuree_data(
            last_name='Custom',
            gender='M'
        )
        # Use generated data
```

### Assertions

Use descriptive assertions and custom assertion methods:

```python
# Use custom assertion methods
self.assertServiceResponse(response, success=True)
self.assertGraphQLResponse(response, has_errors=False)

# Provide descriptive messages
self.assertEqual(
    insuree.status, 
    InsureeStatus.ACTIVE,
    "Newly created insuree should be active"
)
```

### Mocking

Use mocking for external dependencies:

```python
from unittest.mock import patch, MagicMock

class ServiceTest(BaseServiceTestCase):
    @patch('modules.core.services.external_api_call')
    def test_external_service_integration(self, mock_api):
        mock_api.return_value = {'success': True}
        
        result = self.service.process_external_data()
        
        self.assertTrue(result['success'])
        mock_api.assert_called_once()
```

### Database Testing

For tests requiring database transactions:

```python
from tests.base import BaseTransactionTestCase

class TransactionTest(BaseTransactionTestCase):
    def test_transaction_rollback(self):
        """Test that failed operations roll back properly."""
        with self.assertRaises(ValidationError):
            with transaction.atomic():
                # Operations that should fail
                pass
```

## Test Coverage

### Coverage Goals

- **Minimum**: 80% overall coverage
- **Target**: 90% overall coverage
- **Critical modules**: 95% coverage

### Coverage Commands

```bash
# Run tests with coverage
coverage run --source='.' manage.py test

# Generate coverage report
coverage report

# Generate HTML coverage report
coverage html

# View coverage in browser
open htmlcov/index.html
```

### Coverage Configuration

Create `.coveragerc` file:

```ini
[run]
source = .
omit = 
    */venv/*
    */migrations/*
    manage.py
    */settings/*
    */tests/*
    */test_*.py

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
```

## Best Practices

### Test Organization

1. **One test per behavior**: Each test should verify one specific behavior
2. **Arrange-Act-Assert**: Structure tests with clear setup, action, and verification
3. **Independent tests**: Tests should not depend on each other
4. **Descriptive names**: Test names should clearly describe what is being tested

### Test Data

1. **Use factories**: Create reusable test data factories
2. **Minimal data**: Only create data necessary for the test
3. **Clean up**: Ensure tests clean up after themselves
4. **Realistic data**: Use realistic but not production data

### Performance

1. **Fast tests**: Keep unit tests fast (< 1 second each)
2. **Database optimization**: Use `setUpTestData` for shared test data
3. **Parallel execution**: Design tests to run in parallel
4. **Selective testing**: Use tags to run subsets of tests

### Maintainability

1. **DRY principle**: Don't repeat test setup code
2. **Base classes**: Use base test classes for common functionality
3. **Helper methods**: Create helper methods for complex test operations
4. **Documentation**: Document complex test scenarios

## Test Configuration

### Django Settings

Test-specific settings in `vigtra/settings/testing.py`:

```python
from .base import *

# Use in-memory database for speed
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Disable caching in tests
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Disable migrations for speed
class DisableMigrations:
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Test-specific configurations
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',  # Fast for tests
]

EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
```

### Pytest Configuration

Create `pytest.ini`:

```ini
[tool:pytest]
DJANGO_SETTINGS_MODULE = vigtra.settings.testing
python_files = tests.py test_*.py *_tests.py
python_classes = Test* *Tests *Test
python_functions = test_*
addopts = 
    --tb=short
    --strict-markers
    --disable-warnings
markers =
    unit: Unit tests
    integration: Integration tests
    api: API tests
    slow: Slow tests
```

## Continuous Integration

### GitHub Actions

Create `.github/workflows/tests.yml`:

```yaml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.13
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install coverage
    
    - name: Run tests
      run: |
        coverage run --source='.' manage.py test
        coverage xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v1
      with:
        file: ./coverage.xml
```

### Quality Gates

Set up quality gates for:

- **Test coverage**: Minimum 80%
- **Test execution time**: Maximum 5 minutes
- **No failing tests**: All tests must pass
- **No critical security issues**: Security scan must pass

## Troubleshooting

### Common Issues

1. **Database locks**: Use separate test databases
2. **Async issues**: Use `sync_to_async` for async code testing
3. **Cache pollution**: Clear cache between tests
4. **Time-dependent tests**: Use `freeze_time` for consistent results

### Debug Tests

```bash
# Run single test with pdb
python manage.py test tests.core.test_models.MyTest.test_method --pdb

# Run with print statements
python manage.py test --verbosity=2

# Use pytest for better debugging
pytest tests/core/test_models.py::MyTest::test_method -v -s
```

### Performance Profiling

```bash
# Profile test execution
python -m cProfile -o profile_output manage.py test

# Analyze profile
python -c "
import pstats
p = pstats.Stats('profile_output')
p.sort_stats('cumulative').print_stats(10)
"
```

## Resources

- [Django Testing Documentation](https://docs.djangoproject.com/en/stable/topics/testing/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [Factory Boy Documentation](https://factoryboy.readthedocs.io/)
- [Mock Documentation](https://docs.python.org/3/library/unittest.mock.html)