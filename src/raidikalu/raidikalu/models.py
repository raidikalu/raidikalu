
import json
import logging
from datetime import timedelta, datetime
from django.db import models
from django.db.models import Count, Q
from django.utils import timezone
from raidikalu import settings
from raidikalu.pokedex import get_pokemon_number_by_name


LOG = logging.getLogger(__name__)


class TimestampedModel(models.Model):
  created_at = models.DateTimeField(editable=False, default=timezone.now)
  updated_at = models.DateTimeField(editable=False)

  class Meta:
    abstract = True

  def save(self, *args, **kwargs):
    self.updated_at = timezone.now()
    return super(TimestampedModel, self).save(*args, **kwargs)


class EditableSettings(models.Model):
  expires_at = models.DateTimeField()
  raid_types_json = models.TextField()
  _current_settings = None

  def __init__(self, *args, **kwargs):
    super(EditableSettings, self).__init__(*args, **kwargs)
    try:
      raid_types = json.loads(self.raid_types_json)
      for raid_type in raid_types:
        raid_type['pokemon_number'] = get_pokemon_number_by_name(raid_type['pokemon'])
        raid_type['pokemon_image'] = settings.BASE_POKEMON_IMAGE_URL.format(raid_type['pokemon_number'])
      setattr(self, 'raid_types', raid_types)
    except (TypeError, json.decoder.JSONDecodeError) as e:
      setattr(self, 'raid_types', [])

  @classmethod
  def load_current_settings(cls):
    try:
      return cls.objects.filter(expires_at__lt=timezone.now()).earliest('expires_at')
    except cls.DoesNotExist:
      pass
    try:
      return cls.objects.latest('expires_at')
    except cls.DoesNotExist:
      pass
    return cls.objects.create(**{
      'expires_at': timezone.now(),
      'raid_types_json': '[{"tier":1, "pokemon":"Pidgey"}]',
    })

  @classmethod
  def get_current_settings(cls):
    if cls._current_settings and cls._current_settings.expires_at > timezone.now():
      return cls._current_settings
    cls._current_settings = cls.load_current_settings()
    return cls._current_settings

  @classmethod
  def get_tier_for_pokemon(cls, pokemon_name):
    editable_settings = EditableSettings.get_current_settings()
    for raid_type in editable_settings.raid_types:
      if raid_type['pokemon'] == pokemon_name:
        return raid_type['tier']
    return None

  def save(self, *args, **kwargs):
    EditableSettings._current_settings = None
    return super(EditableSettings, self).save(*args, **kwargs)

  def __str__(self):
    return 'Settings until %s' % str(self.expires_at)


class DataSource(models.Model):
  name = models.CharField(max_length=255)
  api_key = models.CharField(max_length=2048)

  def __str__(self):
    return self.name


class Gym(TimestampedModel):
  name = models.CharField(max_length=2048)
  pogo_id = models.CharField(max_length=255, blank=True)
  latitude = models.DecimalField(max_digits=9, decimal_places=6)
  longitude = models.DecimalField(max_digits=9, decimal_places=6)
  image_url = models.CharField(max_length=2048, blank=True)

  def __str__(self):
    return self.name


class GymNickname(TimestampedModel):
  gym = models.ForeignKey(Gym, related_name='nicknames', on_delete=models.CASCADE)
  nickname = models.CharField(max_length=2048)

  def __str__(self):
    return '%s // %s' % (self.gym.name, self.nickname)


