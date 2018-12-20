from rest_framework import serializers

from game_schedules.models import *


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'


class OrganizationSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Organization
        fields = '__all__'


class FieldSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Field
        fields = '__all__'


class SeasonSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Season
        fields = '__all__'


class LeagueSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = League
        fields = '__all__'


class TeamSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = Team
        fields = '__all__'


class GameSerializer(serializers.HyperlinkedModelSerializer):
    home_team = TeamSerializer(read_only=True)
    away_team = TeamSerializer(read_only=True)
    field = serializers.StringRelatedField()
    league = serializers.StringRelatedField()

    class Meta:
        model = Game
        fields = ('id', 'field', 'league', 'name', 'time', 'home_team', 'away_team')
