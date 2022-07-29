from django.contrib.auth.views import PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.urls import path, include
from .views import *


urlpatterns = [
    path('', home, name='home'),
    path('profile/', profile, name='profile'),
    path('logout/', UserLogout.as_view(), name='site_logout'),
    path('login/', UserLogin.as_view(), name='site_login'),
    path('register/', UserCreate.as_view(), name='register'),
    path('profile/change/user/<int:pk>', UserChangeView.as_view(), name='change_user'),
    path('reset-password/', PasswordReset.as_view(), name='reset_password'),
    path('reset-password-done/', PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset-password-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset-password-complete/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('profile/change/password/', PasswdChangeView.as_view(), name='password_change'),
    path('add-telegram/<str:user_name>/', AddTelegram.as_view(), name='add_telegram'),

]


# Создаем вручную маршруты для ViewSet
users_list = UserViewSet.as_view({
    'get': 'list',  # get запрос будет отрабатывать стандартный метод UserViewSet - list
})

users_detail = UserViewSet.as_view({
    'get': 'retrieve',
})
