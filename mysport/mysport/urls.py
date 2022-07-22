"""mysport URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

# JWT токены
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from mysport.settings import MEDIA_URL, MEDIA_ROOT, DEBUG

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('users.urls')),
    path('nutrition/', include('nutrition.urls')),
    path('workout/', include('workout.urls')),
    path('messages/', include('user_messages.urls')),
    path('api-auth/', include('rest_framework.urls')), # страница авторизации
    ]


if DEBUG:  # Если режим разработки
    urlpatterns += static(MEDIA_URL, document_root=MEDIA_ROOT)

# Добавляем авторизацию по токенам (простые и JWT)

# регистрация по токенам через библиотеку djoser
urlpatterns += [
    path('api/auth/', include('djoser.urls')),
    path('api/auth/', include('djoser.urls.authtoken'))
]
# api/auth/users/ - регистрация, нового пользователя
# api/auth/token/login/ - вход на сайт, в ответ получаем токен,
# который надо передавать в загловке запроса для прохождения аутентификации
# api/auth/token/login/ - удаляет токен для пользователя, чтобы получить токен снова
# надо пройти авторизацию снова

# JWT (здесь в заголовок добавляется Bearer вместо Token, как в простых)
urlpatterns += [
    # получения 2 токенов (access и refresh)
    path('api/auth-jwt/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),

    # обновление access токена (post запрос с refresh токеном)
    path('api/auth-jwt/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]