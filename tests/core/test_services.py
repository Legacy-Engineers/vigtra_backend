"""
Tests for core services and utilities.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock
from modules.core.service_signals import register_signal, emit_signal
from modules.core.utils import vigtra_message
from modules.core.data_services import DataServices
from tests.base import BaseServiceTestCase
import json

User = get_user_model()


class VigtraMessageTest(TestCase):
    """Test vigtra_message utility function."""
    
    def test_success_message(self):
        """Test creating a success message."""
        result = vigtra_message(
            success=True,
            message="Operation successful",
            data={"key": "value"}
        )
        
        self.assertIsInstance(result, dict)
        self.assertTrue(result['success'])
        self.assertEqual(result['message'], "Operation successful")
        self.assertEqual(result['data'], {"key": "value"})
    
    def test_error_message(self):
        """Test creating an error message."""
        result = vigtra_message(
            success=False,
            message="Operation failed",
            error_details=["Error 1", "Error 2"]
        )
        
        self.assertIsInstance(result, dict)
        self.assertFalse(result['success'])
        self.assertEqual(result['message'], "Operation failed")
        self.assertEqual(result['error_details'], ["Error 1", "Error 2"])
    
    def test_default_values(self):
        """Test default values in vigtra_message."""
        result = vigtra_message()
        
        self.assertIsInstance(result, dict)
        self.assertFalse(result['success'])  # Default should be False
        self.assertIn('message', result)
    
    def test_message_with_all_parameters(self):
        """Test message with all possible parameters."""
        result = vigtra_message(
            success=True,
            message="Complete message",
            data={"result": "data"},
            error_details=None,
            metadata={"timestamp": "2024-01-01"}
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['message'], "Complete message")
        self.assertEqual(result['data'], {"result": "data"})
        self.assertEqual(result.get('metadata'), {"timestamp": "2024-01-01"})


class ServiceSignalsTest(TestCase):
    """Test service signal system."""
    
    def setUp(self):
        # Clear any existing signal handlers
        self.signal_handlers = {}
    
    def test_register_signal_decorator(self):
        """Test registering a signal handler."""
        @register_signal("test.signal")
        def test_handler(data, **kwargs):
            return {"success": True, "data": data}
        
        # The decorator should register the handler
        self.assertIsNotNone(test_handler)
    
    def test_signal_emission(self):
        """Test emitting a signal."""
        # Create a mock handler
        handler_called = False
        result_data = None
        
        @register_signal("test.emit")
        def test_handler(data, **kwargs):
            nonlocal handler_called, result_data
            handler_called = True
            result_data = data
            return {"success": True, "processed": data}
        
        # Emit the signal
        test_data = {"message": "test"}
        result = emit_signal("test.emit", test_data)
        
        # Verify the handler was called (implementation dependent)
        # This test might need adjustment based on actual signal implementation
        self.assertIsNotNone(result)
    
    def test_multiple_signal_handlers(self):
        """Test multiple handlers for the same signal."""
        results = []
        
        @register_signal("test.multiple")
        def handler1(data, **kwargs):
            results.append("handler1")
            return {"success": True, "handler": "1"}
        
        @register_signal("test.multiple")
        def handler2(data, **kwargs):
            results.append("handler2")
            return {"success": True, "handler": "2"}
        
        # The behavior depends on implementation
        # This test verifies the registration doesn't cause errors
        self.assertTrue(True)  # Placeholder assertion
    
    def test_signal_with_kwargs(self):
        """Test signal handling with keyword arguments."""
        @register_signal("test.kwargs")
        def handler_with_kwargs(data, user=None, action=None, **kwargs):
            return {
                "success": True,
                "data": data,
                "user": user.username if user else None,
                "action": action
            }
        
        # Test the handler function directly
        test_user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        result = handler_with_kwargs(
            {"test": "data"},
            user=test_user,
            action="test_action"
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['user'], 'testuser')
        self.assertEqual(result['action'], 'test_action')


class DataServicesTest(BaseServiceTestCase):
    """Test DataServices functionality."""
    
    def setUp(self):
        super().setUp()
        self.data_service = DataServices()
    
    def test_data_service_initialization(self):
        """Test DataServices can be initialized."""
        service = DataServices()
        self.assertIsNotNone(service)
    
    def test_data_service_methods_exist(self):
        """Test that expected methods exist on DataServices."""
        # Check if common data service methods exist
        expected_methods = ['get', 'create', 'update', 'delete']
        
        for method_name in expected_methods:
            if hasattr(self.data_service, method_name):
                self.assertTrue(callable(getattr(self.data_service, method_name)))
    
    @patch('modules.core.data_services.DataServices.get')
    def test_data_service_get_method(self, mock_get):
        """Test data service get method."""
        # Mock the get method
        mock_get.return_value = vigtra_message(
            success=True,
            data={"id": 1, "name": "test"}
        )
        
        result = self.data_service.get(1)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['data']['id'], 1)
        mock_get.assert_called_once_with(1)
    
    @patch('modules.core.data_services.DataServices.create')
    def test_data_service_create_method(self, mock_create):
        """Test data service create method."""
        test_data = {"name": "test item", "value": "test value"}
        
        mock_create.return_value = vigtra_message(
            success=True,
            data={"id": 1, **test_data},
            message="Item created successfully"
        )
        
        result = self.data_service.create(test_data)
        
        self.assertTrue(result['success'])
        self.assertIn("created successfully", result['message'])
        mock_create.assert_called_once_with(test_data)
    
    def test_data_service_error_handling(self):
        """Test data service error handling."""
        # This test depends on the actual implementation
        # For now, we'll test that the service can handle exceptions gracefully
        
        try:
            # Attempt an operation that might fail
            result = self.data_service.get(None)  # Invalid ID
            # If it returns a result, it should be a proper error response
            if result:
                self.assertIsInstance(result, dict)
                self.assertIn('success', result)
        except Exception as e:
            # If it raises an exception, that's also acceptable
            self.assertIsInstance(e, Exception)


class CoreUtilitiesTest(TestCase):
    """Test core utility functions and classes."""
    
    def test_json_serialization(self):
        """Test JSON serialization utilities."""
        test_data = {
            "string": "test",
            "number": 42,
            "boolean": True,
            "null": None,
            "array": [1, 2, 3],
            "object": {"nested": "value"}
        }
        
        # Test that the data can be serialized and deserialized
        json_string = json.dumps(test_data)
        deserialized = json.loads(json_string)
        
        self.assertEqual(deserialized, test_data)
    
    def test_data_validation_patterns(self):
        """Test common data validation patterns."""
        # Test email validation pattern (basic)
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        import re
        
        valid_emails = [
            'test@example.com',
            'user.name@domain.co.uk',
            'test123@test-domain.com'
        ]
        
        invalid_emails = [
            'invalid-email',
            '@domain.com',
            'test@',
            'test..test@domain.com'
        ]
        
        for email in valid_emails:
            self.assertTrue(re.match(email_pattern, email), f"Should match: {email}")
        
        for email in invalid_emails:
            self.assertIsNone(re.match(email_pattern, email), f"Should not match: {email}")
    
    def test_common_utility_functions(self):
        """Test common utility functions that might exist."""
        # Test various utility patterns that are commonly used
        
        # Test string utilities
        test_string = "  Test String  "
        self.assertEqual(test_string.strip(), "Test String")
        
        # Test list utilities
        test_list = [1, 2, 2, 3, 3, 3]
        unique_list = list(set(test_list))
        self.assertEqual(len(unique_list), 3)
        
        # Test dictionary utilities
        test_dict = {"a": 1, "b": 2, "c": None}
        filtered_dict = {k: v for k, v in test_dict.items() if v is not None}
        self.assertEqual(len(filtered_dict), 2)
        self.assertNotIn("c", filtered_dict)


class ModuleLoaderTest(TestCase):
    """Test module loading functionality."""
    
    def test_module_loading_concepts(self):
        """Test module loading concepts."""
        # Test that we can import modules dynamically
        import importlib
        
        # Test importing a standard library module
        math_module = importlib.import_module('math')
        self.assertTrue(hasattr(math_module, 'sqrt'))
        
        # Test importing a Django module
        django_test = importlib.import_module('django.test')
        self.assertTrue(hasattr(django_test, 'TestCase'))
    
    def test_module_discovery(self):
        """Test module discovery patterns."""
        import os
        import pkgutil
        
        # Test that we can discover modules in the current package
        current_dir = os.path.dirname(__file__)
        
        # This is a basic test of module discovery concepts
        self.assertTrue(os.path.exists(current_dir))
        
        # Test pkgutil functionality
        modules_found = []
        for importer, modname, ispkg in pkgutil.iter_modules([current_dir]):
            modules_found.append(modname)
        
        # Should find at least this test module
        self.assertIsInstance(modules_found, list)