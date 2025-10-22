from django.db import models
from django.utils.translation import gettext_lazy as _
from modules.core.models.openimis_core_models import BaseCodeModel
from modules.core.models import openimis_core_models as core_models
import uuid
from datetime import datetime, date
from django.core.exceptions import ValidationError
from django.conf import settings

# Removed circular import - will use string references and lazy imports
from modules.location import models as location_models
from django.db.models import Q, F
from django_lifecycle import LifecycleModel, hook, BEFORE_SAVE
from modules.insuree.models.insuree_model_dependency import Relation
from modules.insuree.models.insuree_model_dependency import AGE_OF_MAJORITY


class FamilyMembershipStatus(models.TextChoices):
    """Enhanced status choices with better naming."""

    ACTIVE = "AC", _("Active")
    INACTIVE = "IN", _("Inactive")
    TRANSFERRED = "TR", _("Transferred")
    DECEASED = "DE", _("Deceased")


class FamilyMembershipManager(models.Manager):
    """Custom manager for FamilyMembership model."""

    def active(self):
        """Return only active memberships."""
        return self.filter(status=FamilyMembershipStatus.ACTIVE)

    def heads_of_family(self):
        """Return only head of family memberships."""
        return self.filter(is_head=True)

    def for_family(self, family):
        """Return memberships for a specific family."""
        return self.filter(family=family)

    def for_insuree(self, insuree):
        """Return memberships for a specific insuree."""
        return self.filter(insuree=insuree)


