
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
    message = '%s tulee raidille %s' % (attendance.submitter, format_datetime(start_time, 'H:i'))
  else:
    message = '%s ei tule raidille' % attendance.submitter
  send_event(
    'attendance',
    message,
    {
      'raid': raid.pk,
      'choice': attendance.start_time_choice,
      'submitter': attendance.submitter,
    },
  )
