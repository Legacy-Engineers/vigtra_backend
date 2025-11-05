from modules.core.base_demo_generator import BaseDemoDataGenerator
from faker import Faker
import logging

logger = logging.getLogger(__name__)

fake = Faker()


class FormalSectorDemoDataGenerator(BaseDemoDataGenerator):

    def run_demo(self):
        print("Passing..")

    def load_demo_data(self):
        pass