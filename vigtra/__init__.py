from pathlib import Path
from modules.core.celery import app as celery_app
import os

BASE_DIR = Path(__file__).resolve().parent.parent

EXTRA_SETTINGS_CONFIG_FILE = os.path.join(BASE_DIR, "extra_settings.yaml")

__all__ = ("celery_app",)
