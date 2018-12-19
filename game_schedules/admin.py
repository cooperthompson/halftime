# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from game_schedules.importer.breakaway.breakaway_loader import BreakawayLoader
from game_schedules.models import *


# Register your models here.


class LeagueInline(admin.TabularInline):
    model = League
    fk_name = 'season'


class TeamInline(admin.TabularInline):
    model = Team
    fk_name = 'league'
    ordering = ('number',)
    fields = ['number', 'name', 'color']


class OrganizationAdmin(admin.ModelAdmin):
    fields = ['name', 'short_name', 'motto', 'order']
    list_display = ['name', 'short_name', 'motto']
    list_filter = ['name', ]
    search_fields = ['name']


class LeagueAdmin(admin.ModelAdmin):
    inlines = [TeamInline]
    fields = ['name', 'is_active', 'org', 'logo', 'breakaway_import_file']
    list_display = ['__str__', 'name', 'is_active', 'breakaway_import_file', 'logo']
    search_fields = ['name']
    list_filter = ['is_active']
    list_editable = ['name', 'is_active', 'breakaway_import_file', 'logo']
    autocomplete_fields = ['org']

    def save_model(self, request, obj, form, change):
        super(LeagueAdmin, self).save_model(request, obj, form, change)
        if obj.breakaway_import_file:

            if not change:
                # New league being created - import teams and games from file
                loader = BreakawayLoader(obj)
                loader.import_text_file(change)
            else:
                # Existing league is being edited, only import teams and teames if the import file was changed.
                orig = League.objects.get(pk=obj.pk)
                if orig.breakaway_import_file != obj.breakaway_import_file:
                    loader = BreakawayLoader(obj)
                    loader.import_text_file(change)


class TeamAdmin(admin.ModelAdmin):
    list_filter = ['league']
    list_display = ['number', 'name', 'color', 'league']
    list_display_links = ['name']
    search_fields = ['number', 'name']


class GameAdmin(admin.ModelAdmin):
    fields = ['league', 'teams', 'time', 'field']
    list_display = ['id', '__str__',
                    'time',
                    'field']
    list_display_links = ['__str__']
    list_filter = ['league']
    search_fields = ['home_team__name', 'away_team__name']


admin.site.site_header = 'Halftime administration'
admin.site.site_title = 'Halftime administration'


admin.site.register(Organization, OrganizationAdmin)
admin.site.register(League, LeagueAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Game, GameAdmin)
