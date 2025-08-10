from rest_framework_api_key.models import AbstractAPIKey
from django.db import models
from modules.formal_sector.models import FormalSector


class FormalSectorAPIKey(AbstractAPIKey):
    formal_sector = models.ForeignKey(
        FormalSector,
        on_delete=models.PROTECT,
        related_name="api_keys",
    )

    class Meta:
        verbose_name = "Formal Sector API Key"
        verbose_name_plural = "Formal Sector API Keys"
        unique_together = ("key", "formal_sector")
        db_table = "tblFormalSectorAPIKeys"
        permissions = [
            ("can_create_contracts", "Can create contracts"),
        ]

    def __str__(self):
        return f"{self.key} - {self.formal_sector.name}"
