"""
Base test classes and utilities for Vigtra Backend tests.
"""

from django.test import TestCase, TransactionTestCase, Client
from django.contrib.auth import get_user_model
from django.db import transaction
from faker import Faker
import json
from typing import Dict, Any, Optional
from modules.authentication.services.auth_service import AuthService
from modules.core.utils import vigtra_message

User = get_user_model()
fake = Faker()


class BaseTestCase(TestCase):
    """Base test case with common utilities."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.auth_service = AuthService()
        self.fake = fake
        
    def create_test_user(self, **kwargs) -> User:
        """Create a test user with default or provided data."""
        user_data = {
            'username': kwargs.get('username', self.fake.user_name()),
            'email': kwargs.get('email', self.fake.email()),
            'password': kwargs.get('password', 'testpass123'),
            'first_name': kwargs.get('first_name', self.fake.first_name()),
            'last_name': kwargs.get('last_name', self.fake.last_name()),
        }
        user_data.update(kwargs)
        
        response = self.auth_service.create(user_data)
        if response.get('success'):
            return User.objects.get(username=user_data['username'])
        else:
            raise Exception(f"Failed to create test user: {response}")
    
    def create_admin_user(self, **kwargs) -> User:
        """Create a test admin user."""
        kwargs.update({
            'is_staff': True,
            'is_superuser': True,
        })
        return self.create_test_user(**kwargs)
    
    def authenticate_user(self, user: User) -> None:
        """Authenticate a user for the test client."""
        self.client.force_login(user)
    
    def assertServiceResponse(self, response: Dict[str, Any], 
                            success: bool = True, 
                            message: Optional[str] = None,
                            data_keys: Optional[list] = None):
        """Assert service response format and content."""
        self.assertIsInstance(response, dict, "Service response should be a dictionary")
        self.assertIn('success', response, "Response should contain 'success' key")
        self.assertEqual(response['success'], success, 
                        f"Expected success={success}, got {response}")
        
        if message:
            self.assertIn('message', response, "Response should contain 'message' key")
            self.assertIn(message, response['message'])
        
        if data_keys and success:
            self.assertIn('data', response, "Successful response should contain 'data' key")
            for key in data_keys:
                self.assertIn(key, response['data'], 
                            f"Data should contain '{key}' key")
    
    def assertGraphQLResponse(self, response: Dict[str, Any], 
                            has_errors: bool = False,
                            data_keys: Optional[list] = None):
        """Assert GraphQL response format."""
        self.assertIsInstance(response, dict, "GraphQL response should be a dictionary")
        
        if has_errors:
            self.assertIn('errors', response, "Response should contain errors")
        else:
            self.assertNotIn('errors', response, 
                           f"Response should not contain errors: {response.get('errors')}")
            self.assertIn('data', response, "Response should contain data")
            
            if data_keys:
                for key in data_keys:
                    self.assertIn(key, response['data'], 
                                f"Data should contain '{key}' key")


class BaseModelTestCase(BaseTestCase):
    """Base test case for model testing."""
    
    def assertModelFieldsExist(self, model_class, expected_fields: list):
        """Assert that model has expected fields."""
        model_fields = [field.name for field in model_class._meta.fields]
        for field in expected_fields:
            self.assertIn(field, model_fields, 
                        f"Model {model_class.__name__} should have field '{field}'")
    
    def assertModelValidation(self, model_instance, should_be_valid: bool = True):
        """Assert model validation."""
        try:
            model_instance.full_clean()
            if not should_be_valid:
                self.fail(f"Model {model_instance} should not be valid")
        except Exception as e:
            if should_be_valid:
                self.fail(f"Model {model_instance} should be valid, got error: {e}")


class BaseServiceTestCase(BaseTestCase):
    """Base test case for service testing."""
    
    def setUp(self):
        super().setUp()
        self.test_user = self.create_test_user()


class BaseAPITestCase(BaseTestCase):
    """Base test case for API testing."""
    
    def setUp(self):
        super().setUp()
        self.test_user = self.create_test_user()
        self.admin_user = self.create_admin_user()
    
    def graphql_query(self, query: str, variables: Optional[Dict] = None, 
                     user: Optional[User] = None) -> Dict[str, Any]:
        """Execute GraphQL query."""
        if user:
            self.authenticate_user(user)
        
        response = self.client.post(
            '/graphql/',
            data={
                'query': query,
                'variables': json.dumps(variables or {})
            },
            content_type='application/json'
        )
        
        return json.loads(response.content)
    
    def graphql_mutation(self, mutation: str, variables: Optional[Dict] = None,
                        user: Optional[User] = None) -> Dict[str, Any]:
        """Execute GraphQL mutation."""
        return self.graphql_query(mutation, variables, user)


class BaseTransactionTestCase(TransactionTestCase):
    """Base test case for tests requiring transactions."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.auth_service = AuthService()
        self.fake = fake
    
    def create_test_user(self, **kwargs) -> User:
        """Create a test user with transaction support."""
        with transaction.atomic():
            user_data = {
                'username': kwargs.get('username', self.fake.user_name()),
                'email': kwargs.get('email', self.fake.email()),
                'password': kwargs.get('password', 'testpass123'),
            }
            user_data.update(kwargs)
            
            response = self.auth_service.create(user_data)
            if response.get('success'):
                return User.objects.get(username=user_data['username'])
            else:
                raise Exception(f"Failed to create test user: {response}")


class TestDataMixin:
    """Mixin providing test data generation methods."""
    
    @staticmethod
    def generate_insuree_data(**kwargs):
        """Generate test insuree data."""
        return {
            'chf_id': kwargs.get('chf_id', fake.unique.random_number(digits=8)),
            'last_name': kwargs.get('last_name', fake.last_name()),
            'other_names': kwargs.get('other_names', fake.first_name()),
            'dob': kwargs.get('dob', fake.date_of_birth(minimum_age=0, maximum_age=100)),
            'gender': kwargs.get('gender', fake.random_element(['M', 'F', 'O'])),
            'marital': kwargs.get('marital', fake.random_element(['S', 'M', 'D', 'W', 'N'])),
            'phone': kwargs.get('phone', fake.phone_number()),
            'email': kwargs.get('email', fake.email()),
            **kwargs
        }
    
    @staticmethod
    def generate_family_data(**kwargs):
        """Generate test family data."""
        return {
            'address': kwargs.get('address', fake.address()),
            'ethnicity': kwargs.get('ethnicity', fake.word()),
            'confirmation_no': kwargs.get('confirmation_no', fake.uuid4()),
            'confirmation_type': kwargs.get('confirmation_type', fake.random_element(['P', 'V'])),
            **kwargs
        }
    
    @staticmethod
    def generate_policy_data(**kwargs):
        """Generate test policy data."""
        return {
            'product_code': kwargs.get('product_code', fake.random_number(digits=6)),
            'enroll_date': kwargs.get('enroll_date', fake.date_this_year()),
            'start_date': kwargs.get('start_date', fake.date_this_year()),
            'effective_date': kwargs.get('effective_date', fake.date_this_year()),
            'status': kwargs.get('status', fake.random_element(['A', 'I', 'S', 'E'])),
            'value': kwargs.get('value', fake.random_number(digits=4)),
            **kwargs
        }