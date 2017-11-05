
from django.conf.urls import url
from raidikalu.views import RaidListView, RaidCreateView, RaidReceiverView


urlpatterns = [
  url('^$', RaidListView.as_view(), name='raidikalu.raid_list'),
  url('^ilmoita-raidi/$', RaidCreateView.as_view(), name='raidikalu.raid_create'),
  url('^api/1/raid-receiver/(?P<api_key>[^/]+)/$', RaidReceiverView.as_view(), name='raidikalu.raid_receiver'),
]
