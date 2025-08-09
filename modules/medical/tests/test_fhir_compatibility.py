"""
Tests for FHIR compatibility of the Item model.
"""

import uuid
from decimal import Decimal
from django.test import TestCase
from fhir.resources.R4B.medication import Medication
from fhir.resources.R4B.activitydefinition import ActivityDefinition
from fhir.resources.R4B.codeableconcept import CodeableConcept
from fhir.resources.R4B.coding import Coding
from fhir.resources.R4B.identifier import Identifier

from modules.medical.models.item import Item, ItemType, ItemOrService, ItemStatus
from modules.fhir_api.converters.item import ItemConverter


class ItemFHIRCompatibilityTestCase(TestCase):
    """Test FHIR compatibility for Item model"""

    def setUp(self):
        """Set up test data"""
        self.item_type = ItemType.objects.create(code="MED001", name="Medication Type")

        self.service_type = ItemType.objects.create(code="SRV001", name="Service Type")

        # Create test item (medication)
        self.test_item = Item.objects.create(
            code="ASP100",
            name="Aspirin 100mg",
            status=ItemStatus.ACTIVE,
            item_type=self.item_type,
            care_type=ItemOrService.ITEM,
            package="Tablet",
            quantity=Decimal("100.00"),
            price=Decimal("5.99"),
            maximum_amount=Decimal("10.00"),
            frequency=1,
            patient_category=1,
            description="Pain relief medication",
            external_id="EXT123",
        )

        # Create test service
        self.test_service = Item.objects.create(
            code="XRAY01",
            name="Chest X-Ray",
            status=ItemStatus.ACTIVE,
            item_type=self.service_type,
            care_type=ItemOrService.SERVICE,
            price=Decimal("150.00"),
            maximum_amount=Decimal("200.00"),
            patient_category=1,
            description="Chest radiography service",
            external_id="RAD456",
        )

    def test_item_to_fhir_medication(self):
        """Test conversion of Item to FHIR Medication resource"""
        fhir_medication = self.test_item.to_fhir_medication()

        # Test basic properties
        self.assertIsInstance(fhir_medication, Medication)
        self.assertEqual(fhir_medication.id, str(self.test_item.uuid))
        self.assertEqual(fhir_medication.status, "active")

        # Test code mapping
        self.assertIsNotNone(fhir_medication.code)
        self.assertEqual(fhir_medication.code.coding[0].code, "ASP100")
        self.assertEqual(fhir_medication.code.coding[0].display, "Aspirin 100mg")
        self.assertEqual(
            fhir_medication.code.coding[0].system, "http://vigtra.health/item-codes"
        )

        # Test form (package) mapping
        self.assertIsNotNone(fhir_medication.form)
        self.assertEqual(fhir_medication.form.text, "Tablet")

        # Test identifier mapping
        self.assertIsNotNone(fhir_medication.identifier)
        self.assertEqual(fhir_medication.identifier[0].value, "EXT123")

    def test_service_to_fhir_medication_raises_error(self):
        """Test that services cannot be converted to Medication"""
        with self.assertRaises(ValueError):
            self.test_service.to_fhir_medication()

    def test_service_to_fhir_activity_definition(self):
        """Test conversion of Service to FHIR ActivityDefinition resource"""
        fhir_activity_def = self.test_service.to_fhir_activity_definition()

        # Test basic properties
        self.assertIsInstance(fhir_activity_def, ActivityDefinition)
        self.assertEqual(fhir_activity_def.id, str(self.test_service.uuid))
        self.assertEqual(fhir_activity_def.status, "active")
        self.assertEqual(fhir_activity_def.kind, "ServiceRequest")

        # Test code mapping
        self.assertIsNotNone(fhir_activity_def.code)
        self.assertEqual(fhir_activity_def.code.coding[0].code, "XRAY01")
        self.assertEqual(fhir_activity_def.code.coding[0].display, "Chest X-Ray")
        self.assertEqual(
            fhir_activity_def.code.coding[0].system,
            "http://vigtra.health/service-codes",
        )

        # Test name and title
        self.assertEqual(fhir_activity_def.name, "XRAY01")
        self.assertEqual(fhir_activity_def.title, "Chest X-Ray")
        self.assertEqual(fhir_activity_def.description, "Chest radiography service")

        # Test identifier mapping
        self.assertIsNotNone(fhir_activity_def.identifier)
        self.assertEqual(fhir_activity_def.identifier[0].value, "RAD456")

    def test_item_to_fhir_activity_definition_raises_error(self):
        """Test that items cannot be converted to ActivityDefinition"""
        with self.assertRaises(ValueError):
            self.test_item.to_fhir_activity_definition()

    def test_status_mapping_to_fhir(self):
        """Test status mapping from internal to FHIR"""
        test_cases = [
            (ItemStatus.ACTIVE, "active"),
            (ItemStatus.INACTIVE, "inactive"),
            (ItemStatus.ENTERED_IN_ERROR, "entered-in-error"),
            (ItemStatus.DRAFT, "draft"),
        ]

        for internal_status, expected_fhir_status in test_cases:
            self.test_item.status = internal_status
            fhir_medication = self.test_item.to_fhir_medication()
            self.assertEqual(fhir_medication.status, expected_fhir_status)

    def test_from_fhir_medication(self):
        """Test creating Item from FHIR Medication resource"""
        # Create a FHIR Medication resource
        medication = Medication()
        medication.id = str(uuid.uuid4())
        medication.status = "active"

        # Set up code
        coding = Coding()
        coding.system = "http://example.com/medications"
        coding.code = "PARA500"
        coding.display = "Paracetamol 500mg"

        code_concept = CodeableConcept()
        code_concept.coding = [coding]
        code_concept.text = "Paracetamol 500mg"
        medication.code = code_concept

        # Set up form
        form_coding = Coding()
        form_coding.system = "http://example.com/forms"
        form_coding.display = "Capsule"

        form_concept = CodeableConcept()
        form_concept.coding = [form_coding]
        form_concept.text = "Capsule"
        medication.form = form_concept

        # Set up identifier
        identifier = Identifier()
        identifier.value = "MED789"
        identifier.system = "http://example.com/ids"
        medication.identifier = [identifier]

        # Convert to Item
        item = Item.from_fhir_medication(medication, self.item_type)

        # Test the conversion
        self.assertEqual(item.code, "PARA500")
        self.assertEqual(item.name, "Paracetamol 500mg")
        self.assertEqual(item.care_type, ItemOrService.ITEM)
        self.assertEqual(item.status, ItemStatus.ACTIVE)
        self.assertEqual(item.package, "Capsule")
        self.assertEqual(item.external_id, "MED789")
        self.assertEqual(item.item_type, self.item_type)

    def test_from_fhir_activity_definition(self):
        """Test creating Item from FHIR ActivityDefinition resource"""
        # Create a FHIR ActivityDefinition resource
        activity_def = ActivityDefinition()
        activity_def.id = str(uuid.uuid4())
        activity_def.status = "active"
        activity_def.kind = "ServiceRequest"
        activity_def.title = "Blood Test"
        activity_def.description = "Complete blood count test"

        # Set up code
        coding = Coding()
        coding.system = "http://example.com/services"
        coding.code = "CBC001"
        coding.display = "Complete Blood Count"

        code_concept = CodeableConcept()
        code_concept.coding = [coding]
        code_concept.text = "Complete Blood Count"
        activity_def.code = code_concept

        # Set up identifier
        identifier = Identifier()
        identifier.value = "LAB123"
        identifier.system = "http://example.com/lab-ids"
        activity_def.identifier = [identifier]

        # Convert to Item
        item = Item.from_fhir_activity_definition(activity_def, self.service_type)

        # Test the conversion
        self.assertEqual(item.code, "CBC001")
        self.assertEqual(item.name, "Complete Blood Count")
        self.assertEqual(item.care_type, ItemOrService.SERVICE)
        self.assertEqual(item.status, ItemStatus.ACTIVE)
        self.assertEqual(item.description, "Complete blood count test")
        self.assertEqual(item.external_id, "LAB123")
        self.assertEqual(item.item_type, self.service_type)

    def test_status_mapping_from_fhir(self):
        """Test status mapping from FHIR to internal"""
        test_cases = [
            ("active", ItemStatus.ACTIVE),
            ("inactive", ItemStatus.INACTIVE),
            ("entered-in-error", ItemStatus.ENTERED_IN_ERROR),
            ("draft", ItemStatus.DRAFT),
            ("unknown-status", ItemStatus.ACTIVE),  # Default fallback
        ]

        for fhir_status, expected_internal_status in test_cases:
            mapped_status = Item._map_fhir_status_to_internal(fhir_status)
            self.assertEqual(mapped_status, expected_internal_status)