class Raid(TimestampedModel):
  RAID_EGG_DURATION = timedelta(hours=1)
  RAID_BATTLE_DURATION = timedelta(hours=1)
  RAID_DURATION = RAID_EGG_DURATION + RAID_BATTLE_DURATION

  gym = models.ForeignKey(Gym, related_name='raids', on_delete=models.CASCADE)
  tier = models.PositiveSmallIntegerField(null=True, blank=True)
  pokemon_name = models.CharField(max_length=255, blank=True)
  pokemon_number = models.PositiveSmallIntegerField(null=True, blank=True)
  fast_move = models.CharField(max_length=255, blank=True)
  charge_move = models.CharField(max_length=255, blank=True)
  start_at = models.DateTimeField(null=True, blank=True)
  end_at = models.DateTimeField(null=True, blank=True)

  def save(self, *args, **kwargs):
    if self.pokemon_name and not self.tier:
      self.tier = EditableSettings.get_tier_for_pokemon(self.pokemon_name)
    self.end_at = self.start_at + Raid.RAID_BATTLE_DURATION if self.start_at else None
    self.pokemon_number = get_pokemon_number_by_name(self.pokemon_name)
    Raid.objects.filter(Q(end_at__lt=timezone.now()) | Q(created_at__lt=timezone.now() - Raid.RAID_DURATION)).delete()
    return super(Raid, self).save(*args, **kwargs)

  @property
  def has_started(self):
    return timezone.now() >= self.start_at

  def get_pokemon_image_url(self):
    return settings.BASE_POKEMON_IMAGE_URL.format(self.pokemon_number)

  def get_time_left_until_start(self):
    return self.start_at - timezone.now()

  def get_time_left_until_end(self):
    return self.end_at - timezone.now()

  def get_time_left_until_start_display(self):
    return format_timedelta(self.get_time_left_until_start())

  def get_time_left_until_end_display(self):
    return format_timedelta(self.get_time_left_until_end())

  def count_votes_and_update(self):
    tier = RaidVote.get_top_value(self, RaidVote.FIELD_TIER)
    if tier is not None:
      self.tier = int(tier)

    pokemon = RaidVote.get_top_value(self, RaidVote.FIELD_POKEMON)
    if pokemon is not None:
      self.pokemon_name = pokemon

    fast_move = RaidVote.get_top_value(self, RaidVote.FIELD_FAST_MOVE)
    if fast_move is not None:
      self.fast_move = fast_move

    charge_move = RaidVote.get_top_value(self, RaidVote.FIELD_CHARGE_MOVE)
    if charge_move is not None:
      self.charge_move = charge_move

    start_timestamp = RaidVote.get_top_value(self, RaidVote.FIELD_START_AT)
    if start_timestamp is not None:
      start_timestamp = int(start_timestamp)
      start_at = datetime.fromtimestamp(start_timestamp)
      start_at = timezone.make_aware(start_at, timezone.get_current_timezone())
      self.start_at = start_at

    self.save()

  def __str__(self):
    return '%s // %s' % (self.gym.name, self.pokemon_name)


class RaidVote(TimestampedModel):
  FIELD_TIER = 'tier'
  FIELD_POKEMON = 'pokemon'
  FIELD_FAST_MOVE = 'fast_move'
  FIELD_CHARGE_MOVE = 'charge_move'
  FIELD_START_AT = 'start_at'
  FIELD_CHOICES = (
    (FIELD_TIER, 'Taso'),
    (FIELD_POKEMON, 'Pokémon'),
    (FIELD_FAST_MOVE, 'Fast move'),
    (FIELD_CHARGE_MOVE, 'Charge move'),
    (FIELD_START_AT, 'Alkamisaika'),
  )
  raid = models.ForeignKey(Raid, related_name='votes', on_delete=models.CASCADE)
  submitter = models.CharField(max_length=255)
  vote_field = models.CharField(max_length=255, choices=FIELD_CHOICES)
  vote_value = models.CharField(max_length=255)
  data_source = models.ForeignKey(DataSource, on_delete=models.CASCADE, null=True, blank=True)

  @classmethod
  def get_top_value(cls, raid, vote_field):
    try:
      return RaidVote.objects.filter(raid=raid, vote_field=vote_field, data_source__isnull=False).latest('created_at').vote_value
    except RaidVote.DoesNotExist:
      qs = RaidVote.objects.filter(raid=raid, vote_field=vote_field)
      qs = qs.values('vote_value').annotate(count=Count('vote_value')).order_by('-count', '-created_at')
      top_vote = qs.first()
      if top_vote:
        return top_vote['vote_value']
    return None

  def __str__(self):
    return '%s // %s // %s' % (self.raid, self.vote_field, self.vote_value)


class Attendance(TimestampedModel):
  raid = models.ForeignKey(Raid, related_name='attendances', on_delete=models.CASCADE)
  submitter = models.CharField(max_length=255)
  attendee_count = models.PositiveSmallIntegerField(default=1)
  estimated_arrival_at = models.DateTimeField(default=timezone.now)
  has_arrived = models.BooleanField(default=False)
  has_finished = models.BooleanField(default=False)

  def __str__(self):
    return '%s // ' % self.raid


def format_timedelta(timedelta_obj):
  hours, remainder = divmod(timedelta_obj.seconds, 3600)
  minutes, seconds = divmod(remainder, 60)
  return '%02d:%02d:%02d' % (hours, minutes, seconds)
