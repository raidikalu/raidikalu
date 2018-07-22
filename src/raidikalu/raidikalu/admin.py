from django.contrib import admin
from raidikalu.models import InfoBox, Gym, GymNickname, RaidType, Raid, DataSource, RaidVote, Attendance


class GymAdmin(admin.ModelAdmin):
  list_display = ('name', 'is_park', 'is_active')
  list_filter = ('is_park', 'is_active')
  search_fields = ('name',)


admin.site.register(InfoBox)
admin.site.register(Gym, GymAdmin)
admin.site.register(GymNickname)
admin.site.register(RaidType)
admin.site.register(Raid)
admin.site.register(DataSource)
admin.site.register(RaidVote)
admin.site.register(Attendance)
