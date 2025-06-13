from django.db import models
from modules.core.models.openimis_core_models import UUIDModel


class Product(UUIDModel):
    code = models.CharField(max_length=8, unique=True)
    name = models.CharField(max_length=100)
    insurance_period = models.PositiveIntegerField(
        help_text="Insurance period in months"
    )
    date_from = models.DateField()
    date_to = models.DateField()
    ceiling = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    deductible = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tblProducts"
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.code} - {self.name}"
