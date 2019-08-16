from django.http import HttpResponse, Http404
from django.template import loader
from django.views.decorators.clickjacking import xframe_options_exempt

from game_schedules.models import *
from datetime import date, timedelta


def home_view(request):
    today = date.today()
    tomorrow = today + timedelta(days=1)
    games = Game.objects.filter(time__gte=today)
    games = games.filter(time__lt=tomorrow)
    games = games.order_by("time", "field")

    leagues = League.objects.all().order_by('org')

    template = loader.get_template('home.html')
    context = {
        'organizations': Organization.objects.all().order_by('order'),
        'leagues': leagues,
        'games': games,
    }
    return HttpResponse(template.render(context, request=request))


def league_view(request, slug):
    try:
        league = League.objects.get(slug=slug)
    except League.DoesNotExist:
        raise Http404("Oops!  We couldn't find the league you were looking for.")

    teams = Team.objects.filter(league=league)
    games = Game.objects.filter(league=league)
    games = games.select_related('home_team', 'away_team', 'field')

    template = loader.get_template('league.html')
    context = {
        'teams': teams,
        'league': league,
        'games': games
    }
    return HttpResponse(template.render(context, request=request))


def team_view(request, slug):
    try:
        team = Team.objects.get(slug=slug)
    except Team.DoesNotExist:
        raise Http404("Oops!  We couldn't find the team you were looking for.")
    games = team.games()

    template = loader.get_template('team.html')
    context = {
        'games': games,
        'team': team
    }
    return HttpResponse(template.render(context, request=request))


@xframe_options_exempt
def breakaway_iframe(request):
    leagues = League.objects.all().order_by('org')

    template = loader.get_template('breakaway-iframe.html')
    context = {
        'leagues': leagues,
    }
    return HttpResponse(template.render(context, request=request))


def breakaway_mock(request):
    template = loader.get_template('breakaway-mock.html')
    return HttpResponse(template.render(request=request))


def standings(request, slug):
    try:
        league = League.objects.get(slug=slug)
    except League.DoesNotExist:
        raise Http404("Oops!  We couldn't find the league you were looking for.")

    teams = Team.objects.filter(league=league)
    for team in teams:
        team.calculate_stats()

    template = loader.get_template('standings.html')
    context = {
        'teams': teams,
        'league': league,
    }
    return HttpResponse(template.render(context, request=request))
