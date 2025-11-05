from modules.core.base_demo_generator import BaseDemoDataGenerator
from faker import Faker
from modules.location.models import Location, LocationType
from modules.insuree.models.insuree_model_dependency import Gender
from modules.insuree.models.family import (
    FamilyMembership,
    Family,
    FamilyType,
    FamilyMembershipStatus,
    Relation,
)
from modules.insuree.services.insuree import InsureeService
import logging
from django.db import transaction
from django.utils import timezone
from modules.authentication.models.user import User
from datetime import datetime
from .models import Insuree

logger = logging.getLogger(__name__)

fake = Faker()

INSUREE_DATA = []

GENDER_DATA = [
    {
        "code": "M",
        "gender": "Male",
    },
    {
        "code": "F",
        "gender": "Female",
    },
]

FAMILY_TYPE = [
    {
        "code": "GP-001",
        "type": "Family",
    },
    {
        "code": "GP-002",
        "type": "Community",
    },
]

RELATIONSHIPS = [
    {
        "code": "RL-001",
        "relation": "Spouse",
        "is_active": True,
    },
    {
        "code": "RL-002",
        "relation": "Mother",
        "is_active": True,
    },
    {
        "code": "RL-003",
        "relation": "Father",
        "is_active": True,
    },
    {
        "code": "RL-004",
        "relation": "Daughter",
        "is_active": True,
    },
    {
        "code": "RL-005",
        "relation": "Son",
        "is_active": True,
    },
    {
        "code": "RL-006",
        "relation": "Grand Mother",
        "is_active": True,
    },
    {
        "code": "RL-007",
        "relation": "Grand Father",
        "is_active": True,
    },
]


class InsureeDemoDataGenerator(BaseDemoDataGenerator):
    def run_demo(self):
        self.generate_gender()
        self.generate_insuree()
        self.generate_families()

    def generate_families(self):
        self.generate_relation()
        self._generate_family_type()
        self._generate_families()

    # @transaction.atomic
    def _generate_families(self):
        insurees = self.get_random_insurees()
        print("Insurees: ", insurees)

        for insuree in insurees[0:10]:
            fam_membership = FamilyMembership.objects.filter(insuree=insuree)

            if not fam_membership.exists():
                family = Family.objects.create(
                    head_insuree=insuree,
                    location=self.get_random_location(),
                    family_type=FamilyType.objects.filter(code="GP-001").first(),
                    validity_from=timezone.now(),  # ✅ Fix #2
                )

                logger.info(f"Created Family: {family}")  # ✅ Fix #1

                logger.info("Created Family: ", family)

                FamilyMembership.objects.create(
                    family=family,
                    insuree=insuree,
                    is_head=True,
                )

        for insuree in insurees[10:40]:
            if not FamilyMembership.objects.filter(insuree=insuree).exists():
                random_family = Family.objects.all().order_by("?")[1]

                FamilyMembership.objects.create(family=random_family, insuree=insuree)

    def get_random_insurees(self):
        insurees = Insuree.objects.all().order_by("?")
        return insurees

    @transaction.atomic
    def generate_relation(self):
        for item in RELATIONSHIPS:
            if not Relation.objects.filter(code=item["code"]).exists():
                Relation.objects.create(
                    code=item["code"], relation=item["relation"], is_active=True
                )

    @transaction.atomic
    def _generate_family_type(self):
        for item in FAMILY_TYPE:
            if not FamilyType.objects.filter(code=item["code"]).exists():
                FamilyType.objects.create(code=item["code"], type=item["type"])

    @transaction.atomic
    def generate_gender(self):
        for gender_data in GENDER_DATA:
            # Check if gender already exists to avoid UNIQUE constraint violation
            if not Gender.objects.filter(code=gender_data["code"]).exists():
                Gender.objects.create(
                    code=gender_data["code"],
                    gender=gender_data["gender"],
                )
                logger.info(f"Gender generated: {gender_data['gender']}")
            else:
                logger.info(
                    f"Gender {gender_data['gender']} already exists, skipping..."
                )

    @transaction.atomic
    def generate_insuree(self):
        self.load_insuree_demo_data()
        for insuree_data in INSUREE_DATA:
            service_response = InsureeService().create_insuree(
                insuree_data, user=self.get_random_user()
            )
            logger.info(f"Insuree generated: {service_response}")

    def get_random_user(self) -> User:
        return User.objects.order_by("?").first()

    def load_insuree_demo_data(self) -> dict:
        # Check if we have locations available
        if not Location.objects.exists():
            logger.error(
                "No locations found in database. Please run location demo data generation first."
            )
            return []

        for item in range(50):
            random_location = self.get_random_location()
            if not random_location:
                logger.error(
                    "Failed to get random location. Skipping insuree generation."
                )
                return []

            insuree_data = {
                "auto_generate_chf_id": True,
                "other_names": fake.first_name(),
                "last_name": fake.last_name(),
                "dob": timezone.make_aware(
                    datetime.combine(fake.date_of_birth(), datetime.min.time())
                ),
                "gender_code": fake.random_element(elements=("M", "F")),
                "location_id": random_location.id,
            }
            INSUREE_DATA.append(insuree_data)
        return INSUREE_DATA

    def get_random_location(self) -> Location:
        """Only 3 locations based on the location type generated by the location demo data."""
        location_type_names = ["State", "District", "City"]
        location_type = (
            LocationType.objects.filter(name__in=location_type_names)
            .order_by("?")
            .first()
        )

        if not location_type:
            logger.warning(
                "No location types found. Please run location demo data generation first."
            )
            return None

        location = Location.objects.filter(type=location_type).order_by("?").first()

        if not location:
            logger.warning(
                f"No locations found for type {location_type.name}. Please run location demo data generation first."
            )
            return None

        return location
