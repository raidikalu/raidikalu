
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')


from django.core.wsgi import get_wsgi_application
from whitenoise.django import DjangoWhiteNoise

application = get_wsgi_application()

# static files are served with whitenoise
# see more: https://devcenter.heroku.com/articles/django-assets
application = DjangoWhiteNoise(application) # serve static files
