from django.db import models

# Create your models here.


class Organization(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    address = models.JSONField(blank=True, null=True)
    phone = models.CharField(max_length=16, blank=True, null=True)
    fax = models.CharField(max_length=16, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    website = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = "tblOrganization"

    def __str__(self):
        return self.name
