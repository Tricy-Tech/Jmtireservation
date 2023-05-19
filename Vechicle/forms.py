

from django import forms
from django.forms.widgets import DateInput, DateTimeInput
from .models import Reservation

class DateRangeSelectionForm(forms.Form):
    start_date = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}), label='Start Date')
    end_date = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}), label='End Date')



class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['user','name','start_date', 'end_date','participant', 'status']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ReservationForm, self).__init__(*args, **kwargs)
        if user:
            self.initial['user'] = user
            self.initial['name'] = kwargs.get('name')
            self.initial['start_date'] = kwargs.get('start_date')
            self.initial['end_date'] = kwargs.get('end_date')
            self.initial['participant'] = kwargs.get('participant')
            self.initial['status'] = kwargs.get('status')
    



class ParticipantForm(forms.Form):
    participant = forms.CharField(max_length=15, required=False, label='participant')

