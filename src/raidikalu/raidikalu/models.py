
import logging
from datetime import timedelta, datetime
from django.db import models
from django.db.models import Count
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from raidikalu import settings
from raidikalu.bestiary import get_monster_number_by_name
from raidikalu.utils import format_timedelta


LOG = logging.getLogger(__name__)


class TimestampedModel(models.Model):
  created_at = models.DateTimeField(editable=False, default=timezone.now)
  updated_at = models.DateTimeField(editable=False)

  class Meta:
    abstract = True

  def save(self, *args, **kwargs):
    self.updated_at = timezone.now()
    return super(TimestampedModel, self).save(*args, **kwargs)


class InfoBox(models.Model):
  content = models.TextField(blank=True)

  @classmethod
  def get_infobox_content(cls):
    try:
      return cls.objects.all()[0].content
    except IndexError:
      return ''


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
  is_ex_eligible = models.BooleanField(default=False)
  is_active = models.BooleanField(default=True)

  def __str__(self):
    return self.name


class GymNickname(TimestampedModel):
  gym = models.ForeignKey(Gym, related_name='nicknames', on_delete=models.CASCADE)
  nickname = models.CharField(max_length=2048)

  def __str__(self):
    return '%s // %s' % (self.gym.name, self.nickname)


class RaidType(models.Model):
  tier = models.PositiveSmallIntegerField()
  priority = models.PositiveSmallIntegerField(default=1)
  monster_name = models.CharField(max_length=255)
  monster_number = models.PositiveSmallIntegerField(null=True, blank=True)
  image_url = models.CharField(max_length=2048, blank=True)
  is_active = models.BooleanField(default=True)

  class Meta:
    ordering = ['-tier', '-priority']

  def save(self, *args, **kwargs):
    new_monster_number = get_monster_number_by_name(self.monster_name)
    if new_monster_number:
      self.monster_number = new_monster_number
    super().save(*args, **kwargs)

  def get_image_url(self):
    return self.image_url or settings.BASE_RAID_IMAGE_URL.format(self.monster_number)

  def get_tier_display(self):
    if self.tier == 1:
      return '\u2605'
    if self.tier == 2:
      return '\u2605\u2605'
    if self.tier == 3:
      return '\u2605\u2605\u2605'
    if self.tier == 4:
      return '\u2605\u2605\u2605\u2605'
    if self.tier == 5:
      return '\u2605\u2605\u2605\u2605\u2605'
    return '\u2013'


