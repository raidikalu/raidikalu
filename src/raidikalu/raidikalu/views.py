
import json
import logging
import re
from base64 import b64encode
from calendar import timegm
from datetime import timedelta, datetime
from django.core.cache import cache
from django.db.models.signals import post_save, pre_delete
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from raidikalu.messages import attendance_updated
from raidikalu.models import EditableSettings, Gym, Raid, DataSource, RaidVote, Attendance
from raidikalu.utils import get_nickname


LOG = logging.getLogger(__name__)


class BaseRaidView(TemplateView):
  def update_raid_context(self, raid):
    nickname = get_nickname(self.request)
    setattr(raid, 'own_start_time_choice', None)
    start_times_with_attendances = []
    raid_attendances = raid.attendances.all()
    for choice_index, start_time_choice in enumerate(raid.get_start_time_choices()):
      attendances_at_time = []
      for attendance in raid_attendances:
        if attendance.start_time_choice == choice_index:
          attendances_at_time.append(attendance)
          if attendance.submitter == nickname:
            setattr(raid, 'own_start_time_choice', choice_index)
      start_times_with_attendances.append({
        'time': start_time_choice,
        'attendances': attendances_at_time,
      })
    setattr(raid, 'start_times_with_attendances', start_times_with_attendances)
    setattr(raid, 'attendance_count', len(raid_attendances))


class RaidListView(BaseRaidView):
  template_name = 'raidikalu/raid_list.html'
  NICKNAME_CLEANUP_REGEX = re.compile(r'[^A-Za-z0-9]+')

  def post(self, request, *args, **kwargs):
    action = request.POST.get('action', None)

    if action == 'set-nickname':
      nickname = request.POST.get('nickname', None)
      nickname = self.NICKNAME_CLEANUP_REGEX.sub('', nickname)
      nickname = nickname[:16]
      old_nickname = get_nickname(request)
      if old_nickname.startswith('Anonyymi '):
        Attendance.objects.filter(submitter=old_nickname).update(submitter=nickname)
      request.session['nickname'] = nickname
      return HttpResponse('OK')

    if action == 'set-attendance':
      nickname = get_nickname(request)
      raid = get_object_or_404(Raid, pk=request.POST.get('raid', None))
      choice = request.POST.get('choice', '')
      if choice == 'cancel':
        try:
          attendance = Attendance.objects.get(raid=raid, submitter=nickname)
          attendance.start_time_choice = None
          attendance_updated(attendance, raid)
          attendance.delete()
        except Attendance.DoesNotExist:
          return HttpResponse('fail')
        return HttpResponse('OK')
      try:
        choice = int(choice)
      except ValueError:
        return HttpResponse('fail')
      start_time_choices = raid.get_start_time_choices()
      if choice < 0 or choice >= len(start_time_choices):
        return HttpResponse('fail')
      attendance, created = Attendance.objects.get_or_create(raid=raid, submitter=nickname, defaults={'start_time_choice': choice})
      if not created:
        attendance.start_time_choice = choice
        attendance.save()
      attendance_updated(attendance, raid)
      return HttpResponse('OK')
    return self.get(request, *args, **kwargs)

  def get_queryset(self):
    return Raid.objects.exclude(end_at__lte=timezone.now()).select_related('gym').prefetch_related('attendances').order_by('start_at')

  def get_context_data(self, **kwargs):
    context = super(RaidListView, self).get_context_data(**kwargs)
    context['editable_settings'] = EditableSettings.get_current_settings()
    context['raids'] = self.get_queryset()
    context['request_nickname'] = get_nickname(self.request)
    context['now'] = timezone.now()
    for raid in context['raids']:
      self.update_raid_context(raid)
    return context


class RaidSnippetView(BaseRaidView):
  template_name = 'raidikalu/raid_snippet.html'
  CACHE_TIMEOUT = 2 * 60 * 60

  def dispatch(self, request, **kwargs):
    raid_pk = self.kwargs.get('pk')
    cache_key = 'raid_snippet_response_%s' % raid_pk
    response = cache.get(cache_key)
    if response:
      return response
    self.raid = get_object_or_404(Raid, pk=raid_pk)
    response = super(RaidSnippetView, self).dispatch(request, **kwargs)
    if hasattr(response, 'render') and callable(response.render):
      response.add_post_render_callback(lambda r: cache.set(cache_key, r, self.CACHE_TIMEOUT))
    else:
      cache.set(cache_key, response, self.CACHE_TIMEOUT)
    return response

  def get_context_data(self, **kwargs):
    context = super(RaidSnippetView, self).get_context_data(**kwargs)
    self.update_raid_context(self.raid)
    context['raid'] = self.raid
    context['now'] = timezone.now()
    return context

def invalidate_raid_snippet_from_raid(instance, **kwargs):
  cache_key = 'raid_snippet_response_%s' % instance.pk
  cache.delete(cache_key)

def invalidate_raid_snippet_from_attendance(instance, **kwargs):
  cache_key = 'raid_snippet_response_%s' % instance.raid_id
  cache.delete(cache_key)

post_save.connect(invalidate_raid_snippet_from_raid, sender='raidikalu.Raid')
post_save.connect(invalidate_raid_snippet_from_attendance, sender='raidikalu.Attendance')
pre_delete.connect(invalidate_raid_snippet_from_attendance, sender='raidikalu.Attendance')



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

    if created:
      raid.submitter = request.session.get('nickname', None) or ''

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

    if not raid_time_str:
      return None

    if raid_time_value_type == 'absolute':
      try:
        hours, minutes = self.ABSOLUTE_TIME_REGEX.match(raid_time_str).groups()
        hours = int(hours)
        minutes = int(minutes)
        raid_time = timezone.now()
        raid_time = raid_time.astimezone(timezone.get_current_timezone())
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

    start_at = datetime.fromtimestamp(start_timestamp)
    start_at = timezone.make_aware(start_at, timezone.get_current_timezone())
    end_at = start_at + Raid.RAID_BATTLE_DURATION
    if end_at <= timezone.now():
      return HttpResponse('OK')

    gym = Gym.objects.get(pogo_id=raid_data.get('gym_id'))
    raid, created = Raid.objects.get_or_create(gym=gym)

    for vote in votes:
      RaidVote.objects.get_or_create(raid=raid, data_source=data_source, vote_field=vote['vote_field'], defaults=vote)

    raid.count_votes_and_update()
    return HttpResponse('OK')
