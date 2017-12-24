import datetime
from functools import partial

from dal import autocomplete
from django import forms

from game_schedules.models import Team

DateInput = partial(forms.DateInput, {'class': 'datepicker form-control',
                                      'value': datetime.date.today().strftime('%m/%d/%Y')})


class DateRangeForm(forms.Form):
    start_date = forms.DateField(widget=DateInput())
    end_date = forms.DateField(widget=DateInput())


class GameForm(forms.Form):
    date = forms.DateField(widget=DateInput(), required=False)
    team = forms.ModelChoiceField(
        queryset=Team.objects.all(),
        widget=autocomplete.ModelSelect2(url='team-autocomplete',
                                         attrs={
                                             'class': 'form-control',
                                             'data-minimum-input-length': 1,
                                             'data-placeholder': 'Team'
                                         }),
        required=False
    )
