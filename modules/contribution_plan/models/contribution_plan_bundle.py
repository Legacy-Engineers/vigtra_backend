import uuid
import datetime
from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db.models import Q, F
from modules.core.models import abstract_models as core_models
from modules.authentication.models import User
from modules.location import models as location_models
from django_lifecycle import LifecycleModel


class ContributionPlanBundleType(models.TextChoices):
    """Types of contribution plan bundles."""

    STANDARD = "STD", _("Standard Bundle")
    PREMIUM = "PRM", _("Premium Bundle")
    BASIC = "BSC", _("Basic Bundle")
    COMPREHENSIVE = "CMP", _("Comprehensive Bundle")
    CUSTOM = "CST", _("Custom Bundle")


class BundlePricingStrategy(models.TextChoices):
    """How bundle pricing is calculated."""

    SUM_OF_PLANS = "SUM", _("Sum of Individual Plans")
    DISCOUNTED_SUM = "DISC", _("Discounted Sum")
    FIXED_PRICE = "FIXED", _("Fixed Bundle Price")
    WEIGHTED_AVERAGE = "WAVG", _("Weighted Average")
    TIERED_PRICING = "TIER", _("Tiered Pricing")


class BundleStatus(models.TextChoices):
    """Status of contribution plan bundles."""

    DRAFT = "DR", _("Draft")
    ACTIVE = "AC", _("Active")
    SUSPENDED = "SU", _("Suspended")
    EXPIRED = "EX", _("Expired")
    CANCELLED = "CA", _("Cancelled")


class ContributionPlanBundleManager(models.Manager):
    """Custom manager for ContributionPlanBundle model."""

    def active(self):
        """Return only active bundles."""
        return self.filter(
            status=BundleStatus.ACTIVE,
            validity_from__lte=datetime.date.today(),
            validity_to__gte=datetime.date.today(),
        )

    def for_location(self, location):
        """Return bundles available for a specific location."""
        return self.filter(Q(locations__isnull=True) | Q(locations=location)).distinct()

    def by_type(self, bundle_type):
        """Filter by bundle type."""
        return self.filter(bundle_type=bundle_type)

    def with_plan(self, contribution_plan):
        """Return bundles containing a specific plan."""
        return self.filter(bundle_items__contribution_plan=contribution_plan).distinct()

    def affordable_for_budget(self, budget_amount):
        """Return bundles within budget range."""
        return self.filter(
            Q(max_bundle_price__isnull=True) | Q(max_bundle_price__lte=budget_amount),
            Q(min_bundle_price__isnull=True) | Q(min_bundle_price__gte=budget_amount),
        )


