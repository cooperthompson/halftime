from calendar import Calendar

import shortuuid as shortuuid
from django.http import HttpResponse, Http404
from icalendar import Calendar, Event, Alarm
from game_schedules.models import *
import datetime


def ics(request):
    team_id_list = request.GET.getlist('team_id')
    league_id_list = request.GET.getlist('league_id')
    org_id_list = request.GET.getlist('org_id')

    teams = get_teams(team_id_list)
    leagues = get_leagues(league_id_list)
    orgs = get_orgs(org_id_list)

    if len(teams) == 1:
        cal_name = teams[0].name
    elif len(leagues) == 1:
        cal_name = leagues[0].name
    elif len(orgs) == 1:
        cal_name = orgs[0].name
    else:
        cal_name = "Soccer Games"

    cal = Calendar()
    cal.add('prodid', '-//Soccer Game Schedules//Soccer Calendars//EN')
    cal.add('version', '2.0')
    cal.add('X-WR-CALNAME', cal_name)
    cal.add('X-WR-TIMEZONE', 'CST6CDT')
    cal.add('X-WR-CALDESC', 'Soccer Team Schedule')

    for team in teams:
        for game in team.games().order_by("time", "field"):
            add_game(cal, game)

    for league in leagues:
        for game in Game.objects.filter(league=league).order_by("time", "field"):
            add_game(cal, game)

    for org in orgs:
        for league in League.objects.filter(org=org):
            for game in Game.objects.filter(league=league).order_by("time", "field"):
                add_game(cal, game)

    return HttpResponse(cal.to_ical(), content_type='text/calendar')


def get_teams(team_id_list):
    teams = []
    for team_id in team_id_list:
        try:
            team = Team.objects.get(id=team_id)
            teams.append(team)
        except Team.DoesNotExist:
            # Just skip unrecognized teams
            pass
    return teams


def get_leagues(league_id_list):
    leagues = []
    for league_id in league_id_list:
        try:
            league = League.objects.get(id=league_id)
            leagues.append(league)
        except League.DoesNotExist:
            # Just skip unrecognized leagues
            pass
    return leagues


def get_orgs(org_id_list):
    orgs = []
    for org_id in org_id_list:
        try:
            org = Organization.objects.get(id=org_id)
            orgs.append(org)
        except Organization.DoesNotExist:
            # Just skip unrecognized teams
            pass
    return orgs


def add_game(cal, game):
    now_dt = datetime.datetime.now()
    now_string = "%04d%02d%02dT%02d%02d%02d" % (
        now_dt.year,
        now_dt.month,
        now_dt.day,
        now_dt.hour,
        now_dt.minute,
        now_dt.second
    )

    event = Event()
    summary = '%s vs. %s' % (game.home_team, game.away_team)

    if game.color_conflict:
        desc = 'Color conflict! ({} vs. {})'.format(game.away_team.color, game.home_team.color)
        summary += ' (color conflict)'
        event.add('description', desc)

    event.add('summary', summary)
    event.add('dtstart', game.time)
    event.add('dtend', game.time + datetime.timedelta(hours=1))
    event.add('dtstamp', datetime.datetime.now())
    event.add('location', "{}".format(game.field.short_name))
    event['uid'] = '{}/{}@breakawaysports.com'.format(now_string, shortuuid.uuid())
    event.add('priority', 5)

    alarm = Alarm()
    alarm.add("TRIGGER;RELATED=START", "-PT{0}M".format('45'))
    alarm.add('action', 'display')
    alarm.add('description', 'Breakaway game')
    if game.color_conflict:
        alarm.add('description', 'Color Conflict! - bring alternate color')

    event.add_component(alarm)
    cal.add_component(event)
