"""
Tests for authentication models.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from tests.base import BaseModelTestCase, TestDataMixin
from faker import Faker

User = get_user_model()
fake = Faker()


class UserModelTest(BaseModelTestCase, TestDataMixin):
    """Test User model functionality."""
    
    def test_user_creation(self):
        """Test creating a user."""
        user_data = {
            'username': fake.user_name(),
            'email': fake.email(),
            'password': 'testpass123',
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
        }
        
        user = User.objects.create_user(**user_data)
        
        self.assertEqual(user.username, user_data['username'])
        self.assertEqual(user.email, user_data['email'])
        self.assertEqual(user.first_name, user_data['first_name'])
        self.assertEqual(user.last_name, user_data['last_name'])
        self.assertTrue(user.check_password('testpass123'))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
    
    def test_superuser_creation(self):
        """Test creating a superuser."""
        user_data = {
            'username': fake.user_name(),
            'email': fake.email(),
            'password': 'adminpass123',
        }
        
        superuser = User.objects.create_superuser(**user_data)
        
        self.assertEqual(superuser.username, user_data['username'])
        self.assertEqual(superuser.email, user_data['email'])
        self.assertTrue(superuser.check_password('adminpass123'))
        self.assertTrue(superuser.is_active)
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
    
    def test_user_string_representation(self):
        """Test user string representation."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # The string representation might be username or email
        str_repr = str(user)
        self.assertTrue(
            'testuser' in str_repr or 'test@example.com' in str_repr,
            f"String representation should contain username or email: {str_repr}"
        )
    
    def test_user_unique_constraints(self):
        """Test user unique constraints."""
        # Create first user
        user1 = User.objects.create_user(
            username='uniqueuser',
            email='unique@example.com',
            password='testpass123'
        )
        
        # Try to create user with same username
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                username='uniqueuser',  # Same username
                email='different@example.com',
                password='testpass123'
            )
        
        # Try to create user with same email (if email is unique)
        try:
            user2 = User.objects.create_user(
                username='differentuser',
                email='unique@example.com',  # Same email
                password='testpass123'
            )
            # If this succeeds, email uniqueness is not enforced
            self.assertNotEqual(user1.username, user2.username)
        except IntegrityError:
            # Email uniqueness is enforced
            pass
    
    def test_user_required_fields(self):
        """Test user required fields."""
        # Test missing username
        with self.assertRaises((ValueError, IntegrityError)):
            User.objects.create_user(
                username='',
                email='test@example.com',
                password='testpass123'
            )
        
        # Test missing email (might not be required depending on configuration)
        try:
            user = User.objects.create_user(
                username='testuser',
                email='',
                password='testpass123'
            )
            # If this succeeds, email is not required
            self.assertEqual(user.username, 'testuser')
        except (ValueError, IntegrityError):
            # Email is required
            pass
    
    def test_user_password_hashing(self):
        """Test that passwords are properly hashed."""
        password = 'plaintext_password'
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password=password
        )
        
        # Password should be hashed, not stored in plain text
        self.assertNotEqual(user.password, password)
        self.assertTrue(user.password.startswith('pbkdf2_sha256$') or 
                       user.password.startswith('argon2$') or
                       user.password.startswith('bcrypt$'))
        
        # Should be able to check password
        self.assertTrue(user.check_password(password))
        self.assertFalse(user.check_password('wrong_password'))
    
    def test_user_email_normalization(self):
        """Test email normalization."""
        user = User.objects.create_user(
            username='testuser',
            email='Test.Email@EXAMPLE.COM',
            password='testpass123'
        )
        
        # Email domain should be normalized to lowercase
        self.assertTrue(user.email.endswith('@example.com'))
    
    def test_user_full_name(self):
        """Test user full name functionality."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe'
        )
        
        # Test get_full_name method if it exists
        if hasattr(user, 'get_full_name'):
            full_name = user.get_full_name()
            self.assertIn('John', full_name)
            self.assertIn('Doe', full_name)
        
        # Test get_short_name method if it exists
        if hasattr(user, 'get_short_name'):
            short_name = user.get_short_name()
            self.assertEqual(short_name, 'John')
    
    def test_user_permissions(self):
        """Test user permissions functionality."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Regular user should not have permissions
        self.assertFalse(user.has_perm('auth.add_user'))
        self.assertFalse(user.has_perm('auth.change_user'))
        self.assertFalse(user.has_perm('auth.delete_user'))
        
        # Superuser should have all permissions
        superuser = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        
        self.assertTrue(superuser.has_perm('auth.add_user'))
        self.assertTrue(superuser.has_perm('auth.change_user'))
        self.assertTrue(superuser.has_perm('auth.delete_user'))
    
    def test_user_groups_and_permissions(self):
        """Test user groups and permissions functionality."""
        from django.contrib.auth.models import Group, Permission
        from django.contrib.contenttypes.models import ContentType
        
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create a group
        group = Group.objects.create(name='Test Group')
        
        # Add user to group
        user.groups.add(group)
        
        # Check group membership
        self.assertIn(group, user.groups.all())
        
        # Add permission to group
        content_type = ContentType.objects.get_for_model(User)
        permission = Permission.objects.filter(content_type=content_type).first()
        
        if permission:
            group.permissions.add(permission)
            
            # User should have permission through group
            self.assertTrue(user.has_perm(f'{permission.content_type.app_label}.{permission.codename}'))
    
    def test_user_active_status(self):
        """Test user active status functionality."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # User should be active by default
        self.assertTrue(user.is_active)
        
        # Deactivate user
        user.is_active = False
        user.save()
        
        # Refresh from database
        user.refresh_from_db()
        self.assertFalse(user.is_active)
    
    def test_user_last_login_tracking(self):
        """Test last login tracking."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Initially, last_login should be None
        self.assertIsNone(user.last_login)
        
        # Simulate login
        from django.utils import timezone
        user.last_login = timezone.now()
        user.save()
        
        # Refresh from database
        user.refresh_from_db()
        self.assertIsNotNone(user.last_login)
    
    def test_user_date_joined(self):
        """Test date joined functionality."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # date_joined should be set automatically
        self.assertIsNotNone(user.date_joined)
        
        # Should be recent
        from django.utils import timezone
        from datetime import timedelta
        
        recent_time = timezone.now() - timedelta(minutes=1)
        self.assertGreater(user.date_joined, recent_time)


class UserManagerTest(TestCase):
    """Test User manager functionality."""
    
    def test_create_user_method(self):
        """Test create_user manager method."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.assertIsInstance(user, User)
        self.assertEqual(user.username, 'testuser')
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
    
    def test_create_superuser_method(self):
        """Test create_superuser manager method."""
        superuser = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        
        self.assertIsInstance(superuser, User)
        self.assertEqual(superuser.username, 'admin')
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
    
    def test_user_queryset_methods(self):
        """Test custom queryset methods if they exist."""
        # Create test users
        active_user = User.objects.create_user(
            username='active',
            email='active@example.com',
            password='testpass123',
            is_active=True
        )
        
        inactive_user = User.objects.create_user(
            username='inactive',
            email='inactive@example.com',
            password='testpass123',
            is_active=False
        )
        
        # Test filtering active users
        active_users = User.objects.filter(is_active=True)
        self.assertIn(active_user, active_users)
        self.assertNotIn(inactive_user, active_users)
        
        # Test filtering inactive users
        inactive_users = User.objects.filter(is_active=False)
        self.assertIn(inactive_user, inactive_users)
        self.assertNotIn(active_user, inactive_users)