class Raid(TimestampedModel):
  RAID_EGG_DURATION = timedelta(hours=1)
  RAID_BATTLE_DURATION = timedelta(minutes=45)
  RAID_DURATION = RAID_EGG_DURATION + RAID_BATTLE_DURATION

  gym = models.ForeignKey(Gym, related_name='raids', on_delete=models.CASCADE)
  submitter = models.CharField(max_length=255, blank=True)
  data_source = models.ForeignKey(DataSource, on_delete=models.SET_NULL, null=True, blank=True)
  unverified_text = models.CharField(max_length=255, blank=True)
  tier = models.PositiveSmallIntegerField(null=True, blank=True)
  monster_name = models.CharField(max_length=255, blank=True)
  raid_type = models.ForeignKey(RaidType, related_name='raids', on_delete=models.SET_NULL, null=True, blank=True)
  fast_move = models.CharField(max_length=255, blank=True)
  charge_move = models.CharField(max_length=255, blank=True)
  start_at = models.DateTimeField(null=True, blank=True)
  end_at = models.DateTimeField(null=True, blank=True)

  def save(self, *args, **kwargs):
    if self.raid_type:
      self.tier = self.raid_type.tier
      self.monster_name = self.raid_type.monster_name
    elif not self.raid_type and self.monster_name:
      try:
        self.raid_type = RaidType.objects.get(monster_name=self.monster_name)
        self.tier = self.raid_type.tier
      except RaidType.DoesNotExist:
        LOG.error('Could not find raid type for raid', extra={'data': {'raid_monster_name': repr(self.monster_name)}})
    self.end_at = self.start_at + Raid.RAID_BATTLE_DURATION if self.start_at else None
    self.unverified_text = self.get_unverified_text()
    Raid.objects.filter(end_at__lt=timezone.now()).delete()
    return super(Raid, self).save(*args, **kwargs)

  @property
  def has_started(self):
    if self.start_at:
      return timezone.now() >= self.start_at
    return False

  def get_image_url(self):
    if self.raid_type:
      return self.raid_type.get_image_url()
    else:
      return ''

  def get_time_left_until_start(self):
    return self.start_at - timezone.now() if self.start_at else None

  def get_time_left_until_end(self):
    return self.end_at - timezone.now() if self.end_at else None

  def get_time_left_until_start_display(self):
    return format_timedelta(self.get_time_left_until_start()) if self.start_at else '\u2013'

  def get_time_left_until_end_display(self):
    return format_timedelta(self.get_time_left_until_end()) if self.end_at else '\u2013'

  def get_start_time_choices(self):
    start_time_choices = []
    if self.start_at:
      # The first start time choice should be at least 5 minutes in the future
      # So we choose the initial offset based on that
      if self.start_at.minute % 10 > 5:
        start_offset_minutes = 15 - self.start_at.minute % 10
      else:
        start_offset_minutes = 10 - self.start_at.minute % 10
      start_offset = self.start_at + timedelta(minutes=start_offset_minutes)
      start_time_choices = [
        self.start_at,
        start_offset,
        start_offset + timedelta(minutes=10),
        start_offset + timedelta(minutes=20),
        start_offset + timedelta(minutes=30),
      ]
    return start_time_choices

  def get_tier_display(self):
    if self.tier == 1:
      return '\u2605'
    if self.tier == 2:
      return '\u2605\u2605'
    if self.tier == 3:
      return '\u2605\u2605\u2605'
    if self.tier == 4:
      return '\u2605\u2605\u2605\u2605'
    if self.tier == 5:
      return '\u2605\u2605\u2605\u2605\u2605'
    return '\u2013'

  def get_unverified_text(self):
    is_monster_unverified = RaidVote.get_confidence(self, RaidVote.FIELD_MONSTER) < 3
    is_tier_unverified = RaidVote.get_confidence(self, RaidVote.FIELD_TIER) < 3
    if is_monster_unverified and is_tier_unverified:
      return _('raid existence')
    if is_monster_unverified:
      return _('raid boss')
    return ''

  def count_votes_and_update(self):
    tier = RaidVote.get_top_value(self, RaidVote.FIELD_TIER)
    if tier is not None:
      self.tier = int(tier)

    monster_name = RaidVote.get_top_value(self, RaidVote.FIELD_MONSTER)
    if monster_name is not None:
      self.monster_name = monster_name

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
    return '%s // %s' % (self.gym.name, self.monster_name)


class RaidVote(TimestampedModel):
  FIELD_TIER = 'tier'
  FIELD_MONSTER = 'monster_name'
  FIELD_FAST_MOVE = 'fast_move'
  FIELD_CHARGE_MOVE = 'charge_move'
  FIELD_START_AT = 'start_at'
  FIELD_CHOICES = (
    (FIELD_TIER, _('Tier')),
    (FIELD_MONSTER, _('Raid boss')),
    (FIELD_FAST_MOVE, _('Fast move')),
    (FIELD_CHARGE_MOVE, _('Charge move')),
    (FIELD_START_AT, _('Starting time')),
  )
  raid = models.ForeignKey(Raid, related_name='votes', on_delete=models.CASCADE)
  submitter = models.CharField(max_length=255, blank=True)
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

  @classmethod
  def get_confidence(cls, raid, vote_field):
    confidence = 0
    if RaidVote.objects.filter(raid=raid, vote_field=vote_field, data_source__isnull=False).exists():
      confidence = 100
    else:
      votes = RaidVote.objects.filter(raid=raid, vote_field=vote_field)
      raid_value = getattr(raid, vote_field)
      submitters = []
      for vote in votes:
        # Count only one vote per submitter, one for anonymous
        if vote.submitter in submitters:
          continue
        submitters.append(vote.submitter)
        if raid_value == vote.vote_value:
          confidence += 1
        else:
          confidence -= 1
    return confidence

  def __str__(self):
    return '%s // %s // %s' % (self.raid, self.vote_field, self.vote_value)


class Attendance(TimestampedModel):
  raid = models.ForeignKey(Raid, related_name='attendances', on_delete=models.CASCADE)
  submitter = models.CharField(max_length=255)
  start_time_choice = models.PositiveSmallIntegerField()

  def __str__(self):
    return '%s // ' % self.raid
