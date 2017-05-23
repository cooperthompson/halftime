import codecs
from datetime import datetime
import re
import logging

import pytz

from game_schedules.models import *


class GameFileLoader:
    def __init__(self, organization, logger=logging.getLogger(__name__)):
        self.logger = logger
        self.organization = organization

    def load_game_file(self, text_filename, league):
        with codecs.open(text_filename, encoding='utf-8', mode='r') as text_file:
            mode = "start"
            game_date = None

            for line in text_file:
                # skip everything before week 1 because some of the team rows can match the game regexes
                if "WEEK" in line.strip():
                    mode = "sched"
                    continue

                if mode != "sched":
                    continue

                match, parsed_game_date = self.parse_game_date_row(line)
                if match:
                    game_date = parsed_game_date
                else:
                    self.parse_game_row(line, game_date, league)

    def parse_game_row(self, line, game_date, league):

        match = re.match("\s*(\d+)-(\d+)\s+(\d+:\d{2})(\d?)", line)  # regex match example:  19-20 7:002
        if match:
            home_team = self.get_team(int(match.group(1)), league)
            away_team = self.get_team(int(match.group(2)), league)
            game_time = self.parse_game_time(match.group(3), game_date)
            game_field = self.parse_game_field(match.group(4))
            game_name = '{} vs. {} at {}'.format(home_team, away_team, game_field.name)

            game = Game(name=game_name,
                        time=game_time,
                        league=home_team.league)
            game.field = game_field
            game.home_team = home_team
            game.away_team = away_team
            try:
                game.save()
            except Exception as e:
                self.logger.error("Error saving game: {}\n{}".format(game, e))

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
            self.logger.warn("Couldn't find team %s in league %s" % (team_number, league))

        return team

    def parse_game_date_row(self, line):
        # regex check for the date row (i.e. Mo.Feb 3)
        match = re.match("(\w+?)\s*?\.?\s*?(\w+?)\.?\s+?(\d+)", line)
        # match = re.match("(\w{2,3})\.\s?(\w{3}).*?\s?(\d+)", line)

        game_date = None
        if match:
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

            # hard code year transition for now since there isn't anything in the file that says a year
            # TODO:  check the file timestamp and use that to calculate the current and next year
            if game_month == 12:
                game_year = 2018
            else:
                game_year = 2017

            try:
                game_date = datetime(game_year, game_month, game_dt)
            except ValueError as e:
                self.logger.error("Unable to determine game date for {}\n{}".format(line, e))

        return match, game_date