class FamilyMembership(core_models.VersionedModel, LifecycleModel):
    """
    Separate model to manage family memberships with better flexibility.
    This allows insurees to be part of multiple families over time and
    provides better tracking of family composition changes.
    """

    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        help_text=_("Unique identifier for the membership"),
    )

    family = models.ForeignKey(
        "Family",
        on_delete=models.CASCADE,
        related_name="memberships",
        help_text=_("Family this membership belongs to"),
    )

    insuree = models.ForeignKey(
        "Insuree",
        on_delete=models.CASCADE,
        related_name="family_memberships",
        help_text=_("Insuree who is a member"),
    )

    is_head = models.BooleanField(
        default=False, help_text=_("Whether this member is head of family")
    )

    relationship = models.ForeignKey(
        Relation,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text=_("Relationship to head of family"),
    )

    status = models.CharField(
        max_length=2,
        choices=FamilyMembershipStatus.choices,
        default=FamilyMembershipStatus.ACTIVE,
        help_text=_("Membership status"),
    )

    membership_start_date = models.DateField(
        default=date.today, help_text=_("Date membership started")
    )

    membership_end_date = models.DateField(
        blank=True, null=True, help_text=_("Date membership ended")
    )

    notes = models.TextField(
        blank=True, null=True, help_text=_("Notes about this membership")
    )

    created_date = models.DateTimeField(
        auto_now_add=True, help_text=_("Date membership was created")
    )

    last_modified = models.DateTimeField(
        auto_now=True, help_text=_("Date membership was last modified")
    )

    is_valid = models.BooleanField(
        default=True, help_text=_("Whether this membership is valid")
    )

    has_claim_benefits = models.BooleanField(
        default=False, help_text=_("Whether this membership has claim benefits")
    )

    audit_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text=_("User who last modified the membership"),
    )

    objects = FamilyMembershipManager()

    def clean(self):
        """Custom validation for FamilyMembership model."""
        super().clean()

        # Validate that only one head per family exists
        if self.is_head and self.family:
            other_heads = FamilyMembership.objects.filter(
                family=self.family, is_head=True, status=FamilyMembershipStatus.ACTIVE
            ).exclude(pk=self.pk)

            if other_heads.exists():
                raise ValidationError(
                    {"is_head": _("Family can only have one active head")}
                )

        # Validate membership dates
        if self.membership_end_date and self.membership_start_date:
            if self.membership_end_date <= self.membership_start_date:
                raise ValidationError(
                    {"membership_end_date": _("End date must be after start date")}
                )

        # Validate that membership end date is set for inactive statuses
        if (
            self.status != FamilyMembershipStatus.ACTIVE
            and not self.membership_end_date
        ):
            self.membership_end_date = date.today()

    @hook(BEFORE_SAVE)
    def update_family_head_reference(self):
        """Update family head reference when head changes."""
        if self.is_head and self.status == FamilyMembershipStatus.ACTIVE:
            # Update the family's head_insuree reference
            if self.family.head_insuree != self.insuree:
                self.family.head_insuree = self.insuree
                self.family.save(update_fields=["head_insuree"])

    @hook(BEFORE_SAVE)
    def set_end_date_for_inactive(self):
        """Set end date when membership becomes inactive."""
        if (
            self.has_changed("status")
            and self.status != FamilyMembershipStatus.ACTIVE
            and not self.membership_end_date
        ):
            self.membership_end_date = date.today()

    @property
    def is_active(self):
        """Check if membership is active."""
        return self.status == FamilyMembershipStatus.ACTIVE

    @property
    def membership_duration(self):
        """Calculate membership duration in days."""
        end_date = self.membership_end_date or date.today()
        return (end_date - self.membership_start_date).days

    def deactivate(self, reason=None, end_date=None):
        """Deactivate the membership."""
        self.status = FamilyMembershipStatus.INACTIVE
        self.membership_end_date = end_date or date.today()
        if reason:
            self.notes = f"{self.notes or ''}\nDeactivated: {reason}".strip()
        self.save()

    def transfer_to_family(self, new_family, transfer_date=None):
        """Transfer member to a new family."""
        transfer_date = transfer_date or date.today()

        # End current membership
        self.status = FamilyMembershipStatus.TRANSFERRED
        self.membership_end_date = transfer_date
        self.save()

        # Create new membership
        new_membership = FamilyMembership.objects.create(
            family=new_family,
            insuree=self.insuree,
            is_head=False,  # Not head in new family by default
            relationship=self.relationship,
            membership_start_date=transfer_date,
            status=FamilyMembershipStatus.ACTIVE,
            audit_user=self.audit_user,
        )

        return new_membership

    def __str__(self):
        head_status = " (Head)" if self.is_head else ""
        return f"{self.insuree.full_name} in {self.family}{head_status}"

    class Meta:
        managed = True
        db_table = "tblFamilyMemberships"
        verbose_name = _("Family Membership")
        verbose_name_plural = _("Family Memberships")
        ordering = ["family", "-is_head", "insuree__last_name"]
        indexes = [
            models.Index(fields=["family"], name="idx_membership_family"),
            models.Index(fields=["insuree"], name="idx_membership_insuree"),
            models.Index(fields=["status"], name="idx_membership_status"),
            models.Index(fields=["is_head"], name="idx_membership_head"),
            models.Index(fields=["membership_start_date"], name="idx_membership_start"),
            models.Index(fields=["membership_end_date"], name="idx_membership_end"),
            models.Index(
                fields=["family", "status"], name="idx_membership_family_status"
            ),
            models.Index(
                fields=["insuree", "status"], name="idx_membership_insuree_status"
            ),
            models.Index(
                fields=["validity_from", "validity_to"], name="idx_membership_validity"
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["family", "insuree", "validity_from"],
                name="unique_family_member_validity",
            ),
            models.UniqueConstraint(
                fields=["family", "is_head"],
                condition=Q(is_head=True, status=FamilyMembershipStatus.ACTIVE),
                name="unique_family_head_active",
            ),
            models.CheckConstraint(
                check=Q(membership_end_date__isnull=True)
                | Q(membership_end_date__gte=F("membership_start_date")),
                name="chk_membership_end_after_start",
            ),
        ]


class FamilyType(BaseCodeModel):
    """Family type lookup with better structure."""

    code = models.CharField(
        db_column="FamilyTypeCode",
        primary_key=True,
        max_length=2,
        help_text=_("Family type code"),
    )
    type = models.CharField(
        db_column="FamilyType", max_length=50, help_text=_("Family type description")
    )
    is_active = models.BooleanField(
        default=True, help_text=_("Whether this family type is active")
    )
    sort_order = models.PositiveSmallIntegerField(
        default=0, help_text=_("Sort order for display")
    )

    class Meta:
        managed = True
        db_table = "tblFamilyTypes"
        verbose_name = _("Family Type")
        verbose_name_plural = _("Family Types")
        ordering = ["sort_order", "code"]
        indexes = [
            models.Index(fields=["code"], name="idx_family_type_code"),
            models.Index(fields=["is_active"], name="idx_family_type_active"),
        ]


