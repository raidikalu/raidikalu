
import os
import re
from project.settings import *


SECURE_SSL_REDIRECT = True

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',')

RAVEN_CONFIG = {
  'dsn': os.environ.get('SENTRY_DSN', ''),
}

GOOGLE_ANALYTICS_ID = os.environ.get('GOOGLE_ANALYTICS_ID', None)

SCOUT_KEY = os.environ.get('SCOUT_KEY', '')
if SCOUT_KEY:
  SCOUT_MONITOR = True
  SCOUT_NAME = 'raidikalu'
  INSTALLED_APPS = [
    'scout_apm.django',
  ] + INSTALLED_APPS

INSTALLED_APPS += [
  'raven.contrib.django.raven_compat',
]

MIDDLEWARE = [
  'raven.contrib.django.raven_compat.middleware.Sentry404CatchMiddleware',
] + MIDDLEWARE

IGNORABLE_404_URLS = (
  re.compile('api/1/raid-snippet/[^/]+/'),
)

CHANNEL_LAYERS = {
  'default': {
    'BACKEND': 'channels.layers.InMemoryChannelLayer',
    'CONFIG': {
      'capacity': 400,
      'channel_capacity': {
        'http*': 200,
        'websocket*': 200,
      },
    },
  },
}

CACHES = {
  'default': {
    'BACKEND': 'django_bmemcached.memcached.BMemcached',
    'LOCATION': os.environ.get('MEMCACHEDCLOUD_SERVERS').split(','),
    'OPTIONS': {
      'username': os.environ.get('MEMCACHEDCLOUD_USERNAME'),
      'password': os.environ.get('MEMCACHEDCLOUD_PASSWORD'),
    },
  },
}

LOGGING = {
  'version': 1,
  'disable_existing_loggers': True,
  'root': {
    'level': 'WARNING',
    'handlers': ['sentry', 'console'],
  },
  'formatters': {
    'verbose': {
      'format': '%(asctime)s [%(process)d] [%(levelname)s] pathname=%(pathname)s lineno=%(lineno)s funcname=%(funcName)s %(message)s',
      'datefmt': '%Y-%m-%d %H:%M:%S',
    },
  },
  'handlers': {
    'sentry': {
      'level': 'WARNING',
      'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
    },
    'console': {
      'class': 'logging.StreamHandler',
      'formatter': 'verbose',
      'level': 'WARNING',
    },
  },
  'loggers': {
    'django': {
      'level': 'ERROR',
      'handlers': ['console'],
      'formatter': 'verbose',
    },
    'raven': {
      'level': 'DEBUG',
      'handlers': ['console'],
      'propagate': False,
    },
    'sentry.errors': {
      'level': 'DEBUG',
      'handlers': ['console'],
      'propagate': False,
    },
    'raidikalu': {
      'level': 'DEBUG',
      'handlers': ['console', 'sentry'],
      'formatter': 'verbose',
    },
    '': {
      'level': 'WARNING',
      'handlers': ['console', 'sentry'],
      'formatter': 'verbose',
    },
  },
}
