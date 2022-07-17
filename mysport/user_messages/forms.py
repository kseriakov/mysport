from django import forms

from .models import *


class UserMessageCreateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(UserMessageCreateForm, self).__init__(*args, **kwargs)
        self.fields['content'].widget = forms.Textarea(attrs={'rows': 3, 'cols': 100})
        self.fields['content'].label = 'Ваш ответ'

    class Meta:
        model = UserMessage
        fields = ('content', )
