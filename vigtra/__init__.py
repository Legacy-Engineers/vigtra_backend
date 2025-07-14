from pathlib import Path
from modules.core.celery import app as celery_app

BASE_DIR = Path(__file__).resolve().parent.parent

__all__ = ("celery_app",)
