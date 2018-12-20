from django.http import HttpResponse, Http404
from django.template import loader
from game_schedules.models import *
import datetime


def home_view(request):
    # games = Game.objects.filter(time__date=datetime.datetime.now())[:10]

    leagues = League.objects.all().order_by('org')

    template = loader.get_template('home.html')
    context = {
        'organizations': Organization.objects.all().order_by('order'),
        'leagues': leagues,
        # 'games': games,
    }
    return HttpResponse(template.render(context, request=request))


def league_view(request):
    league_id = request.GET.get('id')

    try:
        league = League.objects.get(id=league_id)
    except League.DoesNotExist:
        raise Http404("Oops!  We couldn't find the league you were looking for.")

    teams = Team.objects.filter(league=league)

    template = loader.get_template('league.html')
    context = {
        'teams': teams,
        'league': league
    }
    return HttpResponse(template.render(context, request=request))


def team_view(request):
    team_id = request.GET.get('id')

    try:
        team = Team.objects.get(id=team_id)
    except Team.DoesNotExist:
        raise Http404("Oops!  We couldn't find the team you were looking for.")
    games = team.games()

    template = loader.get_template('team.html')
    context = {
        'games': games,
        'team': team
    }
    return HttpResponse(template.render(context, request=request))



