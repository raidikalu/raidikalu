
from django.conf import settings


BASE_RAID_IMAGE_URL = getattr(settings, 'RAIDIKALU_BASE_RAID_IMAGE_URL', '/static/img/raidicons/%s.png')
GOOGLE_ANALYTICS_ID = getattr(settings, 'GOOGLE_ANALYTICS_ID', None)
