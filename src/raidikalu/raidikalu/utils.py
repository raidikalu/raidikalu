
from django.core.cache import cache
from django.utils.translation import ugettext_lazy as _


def format_timedelta(timedelta_obj):
  hours, remainder = divmod(timedelta_obj.seconds, 3600)
  minutes, seconds = divmod(remainder, 60)
  return '%02d:%02d:%02d' % (hours, minutes, seconds)


def get_nickname(request):
  if request.session.get('nickname', None):
    return request.session['nickname']
  elif request.session.get('anonymous_nickname', None):
    return request.session['anonymous_nickname']
  else:
    anonymous_counter = cache.get('anonymous_nickname_counter') or 0
    anonymous_counter += 1
    cache.set('anonymous_nickname_counter' , anonymous_counter, 300 * 24 * 60 * 60)
    request.session['anonymous_nickname'] = _('#anonymous-nickname') % anonymous_counter
    return request.session['anonymous_nickname']

