from modules.core.models import openimis_core_models as core_models
from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from modules.location import models as location_models
import datetime
from modules.authentication.models import User
import os
from django_lifecycle import LifecycleModel, hook, BEFORE_SAVE
from django.db.models import Q, F
from django.utils.translation import gettext_lazy as _
import uuid

AGE_OF_MAJORITY = int(os.getenv("AGE_OF_MAJORITY", 18))


class BaseCodeModel(models.Model):
    """Abstract base model for code-based lookup tables."""

    class Meta:
        abstract = True
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} - {getattr(self, 'name', getattr(self, 'description', self.code))}"


class Gender(BaseCodeModel):
    """Gender lookup table with improved validation."""

    MALE = "M"
    FEMALE = "F"
    OTHER = "O"

    GENDER_CHOICES = [
        (MALE, _("Male")),
        (FEMALE, _("Female")),
        (OTHER, _("Other")),
    ]

    code = models.CharField(
        db_column="Code",
        primary_key=True,
        max_length=1,
        choices=GENDER_CHOICES,
        help_text=_("Gender code"),
    )
    gender = models.CharField(
        db_column="Gender",
        max_length=50,
        blank=True,
        null=True,
        help_text=_("Gender description"),
    )

    # Add indexes for better performance
    class Meta:
        managed = True
        db_table = "tblGenders"
        verbose_name = _("Gender")
        verbose_name_plural = _("Genders")
        indexes = [
            models.Index(fields=["code"], name="idx_gender_code"),
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
        User,
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
            start_date = datetime.date.today()

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
                check=Q(confirmation_no__isnull=True)
                | Q(confirmation_no__length__gte=3),
                name="chk_family_confirmation_min_length",
            ),
        ]


class Profession(models.Model):
    """Enhanced Profession model."""

    id = models.AutoField(db_column="ProfessionId", primary_key=True)
    profession = models.CharField(
        db_column="Profession",
        max_length=100,  # Increased length
        help_text=_("Profession name"),
    )
    code = models.CharField(
        max_length=10,
        unique=True,
        blank=True,
        null=True,
        help_text=_("Profession code"),
    )
    is_active = models.BooleanField(
        default=True, help_text=_("Whether profession is active")
    )
    sort_order = models.PositiveSmallIntegerField(
        default=0, help_text=_("Sort order for display")
    )

    class Meta:
        managed = True
        db_table = "tblProfessions"
        verbose_name = _("Profession")
        verbose_name_plural = _("Professions")
        ordering = ["sort_order", "profession"]
        indexes = [
            models.Index(fields=["profession"], name="idx_profession_name"),
            models.Index(fields=["is_active"], name="idx_profession_active"),
        ]

    def __str__(self):
        return self.profession


class Education(models.Model):
    """Enhanced Education model."""

    id = models.AutoField(db_column="EducationId", primary_key=True)
    education = models.CharField(
        db_column="Education",
        max_length=100,  # Increased length
        help_text=_("Education level"),
    )
    code = models.CharField(
        max_length=10, unique=True, blank=True, null=True, help_text=_("Education code")
    )
    level = models.PositiveSmallIntegerField(
        default=0, help_text=_("Education level rank")
    )
    is_active = models.BooleanField(
        default=True, help_text=_("Whether education level is active")
    )

    class Meta:
        managed = True
        db_table = "tblEducations"
        verbose_name = _("Education")
        verbose_name_plural = _("Education Levels")
        ordering = ["level", "education"]
        indexes = [
            models.Index(fields=["education"], name="idx_education_name"),
            models.Index(fields=["level"], name="idx_education_level"),
            models.Index(fields=["is_active"], name="idx_education_active"),
        ]

    def __str__(self):
        return self.education


