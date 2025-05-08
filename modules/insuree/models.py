import uuid
import core
from modules.openimis_core import models as core_models
from django.db import models
from location import models as location_models


class Gender(models.Model):
    code = models.CharField(db_column="Code", primary_key=True, max_length=1)
    gender = models.CharField(db_column="Gender", max_length=50, blank=True, null=True)

    class Meta:
        managed = True
        db_table = "tblGender"


class FamilyType(models.Model):
    code = models.CharField(db_column="FamilyTypeCode", primary_key=True, max_length=2)
    type = models.CharField(db_column="FamilyType", max_length=50)

    class Meta:
        managed = True
        db_table = "tblFamilyTypes"


class Family(core_models.VersionedModel, core_models.ExtendableModel):
    id = models.AutoField(db_column="FamilyID", primary_key=True)
    uuid = models.CharField(
        db_column="FamilyUUID", max_length=36, default=uuid.uuid4, unique=True
    )
    # needed because the version model: on head can be on several families (diff validity_to)
    head_insuree = models.ForeignKey(
        "Insuree",
        models.DO_NOTHING,
        db_column="InsureeID",
        null=False,
        related_name="head_of",
    )
    location = models.ForeignKey(
        location_models.Location,
        models.DO_NOTHING,
        db_column="LocationId",
        blank=True,
        null=True,
    )
    poverty = models.BooleanField(db_column="Poverty", blank=True, null=True)
    family_type = models.ForeignKey(
        FamilyType,
        models.DO_NOTHING,
        db_column="FamilyType",
        blank=True,
        null=True,
        related_name="families",
    )
    address = models.CharField(
        db_column="FamilyAddress", max_length=200, blank=True, null=True
    )
    is_offline = models.BooleanField(db_column="isOffline", blank=True, null=True)
    ethnicity = models.CharField(
        db_column="Ethnicity", max_length=1, blank=True, null=True
    )
    confirmation_no = models.CharField(
        db_column="ConfirmationNo", max_length=12, blank=True, null=True
    )
    audit_user_id = models.IntegerField(db_column="AuditUserID")

    def __str__(self):
        return str(self.head_insuree)

    @classmethod
    def filter_queryset(cls, queryset=None):
        if queryset is None:
            queryset = cls.objects.all()
        return queryset

    class Meta:
        managed = True
        db_table = "tblFamilies"


class Profession(models.Model):
    id = models.SmallIntegerField(db_column="ProfessionId", primary_key=True)
    profession = models.CharField(db_column="Profession", max_length=50)

    class Meta:
        managed = True
        db_table = "tblProfessions"


class Education(models.Model):
    id = models.SmallIntegerField(db_column="EducationId", primary_key=True)
    education = models.CharField(db_column="Education", max_length=50)

    class Meta:
        managed = True
        db_table = "tblEducations"


class IdentificationType(models.Model):
    code = models.CharField(
        db_column="IdentificationCode", primary_key=True, max_length=1
    )
    identification_type = models.CharField(
        db_column="IdentificationTypes", max_length=50
    )

    class Meta:
        managed = True
        db_table = "tblIdentificationTypes"


class Relation(models.Model):
    id = models.SmallIntegerField(db_column="RelationId", primary_key=True)
    relation = models.CharField(db_column="Relation", max_length=50)

    class Meta:
        managed = True
        db_table = "tblRelations"


class InsureeStatus(models.TextChoices):
    ACTIVE = "AC"
    INACTIVE = "IN"
    DEAD = "DE"


class InsureeStatusReason(core_models.VersionedModel):
    id = models.SmallIntegerField(db_column="StatusReasonId", primary_key=True)
    insuree_status_reason = models.CharField(db_column="StatusReason", max_length=50)
    code = models.CharField(db_column="Code", max_length=5)
    status_type = models.CharField(
        max_length=2, choices=InsureeStatus.choices, default=InsureeStatus.ACTIVE
    )

    class Meta:
        managed = True
        db_table = "tblInsureeStatusReason"


