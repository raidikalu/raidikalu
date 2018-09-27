
from django.conf.urls import url
from raidikalu.consumers import MainConsumer


websocket_urlpatterns = [
  url(r'^ws/$', MainConsumer),
]
