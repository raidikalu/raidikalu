
from django.apps import AppConfig
from django.db.models.signals import post_save


class RaidikaluConfig(AppConfig):
  name = 'raidikalu'
  verbose_name = 'Raidikalu'

  def ready(self):
    from raidikalu.signals.notifications import notify_raid
    from raidikalu.messages import raid_updated
    post_save.connect(notify_raid, sender='raidikalu.Raid')
    post_save.connect(raid_updated, sender='raidikalu.Raid')

