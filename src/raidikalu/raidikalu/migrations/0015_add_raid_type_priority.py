# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-07-24 14:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('raidikalu', '0014_rename_is_park'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='raidtype',
            options={'ordering': ['-tier', 'priority']},
        ),
        migrations.AddField(
            model_name='raidtype',
            name='priority',
            field=models.PositiveSmallIntegerField(default=1),
        ),
    ]
