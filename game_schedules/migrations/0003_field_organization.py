# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-04-28 03:28
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('game_schedules', '0002_auto_20170427_2205'),
    ]

    operations = [
        migrations.AddField(
            model_name='field',
            name='organization',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='game_schedules.Organization'),
        ),
    ]
