import os

SECRET_KEY = os.getenv("DJANGO_SECRET", None)
DEBUG = False
ALLOWED_HOSTS = []
