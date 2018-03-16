
from channels import Group


def ws_connect(message):
  message.reply_channel.send({'accept': True})
  Group('raidikalu').add(message.reply_channel)


def ws_disconnect(message):
  Group('raidikalu').discard(message.reply_channel)
