from django.contrib.auth.views import PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.urls import path, include
from .views import *

from rest_framework.authtoken import views


urlpatterns = [
    path('', home, name='home'),
    path('profile/', profile, name='profile'),
    path('logout/', UserLogout.as_view(), name='logout'),
    path('login/', UserLogin.as_view(), name='login'),
    path('register/', UserCreate.as_view(), name='register'),
    path('profile/change/user/<int:pk>', UserChangeView.as_view(), name='change_user'),
    path('reset-password/', PasswordReset.as_view(), name='reset_password'),
    path('reset-password-done/', PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset-password-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset-password-complete/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('profile/change/password/', PasswdChangeView.as_view(), name='password_change'),
    path('add-telegram/<str:user_name>/', add_telegram, name='add_telegram'),

]

urlpatterns_api = [
    path('users/api-view/', UserListAPIView.as_view()),
    path('users/api-view/<int:pk>', UserDetailAPIView.as_view()),
    path('api-token-auth/', views.obtain_auth_token)
    
]

urlpatterns += urlpatterns_api