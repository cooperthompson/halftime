import logging
import re
from datetime import datetime

import pytz
from django.conf import settings
from unidecode import unidecode
from game_schedules.models import *


class LeagueImporter:

    def clear_existing_teams_for_league(self):
        Team.objects.filter(league=self.league).delete()

    def clear_existing_games_for_league(self):
        Game.objects.filter(league=self.league).delete()

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