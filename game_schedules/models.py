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
    motto = models.CharField(max_length=100, null=True, blank=True)
    order = models.IntegerField(default=10)

    class Meta:
        managed = True
        db_table = 'soccer_organizations'

    def __str__(self):
        return self.name


class Field(models.Model):
    name = models.CharField(max_length=50)
    short_name = models.CharField(max_length=10)
    identifier = models.CharField(max_length=1, default='1')
    organization = models.ForeignKey(Organization, null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = 'soccer_fields'

    def __str__(self):
        return "Field {}".format(self.identifier)


class Season(models.Model):
    name = models.CharField(max_length=100)
    iscurrent = models.BooleanField(default=False)
    organization = models.ForeignKey(Organization, null=True, on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = 'soccer_seasons'

    def __str__(self):
        return self.name


class League(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField()
    season = models.ForeignKey(Season, related_name='leagues', null=True, blank=True, on_delete=models.CASCADE)
    org = models.ForeignKey(Organization, related_name='org', null=True, blank=True, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=False)
    logo = models.ImageField(null=True, blank=True)
    breakaway_word_file = models.FileField(null=True, blank=True)
    breakaway_import_file = models.FileField(null=True, blank=True)

    team_file = models.FileField(null=True, blank=True)
    game_file = models.FileField(null=True, blank=True)

    google_sheet_id = models.CharField(max_length=50, null=True, blank=True)
    sheets_teams_named_range = models.CharField(max_length=50, null=True, blank=True)
    sheets_games_named_range = models.CharField(max_length=50, null=True, blank=True)

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
    league = models.ForeignKey(League, related_name='teams', on_delete=models.CASCADE)
    manager = models.ForeignKey(User, blank=True, null=True, related_name='manager', on_delete=models.CASCADE)
    roster = models.ManyToManyField(User, related_name='player')

    games_played = models.IntegerField(default=0)
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    ties = models.IntegerField(default=0)
    goals_for = models.IntegerField(default=0)
    goals_against = models.IntegerField(default=0)
    goal_differential = models.IntegerField(default=0)
    league_points = models.IntegerField(default=0)

    def calculate_stats(self):
        # Reset cached stats
        self.games_played = 0
        self.wins = 0
        self.losses = 0
        self.ties = 0
        self.goals_foru = 0
        self.goals_against = 0
        self.goal_differential = 0
        self.league_points = 0

        for game in self.games():
            if not game.played():
                continue

            self.games_played += 1
            game_points = 0
            if game.winner() == self:
                self.wins += 1
                game_points += 6
            if game.loser() == self:
                self.losses += 1
                game_points += 0
            if game.tie():
                self.ties += 1
                game_points += 3

            if game.home_team == self:
                self.goals_for += game.home_team_score
                self.goals_against += game.away_team_score
                game_points += min(3, self.goals_for)  # 1 point per goal, up to 3 max
                if game.away_team_score == 0:
                    game_points += 1  # 1 point for a shutout
            if game.away_team == self:
                self.goals_for += game.away_team_score
                self.goals_against += game.home_team_score
                game_points += min(3, self.goals_for)  # 1 point per goal, up to 3 max
                if game.home_team_score == 0:
                    game_points += 1  # 1 point for a shutout

            self.league_points += game_points

        self.goal_differential = self.goals_for - self.goals_against

    def games(self):
        home_games = Game.objects.filter(home_team=self)
        away_games = Game.objects.filter(away_team=self)
        return away_games | home_games

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
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name="games")
    # home_team = ChainedForeignKey(Team,
    #                               chained_field='league',
    #                               chained_model_field='league',
    #                               related_name='home_team')
    # away_team = ChainedForeignKey(Team,
    #                               chained_field='league',
    #                               chained_model_field='league',
    #                               related_name='away_team')
    home_team = models.ForeignKey(Team, related_name='home_team', on_delete=models.CASCADE)
    away_team = models.ForeignKey(Team, related_name='away_team', on_delete=models.CASCADE)

    home_team_score = models.IntegerField(null=True, blank=True)
    away_team_score = models.IntegerField(null=True, blank=True)

    time = models.DateTimeField()
    field = models.ForeignKey(Field, null=True, blank=True, on_delete=models.CASCADE)

    def winner(self):
        if self.home_team_score > self.away_team_score:
            return self.home_team
        elif self.away_team_score > self.home_team_score:
                return self.away_team
        else:
            return None  # Tie

    def loser(self):
        if self.home_team_score > self.away_team_score:
            return self.away_team
        elif self.away_team_score > self.home_team_score:
                return self.home_team
        else:
            return None  # Tie

    def tie(self):
        # Game hasn't been played yet
        if self.home_team_score is None or self.away_team_score is None:
            return False

        if self.home_team_score == self.away_team_score:
            return True
        else:
            return False

    def played(self):
        if self.home_team_score is None or self.away_team_score is None:
            return False
        else:
            return True

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
