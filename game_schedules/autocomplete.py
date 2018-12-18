from dal import autocomplete
from django.db.models import Q

from game_schedules.models import Team


class TeamAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Team.objects.all()

        if self.q:
            qs = qs.filter(Q(name__icontains=self.q) | Q(number__icontains=self.q))

        return qs
