
import json
from channels import Group
from django.utils.dateformat import format as format_datetime


def send_event(event_name, event_message, event_data=None):
  Group('raidikalu').send({
    'text': json.dumps({
      'event': event_name,
      'message': event_message,
      'data': event_data,
    }),
  })


def attendance_updated(attendance, raid=None):
  raid = raid or attendance.raid
  if attendance.start_time_choice is not None:
    start_time = raid.get_start_time_choices()[attendance.start_time_choice]
    start_time_str = format_datetime(start_time, 'H:i')
    message = '%s tulee raidille %s' % (attendance.submitter, start_time_str)
  else:
    start_time_str = None
    message = '%s ei tule raidille' % attendance.submitter
  send_event(
    'attendance',
    message,
    {
      'raid': raid.pk,
      'choice': attendance.start_time_choice,
      'time': start_time_str,
      'submitter': attendance.submitter,
    },
  )


def raid_updated(instance, created, **kwargs):
  raid = instance
  if created:
    message = 'Raidi %s lisätty' % instance.pk
  else:
    message = 'Raidi %s päivitetty' % instance.pk
  send_event(
    'raid',
    message,
    {
      'raid': raid.pk,
      'gym': raid.gym.name,
      'pokemon': raid.monster_name, # Backwards compatibility
      'monster': raid.monster_name,
      'tier': raid.tier,
      'lat': str(raid.gym.latitude),
      'lng': str(raid.gym.longitude),
      'start': int(raid.start_at.timestamp()) if raid.start_at else None,
      'end': int(raid.end_at.timestamp()) if raid.end_at else None,
      'created': created,
    },
  )
