# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from game_schedules.models import *

# Register your models here.


class LeagueInline(admin.TabularInline):
    model = League
    fk_name = 'season'


class TeamInline(admin.TabularInline):
    model = Team
    fk_name = 'league'
    ordering = ('number', )
    fields = ['number', 'name', 'color']


class LeagueAdmin(admin.ModelAdmin):
    inlines = [TeamInline]
    fields = ['name', 'is_active', 'org', 'logo']
    # readonly_fields = ['key']
    list_display = ['__unicode__', 'key', 'name', 'is_active', 'logo']
    search_fields = ['name']
    list_filter = ['is_active']
    list_editable = ['key', 'name', 'is_active', 'logo']


class TeamAdmin(admin.ModelAdmin):
    list_filter = ['league']
    list_display = ['number', 'name', 'color', 'league']
    list_display_links = ['name']
    search_fields = ['number', 'name']


class GameAdmin(admin.ModelAdmin):
    fields = ['league', 'teams', 'time', 'field']
    list_display = ['id', '__unicode__',
                    'time',
                    'field']
    list_display_links = ['__unicode__']
    list_filter = ['league']
    search_fields = ['teams__name']


admin.site.register(Organization)
admin.site.register(League, LeagueAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Game, GameAdmin)
