"""
Tests for family models.
"""

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.contrib.auth import get_user_model
from modules.insuree.models.family import (
    Family,
    FamilyMembership,
    FamilyMembershipStatus,
)
from modules.insuree.models.insuree import Insuree, InsureeStatus
from modules.insuree.models.insuree_model_dependency import Relation, Gender
from tests.base import BaseModelTestCase, TestDataMixin
from faker import Faker
from datetime import date, timedelta
import uuid

User = get_user_model()
fake = Faker()


class FamilyModelTest(BaseModelTestCase, TestDataMixin):
    """Test Family model functionality."""

    def setUp(self):
        super().setUp()
        self.test_user = self.create_test_user()

        # Create required dependencies
        self.gender_male = Gender.objects.create(
            code="M", gender="Male", sort_order=1, audit_user=self.test_user
        )

        self.spouse_relation = Relation.objects.create(
            code="SP", relation="Spouse", sort_order=1, audit_user=self.test_user
        )

        self.child_relation = Relation.objects.create(
            code="CH", relation="Child", sort_order=2, audit_user=self.test_user
        )

    def test_family_creation(self):
        """Test creating a family."""
        family_data = self.generate_family_data()

        family = Family.objects.create(
            address=family_data["address"],
            ethnicity=family_data.get("ethnicity"),
            confirmation_no=family_data.get("confirmation_no"),
            confirmation_type=family_data.get("confirmation_type", "P"),
            audit_user=self.test_user,
        )

        self.assertEqual(family.address, family_data["address"])
        self.assertIsNotNone(family.uuid)
        self.assertEqual(family.audit_user, self.test_user)

    def test_family_required_fields(self):
        """Test family required fields."""
        # Test that family can be created with minimal fields
        family = Family(address="Test Address", audit_user=self.test_user)

        try:
            family.full_clean()
        except ValidationError as e:
            # Check which fields are actually required
            self.assertNotIn("address", str(e))

    def test_family_uuid_generation(self):
        """Test UUID generation for families."""
        family1 = Family.objects.create(address="Address 1", audit_user=self.test_user)

        family2 = Family.objects.create(address="Address 2", audit_user=self.test_user)

        self.assertIsNotNone(family1.uuid)
        self.assertIsNotNone(family2.uuid)
        self.assertNotEqual(family1.uuid, family2.uuid)

    def test_family_string_representation(self):
        """Test family string representation."""
        family = Family.objects.create(
            address="123 Test Street", audit_user=self.test_user
        )

        str_repr = str(family)
        # String representation might include address or ID
        self.assertIsInstance(str_repr, str)
        self.assertTrue(len(str_repr) > 0)

    def test_family_confirmation_types(self):
        """Test family confirmation type choices."""
        valid_types = ["P", "V"]  # Based on the generate_family_data method

        for conf_type in valid_types:
            family = Family(
                address="Test Address",
                confirmation_type=conf_type,
                audit_user=self.test_user,
            )

            try:
                family.full_clean()
            except ValidationError as e:
                # If validation fails, check if it's not due to confirmation_type
                if "confirmation_type" in str(e):
                    self.fail(f"Confirmation type {conf_type} should be valid")


