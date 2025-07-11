import uuid
import datetime
from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db.models import Q, F
from modules.core.models import openimis_core_models as core_models
from modules.authentication.models import User
from modules.location import models as location_models
from django_lifecycle import LifecycleModel, hook, BEFORE_SAVE


class ContributionPlanType(models.TextChoices):
    """Types of contribution plans."""
    INDIVIDUAL = "IND", _("Individual")
    FAMILY = "FAM", _("Family")
    GROUP = "GRP", _("Group")
    COMMUNITY = "COM", _("Community")


class ContributionCalculationType(models.TextChoices):
    """How contributions are calculated."""
    FIXED_AMOUNT = "FIXED", _("Fixed Amount")
    PERCENTAGE_INCOME = "PERC_INC", _("Percentage of Income")
    PERCENTAGE_PREMIUM = "PERC_PREM", _("Percentage of Premium")
    TIERED_INCOME = "TIERED", _("Tiered by Income")
    CUSTOM_FORMULA = "CUSTOM", _("Custom Formula")


class ContributionFrequency(models.TextChoices):
    """Frequency of contributions."""
    MONTHLY = "M", _("Monthly")
    QUARTERLY = "Q", _("Quarterly")
    SEMI_ANNUAL = "SA", _("Semi-Annual")
    ANNUAL = "A", _("Annual")
    ONE_TIME = "OT", _("One Time")


class ContributionPlanStatus(models.TextChoices):
    """Status of contribution plans."""
    DRAFT = "DR", _("Draft")
    ACTIVE = "AC", _("Active")
    SUSPENDED = "SU", _("Suspended")
    EXPIRED = "EX", _("Expired")
    CANCELLED = "CA", _("Cancelled")


class ContributionPlanManager(models.Manager):
    """Custom manager for ContributionPlan model."""
    
    def active(self):
        """Return only active contribution plans."""
        return self.filter(
            status=ContributionPlanStatus.ACTIVE,
            validity_from__lte=datetime.date.today(),
            validity_to__gte=datetime.date.today()
        )
    
    def for_location(self, location):
        """Return plans available for a specific location."""
        return self.filter(
            Q(locations__isnull=True) | Q(locations=location)
        ).distinct()
    
    def by_type(self, plan_type):
        """Filter by plan type."""
        return self.filter(plan_type=plan_type)
    
    def affordable_for_income(self, income_amount):
        """Return plans affordable for given income."""
        return self.filter(
            Q(max_income_threshold__isnull=True) | 
            Q(max_income_threshold__gte=income_amount),
            Q(min_income_threshold__isnull=True) | 
            Q(min_income_threshold__lte=income_amount)
        )


