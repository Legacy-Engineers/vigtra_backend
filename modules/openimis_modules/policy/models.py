from django.db import models
from modules.openimis_modules.openimis_core import models as core_models


STATUS_CHOICES = [
    (1, "IDLE"),
    (2, "ACTIVE"),
    (4, "SUSPENDED"),
    (8, "EXPIRED"),
    (16, "READY"),
]


STAGE_CHOICES = [
    ("N", "New"),
    ("R", "Renewed"),
    ("C", "Cancelled"),
    ("E", "Expired"),
    ("S", "Suspended"),
    ("T", "Terminated"),
    ("X", "Closed"),
]

class Policy(core_models.VersionedModel):
    id = models.AutoField(primary_key=True)
    uuid = models.CharField(
        max_length=36, default=uuid.uuid4, unique=True
    )

    stage = models.CharField(
        max_length=1, blank=True, null=True, choices=STAGE_CHOICES
    )
    status = models.SmallIntegerField( blank=True, null=True)
    value = models.DecimalField(
        max_digits=18, decimal_places=2, blank=True, null=True
    )

    family = models.ForeignKey(
        Family, models.DO_NOTHING, null=True, blank=True
    )
    enroll_date = models.DateField()
    start_date = models.DateField()
    effective_date = models.DateField(blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)

    product = models.ForeignKey(
        Product, models.DO_NOTHING
    )
    officer = models.ForeignKey(
        Officer,
        models.DO_NOTHING,
        blank=True,
        null=True,
    )

    offline = models.BooleanField( blank=True, null=True)
    audit_user_id = models.IntegerField()
    contribution_plan = models.ForeignKey(
        ContributionPlan,
        models.DO_NOTHING,
        blank=True,
        null=True,
    )
    creation_date = models.DateField(
         default=django_tz.now, blank=True, null=True
    )

    def claim_ded_rems(self):
        return self.claim_ded_rems

    def is_new(self):
        return not self.stage or self.stage == Policy.STAGE_NEW

    def can_add_insuree(self):
        return (
            self.family.members.filter(validity_to__isnull=True).count()
            < self.product.max_members
        )

    class Meta:
        managed = True
        db_table = "tblPolicies"


    @classmethod
    def get_queryset(cls, queryset, user):
        queryset = Policy.filter_queryset(queryset)
        # GraphQL calls with an info object while Rest calls with the user itself
        if isinstance(user, ResolveInfo):
            user = user.context.user
        if settings.ROW_SECURITY and user.is_anonymous:
            return queryset.filter(id=-1)
        # TODO: check the access to the policy information but how ?
        #   Policy -> Product -> Location ? Policy -> Insurees -> HF -> Location ?
        # if settings.ROW_SECURITY:
        #     dist = UserDistrict.get_user_districts(user._u)
        #     return queryset.filter(
        #         health_facility__location_id__in=[l.location.id for l in dist]
        #     )

        return queryset