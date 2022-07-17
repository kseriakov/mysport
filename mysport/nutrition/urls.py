from django.urls import path
from .views import *

urlpatterns = [

    path('', ProductListView.as_view(), name='product'),
    path('product/<slug:slug>/', ProductDetailView.as_view(), name='product_detail'),
    path('create/', ProductCreateView.as_view(), name='product_create'),
]