from django.db import models
from modules.core.models.openimis_core_models import UUIDModel
from simple_history.models import HistoricalRecords
from modules.medical.models.medical_dependencies import (
    CareType,
    MedicalPackage,
    PatientCategory,
)


class ItemOrService(models.TextChoices):
    ITEM = "item", "Item"
    SERVICE = "service", "Service"


class ItemType(UUIDModel):
    code = models.CharField(max_length=6)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.code} - {self.name}"


class ItemStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    INACTIVE = "inactive", "Inactive"
    ENTERED_IN_ERROR = "entered-in-error", "Entered in Error"
    DRAFT = "draft", "Draft"


class Item(UUIDModel):
    code = models.CharField(max_length=6, help_text="Unique identifier code")
    name = models.CharField(max_length=100, help_text="Display name")

    status = models.CharField(
        max_length=20,
        choices=ItemStatus.choices,
        default=ItemStatus.ACTIVE,
    )

    item_type = models.ForeignKey(ItemType, on_delete=models.PROTECT)
    care_type = models.ForeignKey(
        CareType,
        on_delete=models.PROTECT,
        related_name="items",
    )

    package = models.ForeignKey(
        MedicalPackage,
        on_delete=models.PROTECT,
        related_name="items",
        blank=True,
        null=True,
    )
    quantity = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        blank=True,
        null=True,
    )

    price = models.DecimalField(max_digits=18, decimal_places=2)
    maximum_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        blank=True,
        null=True,
    )

    frequency = models.SmallIntegerField(blank=True, null=True)
    patient_category = models.ForeignKey(
        PatientCategory,
        on_delete=models.PROTECT,
        related_name="items",
        default=15,
    )

    description = models.TextField(blank=True, null=True)

    external_id = models.CharField(max_length=100, blank=True, null=True)

    history = HistoricalRecords()

    class Meta:
        ordering = ["code", "name"]
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["status"]),
            models.Index(fields=["care_type"]),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"
