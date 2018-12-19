from calendar import Calendar

from django.http import HttpResponse
from icalendar import Calendar, Event, Alarm
from game_schedules.models import *
import datetime


def ics(request):
    team_id = request.GET.get('team_id')
    team_slug = request.GET.get('team_name')

    if team_id:
        this_team = Team.objects.get(id=team_id)
    elif team_slug:
        this_team = Team.objects.get(slug=team_slug)

    games = Team.games.all()

    games = games.order_by("time", "field")

    cal = Calendar()
    cal.add('prodid', '-//Breakway Schedules//Soccer Calendars//EN')
    cal.add('version', '2.0')
    cal.add('X-WR-CALNAME', this_team.name)
    cal.add('X-WR-TIMEZONE', 'CST6CDT')
    cal.add('X-WR-CALDESC', 'Breakaway Team Schedule')

    now_dt = datetime.now()
    now_string = "%04d%02d%02dT%02d%02d%02d" % (
        now_dt.year,
        now_dt.month,
        now_dt.day,
        now_dt.hour,
        now_dt.minute,
        now_dt.second
    )

    for game in games:
        event = Event()
        try:
            summary = '%s vs. %s' % (game.home_team, game.away_team)
        except Exception:
            summary = 'Breakaway game'

        if game.color_conflict:
            desc = 'Color conflict! (%s vs. %s)' % (game.away_team.color, game.home_team.color)
            summary += ' (color conflict)'
            event.add('description', desc)

        event.add('summary', summary)

        event.add('dtstart', game.time)
        event.add('dtend', game.time + timedelta(hours=1))
        event.add('dtstamp', datetime.now())
        event.add('location', "BreakAway Field %s" % game.field)
        event['uid'] = '%s/%s@breakawaysports.com' % (now_string, shortuuid.uuid())
        event.add('priority', 5)

        alarm = Alarm()
        alarm.add("TRIGGER;RELATED=START", "-PT{0}M".format('45'))
        alarm.add('action', 'display')
        alarm.add('description', 'Breakaway game')

        event.add_component(alarm)
        cal.add_component(event)

    return HttpResponse(cal.to_ical(), content_type='text/calendar')