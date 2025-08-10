from split_settings.tools import include
from vigtra.settings import SETTINGS

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]
SECRET_KEY = "django-insecure-ctr^&ea2p9s8hoq3zkb_kvd$dm=o3abddh@9#6od34mypl9!84"
INTERNAL_IPS = ["127.0.0.1"]

include(*SETTINGS)
