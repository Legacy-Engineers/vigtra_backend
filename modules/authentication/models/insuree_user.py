from django.db import models
from modules.insuree.models import Insuree
from django.utils.translation import gettext_lazy as _
import uuid


class InsureeUser(models.Model):
    """
    A user that is associated with an insuree.
    """

    uuid = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    insuree = models.OneToOneField(
        Insuree,
        on_delete=models.CASCADE,
        related_name="insuree_user",
        help_text=_("The insuree associated with this user"),
    )

    def __str__(self):
        return f"{self.username} - {self.insuree.name}"

    class Meta:
        db_table = "tblInsureeUsers"
        verbose_name = _("Insuree User")
        verbose_name_plural = _("Insuree Users")
