from django.contrib import admin
from django.utils.html import format_html
from raidikalu.models import InfoBox, Gym, GymNickname, RaidType, Raid, DataSource, RaidVote, Attendance


def make_active(modeladmin, request, queryset):
  queryset.update(is_active=True)
make_active.short_description = 'Mark selected as active'


def make_inactive(modeladmin, request, queryset):
  queryset.update(is_active=False)
make_inactive.short_description = 'Mark selected as not active'


class GymAdmin(admin.ModelAdmin):
  list_display = ('name', 'is_ex_eligible', 'is_active')
  list_filter = ('is_ex_eligible', 'is_active')
  search_fields = ('name',)
  actions = [make_active, make_inactive]


class RaidTypeAdmin(admin.ModelAdmin):
  list_display = ('get_tier_display', 'image_tag', 'monster_name', 'monster_number', 'is_active')
  list_filter = ('tier', 'is_active')
  actions = [make_active, make_inactive]
  ordering = ['-tier']

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    RaidType.get_tier_display.short_description = 'Tier'

  def image_tag(self, obj):
    return format_html('<img src="%s" width="32" height="32" style="margin: -8px 0;" />' % obj.get_image_url()) if obj.get_image_url() else ''
  image_tag.short_description = 'Image'


admin.site.register(InfoBox)
admin.site.register(Gym, GymAdmin)
admin.site.register(GymNickname)
admin.site.register(RaidType, RaidTypeAdmin)
admin.site.register(Raid)
admin.site.register(DataSource)
admin.site.register(RaidVote)
admin.site.register(Attendance)