class ContributionPlan(core_models.VersionedModel, core_models.ExtendableModel, LifecycleModel):
    """
    Comprehensive contribution plan model for OpenIMIS system.
    Defines how contributions are calculated and collected.
    """
    
    id = models.AutoField(db_column="ContributionPlanID", primary_key=True)
    uuid = models.UUIDField(
        db_column="ContributionPlanUUID",
        default=uuid.uuid4,
        unique=True,
        editable=False,
        help_text=_("Unique identifier for the contribution plan")
    )
    
    # Basic Plan Information
    code = models.CharField(
        db_column="ContributionPlanCode",
        max_length=20,
        unique=True,
        help_text=_("Unique code for the contribution plan")
    )
    
    name = models.CharField(
        db_column="ContributionPlanName",
        max_length=100,
        help_text=_("Name of the contribution plan")
    )
    
    description = models.TextField(
        db_column="Description",
        blank=True,
        null=True,
        help_text=_("Detailed description of the plan")
    )
    
    plan_type = models.CharField(
        db_column="PlanType",
        max_length=3,
        choices=ContributionPlanType.choices,
        default=ContributionPlanType.FAMILY,
        help_text=_("Type of contribution plan")
    )
    
    status = models.CharField(
        db_column="Status",
        max_length=2,
        choices=ContributionPlanStatus.choices,
        default=ContributionPlanStatus.DRAFT,
        help_text=_("Current status of the plan")
    )
    
    # Calculation Configuration
    calculation_type = models.CharField(
        db_column="CalculationType",
        max_length=10,
        choices=ContributionCalculationType.choices,
        default=ContributionCalculationType.FIXED_AMOUNT,
        help_text=_("How contributions are calculated")
    )
    
    base_amount = models.DecimalField(
        db_column="BaseAmount",
        max_digits=18,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text=_("Base contribution amount")
    )
    
    percentage_rate = models.DecimalField(
        db_column="PercentageRate",
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))],
        help_text=_("Percentage rate for percentage-based calculations")
    )
    
    min_contribution = models.DecimalField(
        db_column="MinContribution",
        max_digits=18,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text=_("Minimum contribution amount")
    )
    
    max_contribution = models.DecimalField(
        db_column="MaxContribution",
        max_digits=18,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text=_("Maximum contribution amount")
    )
    
    # Frequency and Timing
    contribution_frequency = models.CharField(
        db_column="ContributionFrequency",
        max_length=2,
        choices=ContributionFrequency.choices,
        default=ContributionFrequency.MONTHLY,
        help_text=_("How often contributions are due")
    )
    
    grace_period_days = models.PositiveIntegerField(
        db_column="GracePeriodDays",
        default=30,
        help_text=_("Grace period in days for late payments")
    )
    
    # Eligibility Criteria
    min_age = models.PositiveIntegerField(
        db_column="MinAge",
        blank=True,
        null=True,
        help_text=_("Minimum age for eligibility")
    )
    
    max_age = models.PositiveIntegerField(
        db_column="MaxAge",
        blank=True,
        null=True,
        help_text=_("Maximum age for eligibility")
    )
    
    min_income_threshold = models.DecimalField(
        db_column="MinIncomeThreshold",
        max_digits=18,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text=_("Minimum income threshold for eligibility")
    )
    
    max_income_threshold = models.DecimalField(
        db_column="MaxIncomeThreshold",
        max_digits=18,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text=_("Maximum income threshold for eligibility")
    )
    
    # Geographic Coverage
    locations = models.ManyToManyField(
        location_models.Location,
        blank=True,
        related_name="contribution_plans",
        help_text=_("Locations where this plan is available (empty = all locations)")
    )
    
    # Plan Lifecycle
    effective_date = models.DateField(
        db_column="EffectiveDate",
        default=datetime.date.today,
        help_text=_("Date when the plan becomes effective")
    )
    
    expiry_date = models.DateField(
        db_column="ExpiryDate",
        blank=True,
        null=True,
        help_text=_("Date when the plan expires")
    )
    
    # Financial Configuration
    currency = models.CharField(
        db_column="Currency",
        max_length=3,
        default="USD",
        help_text=_("Currency for contributions (ISO 4217 code)")
    )
    
    # Additional Settings
    is_mandatory = models.BooleanField(
        db_column="IsMandatory",
        default=False,
        help_text=_("Whether participation in this plan is mandatory")
    )
    
    allows_partial_payment = models.BooleanField(
        db_column="AllowsPartialPayment",
        default=False,
        help_text=_("Whether partial payments are allowed")
    )
    
    auto_renew = models.BooleanField(
        db_column="AutoRenew",
        default=True,
        help_text=_("Whether contributions auto-renew")
    )
    
    # Formula for custom calculations
    custom_formula = models.TextField(
        db_column="CustomFormula",
        blank=True,
        null=True,
        help_text=_("Custom formula for contribution calculation (Python expression)")
    )
    
    # Administrative fields
    created_date = models.DateTimeField(
        auto_now_add=True,
        help_text=_("Date plan was created")
    )
    
    last_modified = models.DateTimeField(
        auto_now=True,
        help_text=_("Date plan was last modified")
    )
    
    notes = models.TextField(
        blank=True,
        null=True,
        help_text=_("Administrative notes about the plan")
    )
    
    audit_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        db_column="AuditUser",
        null=True,
        blank=True,
        help_text=_("User who last modified the plan")
    )
    
    objects = ContributionPlanManager()
    
    def clean(self):
        """Custom validation for ContributionPlan model."""
        super().clean()
        
        # Validate date ranges
        if self.expiry_date and self.effective_date:
            if self.expiry_date <= self.effective_date:
                raise ValidationError({
                    'expiry_date': _("Expiry date must be after effective date")
                })
        
        # Validate age ranges
        if self.min_age and self.max_age:
            if self.min_age >= self.max_age:
                raise ValidationError({
                    'max_age': _("Maximum age must be greater than minimum age")
                })
        
        # Validate income thresholds
        if self.min_income_threshold and self.max_income_threshold:
            if self.min_income_threshold >= self.max_income_threshold:
                raise ValidationError({
                    'max_income_threshold': _("Maximum income must be greater than minimum income")
                })
        
        # Validate contribution amounts
        if self.min_contribution and self.max_contribution:
            if self.min_contribution >= self.max_contribution:
                raise ValidationError({
                    'max_contribution': _("Maximum contribution must be greater than minimum contribution")
                })
        
        # Validate percentage-based calculations
        if self.calculation_type in [
            ContributionCalculationType.PERCENTAGE_INCOME,
            ContributionCalculationType.PERCENTAGE_PREMIUM
        ]:
            if not self.percentage_rate:
                raise ValidationError({
                    'percentage_rate': _("Percentage rate is required for percentage-based calculations")
                })
        
        # Validate custom formula
        if self.calculation_type == ContributionCalculationType.CUSTOM_FORMULA:
            if not self.custom_formula:
                raise ValidationError({
                    'custom_formula': _("Custom formula is required for custom calculations")
                })
    
    @hook(BEFORE_SAVE)
    def validate_status_transitions(self):
        """Validate status transitions."""
        if self.pk and self.has_changed('status'):
            old_status = self.get_field_diff('status')[0]
            new_status = self.status
            
            # Define valid transitions
            valid_transitions = {
                ContributionPlanStatus.DRAFT: [
                    ContributionPlanStatus.ACTIVE,
                    ContributionPlanStatus.CANCELLED
                ],
                ContributionPlanStatus.ACTIVE: [
                    ContributionPlanStatus.SUSPENDED,
                    ContributionPlanStatus.EXPIRED,
                    ContributionPlanStatus.CANCELLED
                ],
                ContributionPlanStatus.SUSPENDED: [
                    ContributionPlanStatus.ACTIVE,
                    ContributionPlanStatus.CANCELLED
                ],
                # Terminal states
                ContributionPlanStatus.EXPIRED: [],
                ContributionPlanStatus.CANCELLED: []
            }
            
            if new_status not in valid_transitions.get(old_status, []):
                raise ValidationError(
                    f"Invalid status transition from {old_status} to {new_status}"
                )
    
    def calculate_contribution(self, **kwargs):
        """
        Calculate contribution amount based on plan configuration.
        
        Args:
            income: Income amount for percentage calculations
            premium: Premium amount for percentage calculations
            age: Age for tiered calculations
            family_size: Family size for family plans
            **kwargs: Additional parameters for custom formulas
            
        Returns:
            Decimal: Calculated contribution amount
        """
        income = kwargs.get('income', Decimal('0'))
        premium = kwargs.get('premium', Decimal('0'))
        age = kwargs.get('age', 0)
        family_size = kwargs.get('family_size', 1)
        
        if self.calculation_type == ContributionCalculationType.FIXED_AMOUNT:
            amount = self.base_amount
            
        elif self.calculation_type == ContributionCalculationType.PERCENTAGE_INCOME:
            if not income:
                raise ValueError("Income is required for percentage-based calculation")
            amount = income * (self.percentage_rate / 100)
            
        elif self.calculation_type == ContributionCalculationType.PERCENTAGE_PREMIUM:
            if not premium:
                raise ValueError("Premium is required for percentage-based calculation")
            amount = premium * (self.percentage_rate / 100)
            
        elif self.calculation_type == ContributionCalculationType.TIERED_INCOME:
            # Get tiered rates for this plan
            tiers = self.tiered_rates.filter(
                min_income__lte=income
            ).order_by('-min_income').first()
            
            if tiers:
                amount = tiers.contribution_amount
            else:
                amount = self.base_amount
                
        elif self.calculation_type == ContributionCalculationType.CUSTOM_FORMULA:
            # Evaluate custom formula
            try:
                # Create safe namespace for formula evaluation
                namespace = {
                    'base_amount': float(self.base_amount),
                    'income': float(income),
                    'premium': float(premium),
                    'age': age,
                    'family_size': family_size,
                    'percentage_rate': float(self.percentage_rate or 0),
                    **kwargs
                }
                
                # Evaluate the formula
                amount = Decimal(str(eval(self.custom_formula, {"__builtins__": {}}, namespace)))
                
            except Exception as e:
                raise ValueError(f"Error evaluating custom formula: {e}")
        else:
            amount = self.base_amount
        
        # Apply min/max constraints
        if self.min_contribution and amount < self.min_contribution:
            amount = self.min_contribution
        
        if self.max_contribution and amount > self.max_contribution:
            amount = self.max_contribution
        
        return amount.quantize(Decimal('0.01'))
    
    def is_eligible_for_age(self, age):
        """Check if age meets eligibility criteria."""
        if self.min_age and age < self.min_age:
            return False
        if self.max_age and age > self.max_age:
            return False
        return True
    
    def is_eligible_for_income(self, income):
        """Check if income meets eligibility criteria."""
        if self.min_income_threshold and income < self.min_income_threshold:
            return False
        if self.max_income_threshold and income > self.max_income_threshold:
            return False
        return True
    
    def is_available_in_location(self, location):
        """Check if plan is available in given location."""
        if not self.locations.exists():
            return True  # Available everywhere if no locations specified
        return self.locations.filter(pk=location.pk).exists()
    
    def get_next_contribution_date(self, from_date=None):
        """Calculate next contribution due date."""
        if from_date is None:
            from_date = datetime.date.today()
        
        if self.contribution_frequency == ContributionFrequency.MONTHLY:
            # Add one month
            if from_date.month == 12:
                return from_date.replace(year=from_date.year + 1, month=1)
            else:
                return from_date.replace(month=from_date.month + 1)
                
        elif self.contribution_frequency == ContributionFrequency.QUARTERLY:
            # Add 3 months
            month = from_date.month + 3
            year = from_date.year
            if month > 12:
                month -= 12
                year += 1
            return from_date.replace(year=year, month=month)
            
        elif self.contribution_frequency == ContributionFrequency.SEMI_ANNUAL:
            # Add 6 months
            month = from_date.month + 6
            year = from_date.year
            if month > 12:
                month -= 12
                year += 1
            return from_date.replace(year=year, month=month)
            
        elif self.contribution_frequency == ContributionFrequency.ANNUAL:
            # Add 1 year
            return from_date.replace(year=from_date.year + 1)
            
        else:  # ONE_TIME
            return None
    
    @property
    def is_active(self):
        """Check if plan is currently active."""
        today = datetime.date.today()
        return (
            self.status == ContributionPlanStatus.ACTIVE and
            self.effective_date <= today and
            (self.expiry_date is None or self.expiry_date >= today)
        )
    
    @property
    def days_until_expiry(self):
        """Calculate days until plan expires."""
        if not self.expiry_date:
            return None
        
        days = (self.expiry_date - datetime.date.today()).days
        return max(0, days)
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    class Meta:
        managed = True
        db_table = "tblContributionPlans"
        verbose_name = _("Contribution Plan")
        verbose_name_plural = _("Contribution Plans")
        ordering = ['code', 'name']
        indexes = [
            models.Index(fields=['code'], name='idx_contrib_plan_code'),
            models.Index(fields=['status'], name='idx_contrib_plan_status'),
            models.Index(fields=['plan_type'], name='idx_contrib_plan_type'),
            models.Index(fields=['effective_date'], name='idx_contrib_plan_effective'),
            models.Index(fields=['expiry_date'], name='idx_contrib_plan_expiry'),
            models.Index(fields=['calculation_type'], name='idx_contrib_plan_calc_type'),
            models.Index(fields=['contribution_frequency'], name='idx_contrib_plan_frequency'),
            models.Index(fields=['validity_from', 'validity_to'], name='idx_contrib_plan_validity'),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['code'],
                name='unique_contribution_plan_code'
            ),
            models.CheckConstraint(
                check=Q(effective_date__lte=F('expiry_date')) | Q(expiry_date__isnull=True),
                name='chk_contrib_plan_dates'
            ),
            models.CheckConstraint(
                check=Q(min_age__lt=F('max_age')) | Q(max_age__isnull=True) | Q(min_age__isnull=True),
                name='chk_contrib_plan_ages'
            ),
            models.CheckConstraint(
                check=Q(min_contribution__lt=F('max_contribution')) | 
                      Q(max_contribution__isnull=True) | Q(min_contribution__isnull=True),
                name='chk_contrib_plan_amounts'
            ),
        ]


