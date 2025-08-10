from django.test import TestCase, Client
from modules.authentication.services.auth_service import AuthService
from faker import Faker

AUTH_SERVICE = AuthService()

fake = Faker()

user_data = {
    "username": fake.user_name(),
    "email": fake.email(),
    "password": fake.password(),
}


class UserTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_create_user(self):
        service_response = AUTH_SERVICE.create(user_data)

        # Ensure we got a response
        self.assertIsNotNone(service_response, "Service returned None")

        # Ensure 'success' key exists
        self.assertIn("success", service_response, "'success' key missing in response")

        # Ensure 'success' is True
        self.assertTrue(
            service_response["success"], f"Service failed: {service_response}"
        )
