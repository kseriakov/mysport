from django import forms

from .models import *


class ImageCreateForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ('picture', )
        widgets = {
            # 'product': forms.TextInput(attrs={'type': 'hidden'}),
            # 'user': forms.TextInput(attrs={'type': 'hidden'}),
        }

