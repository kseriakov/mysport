from django.contrib.auth import get_user_model

from rest_framework import serializers

from .models import *
from nutrition.models import Product


# сериализатор для вывода данных об опубликованных постах 
class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'product_set', ]