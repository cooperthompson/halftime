# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-04-29 18:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game_schedules', '0003_field_organization'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='short_name',
            field=models.CharField(blank=True, max_length=4, null=True),
        ),
    ]
