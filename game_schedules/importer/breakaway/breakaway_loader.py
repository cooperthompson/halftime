import logging
import re
from datetime import datetime

import pytz
from django.conf import settings
from unidecode import unidecode
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
            org = Organization(name="Breakaway",
                               short_name="BA")
            org.save()

        return org

    def import_file(self, league, reimport):
        if reimport:
            # TODO:  delete existing games/teams for this league
            pass

        self.logger.info("loading file {}".format(league.breakaway_word_file))
        teams_before_count = Team.objects.count()
        games_before_count = Game.objects.count()

        import docx
        doc = docx.Document(league.breakaway_word_file)

        for table in doc.tables:
            if self.is_team_table(table):
                self.load_teams_from_table(table, league)

            if self.is_game_table(table):
                self.load_games_from_table(table, league)

        teams_after_count = Team.objects.count()
        games_after_count = Game.objects.count()
        self.logger.info("A total of {} teams were loaded.\n".format(teams_after_count - teams_before_count))
        self.logger.info("A total of {} games were loaded.\n".format(games_after_count - games_before_count))

    def load_teams_from_table(self, table, league):
        for row in table.rows:
            team_number = row.cells[0].text.replace('.', '')
            if not team_number:
                continue
            team_name = row.cells[1].text

            matches = re.findall("(.*?)\((.*?)\)", team_name)
            for match in matches:
                team_number = int(team_number)
                team_name = unidecode(match[0].strip())
                team_color = unidecode(match[1].strip())
                slug = team_name.replace(" ", "-").lower()

                try:
                    team = Team.objects.filter(league=league).get(slug=slug)
                except Team.MultipleObjectsReturned:
                    team = Team.objects.filter(league=league).filter(slug=slug).get(number=team_number)
                except Team.DoesNotExist:
                    self.logger.info("Creating team {}".format(team_name))
                    team = Team()

                team.number = team_number
                team.name = team_name
                team.slug = slug
                team.color = team_color
                team.league = league
                print("creating team {}".format(team))
                team.save()

    def load_games_from_table(self, table, league):
        column_iter = iter(table.columns)

        # the breakaway word doc has two columns with some merged cells.
        # the first column has the team vs. team data (e.g. 5-4)
        # the second column has the time and field for the game (e.g. 11:002)

        for tvt_column in column_iter:
            time_and_field_column = None
            try:
                time_and_field_column = next(column_iter)
            except StopIteration:
                pass  # TODO:  Figure out why the file has three colum
            game_date = None
            for index, cell in enumerate(tvt_column.cells):
                if "WEEK" in cell.text.strip():
                    continue

                # regex check for the date row (i.e. Mo.Feb 3)
                # these are merged cells, so we just parse this of the first column
                match = re.match("(\w+?)\s*?\.?\s*?(\w+?)\.?\s+?(\d+)", cell.text)
                if match:
                    game_date = self.parse_game_date_cell(match, cell.text)
                    continue

                # this is split across two columns, so we check both
                # team-vs-team regex match example:  19-20
                tvt_match = re.match("\s*(\d+)-(\d+)", cell.text)

                # game-field regex match example:  11:002
                cell = time_and_field_column.cells[index]
                gf_match = re.match("(\d+:\d{2})(\d?)", cell.text)
                if tvt_match and gf_match:
                    self.parse_game_info_cell(tvt_match, gf_match, game_date, league)

    @staticmethod
    def parse_game_date_cell(match, cell):
        game_date = None
        game_mo = match.group(2)
        game_dt = match.group(3)
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
                game_year = datetime.now().year+1
        else:
            game_year = datetime.now().year

        try:
            game_date = datetime(game_year, game_month, game_dt)
        except ValueError as e:
            print("Unable to determine game date for {}\n{}".format(cell, e))

        return game_date

    def parse_game_info_cell(self, tvt_match, gf_match, game_date, league):
        home_team = self.get_team(int(tvt_match.group(1)), league)
        away_team = self.get_team(int(tvt_match.group(2)), league)
        game_time = self.parse_game_time(gf_match.group(1), game_date)
        game_field = self.parse_game_field(gf_match.group(2))
        game_name = '{} vs. {} at {}'.format(home_team, away_team, game_field.name)

        game = Game(name=game_name,
                    time=game_time,
                    league=home_team.league)
        game.field = game_field
        game.home_team = home_team
        game.away_team = away_team
        try:
            print("creating game {}".format(game))
            game.save()
        except Exception as e:
            self.logger.error("Error saving game: {}\n{}".format(game, e))

    def parse_game_time(self, time_string, game_date):
        match = re.match("(\d+):(\d{2})", time_string)
        if not match:
            self.logger.error("Unable to parse the game time from {}".format(time_string))
        game_hr = int(match.group(1))
        game_mn = int(match.group(2))

        central_tz = pytz.timezone('America/Chicago')
        game_date = datetime(game_date.year, game_date.month, game_date.day, game_hr, game_mn, tzinfo=central_tz)

        return game_date

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
            field_number = int(field_number)
        except ValueError:
            self.logger.error("Field number is messed up: {}".format(field_number))
            return None

        try:
            field = Field.objects.filter(organization=self.organization).get(number=field_number)
        except Field.DoesNotExist:
            field = Field(organization=self.organization,
                          number=field_number,
                          name="{} Field {}".format(self.organization, field_number),
                          short_name="{}-F{}".format(self.organization.short_name, field_number)
                          )
            field.save()

        return field

    @staticmethod
    def is_team_table(table):
        for cell in table.rows[0].cells:
            if 'TEAM' in cell.text.upper() and 'COLOR' in cell.text.upper():
                return True
        return False

    @staticmethod
    def is_game_table(table):
        # Simple easy check first
        for cell in table.rows[0].cells:
            if 'WEEK' in cell.text.upper():
                return True

        # Sometimes there are multiple tables and the later ones don't have the week heading in the first row
        for row in table.rows:
            for cell in row.cells:
                if 'WEEK' in cell.text.upper():
                    return True

        return False
