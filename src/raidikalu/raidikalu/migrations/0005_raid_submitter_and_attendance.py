# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-20 18:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('raidikalu', '0004_editablesettings_notifications_json'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='attendance',
            name='attendee_count',
        ),
        migrations.RemoveField(
            model_name='attendance',
            name='estimated_arrival_at',
        ),
        migrations.RemoveField(
            model_name='attendance',
            name='has_arrived',
        ),
        migrations.RemoveField(
            model_name='attendance',
            name='has_finished',
        ),
        migrations.AddField(
            model_name='attendance',
            name='start_time_choice',
            field=models.PositiveSmallIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='raid',
            name='submitter',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='raidvote',
            name='submitter',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='raidvote',
            name='vote_field',
            field=models.CharField(choices=[('tier', 'Taso'), ('pokemon_name', 'Pokémon'), ('fast_move', 'Fast move'), ('charge_move', 'Charge move'), ('start_at', 'Alkamisaika')], max_length=255),
        ),
    ]