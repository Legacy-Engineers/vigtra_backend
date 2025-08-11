from django.db import models
from django.utils.translation import gettext_lazy as _
from modules.insuree.models import Insuree
from modules.formal_sector.models import FormalSector
from modules.premium.models import Premium
from modules.insurance_coverage.models import Coverage
from modules.organization.models import Organization
import uuid


class Policy(models.Model):
    """
    Represents an insurance policy agreement between the insurer and the policyholder.
    FHIR Alignment:
      - Coverage.policyHolder
      - Coverage.payor
      - Coverage.subscriber
    """

    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    POLICY_STATUS = [
        ("active", _("Active")),
        ("cancelled", _("Cancelled")),
        ("draft", _("Draft")),
        ("entered-in-error", _("Entered in Error")),
        ("expired", _("Expired")),
    ]

    policy_number = models.CharField(
        max_length=50, unique=True, help_text="Unique policy identifier."
    )
    status = models.CharField(max_length=20, choices=POLICY_STATUS, default="active")

    policyholder = models.ForeignKey(
        FormalSector,
        on_delete=models.CASCADE,
        related_name="policies",
        help_text="Policyholder (organization or group purchasing the policy).",
    )

    insurer = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="issued_policies",
        help_text="The insurance organization issuing the policy.",
    )

    subscriber = models.ForeignKey(
        Insuree,
        on_delete=models.CASCADE,
        help_text="Primary insured person (if applicable).",
    )

    coverage = models.ManyToManyField(
        Coverage,
        help_text="Coverages provided under this policy.",
    )

    start_date = models.DateField()
    end_date = models.DateField()

    premium = models.ForeignKey(
        Premium,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Premium payment terms linked to this policy.",
    )

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Policy #{self.policy_number} - {self.policyholder}"

    class Meta:
        verbose_name_plural = "Policies"
