from django.conf import settings
import glob
import os
import re
import logging
from team_loader import TeamFileLoader
from game_loader import GameFileLoader
from game_schedules.models import *


class BreakawayLoader:
    def __init__(self, logger=logging.getLogger(__name__)):
        self.logger = logger
        self.organization = self.get_breakaway_org()

    @staticmethod
    def get_breakaway_org():
        try:
            org = Organization.objects.get(name="Breakaway")
        except Organization.DoesNotExist:
            org = Organization(name="Breakaway")
            org.save()

        return org

    def load_teams(self):
        team_loader = TeamFileLoader(self.organization)
        for team_file in self.get_txt_files(1):
            self.logger.info("Loading teams from {}".format(team_file))
            league = self.get_league(team_file)
            before_count = Team.objects.count()
            team_loader.load_team_file(team_file, league)
            after_count = Team.objects.count()
            self.logger.info("A total of {} teams were loaded from {}\n".format(after_count-before_count, team_file))

    def load_games(self):
        game_loader = GameFileLoader(self.organization)
        for game_file in self.get_txt_files(0):
            league = self.get_league(game_file)
            Game.objects.filter(league=league).delete()
            before_count = Game.objects.count()
            game_loader.load_game_file(game_file, league)
            after_count = Game.objects.count()
            self.logger.info("A total of {} games were loaded from {}\n".format(after_count-before_count, game_file))

    @staticmethod
    def get_txt_files(layout):
        txt_files = []

        import_dir = os.path.join(settings.BASE_DIR, "game_schedules", "importer", "breakaway", "files")
        os.chdir(import_dir)

        if layout:
            file_list = glob.glob('*-layout.txt')
        else:
            file_list = glob.glob('*-plain.txt')

        for filename in file_list:
            txt_files.append(filename)

        return txt_files

    def get_league(self, text_filename):
        match = re.match(".*\.(.*).txt", text_filename)
        if match:
            key = match.group(1).replace("-layout", "").replace("-plain", "")
        else:
            self.logger.error("Couldn't determine league name from {}".format(text_filename))
            return None

        try:
            league = League.objects.get(key=key)
        except League.DoesNotExist:
            self.logger.info("Couldn't find league %s.  Creating on-the-fly." % key)
            slug = key.replace(" ", "_")

            # default the name to be the key.
            # the name can be updated in the admin GUI to something user-readable.
            # The key should never be changed.
            league = League(name=key,
                            slug=slug,
                            key=key)
            league.save()
        return league
