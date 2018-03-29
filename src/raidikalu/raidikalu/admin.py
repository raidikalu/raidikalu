from django.contrib import admin
from raidikalu.models import EditableSettings, Gym, GymNickname, Raid, DataSource, RaidVote, Attendance


class GymAdmin(admin.ModelAdmin):
  list_display = ('name', 'is_park')
  list_filter = ('is_park',)
  search_fields = ('name',)


admin.site.register(EditableSettings)
admin.site.register(Gym, GymAdmin)
admin.site.register(GymNickname)
admin.site.register(Raid)
admin.site.register(DataSource)
admin.site.register(RaidVote)
admin.site.register(Attendance)
