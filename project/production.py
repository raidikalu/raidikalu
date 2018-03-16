
import os
from project.settings import *


ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',')

RAVEN_CONFIG = {
  'dsn': os.environ.get('SENTRY_DSN', ''),
}

GOOGLE_ANALYTICS_ID = os.environ.get('GOOGLE_ANALYTICS_ID', None)

INSTALLED_APPS += [
  'raven.contrib.django.raven_compat',
]

MIDDLEWARE = [
  'raven.contrib.django.raven_compat.middleware.Sentry404CatchMiddleware',
] + MIDDLEWARE

CHANNEL_LAYERS = {
  'default': {
    'BACKEND': 'asgi_redis.RedisChannelLayer',
    'CONFIG': {
      'hosts': [os.environ.get('REDIS_URL', 'redis://localhost:6379')],
    },
    'ROUTING': 'raidikalu.routing.channel_routing',
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
      'level': 'DEBUG',
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
