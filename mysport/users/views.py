from django.contrib.auth import logout
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.views import LogoutView, LoginView, PasswordResetView, PasswordChangeView, \
    PasswordResetDoneView, PasswordResetCompleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.forms import ModelForm
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.generic import UpdateView, CreateView
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.edit import FormMixin, FormView

from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework import permissions

from .link_workouts import *
from .models import *
from .forms import *
from .serializers import *


def home(request):
    return render(request, 'users/home.html')


def profile(request):
    get_telegram = True if SecureCode.objects.filter(user=request.user) else False
    return render(request, 'users/profile.html', context={'get_telegram': get_telegram})


class AddTelegram(FormView, LinkWorkouts):
    form_class = SecureCodeForm
    template_name = 'users/add_telegram.html'
    success_url = reverse_lazy('profile')

    def form_valid(self, form):
        self._code = form.cleaned_data['code']
        self.add_telegram()
        return super().form_valid(form)

    def add_telegram(self):
        if qs := SecureCode.objects.filter(code=self._code):
            # Идет перепревязка на другой аккаунт в телеграм
            if qs_sc := SecureCode.objects.filter(user=self.request.user):
                sc = qs_sc.last()
                sc.user = None
                sc.save()
            obj = qs.last()
            obj.user = self.request.user
            obj.save()

            # Далее пробежимся по всем workouts для пользователя, чтобы добавить в них user и telegram_id
            # а также слить дни, где были добавлены тренировки из телеги и сайта одновременно
            self.link_data_user(sec_code_obj=obj)

            messages.add_message(self.request, messages.SUCCESS, 'Telegram-bot успешно привязан')
        else:
            messages.add_message(self.request, messages.ERROR, 'Введен неверный код подтверждения')


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
    from_email = 'infohakhak@yandex.ru'


class UserPasswordResetCompleteView(PasswordResetCompleteView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["login_url"] = reverse_lazy('site_login')
        return context


class UserChangeView(UpdateView):
    form_class = UserUpdateForm
    template_name = 'users/change_user.html'
    model = get_user_model()
    success_url = reverse_lazy('profile')


class PasswdChangeView(PasswordChangeView):
    template_name = 'users/password_change.html'


# DRF

# начальная точка входа в api
@api_view(['GET'])
def api_root(request, format=None):
    # возвращаем список url адресов, на входе в api
    return Response({
        reverse('products-list', request=request, format=None),
        reverse('users-list', request=request, format=None),
        reverse('makers-list', request=request, format=None),
        reverse('countries-list', request=request, format=None),
        reverse('categories-list', request=request, format=None),
    })


class UserListAPIView(generics.ListAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer


class UserDetailAPIView(generics.RetrieveAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer


# Завершая, используем ViewSets

# Заменяет два класса выше, обрабатывает все методы запросов
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
