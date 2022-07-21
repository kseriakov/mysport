from rest_framework import serializers

from .models import *


class ProductSerializer(serializers.ModelSerializer):
    # Настраиваем поле user, в котором будет отображаться не id, а username
    user = serializers.ReadOnlyField(source='user.username')  # source - чем заполнять поле

    class Meta:
        model = Product
        fields = ['id', 'content', 'price', 'maker', 'category', 'create_at', 'user']

