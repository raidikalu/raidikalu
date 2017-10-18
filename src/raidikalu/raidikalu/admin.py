from django.contrib import admin
from raidikalu.models import Gym, GymNickname, Raid, DataSource, RaidVote, Attendance


admin.site.register(Gym)
admin.site.register(GymNickname)
admin.site.register(Raid)
admin.site.register(DataSource)
admin.site.register(RaidVote)
admin.site.register(Attendance)
