import os
from .settings import BASE_DIR


DEBUG=False

ADMINS = (('Ilias Stamatis', 'stamatis.iliass@example.com'), )
MANAGERS = ADMINS

SECRET_KEY = os.environ['SECRET_KEY']

ALLOWED_HOSTS = ['localhost']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# email settings
EMAIL_HOST = 'smtp.example.com'
EMAIL_PORT = -1
EMAIL_HOST_USER = 'user'
EMAIL_HOST_PASSWORD = 'password'
EMAIL_USE_TLS = False

# Compress static files
COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True

RECAPTCHA_PRIVATE_KEY = os.environ['RECAPTCHA_PRIVATE_KEY']
