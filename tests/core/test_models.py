"""
Tests for core models.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from modules.core.models.change_log import ChangeLog, ActionType
from modules.core.models.openimis_core_models import VersionedModel, ExtendableModel
from tests.base import BaseModelTestCase, TestDataMixin
from faker import Faker

User = get_user_model()
fake = Faker()


class ChangeLogModelTest(BaseModelTestCase, TestDataMixin):
    """Test ChangeLog model functionality."""
    
    def setUp(self):
        super().setUp()
        self.test_user = self.create_test_user()
    
    def test_change_log_creation(self):
        """Test creating a change log entry."""
        change_log = ChangeLog.objects.create(
            action=ActionType.CREATED,
            object_type='TestModel',
            object_id='123',
            user=self.test_user,
            changes={'field': 'value'},
            metadata={'source': 'test'}
        )
        
        self.assertEqual(change_log.action, ActionType.CREATED)
        self.assertEqual(change_log.object_type, 'TestModel')
        self.assertEqual(change_log.object_id, '123')
        self.assertEqual(change_log.user, self.test_user)
        self.assertIsNotNone(change_log.timestamp)
        self.assertEqual(change_log.changes, {'field': 'value'})
        self.assertEqual(change_log.metadata, {'source': 'test'})
    
    def test_change_log_required_fields(self):
        """Test that required fields are enforced."""
        # Test missing action
        with self.assertRaises(ValidationError):
            change_log = ChangeLog(
                object_type='TestModel',
                object_id='123',
                user=self.test_user
            )
            change_log.full_clean()
        
        # Test missing object_type
        with self.assertRaises(ValidationError):
            change_log = ChangeLog(
                action=ActionType.CREATED,
                object_id='123',
                user=self.test_user
            )
            change_log.full_clean()
    
    def test_action_type_choices(self):
        """Test all action type choices are valid."""
        valid_actions = [choice[0] for choice in ActionType.choices]
        
        for action in valid_actions:
            change_log = ChangeLog(
                action=action,
                object_type='TestModel',
                object_id='123',
                user=self.test_user
            )
            # Should not raise validation error
            change_log.full_clean()
    
    def test_change_log_ordering(self):
        """Test that change logs are ordered by timestamp."""
        # Create multiple change logs
        change_log1 = ChangeLog.objects.create(
            action=ActionType.CREATED,
            object_type='TestModel',
            object_id='123',
            user=self.test_user
        )
        
        change_log2 = ChangeLog.objects.create(
            action=ActionType.UPDATED,
            object_type='TestModel',
            object_id='123',
            user=self.test_user
        )
        
        # Get all change logs
        change_logs = list(ChangeLog.objects.all())
        
        # Should be ordered by timestamp (newest first if default ordering is -timestamp)
        self.assertTrue(change_logs[0].timestamp >= change_logs[1].timestamp)
    
    def test_change_log_str_representation(self):
        """Test string representation of change log."""
        change_log = ChangeLog.objects.create(
            action=ActionType.CREATED,
            object_type='TestModel',
            object_id='123',
            user=self.test_user
        )
        
        str_repr = str(change_log)
        self.assertIn('CREATED', str_repr)
        self.assertIn('TestModel', str_repr)
        self.assertIn('123', str_repr)
    
    def test_change_log_with_generic_foreign_key(self):
        """Test change log with generic foreign key to actual model."""
        # Use the User model as test target
        change_log = ChangeLog.objects.create(
            action=ActionType.UPDATED,
            content_object=self.test_user,
            user=self.test_user,
            changes={'username': 'new_username'}
        )
        
        self.assertEqual(change_log.content_object, self.test_user)
        self.assertEqual(change_log.object_id, str(self.test_user.pk))
    
    def test_bulk_change_log_creation(self):
        """Test creating multiple change logs efficiently."""
        change_logs = []
        for i in range(10):
            change_logs.append(ChangeLog(
                action=ActionType.CREATED,
                object_type='TestModel',
                object_id=str(i),
                user=self.test_user,
                changes={'index': i}
            ))
        
        ChangeLog.objects.bulk_create(change_logs)
        
        self.assertEqual(ChangeLog.objects.count(), 10)
    
    def test_change_log_filtering(self):
        """Test filtering change logs by various criteria."""
        # Create change logs for different objects
        ChangeLog.objects.create(
            action=ActionType.CREATED,
            object_type='TestModel1',
            object_id='123',
            user=self.test_user
        )
        
        ChangeLog.objects.create(
            action=ActionType.UPDATED,
            object_type='TestModel2',
            object_id='456',
            user=self.test_user
        )
        
        # Filter by action
        created_logs = ChangeLog.objects.filter(action=ActionType.CREATED)
        self.assertEqual(created_logs.count(), 1)
        
        # Filter by object_type
        model1_logs = ChangeLog.objects.filter(object_type='TestModel1')
        self.assertEqual(model1_logs.count(), 1)
        
        # Filter by user
        user_logs = ChangeLog.objects.filter(user=self.test_user)
        self.assertEqual(user_logs.count(), 2)


class CoreModelsTest(BaseModelTestCase):
    """Test core model mixins and base classes."""
    
    def test_versioned_model_fields(self):
        """Test that VersionedModel has expected fields."""
        # We can't instantiate abstract models directly, 
        # but we can check the fields are defined
        expected_fields = ['validity_from', 'validity_to', 'legacy_id']
        
        # Check if the fields exist in the model's meta
        versioned_fields = [field.name for field in VersionedModel._meta.fields]
        
        for field in expected_fields:
            self.assertIn(field, versioned_fields)
    
    def test_extendable_model_fields(self):
        """Test that ExtendableModel has expected fields."""
        expected_fields = ['json_ext']
        
        extendable_fields = [field.name for field in ExtendableModel._meta.fields]
        
        for field in expected_fields:
            self.assertIn(field, extendable_fields)


class ChangeLogQuerySetTest(TestCase):
    """Test ChangeLog QuerySet methods and managers."""
    
    def setUp(self):
        self.test_user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_recent_changes_query(self):
        """Test querying recent changes."""
        # Create some change logs
        ChangeLog.objects.create(
            action=ActionType.CREATED,
            object_type='TestModel',
            object_id='123',
            user=self.test_user
        )
        
        # Query recent changes
        recent_changes = ChangeLog.objects.filter(
            timestamp__gte=timezone.now() - timezone.timedelta(hours=1)
        )
        
        self.assertEqual(recent_changes.count(), 1)
    
    def test_changes_by_user(self):
        """Test querying changes by specific user."""
        # Create another user
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        
        # Create change logs for both users
        ChangeLog.objects.create(
            action=ActionType.CREATED,
            object_type='TestModel',
            object_id='123',
            user=self.test_user
        )
        
        ChangeLog.objects.create(
            action=ActionType.UPDATED,
            object_type='TestModel',
            object_id='456',
            user=other_user
        )
        
        # Query changes by specific user
        user_changes = ChangeLog.objects.filter(user=self.test_user)
        self.assertEqual(user_changes.count(), 1)
        
        other_user_changes = ChangeLog.objects.filter(user=other_user)
        self.assertEqual(other_user_changes.count(), 1)
    
    def test_changes_by_object(self):
        """Test querying changes for specific object."""
        # Create change logs for same object
        ChangeLog.objects.create(
            action=ActionType.CREATED,
            object_type='TestModel',
            object_id='123',
            user=self.test_user
        )
        
        ChangeLog.objects.create(
            action=ActionType.UPDATED,
            object_type='TestModel',
            object_id='123',
            user=self.test_user
        )
        
        # Query changes for specific object
        object_changes = ChangeLog.objects.filter(
            object_type='TestModel',
            object_id='123'
        )
        
        self.assertEqual(object_changes.count(), 2)
    
    def test_action_type_filtering(self):
        """Test filtering by action types."""
        actions = [ActionType.CREATED, ActionType.UPDATED, ActionType.DELETED]
        
        # Create change logs with different actions
        for action in actions:
            ChangeLog.objects.create(
                action=action,
                object_type='TestModel',
                object_id=f'test_{action}',
                user=self.test_user
            )
        
        # Test filtering by each action type
        for action in actions:
            filtered_logs = ChangeLog.objects.filter(action=action)
            self.assertEqual(filtered_logs.count(), 1)
            self.assertEqual(filtered_logs.first().action, action)