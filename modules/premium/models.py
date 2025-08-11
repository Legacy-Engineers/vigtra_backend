import uuid
from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from modules.core.models.openimis_core_models import UUIDModel
from modules.authentication.models import User
from modules.location.models import Location
from modules.contribution_plan.models import ContributionPlan
from modules.insurance_plan.models import InsurancePlan  # adjust import path
from modules.insurance_coverage.models import (
    Coverage,
)
from modules.organization.models import Organization


class PremiumStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    DUE = "due", "Due"
    PARTIALLY_PAID = "partial", "Partially Paid"
    PAID = "paid", "Paid"
    OVERDUE = "overdue", "Overdue"
    CANCELLED = "cancelled", "Cancelled"


class Premium(UUIDModel):
    """
    Represents a premium obligation (one billing item) for a coverage/policy.
    Designed to be compatible with FHIR billing/payment concepts (Coverage.costToBeneficiary,
    Invoice / PaymentNotice / PaymentReconciliation).
    """

    # core identification
    code = models.CharField(
        max_length=64, blank=True, null=True, help_text="Optional reference code"
    )
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    # links
    insurance_plan = models.ForeignKey(
        InsurancePlan,
        on_delete=models.PROTECT,
        related_name="premiums",
        blank=True,
        null=True,
        help_text="The plan this premium is associated with (product level)",
    )

    coverage = models.ForeignKey(
        Coverage,
        on_delete=models.PROTECT,
        related_name="premiums",
        blank=True,
        null=True,
        help_text="The specific coverage/policy instance this premium is for (preferred)",
    )

    contribution_plan = models.ForeignKey(
        ContributionPlan,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="premiums",
        help_text="Optional contribution plan that defines splitting / calculation rules",
    )

    # polymorphic payer (could be Organization, Patient/Insuree, Employer)
    payer_content_type = models.ForeignKey(
        ContentType, on_delete=models.SET_NULL, null=True, blank=True
    )
    payer_object_id = models.TextField(blank=True, null=True)
    payer = GenericForeignKey("payer_content_type", "payer_object_id")

    # who receives the premium (usually the insurer / organization)
    payee = models.ForeignKey(
        Organization,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="received_premiums",
    )

    # amounts & currency
    amount = models.DecimalField(
        max_digits=18, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))]
    )
    currency = models.CharField(
        max_length=3, default="NGN", help_text="ISO 4217 currency code"
    )
    paid_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    # schedule / timing
    due_date = models.DateField(help_text="When this premium installment is due")
    period_start = models.DateField(
        blank=True, null=True, help_text="Coverage start date for this premium period"
    )
    period_end = models.DateField(
        blank=True, null=True, help_text="Coverage end date for this premium period"
    )

    # frequency / recurrence (optional master reference, actual scheduling maintained elsewhere)
    frequency = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        help_text="e.g. M (monthly), A (annual) or free text",
    )
    is_recurring = models.BooleanField(default=False)

    # status / metadata
    status = models.CharField(
        max_length=20, choices=PremiumStatus.choices, default=PremiumStatus.DUE
    )
    grace_period_days = models.PositiveIntegerField(
        default=0, help_text="Days allowed after due_date before overdue"
    )
    invoice_reference = models.CharField(
        max_length=128, blank=True, null=True, help_text="Invoice or billing reference"
    )
    external_reference = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        help_text="External payment gateway reference",
    )

    # audit
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_premiums",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # optional location/context
    location = models.ForeignKey(
        Location, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        db_table = "tblPremiums"
        indexes = [
            models.Index(fields=["insurance_plan"], name="idx_premium_plan"),
            models.Index(fields=["coverage"], name="idx_premium_coverage"),
            models.Index(fields=["due_date"], name="idx_premium_due_date"),
            models.Index(fields=["status"], name="idx_premium_status"),
        ]

    def __str__(self):
        return f"Premium {self.uuid} ({self.amount} {self.currency})"

    @property
    def balance(self):
        return max(Decimal("0.00"), Decimal(self.amount) - Decimal(self.paid_amount))

    def mark_paid(self, amount: Decimal, external_ref: str = None, paid_date=None):
        """
        Record a payment against this premium.
        This should also create a Payment / Transaction record in your payments module.
        """
        from decimal import Decimal as D

        if amount <= D("0.00"):
            raise ValueError("Payment amount must be positive")
        self.paid_amount = D(str(self.paid_amount)) + D(str(amount))
        if self.paid_amount >= D(str(self.amount)):
            self.status = PremiumStatus.PAID
        else:
            self.status = PremiumStatus.PARTIALLY_PAID
        if external_ref:
            self.external_reference = external_ref
        if paid_date:
            # you could store last_paid_date if you add that field
            pass
        self.save(
            update_fields=["paid_amount", "status", "external_reference", "updated_at"]
        )
