from django.db import models
from modules.core.models.openimis_core_models import UUIDModel
from modules.insuree.models import Insuree
from modules.location.models import HealthFacility
from modules.medical.models.diagnosis import Diagnosis
import uuid


class VisitType(models.TextChoices):
    EMERGENCY = "emergency", "Emergency"
    ROUTINE = "routine", "Routine"
    OTHER = "other", "Other"
    UNKNOWN = "unknown", "Unknown"
    ENCOUNTER = "encounter", "Encounter"


class ClaimStatus(models.TextChoices):
    SUBMITTED = "submitted", "Submitted"
    REVIEWED = "reviewed", "Reviewed"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"


def claim_code_generator():
    return "CLM-" + str(uuid.uuid4())[:8].upper()


class Claim(UUIDModel):
    code = models.CharField(max_length=50, unique=True, default=claim_code_generator)
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
    referred_health_facility = models.ForeignKey(
        HealthFacility,
        on_delete=models.PROTECT,
        related_name="referred_claims",
        blank=True,
        null=True,
    )
    claim_date = models.DateField()
    visit_type = models.CharField(
        max_length=50, choices=VisitType.choices, default=VisitType.UNKNOWN
    )

    status = models.CharField(
        max_length=30,
        choices=ClaimStatus.choices,
        default=ClaimStatus.SUBMITTED,
    )
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    explanation = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    diagnosis = models.ForeignKey(
        Diagnosis,
        on_delete=models.PROTECT,
        related_name="claims",
        blank=True,
        null=True,
    )

    secondary_diagnosis = models.ForeignKey(
        Diagnosis,
        on_delete=models.PROTECT,
        related_name="secondary_claims",
        blank=True,
        null=True,
    )

    third_diagnosis = models.ForeignKey(
        Diagnosis,
        on_delete=models.PROTECT,
        related_name="third_claims",
        blank=True,
        null=True,
    )

    fourth_diagnosis = models.ForeignKey(
        Diagnosis,
        on_delete=models.PROTECT,
        related_name="fourth_claims",
        blank=True,
        null=True,
    )

    other_diagnosis = models.ManyToManyField(
        Diagnosis,
        related_name="other_claims",
        blank=True,
    )

    class Meta:
        db_table = "tblClaims"
        verbose_name = "Claim"
        verbose_name_plural = "Claims"

    def __str__(self):
        return f"Claim {self.code}"


class ClaimItem(UUIDModel):
    pass


class ClaimAttachment(UUIDModel):
    claim = models.ForeignKey(
        Claim,
        on_delete=models.PROTECT,
        related_name="attachments",
    )

    class Meta:
        db_table = "tblClaimAttachments"
        verbose_name = "Claim Attachment"
        verbose_name_plural = "Claim Attachments"

    def __str__(self):
        return f"Attachment for claim {self.claim.code}"
