
from django.conf.urls import url
from raidikalu.views import RaidListView, RaidCreateView, RaidReceiverView, GymReceiverView, RaidJsonExportView, GymUuidsView, GymCoordinatesView


urlpatterns = [
  url('^$', RaidListView.as_view(), name='raidikalu.raid_list'),
  url('^ilmoita-raidi/$', RaidCreateView.as_view(), name='raidikalu.raid_create'),
  url('^api/1/raid-receiver/(?P<api_key>[^/]+)/$', RaidReceiverView.as_view(), name='raidikalu.raid_receiver'),
  url('^api/1/gym-receiver/(?P<api_key>[^/]+)/$', GymReceiverView.as_view(), name='raidikalu.gym_receiver'),
  url('^api/1/raid-export/(?P<api_key>[^/]+)/$', RaidJsonExportView.as_view(), name='raidikalu.raid_export'),
  url('^api/1/gym-uuids/(?P<api_key>[^/]+)/$', GymUuidsView.as_view(), name='raidikalu.gym_uuids'),
  url('^api/1/gym-coordinates/$', GymCoordinatesView.as_view(), name='raidikalu.gym_coordinates'),
]