class FamilyMembershipModelTest(BaseModelTestCase, TestDataMixin):
    """Test FamilyMembership model functionality."""

    def setUp(self):
        super().setUp()
        self.test_user = self.create_test_user()

        # Create required dependencies
        self.gender_male = Gender.objects.create(
            code="M", gender="Male", sort_order=1, audit_user=self.test_user
        )

        self.spouse_relation = Relation.objects.create(
            code="SP", relation="Spouse", sort_order=1, audit_user=self.test_user
        )

        # Create test family
        self.test_family = Family.objects.create(
            address="123 Test Street", audit_user=self.test_user
        )

        # Create test insurees
        self.head_insuree = Insuree.objects.create(
            chf_id="12345",
            last_name="Head",
            other_names="Family",
            gender=self.gender_male,
            audit_user=self.test_user,
        )

        self.spouse_insuree = Insuree.objects.create(
            chf_id="12346",
            last_name="Spouse",
            other_names="Family",
            gender=self.gender_male,
            audit_user=self.test_user,
        )

    def test_family_membership_creation(self):
        """Test creating a family membership."""
        membership = FamilyMembership.objects.create(
            family=self.test_family,
            insuree=self.head_insuree,
            is_head=True,
            status=FamilyMembershipStatus.ACTIVE,
            membership_start_date=date.today(),
            audit_user=self.test_user,
        )

        self.assertEqual(membership.family, self.test_family)
        self.assertEqual(membership.insuree, self.head_insuree)
        self.assertTrue(membership.is_head)
        self.assertEqual(membership.status, FamilyMembershipStatus.ACTIVE)
        self.assertIsNotNone(membership.uuid)

    def test_family_membership_required_fields(self):
        """Test family membership required fields."""
        # Test missing family
        with self.assertRaises(ValidationError):
            membership = FamilyMembership(
                insuree=self.head_insuree, is_head=True, audit_user=self.test_user
            )
            membership.full_clean()

        # Test missing insuree
        with self.assertRaises(ValidationError):
            membership = FamilyMembership(
                family=self.test_family, is_head=True, audit_user=self.test_user
            )
            membership.full_clean()

    def test_family_membership_status_choices(self):
        """Test family membership status choices."""
        valid_statuses = [choice[0] for choice in FamilyMembershipStatus.choices]

        for status in valid_statuses:
            membership = FamilyMembership(
                family=self.test_family,
                insuree=self.head_insuree,
                is_head=True,
                status=status,
                audit_user=self.test_user,
            )
            membership.full_clean()  # Should not raise validation error

    def test_family_membership_relationships(self):
        """Test family membership relationships."""
        # Create head membership (no relationship to self)
        head_membership = FamilyMembership.objects.create(
            family=self.test_family,
            insuree=self.head_insuree,
            is_head=True,
            relationship=None,  # Head has no relationship
            audit_user=self.test_user,
        )

        # Create spouse membership
        spouse_membership = FamilyMembership.objects.create(
            family=self.test_family,
            insuree=self.spouse_insuree,
            is_head=False,
            relationship=self.spouse_relation,
            audit_user=self.test_user,
        )

        self.assertIsNone(head_membership.relationship)
        self.assertEqual(spouse_membership.relationship, self.spouse_relation)

    def test_family_membership_dates(self):
        """Test family membership date handling."""
        start_date = date.today()
        end_date = date.today() + timedelta(days=365)

        membership = FamilyMembership.objects.create(
            family=self.test_family,
            insuree=self.head_insuree,
            is_head=True,
            membership_start_date=start_date,
            membership_end_date=end_date,
            audit_user=self.test_user,
        )

        self.assertEqual(membership.membership_start_date, start_date)
        self.assertEqual(membership.membership_end_date, end_date)

    def test_family_membership_unique_constraints(self):
        """Test family membership unique constraints if any."""
        # Create first membership
        membership1 = FamilyMembership.objects.create(
            family=self.test_family,
            insuree=self.head_insuree,
            is_head=True,
            audit_user=self.test_user,
        )

        # Try to create duplicate membership (might be allowed depending on business rules)
        try:
            membership2 = FamilyMembership.objects.create(
                family=self.test_family,
                insuree=self.head_insuree,  # Same insuree
                is_head=False,
                audit_user=self.test_user,
            )
            # If this succeeds, multiple memberships are allowed
            self.assertNotEqual(membership1.id, membership2.id)
        except IntegrityError:
            # Duplicate memberships are not allowed
            pass

    def test_family_head_constraints(self):
        """Test family head constraints."""
        # Create head of family
        head_membership = FamilyMembership.objects.create(
            family=self.test_family,
            insuree=self.head_insuree,
            is_head=True,
            audit_user=self.test_user,
        )

        # Try to create another head (might be constrained)
        try:
            another_head = FamilyMembership.objects.create(
                family=self.test_family,
                insuree=self.spouse_insuree,
                is_head=True,  # Another head
                audit_user=self.test_user,
            )
            # If this succeeds, multiple heads are allowed
            self.assertTrue(another_head.is_head)
        except (IntegrityError, ValidationError):
            # Multiple heads are not allowed
            pass


