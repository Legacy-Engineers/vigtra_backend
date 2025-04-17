import json
import os
import logging
import sys
import uuid

from datetime import datetime as py_datetime
import datetime as base_datetime
from cached_property import cached_property

from dirtyfields import DirtyFieldsMixin
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import models
from django.db.models import Q, DO_NOTHING, F, JSONField
from pandas import DataFrame
from simple_history.models import HistoricalRecords
from django.db.models.signals import pre_save
from django.dispatch import receiver

# from core.datetimes.ad_datetime import datetime as py_datetime
from core.fields import DateTimeField
from core.utils import filter_validity

from django.db import models
from django.db.models import Q, JSONField


logger = logging.getLogger(__name__)


class ExtendableModel(models.Model):
    json_ext = JSONField(db_column="JsonExt", blank=True, null=True)

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


class ModuleConfiguration(UUIDModel):
    """
    Generic entity to save every modules' configuration (json format)
    """

    module = models.CharField(max_length=80)
    MODULE_LAYERS = [("fe", "frontend"), ("be", "backend")]
    layer = models.CharField(
        max_length=2,
        choices=MODULE_LAYERS,
        default="be",
    )
    version = models.CharField(max_length=10)
    config = models.TextField()
    # is_exposed indicates wherever a configuration is safe to be accessible from api
    # DON'T EXPOSE (backend) configurations that contain credentials,...
    is_exposed = models.BooleanField(default=False)
    is_disabled_until = models.DateTimeField(default=None, blank=True, null=True)

    @classmethod
    def get_or_default(cls, module, default, layer="be"):
        if bool(os.environ.get("NO_DATABASE", False)):
            logger.info(
                "env NO_DATABASE set to True: ModuleConfiguration not loaded from db!"
            )
            return default

        try:
            now = py_datetime.now()  # can't use core config here...
            qs = cls.objects.filter(
                Q(is_disabled_until=None) | Q(is_disabled_until__lt=now),
                layer=layer,
                module=module,
            ).first()
            if qs:
                db_configuration = qs._cfg
                return {**default, **db_configuration}
            else:
                logger.info("No %s configuration, using default!" % module)
                return default
        except Exception:
            logger.error(
                "Failed to load %s configuration, using default!\n%s: %s"
                % (module, sys.exc_info()[0].__name__, sys.exc_info()[1])
            )
            return default

    @cached_property
    def _cfg(self):
        import collections

        return json.loads(self.config, object_pairs_hook=collections.OrderedDict)

    def __str__(self):
        return "%s [%s]" % (self.module, self.version)

    class Meta:
        db_table = "core_ModuleConfiguration"


class FieldControl(UUIDModel):
    module = models.ForeignKey(
        ModuleConfiguration, models.DO_NOTHING, related_name="controls"
    )
    field = models.CharField(unique=True, max_length=250)
    # mask: Hidden | Readonly | Mandatory
    usage = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = "core_FieldControl"