class ContributionTieredRate(core_models.VersionedModel):
    """
    Tiered contribution rates for income-based calculations.
    """
    
    id = models.AutoField(primary_key=True)
    contribution_plan = models.ForeignKey(
        ContributionPlan,
        on_delete=models.CASCADE,
        related_name="tiered_rates",
        help_text=_("Contribution plan this tier belongs to")
    )
    
    tier_name = models.CharField(
        max_length=50,
        help_text=_("Name of this tier (e.g., 'Low Income', 'Middle Income')")
    )
    
    min_income = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text=_("Minimum income for this tier")
    )
    
    max_income = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text=_("Maximum income for this tier (null = no upper limit)")
    )
    
    contribution_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text=_("Contribution amount for this tier")
    )
    
    percentage_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))],
        help_text=_("Percentage rate for this tier (if using percentage calculation)")
    )
    
    def clean(self):
        """Validate tier configuration."""
        super().clean()
        
        if self.max_income and self.min_income >= self.max_income:
            raise ValidationError({
                'max_income': _("Maximum income must be greater than minimum income")
            })
    
    def __str__(self):
        max_income_str = str(self.max_income) if self.max_income else "∞"
        return f"{self.tier_name}: {self.min_income} - {max_income_str}"
    
    class Meta:
        managed = True
        db_table = "tblContributionTieredRates"
        verbose_name = _("Contribution Tiered Rate")
        verbose_name_plural = _("Contribution Tiered Rates")
        ordering = ['contribution_plan', 'min_income']
        indexes = [
            models.Index(fields=['contribution_plan'], name='idx_tier_plan'),
            models.Index(fields=['min_income'], name='idx_tier_min_income'),
            models.Index(fields=['max_income'], name='idx_tier_max_income'),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['contribution_plan', 'min_income'],
                name='unique_tier_plan_min_income'
            ),
        ]


