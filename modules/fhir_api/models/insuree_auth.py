from django.db import models
import uuid


class InsureeUser(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    insuree = models.ForeignKey(
        "Insuree", on_delete=models.CASCADE, null=True, blank=True
    )
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)
    email = models.EmailField(max_length=254, unique=True)

    is_email_verified = models.BooleanField(default=False)

    class Meta:
        db_table = "tblInsureeUser"
