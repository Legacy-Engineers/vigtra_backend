from django.db import models
from modules.authentication.models import User

ACTION_CHOICES = [
    (1, "Created"),
    (2, "Updated"),
    (3, "Deleted"),
    (4, "Restored"),
    (5, "Archived"),
    (6, "Unarchived"),
    (7, "Imported"),
    (8, "Exported"),
    (9, "Synced"),
    (10, "Merged"),
    (11, "Split"),
    (12, "Approved"),
    (13, "Rejected"),
    (14, "Cancelled"),
    (15, "Completed"),
    (16, "Failed"),
    (17, "Started"),
    (18, "Paused"),
    (19, "Resumed"),
    (20, "Stopped"),
    (21, "Restarted"),
    (22, "Scheduled"),
    (23, "Unschedule"),
    (24, "Locked"),
    (25, "Unlocked"),
    (26, "Verified"),
    (27, "Unverified"),
    (28, "Confirmed"),
    (29, "Unconfirmed"),
    (30, "Published"),
    (31, "Unpublished"),
    (32, "Drafted"),
    (33, "Undrafted"),
]

REQUEST_RESULT_TYPE_CHOICES = [
    (1, "Successful"),
    (2, "Failed"),
    (3, "Unauthorized"),
    (4, "Forbidden"),
    (5, "Not Found"),
    (6, "Conflict"),
    (7, "Internal Server Error"),
    (8, "Bad Request"),
    (9, "Service Unavailable"),
    (10, "Gateway Timeout"),
]


class ChangeLog(models.Model):
    module = models.CharField(max_length=20)
    model = models.CharField(max_length=20)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    data = models.JSONField(null=True, blank=True)
    object_repr = models.CharField(max_length=255)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, null=True, blank=True)
    request_header = models.JSONField(null=True, blank=True)

    success = models.BooleanField(default=True)
    request_result_type = models.CharField(
        max_length=5, choices=REQUEST_RESULT_TYPE_CHOICES, null=True, blank=True
    )
    error_message = models.TextField(null=True, blank=True)
    error_code = models.CharField(max_length=50, null=True, blank=True)
    api_type = models.CharField(
        max_length=2,
        choices=[
            (1, "Graphql"),
            (2, "Rest"),
            (3, "Web"),
        ],
        default=2,
    )

    class Meta:
        verbose_name = "Change Log"
        verbose_name_plural = "Change Logs"
        ordering = ["-timestamp"]
        db_table = "tblChangeLogs"
