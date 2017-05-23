from functools import partial
from django import forms

DateInput = partial(forms.DateInput, {'class': 'datepicker'})


class DateRangeForm(forms.Form):
    start_date = forms.DateField(widget=DateInput())
    end_date = forms.DateField(widget=DateInput())


class GameDateForm(forms.Form):
    date = forms.DateField(widget=DateInput())