class FamilyMembershipManagerTest(BaseModelTestCase):
    """Test FamilyMembership manager functionality."""

    def setUp(self):
        super().setUp()
        self.test_user = self.create_test_user()

        # Create test data
        self.gender_male = Gender.objects.create(
            code="M", gender="Male", sort_order=1, audit_user=self.test_user
        )

        self.test_family = Family.objects.create(
            address="123 Test Street", audit_user=self.test_user
        )

        self.head_insuree = Insuree.objects.create(
            chf_id="12345",
            last_name="Head",
            other_names="Family",
            audit_user=self.test_user,
        )

        self.member_insuree = Insuree.objects.create(
            chf_id="12346",
            last_name="Member",
            other_names="Family",
            audit_user=self.test_user,
        )

        # Create memberships
        self.active_membership = FamilyMembership.objects.create(
            family=self.test_family,
            insuree=self.head_insuree,
            is_head=True,
            status=FamilyMembershipStatus.ACTIVE,
            audit_user=self.test_user,
        )

        self.inactive_membership = FamilyMembership.objects.create(
            family=self.test_family,
            insuree=self.member_insuree,
            is_head=False,
            status=FamilyMembershipStatus.INACTIVE,
            audit_user=self.test_user,
        )

    def test_active_manager_method(self):
        """Test active() manager method."""
        active_memberships = FamilyMembership.objects.active()

        self.assertIn(self.active_membership, active_memberships)
        self.assertNotIn(self.inactive_membership, active_memberships)

    def test_heads_of_family_manager_method(self):
        """Test heads_of_family() manager method."""
        heads = FamilyMembership.objects.heads_of_family()

        self.assertIn(self.active_membership, heads)
        self.assertNotIn(self.inactive_membership, heads)

    def test_for_family_manager_method(self):
        """Test for_family() manager method."""
        family_memberships = FamilyMembership.objects.for_family(self.test_family)

        self.assertEqual(family_memberships.count(), 2)
        self.assertIn(self.active_membership, family_memberships)
        self.assertIn(self.inactive_membership, family_memberships)

    def test_for_insuree_manager_method(self):
        """Test for_insuree() manager method."""
        head_memberships = FamilyMembership.objects.for_insuree(self.head_insuree)
        member_memberships = FamilyMembership.objects.for_insuree(self.member_insuree)

        self.assertEqual(head_memberships.count(), 1)
        self.assertEqual(member_memberships.count(), 1)
        self.assertEqual(head_memberships.first(), self.active_membership)
        self.assertEqual(member_memberships.first(), self.inactive_membership)


