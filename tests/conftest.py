"""
Pytest configuration and fixtures for Vigtra Backend tests.
"""

import pytest
from django.test import Client
from django.contrib.auth import get_user_model
from faker import Faker
from modules.authentication.services.auth_service import AuthService

User = get_user_model()
fake = Faker()


@pytest.fixture
def client():
    """Django test client fixture."""
    return Client()


@pytest.fixture
def auth_service():
    """Authentication service fixture."""
    return AuthService()


@pytest.fixture
def fake_data():
    """Faker instance fixture."""
    return fake


@pytest.fixture
def test_user(auth_service, fake_data):
    """Create a test user."""
    user_data = {
        'username': fake_data.user_name(),
        'email': fake_data.email(),
        'password': 'testpass123',
        'first_name': fake_data.first_name(),
        'last_name': fake_data.last_name(),
    }
    
    response = auth_service.create(user_data)
    if response.get('success'):
        return User.objects.get(username=user_data['username'])
    else:
        raise Exception(f"Failed to create test user: {response}")


@pytest.fixture
def admin_user(auth_service, fake_data):
    """Create a test admin user."""
    user_data = {
        'username': fake_data.user_name(),
        'email': fake_data.email(),
        'password': 'testpass123',
        'first_name': fake_data.first_name(),
        'last_name': fake_data.last_name(),
        'is_staff': True,
        'is_superuser': True,
    }
    
    response = auth_service.create(user_data)
    if response.get('success'):
        return User.objects.get(username=user_data['username'])
    else:
        raise Exception(f"Failed to create test admin user: {response}")


@pytest.fixture
def authenticated_client(client, test_user):
    """Client authenticated with test user."""
    client.force_login(test_user)
    return client


@pytest.fixture
def admin_client(client, admin_user):
    """Client authenticated with admin user."""
    client.force_login(admin_user)
    return client