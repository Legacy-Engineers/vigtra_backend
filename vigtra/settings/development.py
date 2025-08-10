from split_settings.tools import include
from vigtra.settings import SETTINGS
from datetime import timedelta
import secrets

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]
# Auto-generate temporary Django secret key for development
INTERNAL_IPS = ["127.0.0.1"]

# JWT Settings


include(*SETTINGS)
