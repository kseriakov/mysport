from rest_framework import serializers

from .models import *


class ProductSerializer(serializers.ModelSerializer):
    # Настраиваем поле user, в котором будет отображаться не id, а username
    user = serializers.ReadOnlyField(source='user.username')  # source - чем заполнять поле

    class Meta:
        model = Product
        fields = ['id', 'content', 'price', 'maker', 'category', 'create_at', 'user']


# Перепишем класс, наследовавшись от HyperlinkedModelSerializer,
# который представляет отношения между сущностями с помощью гиперссылок

class ProductSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.ReadOnlyField(
        source='user.username')  # source - чем заполнять поле
    
    # поле __str__ - объекта модели Product
    name = serializers.SerializerMethodField(method_name='get_name')
        
    highlight = serializers.HyperlinkedIdentityField(
        view_name='products-highlight', format='html')  # поле ссылки на объект

    class Meta:
        model = Product
        fields = ['url', 'id', 'name', 'content', 'price', 'maker', 
        'category', 'highlight', 'create_at', 'user']

        # по умолчанию ищет название маршрута - product-detail, но в роутере у нас basename - products
        extra_kwargs = {
            'url': {'view_name': 'products-detail'},
            'maker': {'view_name': 'makers-detail'},
            'category': {'view_name': 'categories-detail'},
        }

    # добавили имя экземпляра модели, поступившего на сериализацию
    def get_name(self, obj):
        return str(obj)


class MakerSerializer(serializers.HyperlinkedModelSerializer):
    country = serializers.ReadOnlyField(source='country.name')

    class Meta:
        model = Maker
        fields = ['url', 'id', 'name', 'country']

        extra_kwargs = {
            'url': {'view_name': 'makers-detail'}
        }


class CategorySerializer(serializers.HyperlinkedModelSerializer):
    product_set = serializers.HyperlinkedRelatedField(
        many=True, read_only=True, view_name='products-detail')

    class Meta:
        model = Category
        fields = ['url', 'id', 'name', 'product_set']

        extra_kwargs = {
            'url': {'view_name': 'categories-detail'}
        }


class CountrySerializer(serializers.HyperlinkedModelSerializer):
    maker_set = serializers.StringRelatedField(many=True)

    class Meta:
        model = Country
        fields = ['url', 'id', 'name', 'maker_set']

        extra_kwargs = {
            'url': {'view_name': 'countries-detail'}
        }