class Insuree(core_models.VersionedModel, core_models.ExtendableModel):
    id = models.AutoField(db_column="InsureeID", primary_key=True)
    uuid = models.CharField(
        db_column="InsureeUUID", max_length=36, default=uuid.uuid4, unique=True
    )

    family = models.ForeignKey(
        Family,
        models.DO_NOTHING,
        blank=True,
        null=True,
        db_column="FamilyID",
        related_name="members",
    )
    chf_id = models.CharField(db_column="CHFID", max_length=50, blank=True, null=True)
    last_name = models.CharField(db_column="LastName", max_length=100)
    other_names = models.CharField(db_column="OtherNames", max_length=100)

    gender = models.ForeignKey(
        Gender,
        models.DO_NOTHING,
        db_column="Gender",
        blank=True,
        null=True,
    )
    dob = core.fields.DateField(db_column="DOB", blank=True, null=True)

    head = models.BooleanField(db_column="IsHead", default=False)
    marital = models.CharField(db_column="Marital", max_length=1, blank=True, null=True)

    passport = models.CharField(max_length=25, blank=True, null=True)
    phone = models.CharField(db_column="Phone", max_length=50, blank=True, null=True)
    email = models.CharField(db_column="Email", max_length=100, blank=True, null=True)
    current_address = models.CharField(
        db_column="CurrentAddress", max_length=200, blank=True, null=True
    )
    geolocation = models.CharField(
        db_column="GeoLocation", max_length=250, blank=True, null=True
    )
    current_village = models.ForeignKey(
        location_models.Location,
        models.DO_NOTHING,
        blank=True,
        null=True,
    )
    photo = models.FileField(
        db_column="Photo",
        upload_to="insuree/photos/",
        blank=True,
        null=True,
        max_length=255,
    )
    photo_date = models.DateField(db_column="PhotoDate", blank=True, null=True)
    card_issued = models.BooleanField(db_column="CardIssued", blank=True, null=True)
    relationship = models.ForeignKey(
        Relation,
        models.DO_NOTHING,
        db_column="Relationship",
        blank=True,
        null=True,
    )
    profession = models.ForeignKey(
        Profession,
        models.DO_NOTHING,
        blank=True,
        null=True,
    )
    education = models.ForeignKey(
        Education,
        models.DO_NOTHING,
        blank=True,
        null=True,
    )
    identification = models.ForeignObject(
        IdentificationType,
        on_delete=models.DO_NOTHING,
    )
    health_facility = models.ForeignKey(
        location_models.HealthFacility,
        models.DO_NOTHING,
        blank=True,
        null=True,
    )

    offline = models.BooleanField(db_column="isOffline", blank=True, null=True)
    status = models.CharField(
        max_length=2,
        choices=InsureeStatus.choices,
        default=InsureeStatus.ACTIVE,
        blank=True,
        null=True,
    )
    status_date = core.fields.DateField(db_column="status_date", null=True, blank=True)
    status_reason = models.ForeignKey(
        InsureeStatusReason,
        models.DO_NOTHING,
        blank=True,
        null=True,
    )
    audit_user_id = models.IntegerField(db_column="AuditUserID")

    def is_head_of_family(self):
        return self.family and self.family.head_insuree == self

    def __str__(self):
        return f"{self.chf_id} {self.last_name} {self.other_names}"

    def age(self, reference_date=None):
        if self.dob:
            today = (
                core.datetime.date.today() if reference_date is None else reference_date
            )
            before_birthday = (today.month, today.day) < (self.dob.month, self.dob.day)
            return today.year - self.dob.year - before_birthday
        else:
            return None

    def is_adult(self, reference_date=None):
        if self.dob:
            return self.age(reference_date) >= core.age_of_majority
        else:
            return None

    @classmethod
    def filter_queryset(cls, queryset=None):
        if queryset is None:
            queryset = cls.objects.all()
        return queryset

    class Meta:
        managed = True
        db_table = "tblInsuree"


class InsureePolicy(core_models.VersionedModel):
    id = models.AutoField(db_column="InsureePolicyID", primary_key=True)

    insuree = models.ForeignKey(
        Insuree,
        models.DO_NOTHING,
        db_column="InsureeRefID",
        related_name="insuree_policies",
    )
    policy = models.ForeignKey(
        "policy.Policy",
        models.DO_NOTHING,
        db_column="PolicyRefID",
        related_name="insuree_policies",
    )

    enrollment_date = core.fields.DateField(
        db_column="PolicyEnrollmentDate", blank=True, null=True
    )
    start_date = core.fields.DateField(db_column="PolicyStartDate", blank=True, null=True)
    effective_date = core.fields.DateField(
        db_column="PolicyEffectiveDate", blank=True, null=True
    )
    expiry_date = core.fields.DateField(db_column="PolicyExpiryDate", blank=True, null=True)

    offline = models.BooleanField(db_column="PolicyIsOffline", blank=True, null=True)
    audit_user_id = models.IntegerField(db_column="PolicyAuditUserID")

    @classmethod
    def filter_queryset(cls, queryset=None):
        if queryset is None:
            queryset = cls.objects.all()
        return queryset

    class Meta:
        managed = True
        db_table = "tblInsureePolicy"


class PolicyRenewalDetail(core_models.VersionedModel):
    """
    When there is a policy renewal in progress, there might also be a need to update the picture or something else.
    As this part is quite specific to the insuree, it is handled in this module rather than policy (like PolicyRenewal)
    """

    id = models.AutoField(db_column="RenewalDetailID", primary_key=True)

    insuree = models.ForeignKey(
        "insuree.Insuree",
        models.DO_NOTHING,
        db_column="InsureeID",
        related_name="policy_renewal_details",
    )
    policy_renewal = models.ForeignKey(
        "policy.PolicyRenewal",
        models.DO_NOTHING,
        db_column="RenewalID",
        related_name="details",
    )

    class Meta:
        managed = True
        db_table = "tblPolicyRenewalDetails"
