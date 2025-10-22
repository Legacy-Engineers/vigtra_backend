from django.test import TestCase, Client
from django.test.testcases import logger
from modules.authentication.models import User
from modules.insuree.services.insuree import InsureeService
from modules.insuree.models.insuree_model_dependency import Gender
from modules.location.models import Location, LocationType
from faker import Faker

fake = Faker()

INSUREE_SERVICE = InsureeService()

insuree_data = {
    "auto_generate_chf_id": True,
    "other_names": fake.first_name(),  # Changed from other_names to first_name
    "last_name": fake.last_name(),
    "dob": fake.date_of_birth(),
    "gender_code": "M",
}


# Create your tests here.
class InsureeTestCase(TestCase):
    def setUp(self):
        """Set up test data before each test method."""
        self.client = Client()
        self.user = User.objects.create(
            username=fake.user_name(),
            email=fake.email(),
        )
        Gender.objects.create(code="M", gender="Male")
        Gender.objects.create(code="F", gender="Female")
        location_type = LocationType.objects.create(
            name="Country",
            level=1,
        )
        location = Location.objects.create(
            name=fake.city(),
            code=fake.city_prefix(),
            type=location_type,
            parent=None,
        )
        self.location_id = location.id

    def test_create_insuree_with_service(self):
        """Test creating an insuree using the service layer."""
        insuree_data["location_id"] = self.location_id
        service_response = INSUREE_SERVICE.create_insuree(insuree_data, user=self.user)

        # Ensure we got a response
        self.assertIsNotNone(service_response, "Service returned None")

        # Ensure 'success' key exists
        self.assertIn("success", service_response, "'success' key missing in response")

        # Ensure 'success' is True
        self.assertTrue(
            service_response["success"], f"Service failed: {service_response}"
        )
