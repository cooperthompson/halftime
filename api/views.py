from datetime import timedelta

from django.http import Http404, JsonResponse
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
    team_id = request.GET.get('id')

    try:
        team = Team.objects.get(id=team_id)
    except Team.DoesNotExist:
        raise Http404("Oops!  We couldn't find the team you were looking for.")

    games = team.games()
    events = []
    for game in games:
        event = {
            'title': game.name,
            'start': game.time,
            'end': game.time + + timedelta(hours=1)
        }
        events.append(event)

    return JsonResponse(events, safe=False)
