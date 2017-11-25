
from django.conf import settings


BASE_POKEMON_IMAGE_URL = getattr(settings, 'RAIDIKALU_BASE_POKEMON_IMAGE_URL', '/static/img/pokemon/%s.png')

