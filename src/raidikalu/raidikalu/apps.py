
from django.apps import AppConfig
from django.db.models.signals import post_save


class RaidikaluConfig(AppConfig):
  name = 'raidikalu'
  verbose_name = 'Raidikalu'

  def ready(self):
    from raidikalu.signals.notifications import notify_raid
    post_save.connect(notify_raid, sender='raidikalu.Raid')