class FamilyManager(models.Manager):
    """Custom manager for Family model."""

    def active(self):
        """Return only active families."""
        return self.filter(validity_to__isnull=True)

    def by_location(self, location):
        """Filter families by location."""
        return self.filter(location=location)

    def in_poverty(self):
        """Filter families in poverty."""
        return self.filter(poverty=True)


class Family(core_models.VersionedModel, core_models.ExtendableModel, LifecycleModel):
    """Enhanced Family model with better validation and indexing."""

    id = models.AutoField(db_column="FamilyID", primary_key=True)
    uuid = models.UUIDField(
        db_column="FamilyUUID",
        default=uuid.uuid4,
        unique=True,
        editable=False,
        help_text=_("Unique identifier for the family"),
    )

    # Keep reference to head insuree for backward compatibility and quick access
    head_insuree = models.ForeignKey(
        "Insuree",
        on_delete=models.PROTECT,  # Prevent deletion of head insuree
        db_column="InsureeID",
        related_name="head_of",
        help_text=_("Head of the family (maintained for compatibility)"),
    )

    location = models.ForeignKey(
        location_models.Location,
        on_delete=models.SET_NULL,
        db_column="LocationId",
        blank=True,
        null=True,
        help_text=_("Family location"),
    )

    poverty = models.BooleanField(
        db_column="Poverty", default=False, help_text=_("Whether family is in poverty")
    )

    family_type = models.ForeignKey(
        FamilyType,
        on_delete=models.SET_NULL,
        db_column="FamilyType",
        blank=True,
        null=True,
        related_name="families",
        help_text=_("Type of family"),
    )

    address = models.CharField(
        db_column="FamilyAddress",
        max_length=200,
        blank=True,
        null=True,
        help_text=_("Family address"),
    )

    is_offline = models.BooleanField(
        db_column="isOffline",
        default=False,
        help_text=_("Whether family was created offline"),
    )

    ethnicity = models.CharField(
        db_column="Ethnicity",
        max_length=50,  # Increased length for better ethnicity support
        blank=True,
        null=True,
        help_text=_("Family ethnicity"),
    )

    confirmation_no = models.CharField(
        db_column="ConfirmationNo",
        max_length=12,
        blank=True,
        null=True,
        unique=True,  # Should be unique if used
        help_text=_("Confirmation number"),
    )

    # Additional useful fields
    created_date = models.DateTimeField(
        auto_now_add=True, help_text=_("Date family was created")
    )

    last_modified = models.DateTimeField(
        auto_now=True, help_text=_("Date family was last modified")
    )

    notes = models.TextField(
        blank=True, null=True, help_text=_("Additional notes about the family")
    )

    audit_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        db_column="AuditUser",
        null=True,
        blank=True,
        help_text=_("User who last modified the family"),
    )

    objects = FamilyManager()

    def clean(self):
        """Custom validation for Family model."""
        super().clean()

        # Validate that head_insuree has an active membership in this family
        if self.head_insuree:
            active_membership = FamilyMembership.objects.filter(
                family=self,
                insuree=self.head_insuree,
                is_head=True,
                status=FamilyMembershipStatus.ACTIVE,
            ).exists()

            if not active_membership:
                # Check if there's any membership for this insuree
                any_membership = FamilyMembership.objects.filter(
                    family=self, insuree=self.head_insuree
                ).exists()

                if not any_membership:
                    raise ValidationError(
                        _("Head insuree must have a membership in this family")
                    )

    @property
    def active_memberships(self):
        """Return active family memberships."""
        return self.memberships.filter(status=FamilyMembershipStatus.ACTIVE)

    @property
    def members(self):
        """Return active family members (for backward compatibility)."""
        from .insuree import Insuree

        return Insuree.objects.filter(
            family_memberships__family=self,
            family_memberships__status=FamilyMembershipStatus.ACTIVE,
        ).distinct()

    @property
    def member_count(self):
        """Return the number of active family members."""
        return self.active_memberships.count()

    @property
    def adult_members(self):
        """Return adult family members."""
        from django.utils import timezone
        from .insuree import Insuree

        today = timezone.now().date()
        cutoff_date = today - datetime.timedelta(days=AGE_OF_MAJORITY * 365.25)

        return Insuree.objects.filter(
            family_memberships__family=self,
            family_memberships__status=FamilyMembershipStatus.ACTIVE,
            dob__lte=cutoff_date,
        ).distinct()

    def add_member(self, insuree, is_head=False, relationship=None, start_date=None):
        """Add a new member to the family."""
        if start_date is None:
            start_date = date.today()

        # Check if insuree already has active membership
        existing_membership = FamilyMembership.objects.filter(
            family=self, insuree=insuree, status=FamilyMembershipStatus.ACTIVE
        ).exists()

        if existing_membership:
            raise ValidationError(
                _("Insuree is already an active member of this family")
            )

        # Create new membership
        membership = FamilyMembership.objects.create(
            family=self,
            insuree=insuree,
            is_head=is_head,
            relationship=relationship,
            membership_start_date=start_date,
            status=FamilyMembershipStatus.ACTIVE,
        )

        # Update family head reference if this is the head
        if is_head:
            self.head_insuree = insuree
            self.save(update_fields=["head_insuree"])

        return membership

    def remove_member(self, insuree, end_date=None, reason=None):
        """Remove a member from the family."""
        try:
            membership = self.memberships.get(
                insuree=insuree, status=FamilyMembershipStatus.ACTIVE
            )
            membership.deactivate(reason=reason, end_date=end_date)

            # If removing head, need to assign new head
            if membership.is_head:
                self._assign_new_head()

            return membership
        except FamilyMembership.DoesNotExist:
            raise ValidationError(_("Insuree is not an active member of this family"))

    def _assign_new_head(self):
        """Assign a new head when current head is removed."""
        # Find the oldest adult member or oldest member if no adults
        potential_heads = self.active_memberships.exclude(
            insuree=self.head_insuree
        ).select_related("insuree")

        # Prefer adults
        adult_members = [m for m in potential_heads if m.insuree.is_adult()]
        if adult_members:
            # Sort by age (oldest first)
            new_head_membership = min(
                adult_members, key=lambda m: m.insuree.dob or datetime.date.min
            )
        elif potential_heads:
            # If no adults, pick oldest member
            new_head_membership = min(
                potential_heads, key=lambda m: m.insuree.dob or datetime.date.min
            )
        else:
            # No other members, clear head reference
            self.head_insuree = None
            self.save(update_fields=["head_insuree"])
            return

        # Update new head
        new_head_membership.is_head = True
        new_head_membership.save()

        self.head_insuree = new_head_membership.insuree
        self.save(update_fields=["head_insuree"])

    def get_head_membership(self):
        """Get the current head membership."""
        try:
            return self.memberships.get(
                is_head=True, status=FamilyMembershipStatus.ACTIVE
            )
        except FamilyMembership.DoesNotExist:
            return None

    def __str__(self):
        return f"Family {self.id} - {self.head_insuree}"

    class Meta:
        managed = True
        db_table = "tblFamilies"
        verbose_name = _("Family")
        verbose_name_plural = _("Families")
        indexes = [
            models.Index(fields=["head_insuree"], name="idx_family_head"),
            models.Index(fields=["location"], name="idx_family_location"),
            models.Index(fields=["family_type"], name="idx_family_type"),
            models.Index(fields=["poverty"], name="idx_family_poverty"),
            models.Index(fields=["confirmation_no"], name="idx_family_confirmation"),
            models.Index(fields=["created_date"], name="idx_family_created"),
            models.Index(
                fields=["validity_from", "validity_to"], name="idx_family_validity"
            ),
        ]
        constraints = [
            models.CheckConstraint(
                check=Q(confirmation_no__isnull=True),
                name="chk_family_confirmation_min_length",
            ),
        ]
