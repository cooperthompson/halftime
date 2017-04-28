# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Create your models here.
from datetime import date
from django.db import models
from urlparse import urlparse
from collections import defaultdict
from django.contrib.auth.models import User


class Organization(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        managed = True
        db_table = 'soccer_organizations'

    def __unicode__(self):
        return self.name


class Field(models.Model):
    name = models.CharField(max_length=50)
    short_name = models.CharField(max_length=10)
    number = models.IntegerField(null=1, blank=1)
    organization = models.ForeignKey(Organization, null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'soccer_fields'


class Season(models.Model):
    name = models.CharField(max_length=100)
    iscurrent = models.BooleanField(default=False)
    organization = models.ForeignKey(Organization, null=True)

    class Meta:
        managed = True
        db_table = 'soccer_seasons'

    def __unicode__(self):
        return self.name


class League(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField()
    season = models.ForeignKey(Season, related_name='leagues', null=True, blank=True)
    org = models.ForeignKey(Organization, related_name='org', null=True, blank=True)
    key = models.CharField(max_length=100)
    is_active = models.BooleanField(default=False)

    class Meta:
        managed = True
        db_table = 'soccer_leagues'

    def __unicode__(self):
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

    def __unicode__(self):
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
    teams = models.ManyToManyField(Team)
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
        colors = defaultdict()
        color_conflict = False

        for team in self.teams.all():
            colors[team.color] += 1
            if colors[team.color] > 1:
                color_conflict = True

        return color_conflict

    class Meta:
        ordering = ['time']
        managed = True
        db_table = 'soccer_games'

    def __unicode__(self):
        return self.name


