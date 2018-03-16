from django.contrib import admin
from raidikalu.models import EditableSettings, Gym, GymNickname, Raid, DataSource, RaidVote, Attendance


class GymAdmin(admin.ModelAdmin):
  list_display = ('name', 'is_park', 'latest_ex_raid_at', 's2_cell_id', 's2_cell_eligible_count')
  list_filter = ('is_park', 's2_cell_id')
  search_fields = ('name', 's2_cell_id')


admin.site.register(EditableSettings)
admin.site.register(Gym, GymAdmin)
admin.site.register(GymNickname)
admin.site.register(Raid)
admin.site.register(DataSource)
admin.site.register(RaidVote)
admin.site.register(Attendance)
