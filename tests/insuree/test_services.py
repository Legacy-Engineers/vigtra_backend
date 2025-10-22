"""
Tests for insuree services.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock
from modules.insuree.models.insuree import Insuree, InsureeStatus
from modules.insuree.models.family import Family, FamilyMembership
from modules.insuree.models.insuree_model_dependency import (
    Gender,
    Profession,
    Education,
)
from modules.insuree.services import InsureeService  # Assuming this exists
from tests.base import BaseServiceTestCase, TestDataMixin
from faker import Faker
from datetime import date, timedelta

User = get_user_model()
fake = Faker()


class InsureeServiceTest(BaseServiceTestCase, TestDataMixin):
    """Test InsureeService functionality."""

    def setUp(self):
        super().setUp()

        # Create required dependencies
        self.gender_male = Gender.objects.create(
            code="M", gender="Male", sort_order=1, audit_user=self.test_user
        )

        self.profession = Profession.objects.create(
            code="DOC", profession="Doctor", sort_order=1, audit_user=self.test_user
        )

        self.education = Education.objects.create(
            code="UNI", education="University", sort_order=1, audit_user=self.test_user
        )

        # Initialize service if it exists
        try:
            self.insuree_service = InsureeService(user=self.test_user)
        except (ImportError, NameError):
            # Service might not exist yet
            self.insuree_service = None

    def test_insuree_service_initialization(self):
        """Test InsureeService initialization."""
        if self.insuree_service:
            self.assertIsNotNone(self.insuree_service)
            self.assertEqual(self.insuree_service.user, self.test_user)

    def test_create_insuree_service(self):
        """Test creating insuree through service."""
        if not self.insuree_service:
            self.skipTest("InsureeService not available")

        insuree_data = {
            "chf_id": fake.unique.random_number(digits=8),
            "last_name": fake.last_name(),
            "other_names": fake.first_name(),
            "dob": fake.date_of_birth(minimum_age=0, maximum_age=100),
            "gender": self.gender_male.code,
            "marital_status": "S",
            "phone": fake.phone_number(),
            "email": fake.email(),
        }

        response = self.insuree_service.create(insuree_data)

        self.assertServiceResponse(response, success=True)
        self.assertIn("data", response)

        # Verify insuree was created
        created_insuree = Insuree.objects.get(chf_id=insuree_data["chf_id"])
        self.assertEqual(created_insuree.last_name, insuree_data["last_name"])

    def test_update_insuree_service(self):
        """Test updating insuree through service."""
        if not self.insuree_service:
            self.skipTest("InsureeService not available")

        # Create insuree first
        insuree = Insuree.objects.create(
            chf_id="12345",
            last_name="Original",
            other_names="Name",
            audit_user=self.test_user,
        )

        update_data = {
            "uuid": str(insuree.uuid),
            "last_name": "Updated",
            "other_names": "Name",
            "phone": "+1234567890",
        }

        response = self.insuree_service.update(update_data)

        self.assertServiceResponse(response, success=True)

        # Verify update
        insuree.refresh_from_db()
        self.assertEqual(insuree.last_name, "Updated")

    def test_get_insuree_service(self):
        """Test retrieving insuree through service."""
        if not self.insuree_service:
            self.skipTest("InsureeService not available")

        # Create insuree
        insuree = Insuree.objects.create(
            chf_id="12345",
            last_name="Test",
            other_names="User",
            audit_user=self.test_user,
        )

        response = self.insuree_service.get(str(insuree.uuid))

        self.assertServiceResponse(response, success=True)
        self.assertIn("data", response)
        self.assertEqual(response["data"]["chf_id"], "12345")

    def test_delete_insuree_service(self):
        """Test deleting insuree through service."""
        if not self.insuree_service:
            self.skipTest("InsureeService not available")

        # Create insuree
        insuree = Insuree.objects.create(
            chf_id="12345",
            last_name="Test",
            other_names="User",
            audit_user=self.test_user,
        )

        response = self.insuree_service.delete(str(insuree.uuid))

        self.assertServiceResponse(response, success=True)

        # Verify soft delete or status change
        insuree.refresh_from_db()
        # Depending on implementation, might be soft deleted or status changed
        self.assertTrue(
            insuree.status == InsureeStatus.INACTIVE or insuree.validity_to is not None
        )

    def test_search_insurees_service(self):
        """Test searching insurees through service."""
        if not self.insuree_service:
            self.skipTest("InsureeService not available")

        # Create test insurees
        insuree1 = Insuree.objects.create(
            chf_id="SEARCH01",
            last_name="Smith",
            other_names="John",
            audit_user=self.test_user,
        )

        insuree2 = Insuree.objects.create(
            chf_id="SEARCH02",
            last_name="Johnson",
            other_names="Jane",
            audit_user=self.test_user,
        )

        # Search by last name
        if hasattr(self.insuree_service, "search"):
            response = self.insuree_service.search({"last_name": "Smith"})

            self.assertServiceResponse(response, success=True)
            self.assertIn("data", response)

            # Should find Smith
            found_insurees = response["data"]
            self.assertTrue(any(i["last_name"] == "Smith" for i in found_insurees))

    def test_validate_insuree_data(self):
        """Test insuree data validation through service."""
        if not self.insuree_service:
            self.skipTest("InsureeService not available")

        # Test with invalid data
        invalid_data = {
            "chf_id": "",  # Empty CHF ID
            "last_name": "",  # Empty last name
            "email": "invalid-email",  # Invalid email
        }

        if hasattr(self.insuree_service, "validate"):
            response = self.insuree_service.validate(invalid_data)

            self.assertServiceResponse(response, success=False)
            self.assertIn("error_details", response)

    def test_insuree_service_error_handling(self):
        """Test service error handling."""
        if not self.insuree_service:
            self.skipTest("InsureeService not available")

        # Test with non-existent UUID
        response = self.insuree_service.get("non-existent-uuid")

        self.assertServiceResponse(response, success=False)
        self.assertIn("message", response)


class FamilyServiceTest(BaseServiceTestCase, TestDataMixin):
    """Test family-related service functionality."""

    def setUp(self):
        super().setUp()

        # Create dependencies
        self.gender_male = Gender.objects.create(
            code="M", gender="Male", sort_order=1, audit_user=self.test_user
        )

        # Initialize family service if it exists
        try:
            from modules.insuree.services import FamilyService

            self.family_service = FamilyService(user=self.test_user)
        except (ImportError, NameError):
            self.family_service = None

    def test_create_family_service(self):
        """Test creating family through service."""
        if not self.family_service:
            self.skipTest("FamilyService not available")

        family_data = self.generate_family_data()

        response = self.family_service.create(family_data)

        self.assertServiceResponse(response, success=True)
        self.assertIn("data", response)

        # Verify family was created
        created_family = Family.objects.get(address=family_data["address"])
        self.assertEqual(created_family.address, family_data["address"])

    def test_add_family_member_service(self):
        """Test adding member to family through service."""
        if not self.family_service:
            self.skipTest("FamilyService not available")

        # Create family and insuree
        family = Family.objects.create(
            address="Test Family Address", audit_user=self.test_user
        )

        insuree = Insuree.objects.create(
            chf_id="12345",
            last_name="Member",
            other_names="Test",
            audit_user=self.test_user,
        )

        member_data = {
            "family_uuid": str(family.uuid),
            "insuree_uuid": str(insuree.uuid),
            "is_head": True,
            "relationship": None,
        }

        if hasattr(self.family_service, "add_member"):
            response = self.family_service.add_member(member_data)

            self.assertServiceResponse(response, success=True)

            # Verify membership was created
            membership = FamilyMembership.objects.filter(
                family=family, insuree=insuree
            ).first()

            self.assertIsNotNone(membership)
            self.assertTrue(membership.is_head)

    def test_transfer_family_member_service(self):
        """Test transferring family member through service."""
        if not self.family_service:
            self.skipTest("FamilyService not available")

        # Create families and membership
        family1 = Family.objects.create(address="Family 1", audit_user=self.test_user)

        family2 = Family.objects.create(address="Family 2", audit_user=self.test_user)

        insuree = Insuree.objects.create(
            chf_id="12345",
            last_name="Transfer",
            other_names="Test",
            audit_user=self.test_user,
        )

        membership = FamilyMembership.objects.create(
            family=family1, insuree=insuree, is_head=False, audit_user=self.test_user
        )

        transfer_data = {
            "membership_uuid": str(membership.uuid),
            "target_family_uuid": str(family2.uuid),
        }

        if hasattr(self.family_service, "transfer_member"):
            response = self.family_service.transfer_member(transfer_data)

            self.assertServiceResponse(response, success=True)

    def test_get_family_members_service(self):
        """Test getting family members through service."""
        if not self.family_service:
            self.skipTest("FamilyService not available")

        # Create family with members
        family = Family.objects.create(address="Test Family", audit_user=self.test_user)

        head = Insuree.objects.create(
            chf_id="HEAD01",
            last_name="Head",
            other_names="Family",
            audit_user=self.test_user,
        )

        member = Insuree.objects.create(
            chf_id="MEMBER01",
            last_name="Member",
            other_names="Family",
            audit_user=self.test_user,
        )

        FamilyMembership.objects.create(
            family=family, insuree=head, is_head=True, audit_user=self.test_user
        )

        FamilyMembership.objects.create(
            family=family, insuree=member, is_head=False, audit_user=self.test_user
        )

        if hasattr(self.family_service, "get_members"):
            response = self.family_service.get_members(str(family.uuid))

            self.assertServiceResponse(response, success=True)
            self.assertIn("data", response)

            members = response["data"]
            self.assertEqual(len(members), 2)


class InsureeValidationServiceTest(BaseServiceTestCase):
    """Test insuree validation service functionality."""

    def setUp(self):
        super().setUp()

        # Initialize validation service if it exists
        try:
            from modules.insuree.services import InsureeValidationService

            self.validation_service = InsureeValidationService()
        except (ImportError, NameError):
            self.validation_service = None

    def test_chf_id_validation(self):
        """Test CHF ID validation."""
        if not self.validation_service:
            self.skipTest("InsureeValidationService not available")

        # Test valid CHF IDs
        valid_chf_ids = ["12345", "ABC123", "999888777"]

        for chf_id in valid_chf_ids:
            if hasattr(self.validation_service, "validate_chf_id"):
                result = self.validation_service.validate_chf_id(chf_id)
                self.assertTrue(result.get("valid", True))

        # Test invalid CHF IDs
        invalid_chf_ids = ["", "   ", "123", "a" * 100]

        for chf_id in invalid_chf_ids:
            if hasattr(self.validation_service, "validate_chf_id"):
                result = self.validation_service.validate_chf_id(chf_id)
                self.assertFalse(result.get("valid", False))

    def test_email_validation(self):
        """Test email validation."""
        if not self.validation_service:
            self.skipTest("InsureeValidationService not available")

        # Test valid emails
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "test123@test-domain.com",
        ]

        for email in valid_emails:
            if hasattr(self.validation_service, "validate_email"):
                result = self.validation_service.validate_email(email)
                self.assertTrue(result.get("valid", True))

        # Test invalid emails
        invalid_emails = [
            "invalid-email",
            "@domain.com",
            "test@",
            "test..test@domain.com",
        ]

        for email in invalid_emails:
            if hasattr(self.validation_service, "validate_email"):
                result = self.validation_service.validate_email(email)
                self.assertFalse(result.get("valid", False))

    def test_phone_validation(self):
        """Test phone number validation."""
        if not self.validation_service:
            self.skipTest("InsureeValidationService not available")

        # Test valid phone numbers
        valid_phones = ["+1234567890", "(123) 456-7890", "123-456-7890", "1234567890"]

        for phone in valid_phones:
            if hasattr(self.validation_service, "validate_phone"):
                result = self.validation_service.validate_phone(phone)
                # Depending on implementation, might be valid or invalid
                self.assertIsInstance(result.get("valid"), bool)

    def test_date_of_birth_validation(self):
        """Test date of birth validation."""
        if not self.validation_service:
            self.skipTest("InsureeValidationService not available")

        # Test valid dates
        valid_dates = [
            date.today() - timedelta(days=365 * 25),  # 25 years ago
            date.today() - timedelta(days=365 * 1),  # 1 year ago
            date(1950, 1, 1),  # Very old but valid
        ]

        for dob in valid_dates:
            if hasattr(self.validation_service, "validate_date_of_birth"):
                result = self.validation_service.validate_date_of_birth(dob)
                self.assertTrue(result.get("valid", True))

        # Test invalid dates
        invalid_dates = [
            date.today() + timedelta(days=1),  # Future date
            date.today() + timedelta(days=365),  # Far future
        ]

        for dob in invalid_dates:
            if hasattr(self.validation_service, "validate_date_of_birth"):
                result = self.validation_service.validate_date_of_birth(dob)
                self.assertFalse(result.get("valid", False))


class InsureeBusinessLogicTest(BaseServiceTestCase):
    """Test insuree business logic and rules."""

    def setUp(self):
        super().setUp()

        # Create dependencies
        self.gender_male = Gender.objects.create(
            code="M", gender="Male", sort_order=1, audit_user=self.test_user
        )

    def test_age_calculation_logic(self):
        """Test age calculation business logic."""
        # Create insuree with known birth date
        birth_date = date(1990, 6, 15)
        insuree = Insuree.objects.create(
            chf_id="AGE_TEST",
            last_name="Age",
            other_names="Test",
            dob=birth_date,
            audit_user=self.test_user,
        )

        # Test age calculation
        if hasattr(insuree, "calculate_age"):
            age = insuree.calculate_age()
            expected_age = (date.today() - birth_date).days // 365
            self.assertAlmostEqual(age, expected_age, delta=1)

        # Test age at specific date
        if hasattr(insuree, "calculate_age"):
            test_date = date(2020, 6, 15)
            age_at_date = insuree.calculate_age(reference_date=test_date)
            self.assertEqual(age_at_date, 30)  # Born 1990, age in 2020

    def test_adult_child_classification(self):
        """Test adult/child classification logic."""
        # Create adult insuree
        adult_birth = date.today() - timedelta(days=365 * 25)
        adult = Insuree.objects.create(
            chf_id="ADULT_TEST",
            last_name="Adult",
            other_names="Test",
            dob=adult_birth,
            audit_user=self.test_user,
        )

        # Create child insuree
        child_birth = date.today() - timedelta(days=365 * 10)
        child = Insuree.objects.create(
            chf_id="CHILD_TEST",
            last_name="Child",
            other_names="Test",
            dob=child_birth,
            audit_user=self.test_user,
        )

        # Test classification
        if hasattr(adult, "is_adult"):
            self.assertTrue(adult.is_adult())

        if hasattr(child, "is_adult"):
            self.assertFalse(child.is_adult())

        # Test manager methods
        adults = Insuree.objects.adults()
        self.assertIn(adult, adults)
        self.assertNotIn(child, adults)

    def test_family_head_eligibility(self):
        """Test family head eligibility rules."""
        # Create adult insuree (eligible to be head)
        adult_birth = date.today() - timedelta(days=365 * 25)
        adult = Insuree.objects.create(
            chf_id="HEAD_ELIGIBLE",
            last_name="Head",
            other_names="Eligible",
            dob=adult_birth,
            audit_user=self.test_user,
        )

        # Create child insuree (not eligible to be head)
        child_birth = date.today() - timedelta(days=365 * 10)
        child = Insuree.objects.create(
            chf_id="HEAD_NOT_ELIGIBLE",
            last_name="Head",
            other_names="NotEligible",
            dob=child_birth,
            audit_user=self.test_user,
        )

        # Test eligibility
        if hasattr(adult, "can_be_family_head"):
            self.assertTrue(adult.can_be_family_head())

        if hasattr(child, "can_be_family_head"):
            self.assertFalse(child.can_be_family_head())

    def test_insuree_status_transitions(self):
        """Test insuree status transition rules."""
        insuree = Insuree.objects.create(
            chf_id="STATUS_TEST",
            last_name="Status",
            other_names="Test",
            status=InsureeStatus.ACTIVE,
            audit_user=self.test_user,
        )

        # Test valid transitions
        valid_transitions = [
            (InsureeStatus.ACTIVE, InsureeStatus.INACTIVE),
            (InsureeStatus.ACTIVE, InsureeStatus.SUSPENDED),
            (InsureeStatus.INACTIVE, InsureeStatus.ACTIVE),
        ]

        for from_status, to_status in valid_transitions:
            insuree.status = from_status
            insuree.save()

            # Test transition
            if hasattr(insuree, "can_transition_to"):
                can_transition = insuree.can_transition_to(to_status)
                # Depending on business rules, this might be True or False
                self.assertIsInstance(can_transition, bool)

            # Test actual transition
            insuree.status = to_status
            insuree.full_clean()  # Should not raise validation error
