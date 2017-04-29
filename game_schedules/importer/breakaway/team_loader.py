import codecs
import re
import logging
from unidecode import unidecode
from game_schedules.models import *


class TeamFileLoader:
    def __init__(self, organization, logger=logging.getLogger(__name__)):
        self.logger = logger
        self.organization = organization

    def load_team_file(self, text_filename, league):
        with codecs.open(text_filename, encoding='utf-8', mode='r') as text_file:
            mode = "team"

            for line in text_file:
                if "TEAM (COLOR)" in line.strip():
                    mode = "team"
                if "QUICK NOTES" in line.strip():
                    mode = "team-complete"
                if line.strip() == "WEEK 1":
                    mode = "sched"
                if "IMPORTANT EVERYONE READ" in line.strip():
                    mode = "sched-complete"

                if mode == "team" and re.match("\d+.*", line.strip()):
                    self.process_team_line(line, league)

    def process_team_line(self, line, league):
        """
        A single line from the PDF to be parsed for team data
        Note that there can be multiple teams per line.
        """
        matches = re.findall("(\d+)\.?\s+(.*?)\((.*?)\)", line)
        for match in matches:
            team_id = match[0]
            team_number = int(team_id)
            team_name = unidecode(match[1].strip())
            team_color = unidecode(match[2].strip())

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
            team.save()

