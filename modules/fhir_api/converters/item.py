from fhir.resources.R4B.medication import Medication
from fhir.resources.R4B.activitydefinition import ActivityDefinition
from fhir.resources.R4B.codeableconcept import CodeableConcept
from fhir.resources.R4B.coding import Coding
from fhir.resources.R4B.identifier import Identifier
from fhir.resources.R4B.money import Money

from .base import BaseConverter
from modules.medical.models.item import Item, ItemOrService


class ItemConverter(BaseConverter):
    """
    Converter for Item model to/from FHIR resources.
    Items are converted to Medication resources.
    Services are converted to ActivityDefinition resources.
    """

    @classmethod
    def to_fhir_obj(cls, item_obj, reference_type=None):
        """
        Convert Item model instance to appropriate FHIR resource.

        Args:
            item_obj: Instance of Item model
            reference_type: Optional type hint for conversion

        Returns:
            Medication or ActivityDefinition resource based on care_type
        """
        if not isinstance(item_obj, Item):
            raise TypeError("Object must be an instance of Item model")

        if item_obj.care_type == ItemOrService.ITEM:
            return item_obj.to_fhir_medication()
        elif item_obj.care_type == ItemOrService.SERVICE:
            return item_obj.to_fhir_activity_definition()
        else:
            raise ValueError(f"Unknown care_type: {item_obj.care_type}")

    @classmethod
    def to_vigtra_obj(cls, fhir_obj, user=None):
        """
        Convert FHIR resource to Item model instance.

        Args:
            fhir_obj: FHIR Medication or ActivityDefinition resource
            user: User context (for audit purposes)

        Returns:
            Item model instance
        """
        if isinstance(fhir_obj, Medication):
            return Item.from_fhir_medication(fhir_obj)
        elif isinstance(fhir_obj, ActivityDefinition):
            return Item.from_fhir_activity_definition(fhir_obj)
        else:
            raise TypeError(
                f"Unsupported FHIR resource type: {type(fhir_obj)}. "
                "Expected Medication or ActivityDefinition."
            )

    @classmethod
    def get_fhir_resource_type(cls, item_obj):
        """
        Get the appropriate FHIR resource type for an Item.

        Args:
            item_obj: Instance of Item model

        Returns:
            String indicating FHIR resource type
        """
        if item_obj.care_type == ItemOrService.ITEM:
            return "Medication"
        elif item_obj.care_type == ItemOrService.SERVICE:
            return "ActivityDefinition"
        else:
            return "Unknown"

    @classmethod
    def validate_fhir_resource(cls, fhir_obj):
        """
        Validate FHIR resource before conversion.

        Args:
            fhir_obj: FHIR resource to validate

        Returns:
            Boolean indicating if resource is valid

        Raises:
            ValidationError: If resource is invalid
        """
        if isinstance(fhir_obj, Medication):
            # Validate required Medication fields
            if not fhir_obj.status:
                raise ValueError("Medication must have a status")
            if not fhir_obj.code:
                raise ValueError("Medication must have a code")
            return True

        elif isinstance(fhir_obj, ActivityDefinition):
            # Validate required ActivityDefinition fields
            if not fhir_obj.status:
                raise ValueError("ActivityDefinition must have a status")
            if not fhir_obj.kind:
                raise ValueError("ActivityDefinition must have a kind")
            return True

        else:
            raise TypeError(f"Unsupported resource type: {type(fhir_obj)}")

    @classmethod
    def bulk_to_fhir(cls, item_queryset):
        """
        Convert multiple Item instances to FHIR resources.

        Args:
            item_queryset: QuerySet or list of Item instances

        Returns:
            List of FHIR resources
        """
        fhir_resources = []

        for item in item_queryset:
            try:
                fhir_resource = cls.to_fhir_obj(item)
                fhir_resources.append(fhir_resource)
            except Exception as e:
                # Log error but continue processing
                print(f"Error converting item {item.code}: {e}")
                continue

        return fhir_resources

    @classmethod
    def bulk_from_fhir(cls, fhir_resources, user=None):
        """
        Convert multiple FHIR resources to Item instances.

        Args:
            fhir_resources: List of FHIR Medication/ActivityDefinition resources
            user: User context for audit purposes

        Returns:
            List of Item instances
        """
        items = []

        for fhir_resource in fhir_resources:
            try:
                cls.validate_fhir_resource(fhir_resource)
                item = cls.to_vigtra_obj(fhir_resource, user)
                items.append(item)
            except Exception as e:
                # Log error but continue processing
                resource_id = getattr(fhir_resource, "id", "unknown")
                print(f"Error converting FHIR resource {resource_id}: {e}")
                continue

        return items
