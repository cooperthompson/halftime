import logging
from game_schedules.models import *


class E608Loader:
    def __init__(self, league):
        self.logger = logging.getLogger('halftime')
        self.league = league
        self.organization = self.get_breakaway_org()

    @staticmethod
    def get_breakaway_org():
        try:
            org = Organization.objects.get(name="608Elite")
        except Organization.DoesNotExist:
            org = Organization(name="608Elite",
                               short_name="608")
            org.save()
        return org

    def clear_existing_teams_for_league(self):
        Team.objects.filter(league=self.league).delete()

    def clear_existing_teams_for_league(self):
        Game.objects.filter(league=self.league).delete()

    def load_teams(self):
        self.clear_existing_teams_for_league()
        self.load_teams_from_file()

    def load_games(self):
        self.clear_existing_games_for_league()
        self.load_games_from_file()

    def load_teams_from_file(self):
        for line in self.league.team_file:
            line = line.decode('utf-8')
            line_array = line.split('\t')
            team = Team(number=line_array[0],
                        name=line_array[1],
                        color=line_array[2],
                        league=self.league)
            team.save()

    def load_games_from_file(self):
        for line in self.league.team_file:
            line = line.decode('utf-8')
