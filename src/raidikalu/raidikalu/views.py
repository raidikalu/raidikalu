
import json
import logging
import re
from calendar import timegm
from datetime import timedelta
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from raidikalu.models import EditableSettings, Gym, Raid, DataSource, RaidVote


LOG = logging.getLogger(__name__)


class RaidListView(TemplateView):
  template_name = 'raidikalu/raid_list.html'

  def post(self, request, *args, **kwargs):
    action = request.POST.get('action', None)
    if action == 'set-nickname':
      request.session['nickname'] = request.POST.get('nickname', None)
      return HttpResponse('OK')
    return self.get(request, *args, **kwargs)

  def get_queryset(self):
    return Raid.objects.filter(end_at__gte=timezone.now()).select_related('gym').order_by('start_at')

  def get_context_data(self, **kwargs):
    context = super(RaidListView, self).get_context_data(**kwargs)
    context['editable_settings'] = EditableSettings.get_current_settings()
    context['raids'] = self.get_queryset()
    return context


class RaidCreateView(TemplateView):
  template_name = 'raidikalu/raid_create.html'
  ABSOLUTE_TIME_REGEX = re.compile(r'^(?P<hours>\d?\d).?(?P<minutes>\d\d)$')

  def post(self, request, *args, **kwargs):
    editable_settings = EditableSettings.get_current_settings()
    ALLOWED_TIERS = ['1', '2', '3', '4', '5']
    ALLOWED_POKEMON = [raid_type['pokemon'] for raid_type in editable_settings.raid_types]

    gym_id = request.POST.get('gym', None)
    gym = get_object_or_404(Gym, pk=gym_id)
    raid, created = Raid.objects.get_or_create(gym=gym)

    votes = []

    raid_start_at = self.get_raid_start_at()
    if raid_start_at:
      utc_timestamp = timegm(raid_start_at.utctimetuple())
      votes.append({
        'vote_field': RaidVote.FIELD_START_AT,
        'vote_value': utc_timestamp,
      })

    raid_boss = request.POST.get('raid-boss', None)
    if raid_boss and raid_boss.startswith('tier-'):
      tier = raid_boss.split('tier-')[1]
      if tier in ALLOWED_TIERS:
        votes.append({
          'vote_field': RaidVote.FIELD_TIER,
          'vote_value': int(tier),
        })
    elif raid_boss in ALLOWED_POKEMON:
      votes.append({
        'vote_field': RaidVote.FIELD_POKEMON,
        'vote_value': raid_boss,
      })

    for vote in votes:
      RaidVote.objects.create(raid=raid, vote_field=vote['vote_field'], vote_value=vote['vote_value'])

    raid.count_votes_and_update()
    return redirect('raidikalu.raid_list')

  def get_raid_start_at(self):
    raid_time_field_type = self.request.POST.get('raid-time-field-type', None)
    raid_time_value_type = self.request.POST.get('raid-time-value-type', None)
    raid_time_str = self.request.POST.get('raid-time', None)
    raid_time = None

    if raid_time_value_type == 'absolute':
      try:
        hours, minutes = self.ABSOLUTE_TIME_REGEX.match(raid_time_str).groups()
        hours = int(hours)
        minutes = int(minutes)
        raid_time = timezone.now()
        raid_time = raid_time.replace(hour=hours, minute=minutes)
      except AttributeError:
        LOG.error('Time input did not match')
      except ValueError:
        LOG.error('Time input not within bounds')
    elif raid_time_value_type == 'relative':
      try:
        minutes = int(raid_time_str)
        if minutes < 0 or minutes > 120:
          raise ValueError('Minutes not within bounds')
        raid_time = timezone.now() + timedelta(minutes=minutes)
      except ValueError:
        LOG.error('Time input not numeric or not within bounds')

    if not raid_time:
      return None

    if raid_time_field_type == 'start':
      raid_start_at = raid_time
    elif raid_time_field_type == 'end':
      raid_start_at = raid_time - Raid.RAID_BATTLE_DURATION
    else:
      raid_start_at = None

    return raid_start_at

  def get_context_data(self, **kwargs):
    context = super(RaidCreateView, self).get_context_data(**kwargs)
    context['editable_settings'] = EditableSettings.get_current_settings()
    context['gyms'] = Gym.objects.all().order_by('name').prefetch_related('nicknames')
    return context


class RaidJsonExportView(View):
  def get(self, request, *args, **kwargs):
    data_source_api_key = self.kwargs.get('api_key')
    data_source = DataSource.objects.get(api_key=data_source_api_key)
    already_received_raid_ids = RaidVote.objects.filter(data_source=data_source, vote_field=RaidVote.FIELD_POKEMON).values_list('raid_id', flat=True).distinct()
    raids = Raid.objects.exclude(id__in=already_received_raid_ids).select_related('gym')
    raids_json = []
    for raid in raids:
      raids_json.append({
        'id': raid.pk,
        'tier': raid.tier,
        'gym_id': raid.gym.pogo_id,
        'latitude': raid.gym.latitude,
        'longitude': raid.gym.longitude,
        'pokemon': raid.pokemon_name,
        'fast_move': raid.fast_move,
        'charge_move': raid.charge_move,
        'start_time': timegm(raid.start_at.utctimetuple()) if raid.start_at else None,
        'end_time': timegm(raid.end_at.utctimetuple()) if raid.end_at else None,
        'created_at': timegm(raid.created_at.utctimetuple()) if raid.created_at else None,
      })
    return JsonResponse(raids_json, safe=False, json_dumps_params={'separators': (',', ':')})


@method_decorator(csrf_exempt, name='dispatch')
class RaidReceiverView(View):
  def post(self, request, *args, **kwargs):
    data_source_api_key = self.kwargs.get('api_key')
    data_source = DataSource.objects.get(api_key=data_source_api_key)
    raid_data = json.loads(request.body)
    gym = Gym.objects.get(pogo_id=raid_data.get('gym_id'))
    raid, created = Raid.objects.get_or_create(gym=gym)

    votes = []

    if raid_data.get('tier', None):
      tier = raid_data.get('tier')
      votes.append({
        'vote_field': RaidVote.FIELD_TIER,
        'vote_value': tier,
      })

    if raid_data.get('pokemon', None):
      votes.append({
        'vote_field': RaidVote.FIELD_POKEMON,
        'vote_value': raid_data.get('pokemon'),
      })

    if raid_data.get('fast_move', None):
      fast_move = raid_data.get('fast_move')
      fast_move = re.sub(r'([A-Z])', r' \1', fast_move)
      votes.append({
        'vote_field': RaidVote.FIELD_FAST_MOVE,
        'vote_value': fast_move,
      })

    if raid_data.get('charge_move', None):
      charge_move = raid_data.get('charge_move')
      charge_move = re.sub(r'([A-Z])', r' \1', charge_move)
      votes.append({
        'vote_field': RaidVote.FIELD_CHARGE_MOVE,
        'vote_value': charge_move,
      })

    if raid_data.get('start_time', None):
      start_timestamp = int(raid_data.get('start_time'))
      is_microtime = start_timestamp > 1000000000000
      if is_microtime:
        start_timestamp = start_timestamp / 1000.0
      votes.append({
        'vote_field': RaidVote.FIELD_START_AT,
        'vote_value': str(int(start_timestamp)),
      })

    for vote in votes:
      RaidVote.objects.get_or_create(raid=raid, data_source=data_source, vote_field=vote['vote_field'], defaults=vote)

    raid.count_votes_and_update()
    return HttpResponse('OK')
