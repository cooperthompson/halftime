# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from importer.breakaway.breakaway_loader import BreakawayLoader
from importer.E608.E608_loader import E608Loader
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


def load_teams_from_sheets(modeladmin, request, queryset):
    for obj in queryset:
        sheet_id = obj.google_sheet_id
        print(sheet_id)


def load_teams_from_file(modeladmin, request, queryset):
    for league in queryset:
        loader = E608Loader(league)
        loader.load_teams()


def load_games_from_file(modeladmin, request, queryset):
    for league in queryset:
        loader = E608Loader(league)
        loader.load_games()


class LeagueAdmin(admin.ModelAdmin):
    inlines = [TeamInline]
    fields = ['name', 'is_active', 'org', 'logo', 'slug',
              'team_file', 'game_file']
    list_display = ['__str__', 'name', 'is_active', 'logo',
                    'team_file', 'game_file']
    search_fields = ['name']
    list_filter = ['is_active']
    list_editable = ['name', 'is_active', 'logo',
                     'team_file', 'game_file']
    autocomplete_fields = ['org']
    actions = [load_teams_from_file, load_games_from_file]

    def save_model_nope(self, request, obj, form, change):
        # Not used anymore.  Using actions instead
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

        if obj.team_file:
            if not change:
                loader = E608Loader(obj)
                loader.load_teams()
            else:
                orig = League.objects.get(pk=obj.pk)
                if orig.team_file != obj.team_file:
                    loader = E608Loader(obj)
                    loader.load_teams()

        if obj.game_file:
            if not change:
                loader = E608Loader(obj)
                loader.load_games()
            else:
                orig = League.objects.get(pk=obj.pk)
                if orig.game_file != obj.game_file:
                    loader = E608Loader(obj)
                    loader.load_games()


class FieldAdmin(admin.ModelAdmin):
    list_filter = ['name']
    list_display = ['name', 'short_name']
    list_display_links = ['name']
    search_fields = ['number', 'name']


class TeamAdmin(admin.ModelAdmin):
    list_filter = ['league']
    list_display = ['number', 'name', 'color', 'league']
    list_display_links = ['name']
    search_fields = ['number', 'name']


class GameAdmin(admin.ModelAdmin):
    fields = ['league', 'home_team', 'away_team', 'time', 'field']
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
admin.site.register(Field, FieldAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Game, GameAdmin)
