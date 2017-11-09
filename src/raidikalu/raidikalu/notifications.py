
from raidikalu.models import EditableSettings


def notify_raid(raid):
  notify_slack(raid)
  notify_discord(raid)


def notify_slack(raid):
  editable_settings = EditableSettings.get_current_settings()
  print('######## ')
  for notification in editable_settings.notifications:
    print(notification)
    print(raid.pokemon_name)
    if notification['service'] == 'slack' and notification['pokemon'] == raid.pokemon_name:
      print(notification)
  print(raid)


def notify_discord(raid):
  print(raid)
