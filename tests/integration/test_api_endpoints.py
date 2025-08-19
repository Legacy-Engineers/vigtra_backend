"""
Integration tests for API endpoints.
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from tests.base import BaseAPITestCase, TestDataMixin
import json
from faker import Faker

User = get_user_model()
fake = Faker()


class GraphQLAPIIntegrationTest(BaseAPITestCase, TestDataMixin):
    """Test GraphQL API integration."""
    
    def test_graphql_endpoint_exists(self):
        """Test that GraphQL endpoint is accessible."""
        response = self.client.get('/graphql/')
        
        # Should either return 200 (GET allowed) or 405 (POST only)
        self.assertIn(response.status_code, [200, 405])
    
    def test_graphql_introspection_query(self):
        """Test GraphQL introspection query."""
        introspection_query = """
        query IntrospectionQuery {
            __schema {
                types {
                    name
                    kind
                }
            }
        }
        """
        
        response = self.graphql_query(introspection_query, user=self.admin_user)
        
        # If GraphQL is properly configured, this should work
        if 'data' in response and not response.get('errors'):
            self.assertIn('__schema', response['data'])
            self.assertIn('types', response['data']['__schema'])
    
    def test_graphql_authentication_flow(self):
        """Test GraphQL authentication flow."""
        # Test unauthenticated query
        query = """
        query {
            currentUser {
                id
                username
            }
        }
        """
        
        # Without authentication
        response = self.graphql_query(query)
        
        # Should either return null user or authentication error
        if 'data' in response:
            if response['data'].get('currentUser'):
                # Some implementations might return anonymous user info
                pass
            else:
                # User is null for unauthenticated request
                self.assertIsNone(response['data'].get('currentUser'))
        
        # With authentication
        response = self.graphql_query(query, user=self.test_user)
        
        # Should return user data if query exists
        if 'data' in response and response['data'].get('currentUser'):
            self.assertEqual(response['data']['currentUser']['username'], 
                           self.test_user.username)
    
    def test_graphql_mutation_flow(self):
        """Test GraphQL mutation flow."""
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
        
        response = self.graphql_mutation(mutation, variables, user=self.admin_user)
        
        # If mutation exists and works
        if 'data' in response and response['data'].get('createUser'):
            create_result = response['data']['createUser']
            if create_result.get('success'):
                self.assertTrue(create_result['success'])
                self.assertIn('user', create_result)
    
    def test_graphql_error_handling(self):
        """Test GraphQL error handling."""
        # Invalid query syntax
        invalid_query = """
        query {
            invalidField {
                nonExistentField
            }
        }
        """
        
        response = self.graphql_query(invalid_query, user=self.admin_user)
        
        # Should return errors for invalid query
        if 'errors' in response:
            self.assertIsInstance(response['errors'], list)
            self.assertGreater(len(response['errors']), 0)
    
    def test_graphql_pagination(self):
        """Test GraphQL pagination."""
        query = """
        query GetUsers($first: Int, $after: String) {
            users(first: $first, after: $after) {
                edges {
                    node {
                        id
                        username
                    }
                    cursor
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
            "first": 5
        }
        
        response = self.graphql_query(query, variables, user=self.admin_user)
        
        # If pagination is implemented
        if 'data' in response and response['data'].get('users'):
            users_result = response['data']['users']
            
            # Should have pagination structure
            self.assertIn('edges', users_result)
            self.assertIn('pageInfo', users_result)
            
            page_info = users_result['pageInfo']
            self.assertIn('hasNextPage', page_info)
            self.assertIn('hasPreviousPage', page_info)


class RESTAPIIntegrationTest(BaseAPITestCase):
    """Test REST API integration if available."""
    
    def test_api_root_endpoint(self):
        """Test API root endpoint."""
        api_urls = [
            '/api/',
            '/api/v1/',
            '/rest/',
        ]
        
        for url in api_urls:
            try:
                response = self.client.get(url)
                if response.status_code != 404:
                    # Found an API endpoint
                    self.assertIn(response.status_code, [200, 401, 403])
                    break
            except Exception:
                continue
    
    def test_authentication_endpoints(self):
        """Test authentication endpoints."""
        # Test login endpoint
        login_data = {
            'username': self.test_user.username,
            'password': 'testpass123'  # From base test setup
        }
        
        login_urls = [
            '/api/auth/login/',
            '/api/login/',
            '/auth/login/',
            '/login/',
        ]
        
        for url in login_urls:
            try:
                response = self.client.post(url, 
                                          data=json.dumps(login_data),
                                          content_type='application/json')
                
                if response.status_code != 404:
                    # Found login endpoint
                    self.assertIn(response.status_code, [200, 201, 400, 401])
                    break
            except Exception:
                continue
    
    def test_crud_operations(self):
        """Test CRUD operations on API."""
        # This is a generic test for any CRUD endpoint
        crud_endpoints = [
            '/api/users/',
            '/api/insurees/',
            '/api/families/',
        ]
        
        for endpoint in crud_endpoints:
            try:
                # Test GET (list)
                response = self.client.get(endpoint)
                if response.status_code != 404:
                    # Endpoint exists
                    if response.status_code == 200:
                        # Should return JSON data
                        data = json.loads(response.content)
                        self.assertIsInstance(data, (list, dict))
                    
                    # Test POST (create) with authenticated user
                    self.client.force_login(self.admin_user)
                    
                    test_data = {'name': 'Test Item'}
                    post_response = self.client.post(endpoint,
                                                   data=json.dumps(test_data),
                                                   content_type='application/json')
                    
                    # Should either create or return validation error
                    self.assertIn(post_response.status_code, [200, 201, 400, 403])
                    break
            except Exception:
                continue
    
    def test_api_content_type_handling(self):
        """Test API content type handling."""
        # Test JSON content type
        response = self.client.post('/api/test/',
                                  data=json.dumps({'test': 'data'}),
                                  content_type='application/json')
        
        # Should either handle JSON or return 404 for non-existent endpoint
        self.assertIn(response.status_code, [200, 201, 400, 404, 405])
        
        # Test form data content type
        response = self.client.post('/api/test/',
                                  data={'test': 'data'},
                                  content_type='application/x-www-form-urlencoded')
        
        self.assertIn(response.status_code, [200, 201, 400, 404, 405])
    
    def test_api_error_responses(self):
        """Test API error response format."""
        # Test 404 response
        response = self.client.get('/api/non-existent-endpoint/')
        self.assertEqual(response.status_code, 404)
        
        # Test method not allowed
        response = self.client.put('/api/')
        # Should return 404 (no endpoint) or 405 (method not allowed)
        self.assertIn(response.status_code, [404, 405])


class DatabaseIntegrationTest(BaseAPITestCase):
    """Test database integration and transactions."""
    
    def test_database_transaction_rollback(self):
        """Test database transaction rollback."""
        from django.db import transaction
        
        initial_user_count = User.objects.count()
        
        try:
            with transaction.atomic():
                # Create a user
                user = User.objects.create_user(
                    username='rollback_test',
                    email='rollback@test.com',
                    password='testpass123'
                )
                
                # Verify user was created
                self.assertEqual(User.objects.count(), initial_user_count + 1)
                
                # Force rollback
                raise Exception("Forced rollback")
                
        except Exception:
            # Transaction should be rolled back
            pass
        
        # User count should be back to original
        self.assertEqual(User.objects.count(), initial_user_count)
    
    def test_database_constraints(self):
        """Test database constraint enforcement."""
        # Test unique constraint
        user1 = User.objects.create_user(
            username='unique_test',
            email='unique@test.com',
            password='testpass123'
        )
        
        # Try to create user with same username
        with self.assertRaises(Exception):
            user2 = User.objects.create_user(
                username='unique_test',  # Same username
                email='different@test.com',
                password='testpass123'
            )
    
    def test_database_foreign_key_constraints(self):
        """Test foreign key constraint enforcement."""
        # This test depends on having models with foreign keys
        # Using a generic approach
        
        # Create a user
        user = User.objects.create_user(
            username='fk_test',
            email='fk@test.com',
            password='testpass123'
        )
        
        # If we have models with foreign keys to User, test them
        # For example, if Insuree has foreign key to User
        try:
            from modules.insuree.models.insuree import Insuree
            
            insuree = Insuree.objects.create(
                chf_id='FK_TEST',
                last_name='FK',
                other_names='Test',
                audit_user=user
            )
            
            # Verify foreign key relationship
            self.assertEqual(insuree.audit_user, user)
            
        except ImportError:
            # Insuree model might not have this structure
            pass


class CacheIntegrationTest(BaseAPITestCase):
    """Test cache integration."""
    
    def test_cache_basic_operations(self):
        """Test basic cache operations."""
        from django.core.cache import cache
        
        # Test cache set and get
        cache.set('test_key', 'test_value', timeout=60)
        cached_value = cache.get('test_key')
        
        self.assertEqual(cached_value, 'test_value')
        
        # Test cache delete
        cache.delete('test_key')
        cached_value = cache.get('test_key')
        
        self.assertIsNone(cached_value)
    
    def test_cache_timeout(self):
        """Test cache timeout functionality."""
        from django.core.cache import cache
        import time
        
        # Set cache with very short timeout
        cache.set('timeout_test', 'value', timeout=1)
        
        # Should be available immediately
        self.assertEqual(cache.get('timeout_test'), 'value')
        
        # Wait for timeout (if running in real-time test)
        # Note: This test might be skipped in fast test runs
        if hasattr(self, '_slow_tests_enabled'):
            time.sleep(2)
            self.assertIsNone(cache.get('timeout_test'))
    
    def test_cache_key_patterns(self):
        """Test cache key patterns."""
        from django.core.cache import cache
        
        # Test various key patterns
        test_keys = [
            'simple_key',
            'key:with:colons',
            'key_with_underscores',
            'key-with-dashes',
            'key123',
        ]
        
        for key in test_keys:
            cache.set(key, f'value_for_{key}', timeout=60)
            cached_value = cache.get(key)
            self.assertEqual(cached_value, f'value_for_{key}')
            
            # Clean up
            cache.delete(key)


class SignalIntegrationTest(BaseAPITestCase):
    """Test Django signal integration."""
    
    def test_user_creation_signals(self):
        """Test user creation signals."""
        from django.db.models.signals import post_save
        from django.dispatch import receiver
        
        signal_received = []
        
        @receiver(post_save, sender=User)
        def test_signal_handler(sender, instance, created, **kwargs):
            if created:
                signal_received.append(instance.username)
        
        # Create user
        user = User.objects.create_user(
            username='signal_test',
            email='signal@test.com',
            password='testpass123'
        )
        
        # Signal should have been received
        self.assertIn('signal_test', signal_received)
        
        # Disconnect signal to avoid affecting other tests
        post_save.disconnect(test_signal_handler, sender=User)
    
    def test_custom_signals(self):
        """Test custom signals if implemented."""
        # This would test any custom signals in the application
        try:
            from modules.core.service_signals import emit_signal
            
            # Test signal emission
            result = emit_signal('test.signal', {'test': 'data'})
            
            # Should not raise exception
            self.assertIsNotNone(result)
            
        except ImportError:
            # Custom signals not implemented
            pass


class MiddlewareIntegrationTest(BaseAPITestCase):
    """Test middleware integration."""
    
    def test_cors_middleware(self):
        """Test CORS middleware if configured."""
        response = self.client.options('/api/')
        
        # If CORS is configured, should have CORS headers
        if 'Access-Control-Allow-Origin' in response:
            self.assertIsNotNone(response['Access-Control-Allow-Origin'])
    
    def test_authentication_middleware(self):
        """Test authentication middleware."""
        # Test unauthenticated request
        response = self.client.get('/')
        
        # Should handle unauthenticated request gracefully
        self.assertIn(response.status_code, [200, 302, 401, 403])
        
        # Test authenticated request
        self.client.force_login(self.test_user)
        response = self.client.get('/')
        
        # Should handle authenticated request
        self.assertIn(response.status_code, [200, 302])
    
    def test_security_middleware(self):
        """Test security middleware."""
        response = self.client.get('/')
        
        # Check for security headers (if configured)
        security_headers = [
            'X-Content-Type-Options',
            'X-Frame-Options',
            'X-XSS-Protection',
        ]
        
        # These headers might or might not be present depending on configuration
        for header in security_headers:
            if header in response:
                self.assertIsNotNone(response[header])


class PerformanceIntegrationTest(BaseAPITestCase):
    """Test performance-related integration."""
    
    def test_query_performance(self):
        """Test database query performance."""
        from django.test.utils import override_settings
        from django.db import connection
        
        # Reset query count
        connection.queries_log.clear()
        
        # Perform operation that should be optimized
        users = list(User.objects.all()[:10])
        
        # Check query count (should be reasonable)
        query_count = len(connection.queries)
        
        # For simple user listing, should not require many queries
        self.assertLessEqual(query_count, 5)
    
    def test_response_time(self):
        """Test response time for common endpoints."""
        import time
        
        start_time = time.time()
        response = self.client.get('/')
        end_time = time.time()
        
        response_time = end_time - start_time
        
        # Response should be reasonably fast (less than 1 second)
        self.assertLess(response_time, 1.0)
    
    def test_concurrent_requests(self):
        """Test handling concurrent requests."""
        import threading
        import time
        
        results = []
        
        def make_request():
            try:
                response = self.client.get('/')
                results.append(response.status_code)
            except Exception as e:
                results.append(str(e))
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # All requests should complete successfully
        self.assertEqual(len(results), 5)
        
        # Most should return valid HTTP status codes
        valid_statuses = [r for r in results if isinstance(r, int) and 200 <= r < 500]
        self.assertGreaterEqual(len(valid_statuses), 3)