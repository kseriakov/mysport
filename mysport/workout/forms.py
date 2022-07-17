from django import forms
from .models import *


class WorkoutFormCreate(forms.Form):
    content = forms.CharField(label='Укажите одно упражнение', widget=forms.Textarea(attrs={'rows': 5}))


class WorkoutFormUpdate(forms.Form):
    exercise = forms.CharField(widget=forms.Textarea(attrs={'rows': 1, 'required': False}))

    def __init__(self, *args, **kwargs):
        super(WorkoutFormUpdate, self).__init__(*args, **kwargs)
        self.fields['exercise'].required = False
