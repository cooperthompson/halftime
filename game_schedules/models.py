# -*- coding: utf-8 -*-
from smart_selects.db_fields import ChainedForeignKey
from game_schedules.managers import *

# Create your models here.
from datetime import date
from django.db import models
from urllib.parse import urlparse
from django.contrib.auth.models import User, Group


class Organization(models.Model):
    name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=4, null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'soccer_organizations'

    def __str__(self):
        return self.name


class Field(models.Model):
    name = models.CharField(max_length=50)
    short_name = models.CharField(max_length=10)
    number = models.IntegerField(null=1, blank=1)
    organization = models.ForeignKey(Organization, null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'soccer_fields'

    def __str__(self):
        return str(self.number)


class Season(models.Model):
    name = models.CharField(max_length=100)
    iscurrent = models.BooleanField(default=False)
    organization = models.ForeignKey(Organization, null=True)

    class Meta:
        managed = True
        db_table = 'soccer_seasons'

    def __str__(self):
        return self.name


class League(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField()
    season = models.ForeignKey(Season, related_name='leagues', null=True, blank=True)
    org = models.ForeignKey(Organization, related_name='org', null=True, blank=True)
    key = models.CharField(max_length=100)
    is_active = models.BooleanField(default=False)
    logo = models.ImageField(null=True, blank=True)
    breakaway_word_file = models.FileField(null=True)

    class Meta:
        managed = True
        db_table = 'soccer_leagues'

    def __str__(self):
        return u"%s" % self.name

    def get_webcal_url(self, request):
        domain = ''
        if request:
            domain = request.build_absolute_uri()
            self.domain = domain

        http_url = urlparse(domain)
        webcal_url = http_url.geturl().replace(http_url.scheme, 'webcal', 1)

        return '%s%s.ics' % (webcal_url, self.name.replace(' ', '_'))


class Team(models.Model):
    number = models.IntegerField()
    name = models.CharField(max_length=100)
    slug = models.SlugField()
    color = models.CharField(max_length=100)
    league = models.ForeignKey(League, related_name='teams')
    manager = models.ForeignKey(User, blank=True, null=True, related_name='manager')
    roster = models.ManyToManyField(User, related_name='player')

    class Meta:
        ordering = ['number']
        managed = True
        db_table = 'soccer_teams'

    def __str__(self):
        return u"[%s] %s" % (self.number, self.name)

    def get_webcal_url(self, request):
        domain = ''
        if request:
            domain = request.build_absolute_uri()
            self.domain = domain

        http_url = urlparse(domain)
        webcal_url = http_url.geturl().replace(http_url.scheme, 'webcal', 1)
        return '%s%s.ics' % (webcal_url, self.slug)


class Game(models.Model):
    # store game "name" to avoid having to do extra database hits on the teams
    # many-to-many field when constructing the name.
    name = models.CharField(max_length=100)  # Example name:  "Stormtroopers vs. Whistlers"
    league = models.ForeignKey(League)
    home_team = ChainedForeignKey(Team,
                                  chained_field='league',
                                  chained_model_field='league',
                                  related_name='home_team')
    away_team = ChainedForeignKey(Team,
                                  chained_field='league',
                                  chained_model_field='league',
                                  related_name='away_team')
    time = models.DateTimeField()
    field = models.ForeignKey(Field, null=True, blank=True)

    @property
    def is_today(self):
        if self.time.date() == date.today():
            return True
        else:
            return False

    @property
    def color_conflict(self):
        if self.home_team.color.upper() == self.away_team.color.upper():
            return True
        else:
            return False

    class Meta:
        ordering = ['time']
        managed = True
        db_table = 'soccer_games'

    def __str__(self):
        return self.name
