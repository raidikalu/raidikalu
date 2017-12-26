from django.core.management.base import BaseCommand
from django.db.models import Count
from raidikalu.models import Gym


class Command(BaseCommand):
  def handle(self, *args, **options):
    s2_cell_ids_with_counts = Gym.objects.filter(is_park=True).values('s2_cell_id').annotate(eligible_count=Count('s2_cell_id'))
    for row in s2_cell_ids_with_counts:
      if row['s2_cell_id']:
        Gym.objects.filter(s2_cell_id=row['s2_cell_id']).update(s2_cell_eligible_count=row['eligible_count'])