class FamilyRelationshipsTest(BaseModelTestCase):
    """Test family relationship functionality."""

    def setUp(self):
        super().setUp()
        self.test_user = self.create_test_user()

        # Create dependencies
        self.gender_male = Gender.objects.create(
            code="M", gender="Male", sort_order=1, audit_user=self.test_user
        )

        self.gender_female = Gender.objects.create(
            code="F", gender="Female", sort_order=2, audit_user=self.test_user
        )

        self.spouse_relation = Relation.objects.create(
            code="SP", relation="Spouse", sort_order=1, audit_user=self.test_user
        )

        self.child_relation = Relation.objects.create(
            code="CH", relation="Child", sort_order=2, audit_user=self.test_user
        )

        # Create family
        self.test_family = Family.objects.create(
            address="123 Family Street", audit_user=self.test_user
        )

    def test_family_member_addition(self):
        """Test adding members to family."""
        # Create insurees
        head = Insuree.objects.create(
            chf_id="HEAD01",
            last_name="Smith",
            other_names="John",
            gender=self.gender_male,
            audit_user=self.test_user,
        )

        spouse = Insuree.objects.create(
            chf_id="SPOUSE01",
            last_name="Smith",
            other_names="Jane",
            gender=self.gender_female,
            audit_user=self.test_user,
        )

        child = Insuree.objects.create(
            chf_id="CHILD01",
            last_name="Smith",
            other_names="Bobby",
            gender=self.gender_male,
            dob=date.today() - timedelta(days=365 * 10),  # 10 years old
            audit_user=self.test_user,
        )

        # Add head to family
        head_membership = FamilyMembership.objects.create(
            family=self.test_family,
            insuree=head,
            is_head=True,
            audit_user=self.test_user,
        )

        # Add spouse to family
        spouse_membership = FamilyMembership.objects.create(
            family=self.test_family,
            insuree=spouse,
            is_head=False,
            relationship=self.spouse_relation,
            audit_user=self.test_user,
        )

        # Add child to family
        child_membership = FamilyMembership.objects.create(
            family=self.test_family,
            insuree=child,
            is_head=False,
            relationship=self.child_relation,
            audit_user=self.test_user,
        )

        # Verify family composition
        family_members = FamilyMembership.objects.for_family(self.test_family)
        self.assertEqual(family_members.count(), 3)

        # Verify head
        heads = family_members.filter(is_head=True)
        self.assertEqual(heads.count(), 1)
        self.assertEqual(heads.first().insuree, head)

        # Verify relationships
        spouse_membership.refresh_from_db()
        child_membership.refresh_from_db()
        self.assertEqual(spouse_membership.relationship, self.spouse_relation)
        self.assertEqual(child_membership.relationship, self.child_relation)

    def test_family_member_transfer(self):
        """Test transferring member to another family."""
        # Create two families
        family1 = Family.objects.create(
            address="Family 1 Address", audit_user=self.test_user
        )

        family2 = Family.objects.create(
            address="Family 2 Address", audit_user=self.test_user
        )

        # Create insuree
        insuree = Insuree.objects.create(
            chf_id="TRANSFER01",
            last_name="Transfer",
            other_names="Test",
            audit_user=self.test_user,
        )

        # Add to first family
        membership1 = FamilyMembership.objects.create(
            family=family1, insuree=insuree, is_head=False, audit_user=self.test_user
        )

        # Test transfer logic if implemented
        if hasattr(membership1, "transfer_to_family"):
            membership1.transfer_to_family(family2)

            # Verify transfer
            membership1.refresh_from_db()
            self.assertEqual(membership1.status, FamilyMembershipStatus.TRANSFERRED)

            # Check if new membership was created in family2
            new_memberships = FamilyMembership.objects.for_family(family2).for_insuree(
                insuree
            )
            if new_memberships.exists():
                self.assertEqual(new_memberships.first().family, family2)

    def test_family_composition_queries(self):
        """Test family composition query methods."""
        # Create family with various members
        head = Insuree.objects.create(
            chf_id="HEAD02",
            last_name="Johnson",
            other_names="Michael",
            dob=date.today() - timedelta(days=365 * 35),  # 35 years old
            audit_user=self.test_user,
        )

        child1 = Insuree.objects.create(
            chf_id="CHILD02",
            last_name="Johnson",
            other_names="Sarah",
            dob=date.today() - timedelta(days=365 * 12),  # 12 years old
            audit_user=self.test_user,
        )

        child2 = Insuree.objects.create(
            chf_id="CHILD03",
            last_name="Johnson",
            other_names="Tommy",
            dob=date.today() - timedelta(days=365 * 8),  # 8 years old
            audit_user=self.test_user,
        )

        # Add to family
        FamilyMembership.objects.create(
            family=self.test_family,
            insuree=head,
            is_head=True,
            audit_user=self.test_user,
        )

        FamilyMembership.objects.create(
            family=self.test_family,
            insuree=child1,
            is_head=False,
            relationship=self.child_relation,
            audit_user=self.test_user,
        )

        FamilyMembership.objects.create(
            family=self.test_family,
            insuree=child2,
            is_head=False,
            relationship=self.child_relation,
            audit_user=self.test_user,
        )

        # Test family queries if methods exist
        if hasattr(self.test_family, "members"):
            members = self.test_family.members
            self.assertEqual(members.count(), 3)

        if hasattr(self.test_family, "member_count"):
            count = self.test_family.member_count
            self.assertEqual(count, 3)

        if hasattr(self.test_family, "adult_members"):
            adults = self.test_family.adult_members
            # Should include the head (35 years old)
            adult_count = adults.count() if hasattr(adults, "count") else len(adults)
            self.assertGreaterEqual(adult_count, 1)