# Usage examples:
"""
# Create a basic contribution plan
plan = ContributionPlan.objects.create(
    code="BASIC_001",
    name="Basic Family Plan",
    plan_type=ContributionPlanType.FAMILY,
    calculation_type=ContributionCalculationType.FIXED_AMOUNT,
    base_amount=Decimal('50.00'),
    contribution_frequency=ContributionFrequency.MONTHLY,
    status=ContributionPlanStatus.ACTIVE
)

# Create tiered income plan
income_plan = ContributionPlan.objects.create(
    code="INCOME_001",
    name="Income-Based Plan",
    calculation_type=ContributionCalculationType.TIERED_INCOME,
    base_amount=Decimal('25.00'),  # fallback amount
    min_income_threshold=Decimal('1000.00'),
    max_income_threshold=Decimal('10000.00')
)

# Add tiers
ContributionTieredRate.objects.create(
    contribution_plan=income_plan,
    tier_name="Low Income",
    min_income=Decimal('1000.00'),
    max_income=Decimal('3000.00'),
    contribution_amount=Decimal('25.00')
)

ContributionTieredRate.objects.create(
    contribution_plan=income_plan,
    tier_name="Middle Income",
    min_income=Decimal('3000.01'),
    max_income=Decimal('7000.00'),
    contribution_amount=Decimal('75.00')
)

# Calculate contributions
family_income = Decimal('4500.00')
contribution = income_plan.calculate_contribution(income=family_income)

# Check eligibility
age = 35
income = Decimal('5000.00')
location = Location.objects.get(pk=1)

eligible_plans = ContributionPlan.objects.active().filter(
    plan__is_eligible_for_age(age),
    plan__is_eligible_for_income(income),
    plan__is_available_in_location(location)
)
"""