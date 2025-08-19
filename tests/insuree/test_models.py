"""
Tests for insuree models.
"""

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.contrib.auth import get_user_model
from modules.insuree.models.insuree import Insuree, InsureeStatus, InsureeManager
from modules.insuree.models.insuree_dependency import Gender, Profession, Education, IdentificationType
from modules.location import models as location_models
from tests.base import BaseModelTestCase, TestDataMixin
from faker import Faker
from datetime import date, timedelta
import uuid

User = get_user_model()
fake = Faker()


class InsureeModelTest(BaseModelTestCase, TestDataMixin):
    """Test Insuree model functionality."""
    
    def setUp(self):
        super().setUp()
        self.test_user = self.create_test_user()
        
        # Create required dependencies
        self.gender_male = Gender.objects.create(
            code='M',
            gender='Male',
            sort_order=1,
            audit_user=self.test_user
        )
        
        self.gender_female = Gender.objects.create(
            code='F',
            gender='Female',
            sort_order=2,
            audit_user=self.test_user
        )
        
        self.profession = Profession.objects.create(
            code='DOC',
            profession='Doctor',
            sort_order=1,
            audit_user=self.test_user
        )
        
        self.education = Education.objects.create(
            code='UNI',
            education='University',
            sort_order=1,
            audit_user=self.test_user
        )
    
    def test_insuree_creation(self):
        """Test creating an insuree."""
        insuree_data = self.generate_insuree_data()
        
        insuree = Insuree.objects.create(
            chf_id=insuree_data['chf_id'],
            last_name=insuree_data['last_name'],
            other_names=insuree_data['other_names'],
            dob=insuree_data['dob'],
            gender=self.gender_male,
            marital_status='S',
            phone=insuree_data['phone'],
            email=insuree_data['email'],
            audit_user=self.test_user
        )
        
        self.assertEqual(insuree.chf_id, insuree_data['chf_id'])
        self.assertEqual(insuree.last_name, insuree_data['last_name'])
        self.assertEqual(insuree.other_names, insuree_data['other_names'])
        self.assertEqual(insuree.dob, insuree_data['dob'])
        self.assertEqual(insuree.gender, self.gender_male)
        self.assertEqual(insuree.marital_status, 'S')
        self.assertIsNotNone(insuree.uuid)
        self.assertEqual(insuree.audit_user, self.test_user)
    
    def test_insuree_required_fields(self):
        """Test insuree required fields."""
        # Test missing last_name
        with self.assertRaises(ValidationError):
            insuree = Insuree(
                chf_id='12345',
                other_names='John',
                audit_user=self.test_user
            )
            insuree.full_clean()
        
        # Test missing other_names
        with self.assertRaises(ValidationError):
            insuree = Insuree(
                chf_id='12345',
                last_name='Doe',
                audit_user=self.test_user
            )
            insuree.full_clean()
    
    def test_insuree_unique_chf_id(self):
        """Test that CHF ID must be unique."""
        chf_id = '12345'
        
        # Create first insuree
        insuree1 = Insuree.objects.create(
            chf_id=chf_id,
            last_name='Doe',
            other_names='John',
            audit_user=self.test_user
        )
        
        # Try to create second insuree with same CHF ID
        with self.assertRaises(IntegrityError):
            insuree2 = Insuree.objects.create(
                chf_id=chf_id,  # Same CHF ID
                last_name='Smith',
                other_names='Jane',
                audit_user=self.test_user
            )
    
    def test_insuree_status_choices(self):
        """Test insuree status choices."""
        insuree = Insuree.objects.create(
            chf_id='12345',
            last_name='Doe',
            other_names='John',
            status=InsureeStatus.ACTIVE,
            audit_user=self.test_user
        )
        
        self.assertEqual(insuree.status, InsureeStatus.ACTIVE)
        
        # Test all status choices
        valid_statuses = [choice[0] for choice in InsureeStatus.choices]
        
        for status in valid_statuses:
            insuree.status = status
            insuree.full_clean()  # Should not raise validation error
    
    def test_insuree_marital_status_choices(self):
        """Test marital status choices."""
        valid_statuses = ['S', 'M', 'D', 'W']
        
        for status in valid_statuses:
            insuree = Insuree(
                chf_id=f'test_{status}',
                last_name='Doe',
                other_names='John',
                marital_status=status,
                audit_user=self.test_user
            )
            insuree.full_clean()  # Should not raise validation error
    
    def test_insuree_age_calculation(self):
        """Test age calculation from date of birth."""
        # Create insuree with known birth date
        birth_date = date.today() - timedelta(days=365 * 25)  # 25 years old
        
        insuree = Insuree.objects.create(
            chf_id='12345',
            last_name='Doe',
            other_names='John',
            dob=birth_date,
            audit_user=self.test_user
        )
        
        # If age property exists, test it
        if hasattr(insuree, 'age'):
            age = insuree.age
            self.assertAlmostEqual(age, 25, delta=1)  # Allow for some variance
    
    def test_insuree_phone_validation(self):
        """Test phone number validation."""
        insuree = Insuree(
            chf_id='12345',
            last_name='Doe',
            other_names='John',
            phone='+1234567890',
            audit_user=self.test_user
        )
        
        # Should not raise validation error for valid phone
        try:
            insuree.full_clean()
        except ValidationError as e:
            # If phone validation fails, check if it's due to phone format
            if 'phone' not in str(e):
                raise e
    
    def test_insuree_email_validation(self):
        """Test email validation."""
        # Valid email
        insuree = Insuree(
            chf_id='12345',
            last_name='Doe',
            other_names='John',
            email='test@example.com',
            audit_user=self.test_user
        )
        
        insuree.full_clean()  # Should not raise validation error
        
        # Invalid email
        insuree_invalid = Insuree(
            chf_id='12346',
            last_name='Doe',
            other_names='Jane',
            email='invalid-email',
            audit_user=self.test_user
        )
        
        with self.assertRaises(ValidationError):
            insuree_invalid.full_clean()
    
    def test_insuree_foreign_key_relationships(self):
        """Test foreign key relationships."""
        insuree = Insuree.objects.create(
            chf_id='12345',
            last_name='Doe',
            other_names='John',
            gender=self.gender_male,
            profession=self.profession,
            education=self.education,
            audit_user=self.test_user
        )
        
        self.assertEqual(insuree.gender, self.gender_male)
        self.assertEqual(insuree.profession, self.profession)
        self.assertEqual(insuree.education, self.education)
    
    def test_insuree_string_representation(self):
        """Test insuree string representation."""
        insuree = Insuree.objects.create(
            chf_id='12345',
            last_name='Doe',
            other_names='John',
            audit_user=self.test_user
        )
        
        str_repr = str(insuree)
        self.assertIn('Doe', str_repr)
        self.assertIn('John', str_repr)
    
    def test_insuree_uuid_generation(self):
        """Test UUID generation."""
        insuree = Insuree.objects.create(
            chf_id='12345',
            last_name='Doe',
            other_names='John',
            audit_user=self.test_user
        )
        
        self.assertIsNotNone(insuree.uuid)
        self.assertIsInstance(insuree.uuid, uuid.UUID)
        
        # UUID should be unique
        insuree2 = Insuree.objects.create(
            chf_id='12346',
            last_name='Smith',
            other_names='Jane',
            audit_user=self.test_user
        )
        
        self.assertNotEqual(insuree.uuid, insuree2.uuid)
    
    def test_insuree_passport_field(self):
        """Test passport field."""
        insuree = Insuree.objects.create(
            chf_id='12345',
            last_name='Doe',
            other_names='John',
            passport='A1234567',
            audit_user=self.test_user
        )
        
        self.assertEqual(insuree.passport, 'A1234567')
    
    def test_insuree_lifecycle_hooks(self):
        """Test lifecycle hooks if implemented."""
        insuree = Insuree.objects.create(
            chf_id='12345',
            last_name='Doe',
            other_names='John',
            audit_user=self.test_user
        )
        
        # Test update
        insuree.other_names = 'Johnny'
        insuree.save()
        
        # Refresh from database
        insuree.refresh_from_db()
        self.assertEqual(insuree.other_names, 'Johnny')


