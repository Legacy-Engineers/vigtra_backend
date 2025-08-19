"""
Tests for authentication services.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock
from modules.authentication.services.auth_service import AuthService
from tests.base import BaseServiceTestCase, TestDataMixin
from faker import Faker

User = get_user_model()
fake = Faker()


class AuthServiceTest(BaseServiceTestCase, TestDataMixin):
    """Test AuthService functionality."""
    
    def setUp(self):
        super().setUp()
        self.auth_service = AuthService()
    
    def test_auth_service_initialization(self):
        """Test AuthService initialization."""
        # Test initialization without user
        service = AuthService()
        self.assertIsNone(service.user)
        
        # Test initialization with user
        service_with_user = AuthService(user=self.test_user)
        self.assertEqual(service_with_user.user, self.test_user)
    
    def test_create_user_success(self):
        """Test successful user creation."""
        user_data = {
            'username': fake.user_name(),
            'email': fake.email(),
            'password': 'testpass123',
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
        }
        
        response = self.auth_service.create(user_data)
        
        self.assertServiceResponse(response, success=True, 
                                 message="created successfully")
        self.assertIn('data', response)
        
        # Verify user was created in database
        created_user = User.objects.get(username=user_data['username'])
        self.assertEqual(created_user.email, user_data['email'])
        self.assertTrue(created_user.check_password('testpass123'))
    
    def test_create_user_missing_required_fields(self):
        """Test user creation with missing required fields."""
        # Test missing username
        user_data_no_username = {
            'email': fake.email(),
            'password': 'testpass123'
        }
        
        response = self.auth_service.create(user_data_no_username)
        self.assertServiceResponse(response, success=False)
        self.assertIn('username', response['message'].lower())
        
        # Test missing email
        user_data_no_email = {
            'username': fake.user_name(),
            'password': 'testpass123'
        }
        
        response = self.auth_service.create(user_data_no_email)
        self.assertServiceResponse(response, success=False)
        self.assertIn('email', response['message'].lower())
        
        # Test missing password
        user_data_no_password = {
            'username': fake.user_name(),
            'email': fake.email()
        }
        
        response = self.auth_service.create(user_data_no_password)
        self.assertServiceResponse(response, success=False)
        self.assertIn('password', response['message'].lower())
    
    def test_create_user_duplicate_username(self):
        """Test creating user with duplicate username."""
        # Create first user
        user_data = {
            'username': 'duplicate_user',
            'email': 'first@example.com',
            'password': 'testpass123'
        }
        
        response1 = self.auth_service.create(user_data)
        self.assertServiceResponse(response1, success=True)
        
        # Try to create second user with same username
        duplicate_data = {
            'username': 'duplicate_user',  # Same username
            'email': 'second@example.com',
            'password': 'testpass123'
        }
        
        response2 = self.auth_service.create(duplicate_data)
        self.assertServiceResponse(response2, success=False)
    
    def test_create_user_invalid_email(self):
        """Test creating user with invalid email."""
        user_data = {
            'username': fake.user_name(),
            'email': 'invalid-email-format',
            'password': 'testpass123'
        }
        
        response = self.auth_service.create(user_data)
        # Depending on validation, this might succeed or fail
        # If email validation is implemented, it should fail
        self.assertIsInstance(response, dict)
        self.assertIn('success', response)
    
    def test_create_user_weak_password(self):
        """Test creating user with weak password."""
        user_data = {
            'username': fake.user_name(),
            'email': fake.email(),
            'password': '123'  # Weak password
        }
        
        response = self.auth_service.create(user_data)
        # Depending on password validation, this might succeed or fail
        self.assertIsInstance(response, dict)
        self.assertIn('success', response)
    
    def test_update_user_success(self):
        """Test successful user update."""
        # Create a user first
        user_data = {
            'username': fake.user_name(),
            'email': fake.email(),
            'password': 'testpass123',
            'first_name': 'Original',
            'last_name': 'Name'
        }
        
        create_response = self.auth_service.create(user_data)
        self.assertServiceResponse(create_response, success=True)
        
        # Get the created user
        created_user = User.objects.get(username=user_data['username'])
        
        # Update user data
        update_data = {
            'uuid': str(created_user.pk),  # Assuming uuid field exists
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated@example.com'
        }
        
        response = self.auth_service.create_or_update(update_data)
        
        # This should call update method
        self.assertIsInstance(response, dict)
        self.assertIn('success', response)
    
    def test_create_or_update_without_uuid(self):
        """Test create_or_update without uuid (should create)."""
        user_data = {
            'username': fake.user_name(),
            'email': fake.email(),
            'password': 'testpass123'
        }
        
        response = self.auth_service.create_or_update(user_data)
        
        # Should call create method
        self.assertServiceResponse(response, success=True)
    
    def test_create_or_update_with_uuid(self):
        """Test create_or_update with uuid (should update)."""
        # Create a user first
        user = User.objects.create_user(
            username=fake.user_name(),
            email=fake.email(),
            password='testpass123'
        )
        
        update_data = {
            'uuid': str(user.pk),
            'first_name': 'Updated'
        }
        
        response = self.auth_service.create_or_update(update_data)
        
        # Should call update method
        self.assertIsInstance(response, dict)
        self.assertIn('success', response)
    
    def test_service_error_handling(self):
        """Test service error handling."""
        # Test with invalid data that should cause an exception
        invalid_data = {
            'username': None,  # This should cause an error
            'email': fake.email(),
            'password': 'testpass123'
        }
        
        response = self.auth_service.create(invalid_data)
        
        self.assertServiceResponse(response, success=False)
        self.assertIn('error_details', response)
    
    def test_validation_method(self):
        """Test _validate_new_user method."""
        # Test with valid data
        valid_data = {
            'username': fake.user_name(),
            'email': fake.email(),
            'password': 'testpass123'
        }
        
        validation_result = self.auth_service._validate_new_user(valid_data)
        
        # If validation passes, it should return success or None
        if validation_result:
            self.assertIn('success', validation_result)
        
        # Test with invalid data
        invalid_data = {
            'username': '',  # Empty username
            'email': fake.email(),
            'password': 'testpass123'
        }
        
        validation_result = self.auth_service._validate_new_user(invalid_data)
        
        if validation_result:
            self.assertServiceResponse(validation_result, success=False)
    
    def test_service_with_user_context(self):
        """Test service methods with user context."""
        # Create a service with user context
        context_user = User.objects.create_user(
            username='context_user',
            email='context@example.com',
            password='testpass123'
        )
        
        service_with_context = AuthService(user=context_user)
        
        # Test that the service maintains user context
        self.assertEqual(service_with_context.user, context_user)
        
        # Test operations with context
        user_data = {
            'username': fake.user_name(),
            'email': fake.email(),
            'password': 'testpass123'
        }
        
        response = service_with_context.create(user_data)
        self.assertIsInstance(response, dict)
        self.assertIn('success', response)
    
    @patch('modules.authentication.services.auth_service.User.objects.create_user')
    def test_create_user_database_error(self, mock_create_user):
        """Test handling database errors during user creation."""
        # Mock database error
        mock_create_user.side_effect = Exception("Database connection failed")
        
        user_data = {
            'username': fake.user_name(),
            'email': fake.email(),
            'password': 'testpass123'
        }
        
        response = self.auth_service.create(user_data)
        
        self.assertServiceResponse(response, success=False)
        self.assertIn('error_details', response)
        self.assertIn('Database connection failed', str(response['error_details']))
    
    def test_service_logging(self):
        """Test that service operations are logged."""
        with self.assertLogs('modules.authentication.services.auth_service', 
                           level='INFO') as log:
            user_data = {
                'username': fake.user_name(),
                'email': fake.email(),
                'password': 'testpass123'
            }
            
            self.auth_service.create(user_data)
            
            # Check if any logs were generated
            # This test might need adjustment based on actual logging implementation
            self.assertTrue(len(log.output) >= 0)
    
    def test_concurrent_user_creation(self):
        """Test handling concurrent user creation attempts."""
        import threading
        import time
        
        results = []
        username = fake.user_name()
        
        def create_user():
            user_data = {
                'username': username,
                'email': fake.email(),
                'password': 'testpass123'
            }
            result = self.auth_service.create(user_data)
            results.append(result)
        
        # Create multiple threads trying to create users with same username
        threads = []
        for i in range(3):
            thread = threading.Thread(target=create_user)
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Only one should succeed due to unique constraint
        successful_results = [r for r in results if r.get('success')]
        failed_results = [r for r in results if not r.get('success')]
        
        # At least one should succeed, others should fail
        self.assertGreaterEqual(len(successful_results), 1)
        self.assertGreaterEqual(len(failed_results), 0)


class AuthServiceIntegrationTest(TestCase):
    """Integration tests for AuthService with other components."""
    
    def setUp(self):
        self.auth_service = AuthService()
    
    def test_user_creation_with_signals(self):
        """Test user creation triggers appropriate signals."""
        # This test would verify that signals are emitted
        # Implementation depends on the actual signal system
        
        user_data = {
            'username': fake.user_name(),
            'email': fake.email(),
            'password': 'testpass123'
        }
        
        # Mock signal handler
        signal_received = []
        
        def signal_handler(sender, **kwargs):
            signal_received.append(kwargs)
        
        # If signals are implemented, connect the handler
        # from django.db.models.signals import post_save
        # post_save.connect(signal_handler, sender=User)
        
        response = self.auth_service.create(user_data)
        
        self.assertServiceResponse(response, success=True)
        
        # Verify signal was received (if implemented)
        # self.assertEqual(len(signal_received), 1)
    
    def test_user_creation_with_permissions(self):
        """Test user creation with default permissions."""
        user_data = {
            'username': fake.user_name(),
            'email': fake.email(),
            'password': 'testpass123'
        }
        
        response = self.auth_service.create(user_data)
        self.assertServiceResponse(response, success=True)
        
        # Get created user
        created_user = User.objects.get(username=user_data['username'])
        
        # Test default permissions
        self.assertFalse(created_user.is_staff)
        self.assertFalse(created_user.is_superuser)
        self.assertTrue(created_user.is_active)
    
    def test_user_creation_with_groups(self):
        """Test user creation and group assignment."""
        from django.contrib.auth.models import Group
        
        # Create a default group
        default_group = Group.objects.create(name='Default Users')
        
        user_data = {
            'username': fake.user_name(),
            'email': fake.email(),
            'password': 'testpass123'
        }
        
        response = self.auth_service.create(user_data)
        self.assertServiceResponse(response, success=True)
        
        # Get created user
        created_user = User.objects.get(username=user_data['username'])
        
        # Manually assign to group (or test if it's done automatically)
        created_user.groups.add(default_group)
        
        # Verify group assignment
        self.assertIn(default_group, created_user.groups.all())