class IdentificationType(models.Model):
    """Enhanced Identification Type model."""

    code = models.CharField(
        db_column="IdentificationCode",
        primary_key=True,
        max_length=10,  # Increased length
        help_text=_("Identification type code"),
    )
    identification_type = models.CharField(
        db_column="IdentificationTypes",
        max_length=100,  # Increased length
        help_text=_("Identification type description"),
    )
    is_active = models.BooleanField(
        default=True, help_text=_("Whether identification type is active")
    )
    requires_validation = models.BooleanField(
        default=False, help_text=_("Whether this ID type requires validation")
    )
    validation_regex = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text=_("Regex pattern for validation"),
    )

    class Meta:
        managed = True
        db_table = "tblIdentificationTypes"
        verbose_name = _("Identification Type")
        verbose_name_plural = _("Identification Types")
        ordering = ["identification_type"]
        indexes = [
            models.Index(fields=["code"], name="idx_id_type_code"),
            models.Index(fields=["is_active"], name="idx_id_type_active"),
        ]

    def __str__(self):
        return f"{self.code} - {self.identification_type}"


class Relation(models.Model):
    """Enhanced Relation model."""

    id = models.AutoField(db_column="RelationId", primary_key=True)
    relation = models.CharField(
        db_column="Relation", max_length=50, help_text=_("Relationship description")
    )
    code = models.CharField(
        max_length=10,
        unique=True,
        blank=True,
        null=True,
        help_text=_("Relationship code"),
    )
    is_active = models.BooleanField(
        default=True, help_text=_("Whether relationship is active")
    )
    sort_order = models.PositiveSmallIntegerField(
        default=0, help_text=_("Sort order for display")
    )

    class Meta:
        managed = True
        db_table = "tblRelations"
        verbose_name = _("Relation")
        verbose_name_plural = _("Relations")
        ordering = ["sort_order", "relation"]
        indexes = [
            models.Index(fields=["relation"], name="idx_relation_name"),
            models.Index(fields=["is_active"], name="idx_relation_active"),
        ]

    def __str__(self):
        return self.relation


class InsureeStatus(models.TextChoices):
    """Enhanced status choices with better naming."""

    ACTIVE = "AC", _("Active")
    INACTIVE = "IN", _("Inactive")
    DECEASED = "DE", _("Deceased")
    SUSPENDED = "SU", _("Suspended")
    PENDING = "PE", _("Pending")