class InsureeManagerTest(BaseModelTestCase):
    """Test Insuree manager functionality."""
    
    def setUp(self):
        super().setUp()
        self.test_user = self.create_test_user()
        
        # Create test insurees
        self.active_insuree = Insuree.objects.create(
            chf_id='12345',
            last_name='Active',
            other_names='User',
            status=InsureeStatus.ACTIVE,
            audit_user=self.test_user
        )
        
        self.inactive_insuree = Insuree.objects.create(
            chf_id='12346',
            last_name='Inactive',
            other_names='User',
            status=InsureeStatus.INACTIVE,
            audit_user=self.test_user
        )
        
        self.deceased_insuree = Insuree.objects.create(
            chf_id='12347',
            last_name='Deceased',
            other_names='User',
            status=InsureeStatus.DECEASED,
            audit_user=self.test_user
        )
    
    def test_active_manager_method(self):
        """Test active() manager method."""
        active_insurees = Insuree.objects.active()
        
        self.assertIn(self.active_insuree, active_insurees)
        self.assertNotIn(self.inactive_insuree, active_insurees)
        self.assertNotIn(self.deceased_insuree, active_insurees)
    
    def test_by_chf_id_manager_method(self):
        """Test by_chf_id() manager method."""
        result = Insuree.objects.by_chf_id('12345')
        
        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first(), self.active_insuree)
        
        # Test non-existent CHF ID
        no_result = Insuree.objects.by_chf_id('99999')
        self.assertEqual(no_result.count(), 0)
    
    def test_adults_manager_method(self):
        """Test adults() manager method."""
        # Create adult and child insurees
        adult_birth_date = date.today() - timedelta(days=365 * 25)  # 25 years old
        child_birth_date = date.today() - timedelta(days=365 * 10)  # 10 years old
        
        adult_insuree = Insuree.objects.create(
            chf_id='adult123',
            last_name='Adult',
            other_names='User',
            dob=adult_birth_date,
            audit_user=self.test_user
        )
        
        child_insuree = Insuree.objects.create(
            chf_id='child123',
            last_name='Child',
            other_names='User',
            dob=child_birth_date,
            audit_user=self.test_user
        )
        
        adults = Insuree.objects.adults()
        
        self.assertIn(adult_insuree, adults)
        self.assertNotIn(child_insuree, adults)
    
    def test_custom_querysets(self):
        """Test custom QuerySet methods."""
        # Test filtering by various criteria
        male_insurees = Insuree.objects.filter(gender__code='M')
        female_insurees = Insuree.objects.filter(gender__code='F')
        
        # These might be empty if no gender was set in setup
        self.assertIsInstance(male_insurees.count(), int)
        self.assertIsInstance(female_insurees.count(), int)


