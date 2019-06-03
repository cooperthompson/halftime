import logging
import re
from datetime import datetime
import pytz
from django.utils.text import slugify

from game_schedules.models import *
from django.conf import settings

from importer.importer import LeagueImporter


class E608Loader(LeagueImporter):
    def __init__(self, league):
        self.logger = logging.getLogger('halftime')
        self.league = league
        self.organization = self.get_org()

    @staticmethod
    def get_org():
        try:
            org = Organization.objects.get(name="608Elite")
        except Organization.DoesNotExist:
            org = Organization(name="608Elite",
                               short_name="608")
            org.save()
        return org

    def load_teams(self):
        self.clear_existing_teams_for_league()
        self.load_teams_from_file()
        pass

    def load_games(self):
        self.clear_existing_games_for_league()
        self.load_games_from_file()
        pass

    def load_teams_from_file(self):
        for line in self.league.team_file:
            line = line.decode('utf-8')
            line_array = line.split('\t')
            team = Team(number=line_array[2],
                        name=line_array[0],
                        color=line_array[1],
                        league=self.league,
                        slug=slugify(line_array[0]))
            team.save()

    def load_games_from_file(self):
        for line in self.league.game_file:
            try:
                line = line.decode('utf-8')

                # regex check for the date row (e.g. 06/09)
                match = re.match(r"\s*(\d+)/(\d+)", line)
                if match:
                    game_date = self.parse_game_date(match, line)
                    self.logger.info("Processing games on {}".format(game_date.strftime('%a %b %d')))

                # regex check for the game row (e.g. 5:00 (1)	1v2)
                match = re.match(r"(\d{1,2}):(\d{2})\s+\((\d)\)\s+(\d+)v(\d+)", line.strip())
                if match:
                    # Combine the date header (e.g. 06/09) with the game time (e.g. 5:00) into a datetime
                    game_datetime = self.parse_game_time(match, game_date)
                    self.save_game(match, game_datetime)
            except Exception as e:
                self.logger.error('{} while processing {}'.format(e, line))

    def save_game(self, match, game_datetime):
        home_team = self.get_team(match.group(4), self.league)
        away_team = self.get_team(match.group(5), self.league)
        game_field = self.parse_game_field(match.group(3))

        game_name = '{} vs. {} at {}'.format(home_team, away_team, game_field.name)

        game = Game(name=game_name,
                    time=game_datetime,
                    league=home_team.league)
        game.field = game_field
        game.home_team = home_team
        game.away_team = away_team

        try:
            game.save()
        except Exception as e:
            self.logger.error("Error saving game: {}\n{}".format(game, e))
        finally:
            self.logger.info("\tCreated game {}".format(game))

    @staticmethod
    def parse_game_date(match, line):
        game_date = None
        game_month = int(match.group(1))
        game_dt = int(match.group(2))

        # Since the year isn't specified, we need to rely on setting the YEAR_CUTOVER flag
        # to turn on special logic to bump the games that run into the subsequent year.
        if settings.YEAR_CUTOVER:
            if game_month == 12:
                game_year = datetime.now().year
            else:
                game_year = datetime.now().year + 1
        else:
            game_year = datetime.now().year

        try:
            game_date = datetime(game_year, game_month, game_dt)
        except ValueError as e:
            print("Unable to determine game date for {}\n{}".format(line, e))

        return game_date

    @staticmethod
    def parse_game_time(match, game_date):
        game_hr = int(match.group(1))
        game_mn = int(match.group(2))
        game_am = ""  # 608 is always PM

        # Assume the game is in the evening, unless it is explicitly indicated to be morning
        if game_am != "AM" and game_hr != 12:
            game_hr = game_hr + 12
        if game_hr == 24:
            game_hr = 0

        central_tz = pytz.timezone('America/Chicago')
        # game_datetime = datetime(game_date.year, game_date.month, game_date.day, game_hr, game_mn, tzinfo=central_tz)
        game_datetime = datetime(year=game_date.year,
                                 month=game_date.month,
                                 day=game_date.day,
                                 hour=game_hr,
                                 minute=game_mn)
        game_datetime = central_tz.localize(game_datetime)

        return game_datetime
