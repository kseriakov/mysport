from django.contrib.auth import get_user_model

from rest_framework import serializers

from .models import *
from nutrition.models import Product


# сериализатор для вывода данных об опубликованных постах 
class UserSerializer(serializers.ModelSerializer):
    # список постов пользователя в формате __str__
    product_set = serializers.StringRelatedField(many=True)  

    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'product_set', ]


# перепишем класс, представляя отношении с помощью гиперссылок
class UserSerializer(serializers.HyperlinkedModelSerializer):
    product_set = serializers.HyperlinkedRelatedField(
        many=True, read_only=True, view_name='product-detail')  

    class Meta:
        model = get_user_model()
        fields = ['url', 'id', 'username', 'product_set', ]
        extra_kwargs = {
            'url': {'view_name': 'users_detail'}
        }