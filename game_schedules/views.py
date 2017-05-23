from django.http import HttpResponse
from django.template import RequestContext, loader
from game_schedules.models import *
from game_schedules.forms import *
from datetime import datetime


def home(request):
    game_date_form = GameDateForm(request.GET)
    games = Game.objects.all()[:10]
    if game_date_form.is_valid():
        games = Game.objects.filter(time__date=datetime.now())[:10]

    leagues = League.objects.all()

    template = loader.get_template('home.html')
    context = RequestContext(request, {
        'leagues': leagues,
        'games': games,
        'form': game_date_form,
    })
    return HttpResponse(template.render(context))