class ContributionPlanBundle(
    core_models.VersionedModel, core_models.ExtendableModel, LifecycleModel
):
    """
    Bundle model that groups multiple contribution plans together.
    Allows for package deals, discounts, and combined offerings.
    """

    id = models.AutoField(db_column="ContributionPlanBundleID", primary_key=True)
    uuid = models.UUIDField(
        db_column="ContributionPlanBundleUUID",
        default=uuid.uuid4,
        unique=True,
        editable=False,
        help_text=_("Unique identifier for the bundle"),
    )

    # Basic Bundle Information
    code = models.CharField(
        db_column="BundleCode",
        max_length=20,
        unique=True,
        help_text=_("Unique code for the bundle"),
    )

    name = models.CharField(
        db_column="BundleName", max_length=100, help_text=_("Name of the bundle")
    )

    description = models.TextField(
        db_column="Description",
        blank=True,
        null=True,
        help_text=_("Detailed description of the bundle"),
    )

    bundle_type = models.CharField(
        db_column="BundleType",
        max_length=3,
        choices=ContributionPlanBundleType.choices,
        default=ContributionPlanBundleType.STANDARD,
        help_text=_("Type of bundle"),
    )

    status = models.CharField(
        db_column="Status",
        max_length=2,
        choices=BundleStatus.choices,
        default=BundleStatus.DRAFT,
        help_text=_("Current status of the bundle"),
    )

    # Pricing Strategy
    pricing_strategy = models.CharField(
        db_column="PricingStrategy",
        max_length=5,
        choices=BundlePricingStrategy.choices,
        default=BundlePricingStrategy.SUM_OF_PLANS,
        help_text=_("How bundle price is calculated"),
    )

    fixed_bundle_price = models.DecimalField(
        db_column="FixedBundlePrice",
        max_digits=18,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text=_("Fixed price for the entire bundle"),
    )

    discount_percentage = models.DecimalField(
        db_column="DiscountPercentage",
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[
            MinValueValidator(Decimal("0.00")),
            MaxValueValidator(Decimal("100.00")),
        ],
        help_text=_("Discount percentage applied to sum of plans"),
    )

    discount_amount = models.DecimalField(
        db_column="DiscountAmount",
        max_digits=18,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text=_("Fixed discount amount applied to bundle"),
    )

    # Price Limits
    min_bundle_price = models.DecimalField(
        db_column="MinBundlePrice",
        max_digits=18,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text=_("Minimum price for the bundle"),
    )

    max_bundle_price = models.DecimalField(
        db_column="MaxBundlePrice",
        max_digits=18,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text=_("Maximum price for the bundle"),
    )

    # Bundle Configuration
    is_mandatory_complete = models.BooleanField(
        db_column="IsMandatoryComplete",
        default=False,
        help_text=_("Whether all plans in bundle must be selected"),
    )

    min_plans_required = models.PositiveIntegerField(
        db_column="MinPlansRequired",
        default=1,
        help_text=_("Minimum number of plans that must be selected from bundle"),
    )

    max_plans_allowed = models.PositiveIntegerField(
        db_column="MaxPlansAllowed",
        blank=True,
        null=True,
        help_text=_("Maximum number of plans that can be selected from bundle"),
    )

    # Eligibility and Availability
    min_family_size = models.PositiveIntegerField(
        db_column="MinFamilySize",
        blank=True,
        null=True,
        help_text=_("Minimum family size for bundle eligibility"),
    )

    max_family_size = models.PositiveIntegerField(
        db_column="MaxFamilySize",
        blank=True,
        null=True,
        help_text=_("Maximum family size for bundle eligibility"),
    )

    requires_all_adults = models.BooleanField(
        db_column="RequiresAllAdults",
        default=False,
        help_text=_("Whether bundle requires all family members to be adults"),
    )

    # Geographic Coverage
    locations = models.ManyToManyField(
        location_models.Location,
        blank=True,
        related_name="contribution_plan_bundles",
        help_text=_("Locations where this bundle is available"),
    )

    # Bundle Lifecycle
    validity_from = models.DateTimeField(
        db_column="ValidityFrom",
        default=datetime.datetime.now,
        help_text=_("Date when the bundle becomes effective"),
    )

    validity_to = models.DateTimeField(
        db_column="ValidityTo",
        blank=True,
        null=True,
        help_text=_("Date when the bundle expires"),
    )

    # Marketing and Display
    display_order = models.PositiveIntegerField(
        db_column="DisplayOrder", default=0, help_text=_("Order for displaying bundles")
    )

    is_featured = models.BooleanField(
        db_column="IsFeatured",
        default=False,
        help_text=_("Whether this bundle is featured/promoted"),
    )

    marketing_description = models.TextField(
        db_column="MarketingDescription",
        blank=True,
        null=True,
        help_text=_("Marketing description for public display"),
    )

    # Terms and Conditions
    terms_and_conditions = models.TextField(
        db_column="TermsAndConditions",
        blank=True,
        null=True,
        help_text=_("Terms and conditions for this bundle"),
    )

    # Administrative fields
    created_date = models.DateTimeField(
        auto_now_add=True, help_text=_("Date bundle was created")
    )

    last_modified = models.DateTimeField(
        auto_now=True, help_text=_("Date bundle was last modified")
    )

    notes = models.TextField(
        blank=True, null=True, help_text=_("Administrative notes about the bundle")
    )

    audit_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        db_column="AuditUser",
        null=True,
        blank=True,
        help_text=_("User who last modified the bundle"),
    )

    objects = ContributionPlanBundleManager()

    def clean(self):
        """Custom validation for ContributionPlanBundle model."""
        super().clean()

        # Validate date ranges
        if self.validity_to and self.validity_from:
            if self.validity_to <= self.validity_from:
                raise ValidationError(
                    {
                        "validity_to": _(
                            "Validity to date must be after validity from date"
                        )
                    }
                )

        # Validate family size ranges
        if self.min_family_size and self.max_family_size:
            if self.min_family_size >= self.max_family_size:
                raise ValidationError(
                    {
                        "max_family_size": _(
                            "Maximum family size must be greater than minimum"
                        )
                    }
                )

        # Validate price limits
        if self.min_bundle_price and self.max_bundle_price:
            if self.min_bundle_price >= self.max_bundle_price:
                raise ValidationError(
                    {
                        "max_bundle_price": _(
                            "Maximum price must be greater than minimum price"
                        )
                    }
                )

        # Validate plan limits
        if self.max_plans_allowed and self.min_plans_required:
            if self.min_plans_required > self.max_plans_allowed:
                raise ValidationError(
                    {
                        "max_plans_allowed": _(
                            "Maximum plans must be greater than or equal to minimum plans"
                        )
                    }
                )

        # Validate pricing strategy requirements
        if self.pricing_strategy == BundlePricingStrategy.FIXED_PRICE:
            if not self.fixed_bundle_price:
                raise ValidationError(
                    {
                        "fixed_bundle_price": _(
                            "Fixed bundle price is required for fixed pricing strategy"
                        )
                    }
                )

    def calculate_bundle_price(self, selected_plans=None, **kwargs):
        """
        Calculate bundle price based on pricing strategy.

        Args:
            selected_plans: List of selected contribution plans
            **kwargs: Additional parameters for calculation

        Returns:
            Decimal: Calculated bundle price
        """
        if selected_plans is None:
            # Use all mandatory plans or all plans if mandatory complete
            if self.is_mandatory_complete:
                selected_plans = [
                    item.contribution_plan for item in self.bundle_items.all()
                ]
            else:
                selected_plans = [
                    item.contribution_plan
                    for item in self.bundle_items.filter(is_mandatory=True)
                ]

        if not selected_plans:
            return Decimal("0.00")

        if self.pricing_strategy == BundlePricingStrategy.FIXED_PRICE:
            price = self.fixed_bundle_price or Decimal("0.00")

        elif self.pricing_strategy == BundlePricingStrategy.SUM_OF_PLANS:
            # Sum all individual plan prices
            total = sum(
                plan.calculate_contribution(**kwargs) for plan in selected_plans
            )
            price = total

        elif self.pricing_strategy == BundlePricingStrategy.DISCOUNTED_SUM:
            # Apply discount to sum of plans
            total = sum(
                plan.calculate_contribution(**kwargs) for plan in selected_plans
            )

            # Apply percentage discount
            if self.discount_percentage > 0:
                discount = total * (self.discount_percentage / 100)
                total -= discount

            # Apply fixed discount
            if self.discount_amount > 0:
                total -= self.discount_amount

            price = max(total, Decimal("0.00"))

        elif self.pricing_strategy == BundlePricingStrategy.WEIGHTED_AVERAGE:
            # Calculate weighted average based on bundle item weights
            total_weighted = Decimal("0.00")
            total_weight = Decimal("0.00")

            for plan in selected_plans:
                try:
                    bundle_item = self.bundle_items.get(contribution_plan=plan)
                    plan_price = plan.calculate_contribution(**kwargs)
                    weight = bundle_item.weight or Decimal("1.00")

                    total_weighted += plan_price * weight
                    total_weight += weight
                except Exception:
                    continue

            if total_weight > 0:
                price = total_weighted / total_weight
            else:
                price = Decimal("0.00")

        elif self.pricing_strategy == BundlePricingStrategy.TIERED_PRICING:
            # Use tiered pricing based on number of plans selected
            plan_count = len(selected_plans)
            tier = (
                self.bundle_tiers.filter(min_plans__lte=plan_count)
                .order_by("-min_plans")
                .first()
            )

            if tier:
                if tier.is_percentage_discount:
                    total = sum(
                        plan.calculate_contribution(**kwargs) for plan in selected_plans
                    )
                    price = (
                        total
                        * (Decimal("100.00") - tier.discount_percentage)
                        / Decimal("100.00")
                    )
                else:
                    price = tier.tier_price
            else:
                # Fallback to sum of plans
                price = sum(
                    plan.calculate_contribution(**kwargs) for plan in selected_plans
                )
        else:
            # Default to sum of plans
            price = sum(
                plan.calculate_contribution(**kwargs) for plan in selected_plans
            )

        # Apply min/max constraints
        if self.min_bundle_price and price < self.min_bundle_price:
            price = self.min_bundle_price

        if self.max_bundle_price and price > self.max_bundle_price:
            price = self.max_bundle_price

        return price.quantize(Decimal("0.01"))

    def get_available_plans(self):
        """Get all available contribution plans in this bundle."""
        return [
            item.contribution_plan
            for item in self.bundle_items.filter(
                contribution_plan__status="AC"  # Active plans only
            )
        ]

    def get_mandatory_plans(self):
        """Get mandatory contribution plans in this bundle."""
        return [
            item.contribution_plan
            for item in self.bundle_items.filter(
                is_mandatory=True, contribution_plan__status="AC"
            )
        ]

    def is_valid_plan_selection(self, selected_plans):
        """
        Validate if selected plans meet bundle requirements.

        Args:
            selected_plans: List of selected contribution plans

        Returns:
            tuple: (is_valid, error_message)
        """
        plan_count = len(selected_plans)

        # Check minimum plans required
        if plan_count < self.min_plans_required:
            return False, f"Minimum {self.min_plans_required} plans required"

        # Check maximum plans allowed
        if self.max_plans_allowed and plan_count > self.max_plans_allowed:
            return False, f"Maximum {self.max_plans_allowed} plans allowed"

        # Check if mandatory complete
        if self.is_mandatory_complete:
            available_plans = self.get_available_plans()
            if len(selected_plans) != len(available_plans):
                return False, "All plans in bundle must be selected"

        # Check mandatory plans are included
        mandatory_plans = self.get_mandatory_plans()
        for mandatory_plan in mandatory_plans:
            if mandatory_plan not in selected_plans:
                return False, f"Mandatory plan '{mandatory_plan.name}' must be included"

        # Check all selected plans are in bundle
        available_plans = self.get_available_plans()
        for plan in selected_plans:
            if plan not in available_plans:
                return False, f"Plan '{plan.name}' is not available in this bundle"

        return True, "Valid selection"

    def is_eligible_for_family_size(self, family_size):
        """Check if family size meets bundle requirements."""
        if self.min_family_size and family_size < self.min_family_size:
            return False
        if self.max_family_size and family_size > self.max_family_size:
            return False
        return True

    def is_available_in_location(self, location):
        """Check if bundle is available in given location."""
        if not self.locations.exists():
            return True  # Available everywhere if no locations specified
        return self.locations.filter(pk=location.pk).exists()

    def get_savings_amount(self, selected_plans=None, **kwargs):
        """Calculate savings compared to individual plan prices."""
        if selected_plans is None:
            selected_plans = self.get_available_plans()

        individual_total = sum(
            plan.calculate_contribution(**kwargs) for plan in selected_plans
        )
        bundle_price = self.calculate_bundle_price(selected_plans, **kwargs)

        return max(individual_total - bundle_price, Decimal("0.00"))

    def get_savings_percentage(self, selected_plans=None, **kwargs):
        """Calculate savings percentage compared to individual plans."""
        if selected_plans is None:
            selected_plans = self.get_available_plans()

        individual_total = sum(
            plan.calculate_contribution(**kwargs) for plan in selected_plans
        )
        if individual_total == 0:
            return Decimal("0.00")

        savings = self.get_savings_amount(selected_plans, **kwargs)
        return (savings / individual_total * 100).quantize(Decimal("0.01"))

    @property
    def is_active(self):
        """Check if bundle is currently active."""
        today = datetime.date.today()
        return (
            self.status == BundleStatus.ACTIVE
            and self.validity_from.date() <= today
            and (self.validity_to is None or self.validity_to.date() >= today)
        )

    @property
    def plan_count(self):
        """Get number of plans in bundle."""
        return self.bundle_items.count()

    @property
    def mandatory_plan_count(self):
        """Get number of mandatory plans in bundle."""
        return self.bundle_items.filter(is_mandatory=True).count()

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        managed = True
        db_table = "tblContributionPlanBundles"
        verbose_name = _("Contribution Plan Bundle")
        verbose_name_plural = _("Contribution Plan Bundles")
        ordering = ["display_order", "code", "name"]
        indexes = [
            models.Index(fields=["code"], name="idx_bundle_code"),
            models.Index(fields=["status"], name="idx_bundle_status"),
            models.Index(fields=["bundle_type"], name="idx_bundle_type"),
            models.Index(fields=["validity_from"], name="idx_bundle_validity_from"),
            models.Index(fields=["validity_to"], name="idx_bundle_validity_to"),
            models.Index(fields=["pricing_strategy"], name="idx_bundle_pricing"),
            models.Index(fields=["display_order"], name="idx_bundle_display_order"),
            models.Index(fields=["is_featured"], name="idx_bundle_featured"),
            models.Index(
                fields=["validity_from", "validity_to"], name="idx_bundle_validity"
            ),
        ]
        constraints = [
            models.UniqueConstraint(fields=["code"], name="unique_bundle_code"),
            models.CheckConstraint(
                check=Q(validity_from__lte=F("validity_to"))
                | Q(validity_to__isnull=True),
                name="chk_bundle_dates",
            ),
            models.CheckConstraint(
                check=Q(min_family_size__lt=F("max_family_size"))
                | Q(max_family_size__isnull=True)
                | Q(min_family_size__isnull=True),
                name="chk_bundle_family_sizes",
            ),
            models.CheckConstraint(
                check=Q(min_bundle_price__lt=F("max_bundle_price"))
                | Q(max_bundle_price__isnull=True)
                | Q(min_bundle_price__isnull=True),
                name="chk_bundle_prices",
            ),
        ]


