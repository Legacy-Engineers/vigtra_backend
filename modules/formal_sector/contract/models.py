from modules.core.models.openimis_core_models import UUIDModel
from modules.formal_sector.models import FormalSector
from django.db import models
from django.contrib.auth import get_user_model
from simple_history.models import HistoricalRecords

User = get_user_model()

CONTRACT_STATUS_CHOICES = [
    ("draft", "Draft"),
    ("active", "Active"),
    ("suspended", "Suspended"),
    ("terminated", "Terminated"),
    ("expired", "Expired"),
]


class Contract(UUIDModel):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=CONTRACT_STATUS_CHOICES, default="draft"
    )
    value = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10, default="USD")
    partner = models.CharField(
        max_length=255, help_text="Contracting party or organization"
    )
    formal_sector = models.ForeignKey(
        FormalSector,
        related_name="contracts",
        on_delete=models.CASCADE,
        help_text="Formal sector associated with the contract",
    )
    history = HistoricalRecords()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        related_name="created_contracts",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Contract"
        verbose_name_plural = "Contracts"
        db_table = "tblContracts"

    def __str__(self):
        return f"{self.code} - {self.name}"


class ContractDetail(UUIDModel):
    contract = models.ForeignKey(
        Contract, related_name="details", on_delete=models.CASCADE
    )
    item_description = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        db_table = "tblContractDetails"
        ordering = ["item_description"]
        verbose_name = "Contract Detail"
        verbose_name_plural = "Contract Details"

    def __str__(self):
        return f"{self.item_description} - {self.quantity} @ {self.unit_price}"