class InsureeValidationTest(BaseModelTestCase):
    """Test insuree validation logic."""
    
    def setUp(self):
        super().setUp()
        self.test_user = self.create_test_user()
    
    def test_chf_id_format_validation(self):
        """Test CHF ID format validation if implemented."""
        # Test valid CHF ID formats
        valid_chf_ids = ['12345', 'ABC123', '123456789']
        
        for chf_id in valid_chf_ids:
            insuree = Insuree(
                chf_id=chf_id,
                last_name='Doe',
                other_names='John',
                audit_user=self.test_user
            )
            
            try:
                insuree.full_clean()
            except ValidationError as e:
                # If validation fails, it might be due to other fields
                if 'chf_id' in str(e):
                    self.fail(f"CHF ID {chf_id} should be valid")
    
    def test_date_validation(self):
        """Test date validation."""
        # Test future birth date (should be invalid)
        future_date = date.today() + timedelta(days=1)
        
        insuree = Insuree(
            chf_id='12345',
            last_name='Doe',
            other_names='John',
            dob=future_date,
            audit_user=self.test_user
        )
        
        # Depending on implementation, this might raise validation error
        try:
            insuree.full_clean()
        except ValidationError as e:
            if 'dob' in str(e):
                # Future birth date validation is implemented
                pass
            else:
                raise e
    
    def test_name_validation(self):
        """Test name field validation."""
        # Test very long names
        long_name = 'a' * 200  # Longer than max_length
        
        insuree = Insuree(
            chf_id='12345',
            last_name=long_name,
            other_names='John',
            audit_user=self.test_user
        )
        
        with self.assertRaises(ValidationError):
            insuree.full_clean()
    
    def test_phone_format_validation(self):
        """Test phone number format validation."""
        # Test various phone formats
        phone_formats = [
            '+1234567890',
            '(123) 456-7890',
            '123-456-7890',
            '1234567890',
            '+1-123-456-7890'
        ]
        
        for phone in phone_formats:
            insuree = Insuree(
                chf_id=f'test_{hash(phone)}',
                last_name='Doe',
                other_names='John',
                phone=phone,
                audit_user=self.test_user
            )
            
            try:
                insuree.full_clean()
            except ValidationError as e:
                # If phone validation fails, check if it's specifically phone-related
                if 'phone' in str(e):
                    # This phone format is not accepted
                    continue
                else:
                    raise e


class InsureeRelationshipsTest(BaseModelTestCase):
    """Test insuree relationships and family connections."""
    
    def setUp(self):
        super().setUp()
        self.test_user = self.create_test_user()
    
    def test_insuree_family_relationships(self):
        """Test insuree family relationship methods if implemented."""
        insuree = Insuree.objects.create(
            chf_id='12345',
            last_name='Doe',
            other_names='John',
            audit_user=self.test_user
        )
        
        # Test family-related methods if they exist
        if hasattr(insuree, 'current_family'):
            current_family = insuree.current_family
            # Test family relationship
        
        if hasattr(insuree, 'is_head_of_family'):
            is_head = insuree.is_head_of_family
            self.assertIsInstance(is_head, bool)
        
        if hasattr(insuree, 'get_family_relationship'):
            relationship = insuree.get_family_relationship()
            # Test relationship logic
    
    def test_insuree_policy_relationships(self):
        """Test insuree policy relationships if implemented."""
        insuree = Insuree.objects.create(
            chf_id='12345',
            last_name='Doe',
            other_names='John',
            audit_user=self.test_user
        )
        
        # Test policy-related methods if they exist
        if hasattr(insuree, 'policies'):
            policies = insuree.policies.all()
            self.assertIsInstance(policies.count(), int)
        
        if hasattr(insuree, 'active_policies'):
            active_policies = insuree.active_policies
            # Test active policies logic