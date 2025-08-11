from django.db import models
from modules.core.models.openimis_core_models import UUIDModel
from modules.insuree.models import Insuree, Family
from modules.location.models import HealthFacility
from modules.medical.models import Diagnosis, Item, Service
from modules.claim.utils import claim_code_generator
from modules.insurance_coverage.models import Coverage


class VisitType(models.TextChoices):
    EMERGENCY = "emergency", "Emergency"
    ROUTINE = "routine", "Routine"
    OTHER = "other", "Other"
    UNKNOWN = "unknown", "Unknown"
    ENCOUNTER = "encounter", "Encounter"


class ClaimStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    PENDING = "pending", "Pending"
    SUBMITTED = "submitted", "Submitted"
    REVIEWED = "reviewed", "Reviewed"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"


class ClaimType(models.TextChoices):
    INDIVIDUAL = "individual", "Individual"
    GROUP = "group", "Group"


class Claim(UUIDModel):
    code = models.CharField(max_length=50, unique=True, default=claim_code_generator)
    insuree = models.ForeignKey(
        Insuree,
        on_delete=models.PROTECT,
        related_name="claims",
        blank=True,
        null=True,
    )
    family = models.ForeignKey(
        Family,
        on_delete=models.PROTECT,
        related_name="claims",
        blank=True,
        null=True,
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
    claim_type = models.CharField(
        max_length=50, choices=ClaimType.choices, default=ClaimType.INDIVIDUAL
    )
    status = models.CharField(
        max_length=30,
        choices=ClaimStatus.choices,
        default=ClaimStatus.DRAFT,
    )
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    explanation = models.TextField(blank=True, null=True)

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

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    coverage = models.ForeignKey(
        Coverage,
        on_delete=models.PROTECT,
        related_name="claims",
        blank=True,
        null=True,
    )

    use = models.CharField(
        max_length=30,
        choices=[
            ("claim", "Claim"),
            ("preauthorization", "Pre-authorization"),
            ("predetermination", "Predetermination"),
        ],
        default="claim",
    )

    class Meta:
        db_table = "tblClaims"
        verbose_name = "Claim"
        verbose_name_plural = "Claims"

    def __str__(self):
        return f"Claim {self.code}"


class ClaimDetail(UUIDModel):
    """
    Represents a detailed grouping or service category within a claim.
    """

    claim = models.ForeignKey(
        Claim,
        on_delete=models.CASCADE,
        related_name="details",
        help_text="The claim this detail belongs to",
    )
    service_date = models.DateField(help_text="Date the service was provided")
    service_code = models.CharField(
        max_length=50, blank=True, null=True, help_text="Code for the service category"
    )
    description = models.TextField(
        blank=True, null=True, help_text="Description of the service or detail"
    )
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Total amount for this claim detail",
    )

    class Meta:
        db_table = "tblClaimDetails"
        verbose_name = "Claim Detail"
        verbose_name_plural = "Claim Details"

    def __str__(self):
        return f"ClaimDetail {self.id} for Claim {self.claim.code}"


class ClaimLineItem(UUIDModel):
    """
    Represents individual billed items (procedures, medications, etc.) within a Claim Detail.
    """

    claim_detail = models.ForeignKey(
        ClaimDetail,
        on_delete=models.CASCADE,
        related_name="line_items",
        help_text="The claim detail this line item belongs to",
    )
    item = models.ForeignKey(Item, on_delete=models.PROTECT, related_name="line_items")
    description = models.TextField(
        blank=True, null=True, help_text="Description of the item"
    )
    quantity = models.PositiveIntegerField(default=1, help_text="Quantity of the item")
    unit_price = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, help_text="Price per unit"
    )
    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Total price (quantity * unit price)",
    )

    class Meta:
        db_table = "tblClaimLineItems"
        verbose_name = "Claim Line Item"
        verbose_name_plural = "Claim Line Items"

    def __str__(self):
        return f"LineItem {self.item.code} for ClaimDetail {self.claim_detail.id}"


class ClaimServiceItem(UUIDModel):
    """
    Optional: A finer categorization or attributes of ClaimLineItem services (e.g., modifiers, sub-procedures).
    Use this if your domain needs it; otherwise, you may skip it.
    """

    claim_line_item = models.ForeignKey(
        ClaimLineItem,
        on_delete=models.CASCADE,
        related_name="service_items",
        help_text="The claim line item this service item belongs to",
    )
    service = models.ForeignKey(
        Service, on_delete=models.PROTECT, related_name="service_items"
    )
    description = models.TextField(
        blank=True, null=True, help_text="Description of the service item"
    )
    quantity = models.PositiveIntegerField(
        default=1, help_text="Quantity of the service item"
    )
    unit_price = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, help_text="Price per unit"
    )
    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Total price (quantity * unit price)",
    )

    class Meta:
        db_table = "tblClaimServiceItems"
        verbose_name = "Claim Service Item"
        verbose_name_plural = "Claim Service Items"

    def __str__(self):
        return f"ServiceItem {self.service.code} for ClaimLineItem {self.claim_line_item.id}"


class ClaimAttachment(UUIDModel):
    claim = models.ForeignKey(
        Claim,
        on_delete=models.PROTECT,
        related_name="attachments",
    )
    file = models.FileField(upload_to="claims/attachments/")
    description = models.TextField(
        blank=True, null=True, help_text="Description of the attachment"
    )

    class Meta:
        db_table = "tblClaimAttachments"
        verbose_name = "Claim Attachment"
        verbose_name_plural = "Claim Attachments"

    def __str__(self):
        return f"Attachment for claim {self.claim.code}"
