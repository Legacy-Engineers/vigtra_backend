import logging
import uuid
from datetime import datetime as py_datetime
from django.db import models


logger = logging.getLogger(__name__)


class ExtendableModel(models.Model):
    json_ext = models.JSONField(db_column="JsonExt", blank=True, null=True)

    class Meta:
        abstract = True


class UUIDModel(models.Model):
    """
    Abstract entity, parent of all (new) openIMIS entities.
    Enforces the UUID identifier.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True

    def __str__(self):
        return "[%s]" % (self.id,)


class BaseVersionedModel(models.Model):
    validity_from = models.DateTimeField(
        db_column="ValidityFrom", default=py_datetime.now
    )
    validity_to = models.DateTimeField(db_column="ValidityTo", blank=True, null=True)

    class Meta:
        abstract = True


class VersionedModel(BaseVersionedModel):
    legacy_id = models.IntegerField(db_column="LegacyID", blank=True, null=True)

    class Meta:
        abstract = True


class BaseCodeModel(models.Model):
    """Abstract base model for code-based lookup tables."""

    class Meta:
        abstract = True
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} - {getattr(self, 'name', getattr(self, 'description', self.code))}"
