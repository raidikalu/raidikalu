from rest_framework import serializers
from raidikalu.models import RaidType


class RaidTypeSerializer(serializers.ModelSerializer):
  class Meta:
    model = RaidType
    fields = [
      'tier',
      'priority',
      'monster_name',
      'monster_number',
      'image_url',
      'is_active',
    ]