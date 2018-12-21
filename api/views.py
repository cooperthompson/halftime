from datetime import timedelta

from dateutil import parser
from django.http import JsonResponse
from django_filters import rest_framework as filters
from rest_framework import viewsets
from api.serializers import *
from game_schedules.models import *


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class OrganizationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer


class FieldViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Field.objects.all()
    serializer_class = FieldSerializer


class SeasonViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Season.objects.all()
    serializer_class = SeasonSerializer


class LeagueViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = League.objects.all()
    serializer_class = LeagueSerializer


class TeamViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer


class GameDateFilter(filters.FilterSet):
    time = filters.DateTimeFilter(lookup_expr="date")

    class Meta:
        model = Game
        fields = ['time']


class GameViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    search_fields = ('name', 'time', 'field__name', 'league__name')
    filter_class = GameDateFilter


def team_events(request):
    team_id = request.GET.get('team_id')
    start = request.GET.get('start')
    end = request.GET.get('end')

    start_date = parser.parse(start).date()
    end_date = parser.parse(end).date()

    try:
        team = Team.objects.get(id=team_id)
        games = team.games()
    except Team.DoesNotExist:
        games = Game.objects.all()

    if start:
        games = games.filter(time__date__gte=start_date)
    if end:
        games = games.filter(time__date__lt=end_date)
    events = []
    for game in games:
        start_time = game.time
        end_time = game.time + timedelta(hours=1)
        event = {
            'title': game.name,
            'start': start_time,
            'end': end_time
        }
        events.append(event)

    return JsonResponse(events, safe=False)