class ContributionPlanBundleItem(core_models.VersionedModel):
    """
    Individual items within a contribution plan bundle.
    Links specific contribution plans to bundles with configuration.
    """

    id = models.AutoField(primary_key=True)

    bundle = models.ForeignKey(
        ContributionPlanBundle,
        on_delete=models.CASCADE,
        related_name="bundle_items",
        help_text=_("Bundle this item belongs to"),
    )

    contribution_plan = models.ForeignKey(
        "ContributionPlan",  # Forward reference to avoid circular import
        on_delete=models.CASCADE,
        related_name="bundle_memberships",
        help_text=_("Contribution plan included in bundle"),
    )

    is_mandatory = models.BooleanField(
        default=False, help_text=_("Whether this plan is mandatory in the bundle")
    )

    weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("1.00"),
        validators=[MinValueValidator(Decimal("0.01"))],
        help_text=_("Weight for weighted average calculations"),
    )

    custom_price = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text=_("Custom price for this plan within the bundle"),
    )

    display_order = models.PositiveIntegerField(
        default=0, help_text=_("Order for displaying this item in the bundle")
    )

    description_override = models.TextField(
        blank=True,
        null=True,
        help_text=_("Custom description for this plan within the bundle"),
    )

    def clean(self):
        """Validate bundle item configuration."""
        super().clean()

        # Validate that plan and bundle are active/compatible
        if self.contribution_plan and self.bundle:
            # Add any business logic validation here
            pass

    def __str__(self):
        mandatory_str = " (Mandatory)" if self.is_mandatory else ""
        return f"{self.bundle.code} -> {self.contribution_plan.code}{mandatory_str}"

    class Meta:
        managed = True
        db_table = "tblContributionPlanBundleItems"
        verbose_name = _("Bundle Item")
        verbose_name_plural = _("Bundle Items")
        ordering = ["bundle", "display_order", "contribution_plan__code"]
        indexes = [
            models.Index(fields=["bundle"], name="idx_bundle_item_bundle"),
            models.Index(fields=["contribution_plan"], name="idx_bundle_item_plan"),
            models.Index(fields=["is_mandatory"], name="idx_bundle_item_mandatory"),
            models.Index(fields=["display_order"], name="idx_bundle_item_order"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["bundle", "contribution_plan"], name="unique_bundle_plan"
            ),
        ]


