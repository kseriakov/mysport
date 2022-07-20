from rest_framework import serializers

from .models import *


class ProductSerializer(serializers.ModelSerializer):
    # Настраиваем поле user, в котором будет отображаться не id, а username
    user = serializers.ReadOnlyField(source='user.username')  # source - чем заполнять поле

    class Meta:
        model = Product
        fields = ['id', 'content', 'price', 'maker', 'category', 'create_at', 'user']


# Перепишем класс, наследовавшись от HyperlinkedModelSerializer,
# который представляет отношения между сущностями с помошью гиперссылок

class ProductSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.ReadOnlyField(
        source='user.username')  # source - чем заполнять поле
    
    # поле __str__ - объекта модели Product
    name = serializers.SerializerMethodField(method_name='get_name')
        
    highlight = serializers.HyperlinkedIdentityField(
        view_name='product-highlight', format='html') # поле ссылки на объект

    class Meta:
        model = Product
        fields = ['url', 'id', 'name', 'content', 'price', 'maker', 
        'category', 'highlight', 'create_at', 'user']

    # добавили имя экземпляра модели, поступившего на сериализацию
    def get_name(self, obj):
        return str(obj)


class MakerSerializer(serializers.HyperlinkedModelSerializer):
    country = serializers.ReadOnlyField(source='country.name')

    class Meta:
        model = Maker
        fields = ['url', 'id', 'name', 'country']


class CategorySerializer(serializers.HyperlinkedModelSerializer):
    product_set = serializers.HyperlinkedRelatedField(
        many=True, read_only=True, view_name='product-detail')

    class Meta:
        model = Category
        fields = ['url', 'id', 'name', 'product_set']


class CountrySerializer(serializers.HyperlinkedModelSerializer):
    maker_set = serializers.StringRelatedField(many=True)

    class Meta:
        model = Country
        fields = ['url', 'id', 'name', 'maker_set']