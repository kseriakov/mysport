from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.routers import DefaultRouter

from users.views import *
from nutrition.views import *
from users.urls import *

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
    ]


if DEBUG:  # Если режим разработки
    urlpatterns += static(MEDIA_URL, document_root=MEDIA_ROOT)


# DRF

# Регистрируем роутер для построения им маршрутов для имеющихся у нас ViewSets
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'products', ProductViewSet, basename='products')
router.register(r'makers', MakerViewSet, basename='makers')
router.register(r'countries', CountryViewSet, basename='countries')
router.register(r'categories', CategoryViewSet, basename='categories'),

urlpatterns += [path('api/', include(router.urls))]

# Добавляем авторизацию по токенам (простые и JWT)

# регистрация по токенам через библиотеку djoser
urlpatterns += [
    path('api/auth/session/', include('rest_framework.urls')),  # страница авторизации, сессии и куки
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
    path('api/auth/jwt/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),

    # обновление access токена (post запрос с refresh токеном)
    path('api/auth/jwt/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

# Маршруты указанные ниже не нужны


# urlpatterns += format_suffix_patterns([
#     path('api/', api_root),  # точка входа в api
#     # path('api/users/', UserListAPIView.as_view(), name='users-list'),
#     # path('api/users/<int:pk>/', UserDetailAPIView.as_view(), name='users_detail'),
#
#     # используем ViewSet
#     path('api/users/', users_list, name='users-list'),
#     path('api/users/<int:pk>/', users_detail, name='users_detail'),
#
# ])

# Product urls

# Добавляем суффиксы к url адресам
# т.е. сделав запрос http://127.0.0.1:8000/api/products/6.json -
# получим ответ c данными в json
# сделав на http://127.0.0.1:8000/nutrition/api-view/6.api
# получим данные в html форме
# urlpatterns += format_suffix_patterns([
#     path('api/products/', ProductListAPIView.as_view(), name='products-list'),
#
#     path('api/products/<int:pk>/highlight/',
#     ProdutsListHighlightsAPIView().as_view(), name='product-highlight'),
#
#     path('api/products/<int:pk>/', ProductDetailAPIView.as_view(), name='product-detail'),
# ])
#
# # Maker urls
# urlpatterns += format_suffix_patterns([
#     path('api/makers/', MakerListAPIView.as_view(), name='makers-list'),
#
#     path('api/makers/<int:pk>/', MakerDetailAPIView.as_view(), name='maker-detail'),
# ])

# Country urls
# urlpatterns += format_suffix_patterns([
#     path('api/countries/', CountryListAPIView.as_view(), name='countries-list'),
#
#     path('api/countries/<int:pk>/', CountryDetailAPIView.as_view(), name='country-detail'),
# ])
#
# # Category urls
# urlpatterns += format_suffix_patterns([
#     path('api/categories/', CategoryListAPIView.as_view(), name='categories-list'),
#
#     path('api/categories/<int:pk>/', CategoryDetailAPIView.as_view(), name='category-detail'),
# ])