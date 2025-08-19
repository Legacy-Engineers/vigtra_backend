"""
Static files optimization settings for production
"""
import os
from pathlib import Path
from .. import BASE_DIR

# Static files optimization
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# Enable GZip compression for static files
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

# Static files directories
STATICFILES_DIRS = [
    BASE_DIR / "static",
    BASE_DIR / "assets",  # For compiled assets
]

# Media files optimization
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# File upload optimization
FILE_UPLOAD_MAX_MEMORY_SIZE = 2621440  # 2.5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880   # 5MB
FILE_UPLOAD_TEMP_DIR = os.path.join(BASE_DIR, 'tmp')

# Create temp directory if it doesn't exist
Path(FILE_UPLOAD_TEMP_DIR).mkdir(exist_ok=True)

# Static files caching headers (for nginx/apache)
if not os.getenv('DEBUG', 'False').lower() == 'true':
    # Production static file settings
    STATIC_URL = '/static/'
    STATIC_ROOT = BASE_DIR / 'staticfiles'
    
    # Enable static file compression
    COMPRESS_ENABLED = True
    COMPRESS_OFFLINE = True
    COMPRESS_CSS_FILTERS = [
        'compressor.filters.css_default.CssAbsoluteFilter',
        'compressor.filters.cssmin.rCSSMinFilter',
    ]
    COMPRESS_JS_FILTERS = [
        'compressor.filters.jsmin.JSMinFilter',
    ]
    
    # Compress storage
    COMPRESS_STORAGE = 'compressor.storage.GzipCompressorFileStorage'
    COMPRESS_URL = STATIC_URL
    COMPRESS_ROOT = STATIC_ROOT

# Browser caching headers (to be used with web server)
STATICFILES_MAX_AGE = 31536000  # 1 year

# Whitenoise configuration for serving static files
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = False
WHITENOISE_MAX_AGE = 31536000  # 1 year
WHITENOISE_SKIP_COMPRESS_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'zip', 'gz', 'tgz', 'bz2', 'tbz', 'xz', 'br']