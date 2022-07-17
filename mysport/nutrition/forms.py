from django import forms

from .models import *


class ProductCreateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ProductCreateForm, self).__init__(*args, **kwargs)
        self.fields['maker'].empty_label = 'Выберите'
        self.fields['category'].empty_label = 'Выберите'

    class Meta:
        model = Product
        fields = ('category', 'maker', 'price', 'content', )
        widgets = {
            'content': forms.Textarea(attrs={'cols': 50, 'rows': 10}),
        }


class CommentCreateForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('content', )
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3})
        }


