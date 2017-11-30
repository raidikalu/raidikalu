
from raidikalu.settings import GOOGLE_ANALYTICS_ID

def settings_context(request):
  return {
    'GOOGLE_ANALYTICS_ID': GOOGLE_ANALYTICS_ID,
  }
