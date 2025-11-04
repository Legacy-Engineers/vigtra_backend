from django.db import models
from modules.formal_sector.models import FormalSector
from django.utils.translation import gettext_lazy as _
import uuid


class FormalSectorUser(models.Model):
    """
    A user that is associated with a formal sector.
    """

    uuid = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    formal_sector = models.OneToOneField(
        FormalSector,
        on_delete=models.CASCADE,
        related_name="formal_sector_user",
        help_text=_ ("The formal sector associated with this user"),
    )

    def __str__(self):
        return f"{self.username} - {self.formal_sector.trade_name}"

    class Meta:
        db_table = "tblFormalSectorUsers"
        permissions = [
            ("can_create_formal_sector_user", "Can create formal sector user"),
            ("can_update_formal_sector_user", "Can update formal sector user"),
            ("can_delete_formal_sector_user", "Can delete formal sector user"),
            ("can_view_formal_sector_user", "Can view formal sector user"),
            ("can_generate_payment_reference", "Can generate payment reference"),
            ("can_create_contract", "Can create contract"),
            ("can_update_contract", "Can update contract"),
            ("can_delete_contract", "Can delete contract"),
            ("can_view_contract", "Can view contract"),
        ]
