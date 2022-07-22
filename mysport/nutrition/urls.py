from django.urls import path
from .views import *

from rest_framework.urlpatterns import format_suffix_patterns


urlpatterns = [

    path('', ProductListView.as_view(), name='product'),
    path('product/<slug:slug>/', ProductDetailView.as_view(), name='product_detail'),
    path('create/', ProductCreateView.as_view(), name='product_create'),
]