from rest_framework import serializers

from game_schedules.models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'teams', )


class TeamSerializer(serializers.ModelSerializer):

    class Meta:
        model = Team


class GameSerializer(serializers.ModelSerializer):
    #league = serializers.HyperlinkedIdentityField('league', view_name='league-list')

    class Meta:
        model = Game
        fields = ('name', 'league', 'teams', 'time', 'field', 'is_today', 'color_conflict')
