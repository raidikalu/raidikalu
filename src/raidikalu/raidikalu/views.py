
import json
import re
from django.http import HttpResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from raidikalu.models import EditableSettings, Gym, Raid, DataSource, RaidVote


class RaidListView(TemplateView):
  template_name = 'raidikalu/raid_list.html'

  def get_queryset(self):
    return Raid.objects.all().select_related('gym').order_by('start_at')

  def get_context_data(self, **kwargs):
    context = super(RaidListView, self).get_context_data(**kwargs)

    context['editable_settings'] = EditableSettings.get_current_settings()
    context['raids'] = self.get_queryset()

    return context


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
