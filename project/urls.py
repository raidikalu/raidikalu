
from django.conf.urls import include, url
from django.contrib import admin


urlpatterns = [
  url(r'', include('raidikalu.urls')),
  url(r'^sysadmin/', include(admin.site.urls)),
]