class ContributionPlanBundleTier(core_models.VersionedModel):
    """
    Tiered pricing for bundles based on number of plans selected.
    """

    id = models.AutoField(primary_key=True)

    bundle = models.ForeignKey(
        ContributionPlanBundle,
        on_delete=models.CASCADE,
        related_name="bundle_tiers",
        help_text=_("Bundle this tier belongs to"),
    )

    tier_name = models.CharField(
        max_length=50, help_text=_("Name of this pricing tier")
    )

    min_plans = models.PositiveIntegerField(
        help_text=_("Minimum number of plans for this tier")
    )

    max_plans = models.PositiveIntegerField(
        blank=True, null=True, help_text=_("Maximum number of plans for this tier")
    )

    tier_price = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text=_("Fixed price for this tier"),
    )

    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[
            MinValueValidator(Decimal("0.00")),
            MaxValueValidator(Decimal("100.00")),
        ],
        help_text=_("Discount percentage for this tier"),
    )

    is_percentage_discount = models.BooleanField(
        default=True,
        help_text=_("Whether to use percentage discount or fixed tier price"),
    )

    def clean(self):
        """Validate tier configuration."""
        super().clean()

        if self.max_plans and self.min_plans >= self.max_plans:
            raise ValidationError(
                {"max_plans": _("Maximum plans must be greater than minimum plans")}
            )

        if not self.is_percentage_discount and not self.tier_price:
            raise ValidationError(
                {
                    "tier_price": _(
                        "Tier price is required when not using percentage discount"
                    )
                }
            )

    def __str__(self):
        max_plans_str = str(self.max_plans) if self.max_plans else "∞"
        return f"{self.tier_name}: {self.min_plans} - {max_plans_str} plans"

    class Meta:
        managed = True
        db_table = "tblContributionPlanBundleTiers"
        verbose_name = _("Bundle Tier")
        verbose_name_plural = _("Bundle Tiers")
        ordering = ["bundle", "min_plans"]
        indexes = [
            models.Index(fields=["bundle"], name="idx_tier_bundle"),
            models.Index(fields=["min_plans"], name="idx_tier_min_plans"),
            models.Index(fields=["max_plans"], name="idx_tier_max_plans"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["bundle", "min_plans"], name="unique_bundle_tier_min_plans"
            ),
        ]


