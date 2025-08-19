"""
Tests for core utility functions and classes.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock
from modules.core import utils
from tests.base import BaseTestCase
import json
import uuid
from datetime import datetime, date

User = get_user_model()


class UtilityFunctionsTest(BaseTestCase):
    """Test core utility functions."""
    
    def test_vigtra_message_function(self):
        """Test vigtra_message utility function."""
        # Test success message
        success_msg = utils.vigtra_message(
            success=True,
            message="Operation completed",
            data={"result": "success"}
        )
        
        self.assertIsInstance(success_msg, dict)
        self.assertTrue(success_msg['success'])
        self.assertEqual(success_msg['message'], "Operation completed")
        self.assertEqual(success_msg['data'], {"result": "success"})
        
        # Test error message
        error_msg = utils.vigtra_message(
            success=False,
            message="Operation failed",
            error_details=["Validation error", "Database error"]
        )
        
        self.assertIsInstance(error_msg, dict)
        self.assertFalse(error_msg['success'])
        self.assertEqual(error_msg['message'], "Operation failed")
        self.assertEqual(error_msg['error_details'], ["Validation error", "Database error"])
    
    def test_vigtra_message_defaults(self):
        """Test vigtra_message with default values."""
        default_msg = utils.vigtra_message()
        
        self.assertIsInstance(default_msg, dict)
        self.assertIn('success', default_msg)
        self.assertIn('message', default_msg)
    
    def test_vigtra_message_with_metadata(self):
        """Test vigtra_message with metadata."""
        msg_with_metadata = utils.vigtra_message(
            success=True,
            message="Operation with metadata",
            metadata={
                "timestamp": datetime.now().isoformat(),
                "version": "1.0",
                "source": "test"
            }
        )
        
        self.assertTrue(msg_with_metadata['success'])
        self.assertIn('metadata', msg_with_metadata)
        self.assertEqual(msg_with_metadata['metadata']['version'], "1.0")


class DataValidationTest(TestCase):
    """Test data validation utilities."""
    
    def test_uuid_validation(self):
        """Test UUID validation patterns."""
        # Valid UUIDs
        valid_uuids = [
            str(uuid.uuid4()),
            "123e4567-e89b-12d3-a456-426614174000",
            "00000000-0000-0000-0000-000000000000"
        ]
        
        # Invalid UUIDs
        invalid_uuids = [
            "not-a-uuid",
            "123456789",
            "123e4567-e89b-12d3-a456",  # Too short
            "123e4567-e89b-12d3-a456-426614174000-extra"  # Too long
        ]
        
        for valid_uuid in valid_uuids:
            try:
                uuid.UUID(valid_uuid)
                is_valid = True
            except ValueError:
                is_valid = False
            self.assertTrue(is_valid, f"Should be valid UUID: {valid_uuid}")
        
        for invalid_uuid in invalid_uuids:
            try:
                uuid.UUID(invalid_uuid)
                is_valid = True
            except ValueError:
                is_valid = False
            self.assertFalse(is_valid, f"Should be invalid UUID: {invalid_uuid}")
    
    def test_date_validation(self):
        """Test date validation patterns."""
        # Test date parsing
        date_strings = [
            "2024-01-01",
            "2023-12-31",
            "2025-06-15"
        ]
        
        for date_string in date_strings:
            try:
                parsed_date = datetime.strptime(date_string, "%Y-%m-%d").date()
                self.assertIsInstance(parsed_date, date)
            except ValueError:
                self.fail(f"Should be able to parse date: {date_string}")
        
        # Test invalid dates
        invalid_dates = [
            "2024-13-01",  # Invalid month
            "2024-02-30",  # Invalid day for February
            "not-a-date"
        ]
        
        for invalid_date in invalid_dates:
            with self.assertRaises(ValueError):
                datetime.strptime(invalid_date, "%Y-%m-%d").date()
    
    def test_email_validation_pattern(self):
        """Test email validation patterns."""
        import re
        
        # Basic email pattern (simplified)
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "test123@test-domain.com",
            "user+tag@example.org"
        ]
        
        invalid_emails = [
            "invalid-email",
            "@domain.com",
            "test@",
            "test..test@domain.com",
            "test@domain",
            ""
        ]
        
        for email in valid_emails:
            self.assertTrue(re.match(email_pattern, email), 
                          f"Should match valid email: {email}")
        
        for email in invalid_emails:
            self.assertIsNone(re.match(email_pattern, email), 
                            f"Should not match invalid email: {email}")


class JSONUtilitiesTest(TestCase):
    """Test JSON handling utilities."""
    
    def test_json_serialization(self):
        """Test JSON serialization of common data types."""
        test_data = {
            "string": "test string",
            "integer": 42,
            "float": 3.14159,
            "boolean": True,
            "null": None,
            "array": [1, 2, 3, "four"],
            "nested_object": {
                "key": "value",
                "number": 123
            }
        }
        
        # Test serialization
        json_string = json.dumps(test_data)
        self.assertIsInstance(json_string, str)
        
        # Test deserialization
        deserialized = json.loads(json_string)
        self.assertEqual(deserialized, test_data)
    
    def test_json_with_dates(self):
        """Test JSON handling with date objects."""
        from datetime import datetime, date
        
        # Dates need special handling in JSON
        test_date = date(2024, 1, 1)
        test_datetime = datetime(2024, 1, 1, 12, 0, 0)
        
        # Convert to ISO format strings for JSON
        date_data = {
            "date": test_date.isoformat(),
            "datetime": test_datetime.isoformat()
        }
        
        json_string = json.dumps(date_data)
        deserialized = json.loads(json_string)
        
        self.assertEqual(deserialized["date"], "2024-01-01")
        self.assertEqual(deserialized["datetime"], "2024-01-01T12:00:00")
    
    def test_json_error_handling(self):
        """Test JSON error handling."""
        # Test invalid JSON
        invalid_json = '{"invalid": json}'
        
        with self.assertRaises(json.JSONDecodeError):
            json.loads(invalid_json)
        
        # Test circular reference handling
        circular_data = {}
        circular_data['self'] = circular_data
        
        with self.assertRaises(ValueError):
            json.dumps(circular_data)


class StringUtilitiesTest(TestCase):
    """Test string manipulation utilities."""
    
    def test_string_cleaning(self):
        """Test string cleaning operations."""
        test_strings = [
            ("  whitespace  ", "whitespace"),
            ("UPPERCASE", "uppercase"),
            ("MixedCase", "mixedcase"),
            ("special!@#characters", "special!@#characters")
        ]
        
        for original, expected_clean in test_strings:
            cleaned = original.strip().lower()
            if expected_clean.lower() == expected_clean:
                self.assertEqual(cleaned, expected_clean)
    
    def test_string_validation(self):
        """Test string validation patterns."""
        # Test empty string validation
        empty_strings = ["", "   ", "\t", "\n"]
        for empty in empty_strings:
            self.assertTrue(not empty.strip(), f"Should be considered empty: '{empty}'")
        
        # Test non-empty strings
        non_empty_strings = ["text", "  text  ", "123", "special@chars"]
        for non_empty in non_empty_strings:
            self.assertTrue(non_empty.strip(), f"Should not be considered empty: '{non_empty}'")
    
    def test_string_formatting(self):
        """Test string formatting patterns."""
        # Test template formatting
        template = "Hello {name}, you have {count} messages"
        formatted = template.format(name="John", count=5)
        expected = "Hello John, you have 5 messages"
        self.assertEqual(formatted, expected)
        
        # Test f-string equivalent
        name = "Jane"
        count = 3
        f_formatted = f"Hello {name}, you have {count} messages"
        f_expected = "Hello Jane, you have 3 messages"
        self.assertEqual(f_formatted, f_expected)


class CollectionUtilitiesTest(TestCase):
    """Test collection manipulation utilities."""
    
    def test_list_operations(self):
        """Test list manipulation operations."""
        test_list = [1, 2, 2, 3, 3, 3, 4]
        
        # Test unique elements
        unique_elements = list(set(test_list))
        self.assertEqual(len(unique_elements), 4)
        
        # Test filtering
        filtered = [x for x in test_list if x > 2]
        self.assertEqual(filtered, [3, 3, 3, 4])
        
        # Test sorting
        sorted_list = sorted(test_list, reverse=True)
        self.assertEqual(sorted_list[0], 4)
        self.assertEqual(sorted_list[-1], 1)
    
    def test_dictionary_operations(self):
        """Test dictionary manipulation operations."""
        test_dict = {
            "a": 1,
            "b": 2,
            "c": None,
            "d": "",
            "e": 0,
            "f": False,
            "g": []
        }
        
        # Test filtering None values
        no_none = {k: v for k, v in test_dict.items() if v is not None}
        self.assertNotIn("c", no_none)
        self.assertIn("d", no_none)  # Empty string is not None
        
        # Test filtering falsy values
        truthy_only = {k: v for k, v in test_dict.items() if v}
        expected_truthy = {"a": 1, "b": 2}
        self.assertEqual(truthy_only, expected_truthy)
        
        # Test key extraction
        keys = list(test_dict.keys())
        self.assertEqual(len(keys), 7)
        
        # Test value extraction
        values = list(test_dict.values())
        self.assertEqual(len(values), 7)
    
    def test_set_operations(self):
        """Test set operations."""
        set1 = {1, 2, 3, 4}
        set2 = {3, 4, 5, 6}
        
        # Test intersection
        intersection = set1 & set2
        self.assertEqual(intersection, {3, 4})
        
        # Test union
        union = set1 | set2
        self.assertEqual(union, {1, 2, 3, 4, 5, 6})
        
        # Test difference
        difference = set1 - set2
        self.assertEqual(difference, {1, 2})


class ErrorHandlingUtilitiesTest(TestCase):
    """Test error handling utilities."""
    
    def test_exception_handling_patterns(self):
        """Test common exception handling patterns."""
        # Test try-except with specific exceptions
        try:
            result = 10 / 0
        except ZeroDivisionError as e:
            self.assertIsInstance(e, ZeroDivisionError)
        else:
            self.fail("Should have raised ZeroDivisionError")
        
        # Test try-except with multiple exceptions
        def risky_operation(operation_type):
            if operation_type == "zero_division":
                return 10 / 0
            elif operation_type == "key_error":
                return {}["missing_key"]
            elif operation_type == "type_error":
                return "string" + 123
            else:
                return "success"
        
        # Test handling multiple exception types
        for op_type in ["zero_division", "key_error", "type_error"]:
            try:
                risky_operation(op_type)
            except (ZeroDivisionError, KeyError, TypeError) as e:
                self.assertIsInstance(e, (ZeroDivisionError, KeyError, TypeError))
            else:
                self.fail(f"Should have raised an exception for {op_type}")
        
        # Test successful operation
        result = risky_operation("success")
        self.assertEqual(result, "success")
    
    def test_error_message_formatting(self):
        """Test error message formatting."""
        try:
            raise ValueError("Test error message")
        except ValueError as e:
            error_msg = str(e)
            self.assertEqual(error_msg, "Test error message")
            
            # Test error with context
            contextual_error = f"Operation failed: {error_msg}"
            self.assertEqual(contextual_error, "Operation failed: Test error message")