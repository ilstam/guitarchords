import os
from .settings import BASE_DIR

DEBUG=True

SECRET_KEY = 'p-gvap=o0(jm%14k&zn5wc4-u!7b-3#6#z@-@y)%$-k)!-u5)*'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

DUMMY_CACHE = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

CACHES = DUMMY_CACHE
