from importer.breakaway.breakaway_loader import BreakawayLoader
from django.core.management.base import BaseCommand
import logging
import sys
from game_schedules.models import *


class Command(BaseCommand):
    help = 'Load team and game data into the database'

    def __init__(self):
        super(Command, self).__init__()

        logger = logging.getLogger()
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
        handler.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        self.loader = BreakawayLoader(logger)

    def add_arguments(self, parser):
        parser.add_argument('--teams', action='store_true', default=False)
        parser.add_argument('--games', action='store_true', default=False)
        parser.add_argument('--reset', action='store_true', default=False)

    def handle(self, *args, **options):
        if options['teams']:
            self.loader.load_teams()
        if options['games']:
            self.loader.load_games()
        if options['reset']:
            Organization.objects.all().delete()
            Field.objects.all().delete()
            Season.objects.all().delete()
            League.objects.all().delete()
            Game.objects.all().delete()
            Team.objects.all().delete()

