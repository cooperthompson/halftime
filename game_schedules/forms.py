import datetime
from functools import partial
from django import forms

DateInput = partial(forms.DateInput, {'class': 'datepicker', 'value': datetime.date.today().strftime('%m/%d/%Y')})


class DateRangeForm(forms.Form):
    start_date = forms.DateField(widget=DateInput())
    end_date = forms.DateField(widget=DateInput())


class GameDateForm(forms.Form):
    date = forms.DateField(widget=DateInput())
