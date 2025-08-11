from django.test import TestCase
from modules.authentication.models.user import User
from modules.contribution_plan.services.contribution_plan import ContributionPlanService
from modules.contribution_plan.models.contribution_plan import (
    ContributionPlanType,
    ContributionCalculationType,
    ContributionFrequency,
    ContributionPlanStatus,
)
import random
from datetime import datetime, timedelta
# Create your tests here.


class ContributionPlanTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpassword",
        )
        self.contribution_plan_service = ContributionPlanService()

    def test_create_contribution_plan(self):
        for item in range(10):
            random_status = random.choice(
                [status.value for status in ContributionPlanStatus]
            )
            random_plan_type = random.choice(
                [plan_type.value for plan_type in ContributionPlanType]
            )
            random_calculation_type = random.choice(
                [
                    calculation_type.value
                    for calculation_type in ContributionCalculationType
                ]
            )
            random_contribution_frequency = random.choice(
                [
                    contribution_frequency.value
                    for contribution_frequency in ContributionFrequency
                ]
            )
            random_start_date = datetime.now()
            random_end_date = random_start_date + timedelta(days=random.randint(1, 365))
            prepared_data = {
                "auto_generate_code": True,
                "name": f"Test Contribution Plan {item}",
                "plan_type": random_plan_type,
                "calculation_type": random_calculation_type,
                "base_amount": random.randint(100, 1000),
                "contribution_frequency": random_contribution_frequency,
                "status": random_status,
            }
            contribution_tired_rates = []
            for item in range(random.randint(1, 5)):
                contribution_tired_rates.append(
                    {
                        "tier_name": f"Tier {item}",
                        "min_income": random.randint(100, 1000),
                        "max_income": random.randint(1000, 10000),
                        "contribution_amount": random.randint(100, 1000),
                    }
                )

            if random_status == ContributionPlanStatus.ACTIVE:
                prepared_data["validity_from"] = random_start_date
                prepared_data["validity_to"] = None
                prepared_data["contribution_tired_rates"] = contribution_tired_rates
            elif random_status == ContributionPlanStatus.INACTIVE:
                prepared_data["validity_to"] = random_end_date
                prepared_data["contribution_tired_rates"] = contribution_tired_rates
            elif random_status == ContributionPlanStatus.DRAFT:
                prepared_data["validity_from"] = None
                prepared_data["validity_to"] = None
            elif random_status == ContributionPlanStatus.SUSPENDED:
                prepared_data["validity_from"] = random_start_date
                prepared_data["validity_to"] = random_end_date
                prepared_data["contribution_tired_rates"] = contribution_tired_rates
            elif random_status == ContributionPlanStatus.EXPIRED:
                prepared_data["validity_to"] = random_end_date
                prepared_data["contribution_tired_rates"] = contribution_tired_rates
            elif random_status == ContributionPlanStatus.CANCELLED:
                prepared_data["validity_to"] = random_end_date
                prepared_data["contribution_tired_rates"] = contribution_tired_rates
            service_result = self.contribution_plan_service.create_contribution_plan(
                prepared_data,
                self.user,
            )

            self.assertEqual(service_result["success"], True)
            self.assertEqual(
                service_result["message"], "Contribution plan created successfully"
            )
            self.assertEqual(service_result["data"]["name"], prepared_data["name"])
            self.assertEqual(
                service_result["data"]["plan_type"], prepared_data["plan_type"]
            )
            self.assertEqual(
                service_result["data"]["calculation_type"],
                prepared_data["calculation_type"],
            )
            self.assertEqual(
                service_result["data"]["base_amount"], prepared_data["base_amount"]
            )
            self.assertEqual(
                service_result["data"]["contribution_frequency"],
                prepared_data["contribution_frequency"],
            )
            self.assertEqual(service_result["data"]["status"], prepared_data["status"])
