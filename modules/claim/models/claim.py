from django.db import models
from modules.core.models.openimis_core_models import UUIDModel
from modules.insuree.models import Insuree
from modules.location.models import HealthFacility


class Claim(UUIDModel):
    code = models.CharField(max_length=120, unique=True)
    insuree = models.ForeignKey(
        Insuree,
        on_delete=models.PROTECT,
        related_name="claims",
    )
    health_facility = models.ForeignKey(
        HealthFacility,
        on_delete=models.PROTECT,
        related_name="claims",
    )
    claim_date = models.DateField()
    visit_type = models.CharField(
        max_length=50, choices=[("emergency", "Emergency"), ("routine", "Routine")]
    )
    diagnosis = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=30,
        choices=[
            ("submitted", "Submitted"),
            ("reviewed", "Reviewed"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
        default="submitted",
    )
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    explanation = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tblClaims"
        verbose_name = "Claim"
        verbose_name_plural = "Claims"

    def __str__(self):
        return f"Claim {self.code}"
