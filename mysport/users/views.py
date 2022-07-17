from django.contrib.auth import logout
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User
from django.contrib.auth.views import LogoutView, LoginView, PasswordResetView, PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.generic import UpdateView, CreateView
from django.contrib import messages

from .link_workouts import *
from .models import *
from .forms import *


def home(request):
    return render(request, 'users/home.html')


def profile(request):
    get_telegram = True if SecureCode.objects.filter(user=request.user) else False
    return render(request, 'users/profile.html', context={'get_telegram': get_telegram})


def add_telegram(request, user_name):
    if request.method == 'POST':
        secure_code = request.POST.get('secure-code')
        if qs := SecureCode.objects.filter(code=secure_code):
            # Идет перепревязка на другой аккаунт в телеграм
            if qs_sc := SecureCode.objects.filter(user=request.user):
                sc = qs_sc.last()
                sc.user = None
                sc.save()
            obj = qs.last()
            obj.user = request.user
            obj.save()

            # Далее пробежимся по всем workouts для пользователя, чтобы добавить в них user и telegram_id
            link_data_user(sec_code_obj=obj)

            messages.add_message(request, messages.SUCCESS, 'Telegram-bot успешно привязан')
            return redirect('profile')
        else:
            messages.add_message(request, messages.ERROR, 'Введен неверный код подтверждения')

    return render(request, 'users/add_telegram.html')


class UserLogout(LogoutView):
    next_page = reverse_lazy('home')

    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        messages.add_message(self.request, messages.SUCCESS, 'Вы успешно вышли из системы')
        return super(UserLogout, self).dispatch(request, *args, **kwargs)


class UserLogin(LoginView):
    authentication_form = UserLoginForm
    template_name = 'users/login.html'
    next_page = reverse_lazy('home')


class UserCreate(CreateView):
    form_class = UserCreateForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('home')


class PasswordReset(PasswordResetView):
    template_name = 'users/reset_password.html'
    email_template_name = 'users/reset_password_email.html'
    subject_template_name = 'users/reset_password_email_subject.html'
    from_email = 'pinkhit@mail.ru'


class UserChangeView(UpdateView):
    form_class = UserUpdateForm
    template_name = 'users/change_user.html'
    model = get_user_model()
    success_url = reverse_lazy('profile')


class PasswdChangeView(PasswordChangeView):
    template_name = 'users/password_change.html'

