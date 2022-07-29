from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UsernameField, UserChangeForm
from django import forms
from django.core.exceptions import ValidationError

from users.models import SecureCode


class UserLoginForm(AuthenticationForm):
    password = forms.CharField(label='Пароль', max_length=100,
                               widget=forms.PasswordInput(attrs={'class': 'passwd'}),
                               )
    username = forms.CharField(label='Имя пользователя', max_length=100,
                               widget=forms.TextInput(attrs={'class': 'usermane'}),
                               )


class UserCreateForm(UserCreationForm):
    telegram = forms.CharField(max_length=50, label='Привязать телеграм-бота MySport', required=False)

    def __init__(self, *args, **kwargs):
        super(UserCreateForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].label = 'Ваше имя'
        self.fields['first_name'].required = False
        self.fields['last_name'].label = 'Ваша фамилия'
        self.fields['last_name'].required = False
        self.fields['username'].label = 'Ваш логин'
        self.fields['username'].widget.attrs.update({'class': 'req-field'})
        self.fields['username'].widget.attrs['autofocus'] = False
        self.fields['password1'].widget.attrs.update({'class': 'req-field'})
        self.fields['password2'].widget.attrs.update({'class': 'req-field'})
        self.fields['email'].widget.attrs.update({'class': 'req-field'})

    def clean_telegram(self):
        if code := self.cleaned_data.get('telegram'):
            if qs := SecureCode.objects.filter(code=code):
                return code
            else:
                raise ValidationError(
                    ("Неверный код, вы можете привязать bot'a после регистрации в личном "
                     "кабинете просто оставьте данное поле пустым"),
                    code='invalid'
                )

    class Meta:
        model = get_user_model()
        fields = ('first_name', 'last_name', 'username', 'email', 'password1', 'password2')


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ('first_name', 'last_name', 'username', 'email', )


class SecureCodeForm(forms.Form):
    code = forms.CharField(max_length=50, )