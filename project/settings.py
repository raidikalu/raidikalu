
import os
import dj_database_url

#
# Core configuration
#

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', '')

ALLOWED_HOSTS = []

ROOT_URLCONF = 'project.urls'

INSTALLED_APPS = [
  'raidikalu',

  'corsheaders',

  'django.contrib.admin',
  'django.contrib.auth',
  'django.contrib.contenttypes',
  'django.contrib.humanize',
  'django.contrib.sessions',
  'django.contrib.messages',
  'django.contrib.staticfiles',

  'channels',
]

MIDDLEWARE = [
  'django.middleware.security.SecurityMiddleware',
  'corsheaders.middleware.CorsMiddleware',
  'whitenoise.middleware.WhiteNoiseMiddleware',
  'django.contrib.sessions.middleware.SessionMiddleware',
  'django.middleware.common.CommonMiddleware',
  'django.middleware.csrf.CsrfViewMiddleware',
  'django.contrib.auth.middleware.AuthenticationMiddleware',
  'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
  'django.contrib.messages.middleware.MessageMiddleware',
  'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

TEMPLATES = [
  {
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [],
    'APP_DIRS': True,
    'OPTIONS': {
      'context_processors': [
        'django.template.context_processors.debug',
        'django.template.context_processors.request',
        'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
      ],
    },
  },
]

CHANNEL_LAYERS = {
  'default': {
    'BACKEND': 'asgiref.inmemory.ChannelLayer',
    'ROUTING': 'raidikalu.routing.channel_routing',
  },
}

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


#
# Database
#

is_windows = os.name == 'nt'

if is_windows:
  DEFAULT_DATABASE_URL = 'sqlite:///' + os.path.join(BASE_DIR, 'database.db')
else:
  DEFAULT_DATABASE_URL = 'sqlite:////' + os.path.join(BASE_DIR, 'database.db')

DATABASES = {
  'default': dj_database_url.config(default=DEFAULT_DATABASE_URL),
}


#
# Password validation
#

AUTH_PASSWORD_VALIDATORS = [
  {
    'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
  },
  {
    'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
  },
  {
    'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
  },
  {
    'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
  },
]


#
# Internationalization
#

LANGUAGE_CODE = 'fi'

TIME_ZONE = 'Europe/Helsinki'

USE_I18N = True

USE_L10N = True

USE_TZ = True


#
# Static files
#

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, '..', 'staticroot')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


#
# Cross-Origin Resource Sharing
#

CORS_ORIGIN_ALLOW_ALL = True
CORS_URLS_REGEX = r'^/api/.*$'


#
# Sessions
#

SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'
SESSION_COOKIE_AGE = 15769000 # about 6 months


#
# Raidikalu
#

RAIDIKALU_BASE_POKEMON_IMAGE_URL = os.environ.get('BASE_POKEMON_IMAGE_URL', '/static/img/pokemon/%s.png')