class ItemConverterTestCase(TestCase):
    """Test the ItemConverter class"""

    def setUp(self):
        """Set up test data"""
        self.item_type = ItemType.objects.create(code="TEST01", name="Test Type")

        self.test_item = Item.objects.create(
            code="TEST100",
            name="Test Item",
            status=ItemStatus.ACTIVE,
            item_type=self.item_type,
            care_type=ItemOrService.ITEM,
            price=Decimal("10.00"),
            patient_category=1,
        )

        self.test_service = Item.objects.create(
            code="TESTSRV",
            name="Test Service",
            status=ItemStatus.ACTIVE,
            item_type=self.item_type,
            care_type=ItemOrService.SERVICE,
            price=Decimal("50.00"),
            patient_category=1,
        )

    def test_converter_to_fhir_item(self):
        """Test ItemConverter.to_fhir_obj with item"""
        fhir_resource = ItemConverter.to_fhir_obj(self.test_item)

        self.assertIsInstance(fhir_resource, Medication)
        self.assertEqual(fhir_resource.id, str(self.test_item.uuid))

    def test_converter_to_fhir_service(self):
        """Test ItemConverter.to_fhir_obj with service"""
        fhir_resource = ItemConverter.to_fhir_obj(self.test_service)

        self.assertIsInstance(fhir_resource, ActivityDefinition)
        self.assertEqual(fhir_resource.id, str(self.test_service.uuid))

    def test_converter_invalid_object_type(self):
        """Test ItemConverter with invalid object type"""
        with self.assertRaises(TypeError):
            ItemConverter.to_fhir_obj("not an item")

    def test_get_fhir_resource_type(self):
        """Test getting FHIR resource type"""
        self.assertEqual(
            ItemConverter.get_fhir_resource_type(self.test_item), "Medication"
        )
        self.assertEqual(
            ItemConverter.get_fhir_resource_type(self.test_service),
            "ActivityDefinition",
        )

    def test_bulk_conversion(self):
        """Test bulk conversion of items to FHIR"""
        items = [self.test_item, self.test_service]
        fhir_resources = ItemConverter.bulk_to_fhir(items)

        self.assertEqual(len(fhir_resources), 2)
        self.assertIsInstance(fhir_resources[0], Medication)
        self.assertIsInstance(fhir_resources[1], ActivityDefinition)

    def test_converter_validation(self):
        """Test FHIR resource validation"""
        # Test valid Medication
        medication = Medication()
        medication.status = "active"
        medication.code = CodeableConcept()

        self.assertTrue(ItemConverter.validate_fhir_resource(medication))

        # Test invalid Medication (missing status)
        invalid_medication = Medication()
        invalid_medication.code = CodeableConcept()

        with self.assertRaises(ValueError):
            ItemConverter.validate_fhir_resource(invalid_medication)

        # Test valid ActivityDefinition
        activity_def = ActivityDefinition()
        activity_def.status = "active"
        activity_def.kind = "ServiceRequest"

        self.assertTrue(ItemConverter.validate_fhir_resource(activity_def))

        # Test unsupported resource type
        with self.assertRaises(TypeError):
            ItemConverter.validate_fhir_resource("not a fhir resource")
