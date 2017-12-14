from django.http import HttpResponse
from django.template import loader
from game_schedules.models import *
from game_schedules.forms import *
import datetime


def home(request):
    game_form = GameForm(request.GET)
    if game_form.is_valid():
        game_date = game_form.cleaned_data['date']
        games = Game.objects.filter(time__date=game_date)

        if game_date == datetime.date.today():
            game_date_display = "Today's Games"
        elif datetime.date.today() + datetime.timedelta(7) > game_date >= datetime.date.today():
            game_date_display = "Games for this {}".format(game_date.strftime('%A'))
        else:
            game_date_display = "Games for {}".format(game_date.strftime('%A %b %#d'))
    else:
        games = Game.objects.filter(time__date=datetime.datetime.now())[:10]
        game_date_display = "Today's Games"

    leagues = League.objects.all().order_by('org')

    template = loader.get_template('home.html')
    context = {
        'leagues': leagues,
        'games': games,
        'form': game_form,
        'game_date_display': game_date_display
    }
    return HttpResponse(template.render(context))


