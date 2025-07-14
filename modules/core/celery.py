import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vigtra.settings")

app = Celery("vigtra")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Optional: Configure Celery Beat for periodic tasks
# app.conf.beat_schedule = {
#     "send-daily-report": {
#         "task": "your_app.tasks.send_daily_report",
#         "schedule": 30.0,  # Every 30 seconds (for testing)
#         # 'schedule': crontab(hour=9, minute=0),  # Daily at 9 AM
#     },
#     "cleanup-old-files": {
#         "task": "your_app.tasks.cleanup_old_files",
#         "schedule": 60.0 * 60,  # Every hour
#     },
# }

app.conf.timezone = "UTC"


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
