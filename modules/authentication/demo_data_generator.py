from modules.core.base_demo_generator import BaseDemoDataGenerator
from faker import Faker
from modules.authentication.models.user import User
import logging

logger = logging.getLogger(__name__)
fake = Faker()


class AuthenticationDemoDataGenerator(BaseDemoDataGenerator):
    def run_demo(self):
        self.generate_user()

    def load_user_demo_data(self) -> dict:
        USER_DATA = []
        for item in range(20):
            user_data = {
                "username": fake.user_name(),
                "email": fake.email(),
                "password": fake.password(),
            }
            USER_DATA.append(user_data)
        return USER_DATA

    def generate_user(self):
        for user_data in self.load_user_demo_data():
            User.objects.create(
                username=user_data["username"],
                email=user_data["email"],
                password=user_data["password"],
            )
            logger.info(f"User generated: {user_data['username']}")
