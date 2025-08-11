from modules.core.base_demo_generator import BaseDemoDataGenerator
from faker import Faker
import logging

logger = logging.getLogger(__name__)

fake = Faker()


CONTRIBUTION_PLAN_DATA = []


class ContributionPlanDemoDataGenerator(BaseDemoDataGenerator):
    def run_demo(self):
        self.generate_contribution_plan()

    def generate_contribution_plan(self):
        pass

    def load_contribution_plan_demo_data(self):
        for item in range(20):
            prepared_data = {}
