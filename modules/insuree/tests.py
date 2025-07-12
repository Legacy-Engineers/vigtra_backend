from django.test import TestCase, Client
from .models import Insuree
from modules.authentication.models import User
from faker import Faker

fake = Faker()

insuree_data = {""}


# Create your tests here.
class InsureeTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(
            username=fake.user_name(),
            email=fake.email(),
        )

        self, insuree = Insuree.objects.create(**insuree_data)

    def test_update_insuree(self):
        insuree = self.insuree
        insuree.last_name = fake.last_name()
        insuree.save()
