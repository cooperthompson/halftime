import logging
import re
from datetime import datetime

import pytz
from django.conf import settings
from unidecode import unidecode
from game_schedules.models import *


class BreakawayLoader:
    def __init__(self, league):
        self.logger = logging.getLogger('halftime')
        self.league = league
        self.organization = self.get_breakaway_org()

    @staticmethod
    def get_breakaway_org():
        try:
            org = Organization.objects.get(name="Breakaway")
        except Organization.DoesNotExist:
            org = Organization(name="Breakaway",
                               short_name="BA")
            org.save()
        return org

    def clear_existing_teams_for_league(self):
        Game.objects.filter(league=self.league).delete()

    def import_text_file(self, reimport):
        if reimport:
            self.clear_existing_teams_for_league()

        self.logger.info("loading file {}".format(self.league.breakaway_import_file))
        teams_before_count = Team.objects.count()
        games_before_count = Game.objects.count()

        self.load_teams_and_games_from_text_file()

        teams_after_count = Team.objects.count()
        games_after_count = Game.objects.count()
        self.logger.info("A total of {} new teams were loaded.\n".format(teams_after_count - teams_before_count))
        self.logger.info("A total of {} new games were loaded.\n".format(games_after_count - games_before_count))

    def load_teams_and_games_from_text_file(self):
        # text_file = open(self.league.breakaway_import_file, encoding='utf-8', mode='r')

        parse_state = "start"
        game_date = "0"

        for line in self.league.breakaway_import_file:
            try:
                line = line.decode('utf-8')
                if settings.BREAKAWAY_START_TEAM_MARKER in line.strip():
                    self.logger.info("Entering team parsing state.")
                    parse_state = "teams"
                    continue
                if settings.BREAKAWAY_START_GAMES_MARKER in line.strip():
                    self.logger.info("Entering game parsing state.")
                    parse_state = "games"
                    continue

                if parse_state == "teams" and re.match("\\d+.*", line.strip()):
                    self.save_team(line)

                # regex check for the date row (e.g. Mo.Feb 3)
                match = re.match(r"\w+\.\s?(\w+)\.?\s+?(\d+)", line)
                if parse_state == "games" and match:
                    game_date = self.parse_game_date(match, line)
                    self.logger.info("Processing games on {}".format(game_date.strftime('%a %b %d')))

                # regex check for the game row (e.g. 19-20 7:002)
                match = re.match(r"(\d+)-(\d+)\s+(\d{1,2}):(\d{2})\s*([AaPp]?[Mm]?)(\w?)", line.strip())
                if parse_state == "games" and match:
                    # Combine the date header (e.g. Mo.Feb 3) with the game time (e.g. 7:002) into a datetime
                    game_datetime = self.parse_game_time(match, game_date)
                    self.save_game(match, game_datetime)
            except Exception as e:
                self.logger.error('{} while processing {}'.format(e, line))

    def save_team(self, line):
        matches = re.findall(r'(\d+)\.?\s+(.*?)\((.*?)\)', line)
        for match in matches:
            team_number = int(match[0].strip())
            team_name = unidecode(match[1].strip())
            team_color = unidecode(match[2].strip())
            slug = team_name.replace(" ", "-").lower()

            try:
                team = Team.objects.filter(league=self.league).get(slug=slug)
                self.logger.info("Using existing team {}".format(team_name))
            except Team.MultipleObjectsReturned:
                team = Team.objects.filter(league=self.league).filter(slug=slug).get(number=team_number)
                self.logger.info("Using existing team {}".format(team_name))
            except Team.DoesNotExist:
                self.logger.info("Creating a new team {}".format(team_name))
                team = Team()

            team.number = team_number
            team.name = team_name
            team.slug = slug
            team.color = team_color
            team.league = self.league
            team.save()

    def save_game(self, match, game_datetime):
        home_team = self.get_team(match.group(1), self.league)
        away_team = self.get_team(match.group(2), self.league)
        game_field = self.parse_game_field(match.group(6))

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

    def get_team(self, team_number, league):
        team = None
        try:
            team = Team.objects.filter(league=league).get(number=team_number)
            # TODO: add slug matching to try to handle cross-season team linking when their number changes
        except Team.DoesNotExist:
            self.logger.warning("Couldn't find team %s in league %s" % (team_number, league))

        return team

    def parse_game_field(self, field_number):
        if not field_number:
            field_number = 1

        try:
            field = Field.objects.filter(organization=self.organization).get(identifier=field_number)
        except Field.DoesNotExist:
            field = Field(organization=self.organization,
                          identifier=field_number,
                          name="{} Field {}".format(self.organization, field_number),
                          short_name="{}-F{}".format(self.organization.short_name, field_number)
                          )
            field.save()
        except Field.MultipleObjectsReturned:
            field = Field.objects.filter(organization=self.organization).filter(identifier=field_number)[0]

        return field

    @staticmethod
    def parse_game_date(match, line):
        game_date = None
        game_mo = match.group(1)
        game_dt = match.group(2)
        game_dt = int(game_dt)
        game_month = None
        try:
            game_month = datetime.strptime(game_mo, '%b').month  # convert string format to month number
        except ValueError:
            try:
                game_month = datetime.strptime(game_mo, '%B').month  # convert string format to month number
            except ValueError:
                pass

        # Since breakaway doesn't specify the year, we need to rely on setting the YEAR_CUTOVER flag
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
        game_hr = int(match.group(3))
        game_mn = int(match.group(4))
        game_am = match.group(5)

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