class FamilyMembershipStatus(models.TextChoices):
    """Status choices for family membership."""

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
        Family,
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
        default=datetime.date.today, help_text=_("Date membership started")
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

    audit_user = models.ForeignKey(
        User,
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
            self.membership_end_date = datetime.date.today()

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
            self.membership_end_date = datetime.date.today()

    @property
    def is_active(self):
        """Check if membership is active."""
        return self.status == FamilyMembershipStatus.ACTIVE

    @property
    def membership_duration(self):
        """Calculate membership duration in days."""
        end_date = self.membership_end_date or datetime.date.today()
        return (end_date - self.membership_start_date).days

    def deactivate(self, reason=None, end_date=None):
        """Deactivate the membership."""
        self.status = FamilyMembershipStatus.INACTIVE
        self.membership_end_date = end_date or datetime.date.today()
        if reason:
            self.notes = f"{self.notes or ''}\nDeactivated: {reason}".strip()
        self.save()

    def transfer_to_family(self, new_family, transfer_date=None):
        """Transfer member to a new family."""
        transfer_date = transfer_date or datetime.date.today()

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


class InsureeManager(models.Manager):
    """Custom manager for Insuree model."""

    def active(self):
        """Return only active insurees."""
        return self.filter(status=InsureeStatus.ACTIVE)

    def heads_of_family(self):
        """Return only heads of families."""
        return self.filter(
            family_memberships__is_head=True,
            family_memberships__status=FamilyMembershipStatus.ACTIVE,
        ).distinct()

    def adults(self, reference_date=None):
        """Return only adult insurees."""
        if reference_date is None:
            reference_date = datetime.date.today()

        cutoff_date = reference_date - datetime.timedelta(days=AGE_OF_MAJORITY * 365.25)
        return self.filter(dob__lte=cutoff_date)

    def by_chf_id(self, chf_id):
        """Find insuree by CHF ID."""
        return self.filter(chf_id=chf_id)

    def in_family(self, family):
        """Return insurees in a specific family."""
        return self.filter(
            family_memberships__family=family,
            family_memberships__status=FamilyMembershipStatus.ACTIVE,
        ).distinct()


class Insuree(core_models.VersionedModel, core_models.ExtendableModel, LifecycleModel):
    """Enhanced Insuree model with better validation and performance."""

    # Usage examples and migration helpers:
    """
    # Example usage of the new FamilyMembership model:

    # Create a family
    family = Family.objects.create(
        location=some_location,
        family_type=some_type,
        address="123 Main St",
        audit_user=user
    )

    # Create insurees
    head_insuree = Insuree.objects.create(
        chf_id="12345",
        last_name="Doe",
        other_names="John",
        # ... other fields
    )

    spouse_insuree = Insuree.objects.create(
        chf_id="12346",
        last_name="Doe",
        other_names="Jane",
        # ... other fields
    )

    # Add members to family using the new system
    head_membership = family.add_member(
        insuree=head_insuree,
        is_head=True,
        relationship=None  # Head has no relationship to themselves
    )

    spouse_membership = family.add_member(
        insuree=spouse_insuree,
        is_head=False,
        relationship=spouse_relation  # Relation object for spouse
    )

    # Transfer member to another family
    new_family = Family.objects.create(...)
    spouse_membership.transfer_to_family(new_family)

    # Get family members
    active_members = family.members  # Returns QuerySet of active members
    member_count = family.member_count
    adult_members = family.adult_members

    # Access family through insuree
    current_family = head_insuree.current_family
    is_head = head_insuree.is_head_of_family
    family_relationship = head_insuree.get_family_relationship()

    # Get family history for an insuree
    history = head_insuree.get_family_history()
    """

    id = models.AutoField(db_column="InsureeID", primary_key=True)
    uuid = models.UUIDField(
        db_column="InsureeUUID",
        default=uuid.uuid4,
        unique=True,
        editable=False,
        help_text=_("Unique identifier for the insuree"),
    )

    chf_id = models.CharField(
        db_column="CHFID",
        max_length=50,
        blank=True,
        null=True,
        unique=True,
        help_text=_("CHF identification number"),
    )

    last_name = models.CharField(
        db_column="LastName", max_length=100, help_text=_("Last name")
    )

    other_names = models.CharField(
        db_column="OtherNames", max_length=100, help_text=_("Other names")
    )

    gender = models.ForeignKey(
        Gender,
        on_delete=models.PROTECT,
        db_column="Gender",
        blank=True,
        null=True,
        help_text=_("Gender"),
    )

    dob = models.DateField(
        db_column="DOB", blank=True, null=True, help_text=_("Date of birth")
    )

    marital = models.CharField(
        db_column="Marital",
        max_length=1,
        blank=True,
        null=True,
        choices=[
            ("S", _("Single")),
            ("M", _("Married")),
            ("D", _("Divorced")),
            ("W", _("Widowed")),
        ],
        help_text=_("Marital status"),
    )

    # Enhanced validation for passport
    passport = models.CharField(
        max_length=25, blank=True, null=True, help_text=_("Passport number")
    )

    # Enhanced phone validation
    phone_regex = RegexValidator(
        regex=r"^\+?1?\d{9,15}",
        message=_(
            "Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
        ),
    )

    profession = models.ForeignKey(
        Profession,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text=_("Profession"),
    )

    education = models.ForeignKey(
        Education,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text=_("Education level"),
    )

    identification = models.ForeignKey(
        IdentificationType,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        help_text=_("Identification type"),
    )

    identification_number = models.CharField(
        max_length=50, blank=True, null=True, help_text=_("Identification number")
    )

    health_facility = models.ForeignKey(
        location_models.HealthFacility,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text=_("Associated health facility"),
    )

    offline = models.BooleanField(
        db_column="isOffline", default=False, help_text=_("Whether created offline")
    )

    status = models.CharField(
        max_length=2,
        choices=InsureeStatus.choices,
        default=InsureeStatus.ACTIVE,
        help_text=_("Current status"),
    )

    status_date = models.DateField(
        db_column="StatusDate",
        null=True,
        blank=True,
        help_text=_("Date status was changed"),
    )

    # Additional useful fields
    created_date = models.DateTimeField(
        auto_now_add=True, help_text=_("Date insuree was created")
    )

    last_modified = models.DateTimeField(
        auto_now=True, help_text=_("Date insuree was last modified")
    )

    notes = models.TextField(blank=True, null=True, help_text=_("Additional notes"))

    audit_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        db_column="AuditUser",
        null=True,
        blank=True,
        help_text=_("User who last modified the insuree"),
    )

    objects = InsureeManager()

    def clean(self):
        """Enhanced validation for Insuree model."""
        super().clean()

        # Validate CHF ID uniqueness
        if self.chf_id:
            existing = Insuree.objects.filter(chf_id=self.chf_id).exclude(pk=self.pk)
            if existing.exists():
                raise ValidationError({"chf_id": _("CHF ID must be unique")})

        # Validate date of birth
        if self.dob and self.dob > datetime.date.today():
            raise ValidationError({"dob": _("Date of birth cannot be in the future")})

        # Validate identification number if type requires it
        if self.identification and self.identification.requires_validation:
            if not self.identification_number:
                raise ValidationError(
                    {
                        "identification_number": _(
                            "Identification number is required for this type"
                        )
                    }
                )

            if self.identification.validation_regex:
                import re

                if not re.match(
                    self.identification.validation_regex, self.identification_number
                ):
                    raise ValidationError(
                        {
                            "identification_number": _(
                                "Invalid identification number format"
                            )
                        }
                    )

    @hook(BEFORE_SAVE)
    def update_status_date(self):
        """Update status date when status changes."""
        if self.has_changed("status") and self.status:
            self.status_date = datetime.date.today()

    @hook(BEFORE_SAVE)
    def update_card_issued_date(self):
        """Update card issued date when card is issued."""
        if self.has_changed("card_issued") and self.card_issued:
            self.card_issued_date = datetime.date.today()

    @property
    def current_family(self):
        """Get current family through active membership."""
        try:
            active_membership = self.family_memberships.get(
                status=FamilyMembershipStatus.ACTIVE
            )
            return active_membership.family
        except (
            FamilyMembership.DoesNotExist,
            FamilyMembership.MultipleObjectsReturned,
        ):
            return None

    @property
    def current_family_membership(self):
        """Get current family membership."""
        try:
            return self.family_memberships.get(status=FamilyMembershipStatus.ACTIVE)
        except (
            FamilyMembership.DoesNotExist,
            FamilyMembership.MultipleObjectsReturned,
        ):
            return None

    @property
    def is_head_of_family(self):
        """Check if insuree is head of any family."""
        return self.family_memberships.filter(
            is_head=True, status=FamilyMembershipStatus.ACTIVE
        ).exists()

    def get_family_relationship(self):
        """Get relationship to head of current family."""
        membership = self.current_family_membership
        return membership.relationship if membership else None

    def join_family(self, family, is_head=False, relationship=None, start_date=None):
        """Join a family."""
        return family.add_member(
            insuree=self,
            is_head=is_head,
            relationship=relationship,
            start_date=start_date,
        )

    def leave_family(self, end_date=None, reason=None):
        """Leave current family."""
        current_family = self.current_family
        if current_family:
            return current_family.remove_member(
                insuree=self, end_date=end_date, reason=reason
            )
        else:
            raise ValidationError(_("Insuree is not currently in any family"))

    def transfer_to_family(self, new_family, transfer_date=None):
        """Transfer to a new family."""
        current_membership = self.current_family_membership
        if current_membership:
            return current_membership.transfer_to_family(
                new_family=new_family, transfer_date=transfer_date
            )
        else:
            # If not in any family, just join the new one
            return self.join_family(new_family, start_date=transfer_date)

    def get_family_history(self):
        """Get complete family membership history."""
        return self.family_memberships.select_related(
            "family", "relationship"
        ).order_by("-membership_start_date")

    def age(self, reference_date=None):
        """Calculate age with better precision."""
        if not self.dob:
            return None

        if reference_date is None:
            reference_date = datetime.date.today()

        age = reference_date.year - self.dob.year
        if (reference_date.month, reference_date.day) < (self.dob.month, self.dob.day):
            age -= 1

        return max(0, age)  # Ensure age is not negative

    def is_adult(self, reference_date=None):
        """Check if insuree is adult."""
        age = self.age(reference_date)
        return age >= AGE_OF_MAJORITY if age is not None else None

    @property
    def full_name(self):
        """Return full name."""
        return f"{self.other_names} {self.last_name}".strip()

    @property
    def is_active(self):
        """Check if insuree is active."""
        return self.status == InsureeStatus.ACTIVE

    def __str__(self):
        return f"{self.chf_id or 'No CHF ID'} - {self.full_name}"

    class Meta:
        managed = True
        db_table = "tblInsurees"
        verbose_name = _("Insuree")
        verbose_name_plural = _("Insurees")
        indexes = [
            models.Index(fields=["chf_id"], name="idx_insuree_chfid"),
            models.Index(fields=["last_name", "other_names"], name="idx_insuree_names"),
            models.Index(fields=["dob"], name="idx_insuree_dob"),
            models.Index(fields=["status"], name="idx_insuree_status"),
            models.Index(fields=["gender"], name="idx_insuree_gender"),
            models.Index(fields=["created_date"], name="idx_insuree_created"),
            models.Index(
                fields=["validity_from", "validity_to"], name="idx_insuree_validity"
            ),
            models.Index(
                fields=["identification_number"], name="idx_insuree_id_number"
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["chf_id"],
                condition=Q(chf_id__isnull=False),
                name="unique_chf_id",
            ),
            models.CheckConstraint(
                check=Q(dob__lte=datetime.date.today()),
                name="chk_insuree_dob_not_future",
            ),
        ]

    phone = models.CharField(
        db_column="Phone",
        validators=[phone_regex],
        max_length=17,
        blank=True,
        null=True,
        help_text=_("Phone number"),
    )

    # Enhanced email validation
    email = models.EmailField(
        db_column="Email",
        max_length=100,
        blank=True,
        null=True,
        help_text=_("Email address"),
    )

    current_address = models.CharField(
        db_column="CurrentAddress",
        max_length=200,
        blank=True,
        null=True,
        help_text=_("Current address"),
    )

    geolocation = models.CharField(
        db_column="GeoLocation",
        max_length=250,
        blank=True,
        null=True,
        help_text=_("GPS coordinates"),
    )

    current_village = models.ForeignKey(
        location_models.Location,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text=_("Current village"),
    )

    photo = models.ImageField(  # Changed to ImageField for better validation
        db_column="Photo",
        upload_to="insuree/photos/%Y/%m/",  # Better organization
        blank=True,
        null=True,
        max_length=255,
        help_text=_("Photo of the insuree"),
    )

    photo_date = models.DateField(
        db_column="PhotoDate",
        blank=True,
        null=True,
        help_text=_("Date photo was taken"),
    )

    card_issued = models.BooleanField(
        db_column="CardIssued",
        default=False,
        help_text=_("Whether card has been issued"),
    )

    card_issued_date = models.DateField(
        blank=True, null=True, help_text=_("Date card was issued")
    )

    profession = models.ForeignKey(
        Profession,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text=_("Profession"),
    )

    education = models.ForeignKey(
        Education,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text=_("Education level"),
    )

    identification = models.ForeignKey(
        IdentificationType,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        help_text=_("Identification type"),
    )

    identification_number = models.CharField(
        max_length=50, blank=True, null=True, help_text=_("Identification number")
    )

    health_facility = models.ForeignKey(
        location_models.HealthFacility,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text=_("Associated health facility"),
    )

    offline = models.BooleanField(
        db_column="isOffline", default=False, help_text=_("Whether created offline")
    )

    status = models.CharField(
        max_length=2,
        choices=InsureeStatus.choices,
        default=InsureeStatus.ACTIVE,
        help_text=_("Current status"),
    )

    status_date = models.DateField(
        db_column="StatusDate",
        null=True,
        blank=True,
        help_text=_("Date status was changed"),
    )

    # Additional useful fields
    created_date = models.DateTimeField(
        auto_now_add=True, help_text=_("Date insuree was created")
    )

    last_modified = models.DateTimeField(
        auto_now=True, help_text=_("Date insuree was last modified")
    )

    notes = models.TextField(blank=True, null=True, help_text=_("Additional notes"))

    audit_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        db_column="AuditUser",
        null=True,
        blank=True,
        help_text=_("User who last modified the insuree"),
    )

    objects = InsureeManager()

    def clean(self):  # noqa: F811
        """Enhanced validation for Insuree model."""
        super().clean()

        # Validate CHF ID uniqueness
        if self.chf_id:
            existing = Insuree.objects.filter(chf_id=self.chf_id).exclude(pk=self.pk)
            if existing.exists():
                raise ValidationError({"chf_id": _("CHF ID must be unique")})

        # Validate date of birth
        if self.dob and self.dob > datetime.date.today():
            raise ValidationError({"dob": _("Date of birth cannot be in the future")})

        # Validate head of family
        if self.head and self.family:
            other_heads = self.family.members.filter(head=True).exclude(pk=self.pk)
            if other_heads.exists():
                raise ValidationError({"head": _("Family can only have one head")})

        # Validate identification number if type requires it
        if self.identification and self.identification.requires_validation:
            if not self.identification_number:
                raise ValidationError(
                    {
                        "identification_number": _(
                            "Identification number is required for this type"
                        )
                    }
                )

            if self.identification.validation_regex:
                import re

                if not re.match(
                    self.identification.validation_regex, self.identification_number
                ):
                    raise ValidationError(
                        {
                            "identification_number": _(
                                "Invalid identification number format"
                            )
                        }
                    )

    @hook(BEFORE_SAVE)
    def update_status_date(self):  # noqa: F811
        """Update status date when status changes."""
        if self.has_changed("status") and self.status:
            self.status_date = datetime.date.today()

    @hook(BEFORE_SAVE)
    def update_card_issued_date(self):  # noqa: F811
        """Update card issued date when card is issued."""
        if self.has_changed("card_issued") and self.card_issued:
            self.card_issued_date = datetime.date.today()

    def is_head_of_family(self):  # noqa: F811
        """Check if insuree is head of family."""
        return self.family and self.family.head_insuree == self

    def age(self, reference_date=None):  # noqa: F811
        """Calculate age with better precision."""
        if not self.dob:
            return None

        if reference_date is None:
            reference_date = datetime.date.today()

        age = reference_date.year - self.dob.year
        if (reference_date.month, reference_date.day) < (self.dob.month, self.dob.day):
            age -= 1

        return max(0, age)  # Ensure age is not negative

    def is_adult(self, reference_date=None):  # noqa: F811
        """Check if insuree is adult."""
        age = self.age(reference_date)
        return age >= AGE_OF_MAJORITY if age is not None else None

    @property
    def full_name(self):  # noqa: F811
        """Return full name."""
        return f"{self.other_names} {self.last_name}".strip()

    @property
    def is_active(self):  # noqa: F811
        """Check if insuree is active."""
        return self.status == InsureeStatus.ACTIVE

    def __str__(self):  # noqa: F811
        return f"{self.chf_id or 'No CHF ID'} - {self.full_name}"

    class Meta:  # noqa: F811
        managed = True
        db_table = "tblInsurees"
        verbose_name = _("Insuree")
        verbose_name_plural = _("Insurees")
        indexes = [
            models.Index(fields=["chf_id"], name="idx_insuree_chfid"),
            models.Index(fields=["last_name", "other_names"], name="idx_insuree_names"),
            models.Index(fields=["dob"], name="idx_insuree_dob"),
            models.Index(fields=["status"], name="idx_insuree_status"),
            models.Index(fields=["gender"], name="idx_insuree_gender"),
            models.Index(fields=["created_date"], name="idx_insuree_created"),
            models.Index(
                fields=["validity_from", "validity_to"], name="idx_insuree_validity"
            ),
            models.Index(
                fields=["identification_number"], name="idx_insuree_id_number"
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["chf_id"],
                condition=Q(chf_id__isnull=False),
                name="unique_chf_id",
            ),
            models.UniqueConstraint(
                fields=["family", "head"],
                condition=Q(head=True),
                name="unique_family_head",
            ),
            models.CheckConstraint(
                check=Q(dob__lte=datetime.date.today()),
                name="chk_insuree_dob_not_future",
            ),
        ]
