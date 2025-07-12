from .base import *
from .database import *
from .cache import *
from .graphql import *

# Import logging settings correctly (not logging_config)
from .logging import *

# Development-specific overrides
DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]
SECRET_KEY = "django-insecure-ctr^&ea2p9s8hoq3zkb_kvd$dm=o3abddh@9#6od34mypl9!84"
