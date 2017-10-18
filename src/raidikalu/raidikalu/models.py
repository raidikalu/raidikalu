
from datetime import timedelta
from django.db import models
from django.utils.timezone import now


class TimestampedModel(models.Model):
  created_at = models.DateTimeField(editable=False, default=now)
  updated_at = models.DateTimeField()

  class Meta:
    abstract = True

  def save(self, *args, **kwargs):
    self.updated_at = now()
    return super(TimestampedModel, self).save(*args, **kwargs)


class Gym(TimestampedModel):
  name = models.CharField(max_length=2048)
  pogo_id = models.CharField(max_length=255, blank=True)
  external_id = models.CharField(max_length=255, blank=True)
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

  gym = models.ForeignKey(Gym, related_name='raids', on_delete=models.CASCADE)
  tier = models.PositiveSmallIntegerField(default=0)
  pokemon = models.CharField(max_length=255, blank=True)
  fast_move = models.CharField(max_length=255, blank=True)
  charge_move = models.CharField(max_length=255, blank=True)
  start_at = models.DateTimeField(null=True)
  end_at = models.DateTimeField(null=True)

  def save(self, *args, **kwargs):
    self.end_at = self.start_at + Raid.RAID_BATTLE_DURATION
    return super(TimestampedModel, self).save(*args, **kwargs)

  def __str__(self):
    return '%s // %s' % (self.gym.name, self.pokemon)


class DataSource(models.Model):
  name = models.CharField(max_length=255)
  api_key = models.CharField(max_length=2048)

  def __str__(self):
    return self.name


class RaidVote(TimestampedModel):
  FIELD_TIER = 'tier'
  FIELD_POKEMON = 'pokemon'
  FIELD_FAST_MOVE = 'fast_move'
  FIELD_CHARGE_MOVE = 'charge_move'
  FIELD_START_AT = 'start_at'
  FIELD_CHOICES = (
    (FIELD_TIER, 'Tier'),
    (FIELD_POKEMON, 'Pokémon'),
    (FIELD_FAST_MOVE, 'Fast move'),
    (FIELD_CHARGE_MOVE, 'Charge move'),
    (FIELD_START_AT, 'Starting time'),
  )
  raid = models.ForeignKey(Raid, related_name='votes', on_delete=models.CASCADE)
  submitter = models.CharField(max_length=255)
  vote_field = models.CharField(max_length=255, choices=FIELD_CHOICES)
  vote_value = models.CharField(max_length=255)
  data_source = models.ForeignKey(DataSource, on_delete=models.CASCADE, null=True, blank=True)

  def __str__(self):
    return '%s // %s // %s' % (self.raid, self.vote_type, self.value)


class Attendance(TimestampedModel):
  raid = models.ForeignKey(Raid, related_name='attendances', on_delete=models.CASCADE)
  submitter = models.CharField(max_length=255)
  attendee_count = models.PositiveSmallIntegerField(default=1)
  estimated_arrival_at = models.DateTimeField(default=now)
  has_arrived = models.BooleanField(default=False)
  has_finished = models.BooleanField(default=False)

  def __str__(self):
    return '%s // ' % self.raid
