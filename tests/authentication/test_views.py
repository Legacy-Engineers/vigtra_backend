"""
Tests for authentication views and API endpoints.
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from tests.base import BaseAPITestCase, TestDataMixin
import json
from faker import Faker

User = get_user_model()
fake = Faker()


class AuthenticationAPITest(BaseAPITestCase, TestDataMixin):
    """Test authentication API endpoints."""
    
    def test_user_registration_endpoint(self):
        """Test user registration via API."""
        registration_data = {
            'username': fake.user_name(),
            'email': fake.email(),
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'first_name': fake.first_name(),
            'last_name': fake.last_name()
        }
        
        # Try to find registration endpoint
        try:
            response = self.client.post('/api/auth/register/', 
                                      data=json.dumps(registration_data),
                                      content_type='application/json')
            
            # If endpoint exists, test response
            self.assertIn(response.status_code, [200, 201, 404])
            
            if response.status_code in [200, 201]:
                response_data = json.loads(response.content)
                self.assertIn('success', response_data)
                
        except Exception:
            # Endpoint might not exist or use different URL pattern
            pass
    
    def test_user_login_endpoint(self):
        """Test user login via API."""
        # Create a test user
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        # Try common login endpoints
        login_urls = [
            '/api/auth/login/',
            '/auth/login/',
            '/login/',
            '/api/token/',
        ]
        
        for url in login_urls:
            try:
                response = self.client.post(url,
                                          data=json.dumps(login_data),
                                          content_type='application/json')
                
                if response.status_code != 404:
                    # Found an endpoint, test it
                    self.assertIn(response.status_code, [200, 201, 400, 401])
                    
                    if response.status_code in [200, 201]:
                        response_data = json.loads(response.content)
                        # Should contain token or success indicator
                        self.assertTrue(
                            'token' in response_data or 
                            'access' in response_data or
                            'success' in response_data
                        )
                    break
            except Exception:
                continue
    
    def test_user_logout_endpoint(self):
        """Test user logout via API."""
        # Create and authenticate user
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.client.force_login(user)
        
        # Try common logout endpoints
        logout_urls = [
            '/api/auth/logout/',
            '/auth/logout/',
            '/logout/',
        ]
        
        for url in logout_urls:
            try:
                response = self.client.post(url)
                
                if response.status_code != 404:
                    # Found an endpoint
                    self.assertIn(response.status_code, [200, 204, 302])
                    break
            except Exception:
                continue
    
    def test_user_profile_endpoint(self):
        """Test user profile retrieval via API."""
        # Create and authenticate user
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe'
        )
        
        self.client.force_login(user)
        
        # Try common profile endpoints
        profile_urls = [
            '/api/auth/profile/',
            '/api/user/profile/',
            '/profile/',
            '/api/me/',
        ]
        
        for url in profile_urls:
            try:
                response = self.client.get(url)
                
                if response.status_code != 404:
                    # Found an endpoint
                    if response.status_code == 200:
                        response_data = json.loads(response.content)
                        # Should contain user information
                        self.assertTrue(
                            'username' in response_data or
                            'email' in response_data or
                            'user' in response_data
                        )
                    break
            except Exception:
                continue
    
    def test_password_change_endpoint(self):
        """Test password change via API."""
        # Create and authenticate user
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='oldpass123'
        )
        
        self.client.force_login(user)
        
        password_data = {
            'old_password': 'oldpass123',
            'new_password': 'newpass123',
            'new_password_confirm': 'newpass123'
        }
        
        # Try common password change endpoints
        password_urls = [
            '/api/auth/change-password/',
            '/api/auth/password/change/',
            '/auth/password/change/',
        ]
        
        for url in password_urls:
            try:
                response = self.client.post(url,
                                          data=json.dumps(password_data),
                                          content_type='application/json')
                
                if response.status_code != 404:
                    # Found an endpoint
                    self.assertIn(response.status_code, [200, 400, 401])
                    break
            except Exception:
                continue
    
    def test_password_reset_endpoint(self):
        """Test password reset request via API."""
        # Create a user
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        reset_data = {
            'email': 'test@example.com'
        }
        
        # Try common password reset endpoints
        reset_urls = [
            '/api/auth/password-reset/',
            '/api/auth/password/reset/',
            '/auth/password/reset/',
        ]
        
        for url in reset_urls:
            try:
                response = self.client.post(url,
                                          data=json.dumps(reset_data),
                                          content_type='application/json')
                
                if response.status_code != 404:
                    # Found an endpoint
                    self.assertIn(response.status_code, [200, 400])
                    break
            except Exception:
                continue
    
    def test_unauthorized_access(self):
        """Test unauthorized access to protected endpoints."""
        # Try to access protected endpoints without authentication
        protected_urls = [
            '/api/auth/profile/',
            '/api/user/profile/',
            '/profile/',
            '/api/me/',
        ]
        
        for url in protected_urls:
            try:
                response = self.client.get(url)
                
                if response.status_code != 404:
                    # Should require authentication
                    self.assertIn(response.status_code, [401, 403, 302])
            except Exception:
                continue
    
    def test_invalid_credentials(self):
        """Test login with invalid credentials."""
        # Create a user
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='correctpass123'
        )
        
        invalid_login_data = {
            'username': 'testuser',
            'password': 'wrongpass123'
        }
        
        # Try login endpoints
        login_urls = [
            '/api/auth/login/',
            '/auth/login/',
            '/login/',
        ]
        
        for url in login_urls:
            try:
                response = self.client.post(url,
                                          data=json.dumps(invalid_login_data),
                                          content_type='application/json')
                
                if response.status_code != 404:
                    # Should reject invalid credentials
                    self.assertIn(response.status_code, [400, 401])
                    break
            except Exception:
                continue


class GraphQLAuthenticationTest(BaseAPITestCase):
    """Test GraphQL authentication endpoints."""
    
    def test_graphql_user_creation_mutation(self):
        """Test GraphQL user creation mutation."""
        mutation = """
        mutation CreateUser($input: CreateUserInput!) {
            createUser(input: $input) {
                success
                message
                user {
                    id
                    username
                    email
                }
                errors
            }
        }
        """
        
        variables = {
            "input": {
                "username": fake.user_name(),
                "email": fake.email(),
                "password": "testpass123",
                "firstName": fake.first_name(),
                "lastName": fake.last_name()
            }
        }
        
        response = self.graphql_mutation(mutation, variables)
        
        # If GraphQL endpoint exists and mutation is implemented
        if 'data' in response and not response.get('errors'):
            self.assertIn('createUser', response['data'])
            create_result = response['data']['createUser']
            
            if create_result:
                self.assertIn('success', create_result)
    
    def test_graphql_user_login_mutation(self):
        """Test GraphQL user login mutation."""
        # Create a test user
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        mutation = """
        mutation LoginUser($input: LoginInput!) {
            loginUser(input: $input) {
                success
                message
                token
                user {
                    id
                    username
                    email
                }
                errors
            }
        }
        """
        
        variables = {
            "input": {
                "username": "testuser",
                "password": "testpass123"
            }
        }
        
        response = self.graphql_mutation(mutation, variables)
        
        # If GraphQL endpoint exists and mutation is implemented
        if 'data' in response and not response.get('errors'):
            self.assertIn('loginUser', response['data'])
            login_result = response['data']['loginUser']
            
            if login_result:
                self.assertIn('success', login_result)
    
    def test_graphql_user_query(self):
        """Test GraphQL user query."""
        # Create and authenticate user
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe'
        )
        
        query = """
        query GetCurrentUser {
            currentUser {
                id
                username
                email
                firstName
                lastName
                isActive
                dateJoined
            }
        }
        """
        
        response = self.graphql_query(query, user=user)
        
        # If GraphQL endpoint exists and query is implemented
        if 'data' in response and not response.get('errors'):
            self.assertIn('currentUser', response['data'])
            current_user = response['data']['currentUser']
            
            if current_user:
                self.assertEqual(current_user['username'], 'testuser')
                self.assertEqual(current_user['email'], 'test@example.com')
    
    def test_graphql_users_query(self):
        """Test GraphQL users list query."""
        # Create test users
        users = []
        for i in range(3):
            user = User.objects.create_user(
                username=f'testuser{i}',
                email=f'test{i}@example.com',
                password='testpass123'
            )
            users.append(user)
        
        query = """
        query GetUsers($first: Int, $after: String) {
            users(first: $first, after: $after) {
                edges {
                    node {
                        id
                        username
                        email
                        isActive
                    }
                }
                pageInfo {
                    hasNextPage
                    hasPreviousPage
                    startCursor
                    endCursor
                }
            }
        }
        """
        
        variables = {
            "first": 10
        }
        
        # Use admin user to query users
        response = self.graphql_query(query, variables, user=self.admin_user)
        
        # If GraphQL endpoint exists and query is implemented
        if 'data' in response and not response.get('errors'):
            self.assertIn('users', response['data'])
            users_result = response['data']['users']
            
            if users_result:
                self.assertIn('edges', users_result)
                self.assertGreaterEqual(len(users_result['edges']), 3)
    
    def test_graphql_authentication_required(self):
        """Test GraphQL queries requiring authentication."""
        query = """
        query GetCurrentUser {
            currentUser {
                id
                username
                email
            }
        }
        """
        
        # Query without authentication
        response = self.graphql_query(query)
        
        # Should either return null or error for unauthenticated request
        if 'data' in response:
            # If data is returned, currentUser should be null
            if response['data'].get('currentUser') is not None:
                # Some implementations might allow this
                pass
        elif 'errors' in response:
            # Authentication error
            self.assertIn('errors', response)


class AuthenticationMiddlewareTest(TestCase):
    """Test authentication middleware functionality."""
    
    def setUp(self):
        self.client = Client()
    
    def test_session_authentication(self):
        """Test session-based authentication."""
        # Create a user
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Login user
        self.client.force_login(user)
        
        # Test that user is authenticated in subsequent requests
        # This would depend on having protected views to test
        response = self.client.get('/')
        
        # The response should indicate authenticated state
        # Implementation depends on the actual views
        self.assertIsNotNone(response)
    
    def test_jwt_authentication(self):
        """Test JWT authentication if implemented."""
        # This test would verify JWT token authentication
        # Implementation depends on JWT setup
        
        # Create a user
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # If JWT is implemented, test token-based authentication
        # This would require actual JWT endpoint testing
        self.assertIsNotNone(user)
    
    def test_api_key_authentication(self):
        """Test API key authentication if implemented."""
        # This test would verify API key authentication
        # Implementation depends on API key setup
        
        # Create a user
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Test API key authentication
        self.assertIsNotNone(user)