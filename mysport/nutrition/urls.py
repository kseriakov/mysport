from django.urls import path
from .views import *

from rest_framework.urlpatterns import format_suffix_patterns


urlpatterns = [

    path('', ProductListView.as_view(), name='product'),
    path('product/<slug:slug>/', ProductDetailView.as_view(), name='product_detail'),
    path('create/', ProductCreateView.as_view(), name='product_create'),
]

# DRF
urlpatterns_api = [
    path('api-view/', ProductListAPIView.as_view()), 
    path('api-view/<int:pk>', ProductDetailAPIView.as_view()), 
]

# Добавляем суффиксы к url адресам
# т.е. сделав запрос http://127.0.0.1:8000/nutrition/api-view/6.json -
# получим ответ c данными в json
# сделав на http://127.0.0.1:8000/nutrition/api-view/6.api
# получим данные обработанные представлением DRF
urlpatterns_api = format_suffix_patterns(urlpatterns_api)

urlpatterns += urlpatterns_api