# Usage examples:
"""
# Create a bundle with multiple plans
bundle = ContributionPlanBundle.objects.create(
    code="FAMILY_BASIC",
    name="Basic Family Package",
    bundle_type=ContributionPlanBundleType.BASIC,
    pricing_strategy=BundlePricingStrategy.DISCOUNTED_SUM,
    discount_percentage=Decimal('15.00'),
    min_plans_required=2,
    status=BundleStatus.ACTIVE
)

# Add plans to bundle
ContributionPlanBundleItem.objects.create(
    bundle=bundle,
    contribution_plan=health_plan,
    is_mandatory=True,
    weight=Decimal('2.00')
)

ContributionPlanBundleItem.objects.create(
    bundle=bundle,
    contribution_plan=dental_plan,
    is_mandatory=False,
    weight=Decimal('1.00')
)

# Create tiered pricing
ContributionPlanBundleTier.objects.create(
    bundle=bundle,
    tier_name="2 Plans",
    min_plans=2,
    max_plans=2,
    discount_percentage=Decimal('10.00'),
    is_percentage_discount=True
)

ContributionPlanBundleTier.objects.create(
    bundle=bundle,
    tier_name="3+ Plans",
    min_plans=3,
    discount_percentage=Decimal('20.00'),
    is_percentage_discount=True
)

# Calculate bundle price
selected_plans = [health_plan, dental_plan]
bundle_price = bundle.calculate_bundle_price(
    selected_plans=selected_plans,
    income=Decimal('5000.00'),
    family_size=4
)

# Validate selection
is_valid, message = bundle.is_valid_plan_selection(selected_plans)

# Get savings
savings = bundle.get_savings_amount(selected_plans)
savings_pct = bundle.get_savings_percentage(selected_plans)
"""
