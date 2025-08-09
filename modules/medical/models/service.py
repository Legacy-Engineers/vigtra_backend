from django.db import models
from modules.core.models.openimis_core_models import UUIDModel


class PackageTypes(models.TextChoices):
    SINGLE = "S", "Single"
    PACKAGE = "P", "Package"
    COMBINATION = "C", "Combination"


class CareTypes(models.TextChoices):
    SERVICE = "S", "Service"
    PROCEDURE = "P", "Procedure"
    CONSULTATION = "C", "Consultation"


class ServiceCategory(UUIDModel):
    code = models.CharField(max_length=6)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        managed = True
        db_table = "tblServiceCategories"


class Service(UUIDModel):
    category = models.ForeignKey(
        ServiceCategory,
        on_delete=models.DO_NOTHING,
        related_name="services",
    )
    code = models.CharField(max_length=6)
    name = models.CharField(max_length=100)
    care_type = models.CharField(max_length=1, choices=CareTypes.choices)
    packagetype = models.CharField(
        choices=PackageTypes.choices, max_length=1, default=PackageTypes.SINGLE
    )
    manualPrice = models.BooleanField(default=False)
    level = models.CharField(max_length=1)
    price = models.DecimalField(max_digits=18, decimal_places=2)
    maximum_amount = models.DecimalField(
        max_digits=18, decimal_places=2, blank=True, null=True
    )
    care_type = models.CharField(max_length=1, choices=CareTypes.choices)
    frequency = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = "tblServices"
