from dal import autocomplete

from game_schedules.models import Team


class TeamAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Team.objects.all()

        return qs
