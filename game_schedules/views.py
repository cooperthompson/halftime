from django.http import HttpResponse
from django.template import loader
from game_schedules.models import *
import datetime


def home(request):
    games = Game.objects.filter(time__date=datetime.datetime.now())[:10]
    game_date_display = "Today's Games"

    leagues = League.objects.all().order_by('org')

    template = loader.get_template('home.html')
    context = {
        'organizations': Organization.objects.all().order_by('order'),
        'leagues': leagues,
        'games': games,
        'game_date_display': game_date_display
    }
    return HttpResponse(template.render(context, request=request))


