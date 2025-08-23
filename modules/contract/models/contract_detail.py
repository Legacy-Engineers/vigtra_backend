from modules.core.models.openimis_core_models import UUIDModel
from modules.contract.models.contract import Contract
from django.db import models


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
