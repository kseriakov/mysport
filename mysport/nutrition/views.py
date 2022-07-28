from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework import mixins
from rest_framework import generics
from rest_framework import permissions
from rest_framework import authentication
from rest_framework.renderers import StaticHTMLRenderer
from rest_framework.decorators import action
from rest_framework import viewsets

from rest_framework_simplejwt.authentication import JWTAuthentication

from .mixins import AddRatio
from .models import *
from .forms import *
from photo.views import ImageCreateView
from .serializers import *
from .permissions import *


class ProductListView(ListView, AddRatio):
    model = Product
    context_object_name = 'products'
    template_name = 'nutrition/list_nutrition.html'
    paginate_by = 4

    def get(self, request, **kwargs):
        if (pk := request.GET.get('take-maker')) and pk.isdigit():
            self.object_list = self.get_queryset().filter(maker_id=pk)
            maker = self.extra_context.get('makers').get(id=pk)
            self.extra_context.update({'title': maker, 'on_maker': maker})
            # Исключаем выбранного производителя, он передается в контекст выше
            self.extra_context['makers'] = self.extra_context['makers'].exclude(pk=pk)

            if not self.object_list:
                raise Http404()
        else:
            self.object_list = self.get_queryset()

        return self.render_to_response(self.get_context_data(object_list=self.object_list, **kwargs))

    def post(self, request, **kwargs):
        self.add_ratio(request)
        self.object_list = self.get_queryset()
        return self.render_to_response(self.get_context_data(object_list=self.object_list, **kwargs))

    def get_queryset(self):
        qs = Product.objects.filter(published=True).select_related('maker')
        self.extra_context = {'makers': Maker.objects.filter(product__in=qs).distinct()}
        return qs
    
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ProductListView, self).get_context_data(**kwargs)
        if not context.get('title'):
            context['title'] = 'My Питание'
        return context


class ProductDetailView(DetailView, AddRatio):
    model = Product
    template_name = 'nutrition/product_detail.html'
    context_object_name = 'product'

    def post(self, request, **kwargs):
        self.add_ratio(request)
        self.object = self.get_object()
        self.save_comment(request)
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context=context)

    def get_context_data(self, **kwargs):
        context = super(ProductDetailView, self).get_context_data(**kwargs)
        context['title'] = self.object
        context['products'] = [self.object]
        comments_list = Comment.objects.filter(product=self.object).order_by('create_at')
        paginator = Paginator(comments_list, 15)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj
        context['paginator'] = paginator

        context['form'] = CommentsCreate().get_form_class()

        return context

    def save_comment(self, request):
        content = request.POST.get('content')
        if content:
            dict_args = {
                'user_id': request.user.pk,
                'product': self.object,
                'maker': self.object.maker,
                'content': content,
            }
            obj = Comment.objects.create(**dict_args)


class ProductCreateView(CreateView):
    form_class = ProductCreateForm
    template_name = 'nutrition/product_create.html'
    success_url = reverse_lazy('product')

    def get(self, request, *args, **kwargs):
        self.object = None
        # метод get_form_class - возвращает экземпляр формы, для использования в шаблоне
        form_img = ImageCreateView().get_form_class()
        self.extra_context = {'form_img': form_img}
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        # Получаем данные для ImageCreateView
        user_id = self.request.user.pk
        request = self.request
        self.object.user = get_user_model().objects.get(pk=user_id)
        self.object = form.save()
        product_id = self.object.pk
        # Создаем экземпляр формы
        form_img = ImageCreateView(request=request, user_id=user_id, product_id=product_id)
        # Реализуем метод post
        form_img.post(request)

        return super().form_valid(form)


class CommentsCreate(CreateView):
    form_class = CommentCreateForm


# DRF
# Самый простой вариант
@csrf_exempt
def nutrition_list(request):
    if request.method == 'GET':
        products = Product.objects.all()
        serailizer = ProductSerializer(products, many=True)
        return JsonResponse(serailizer.data, safe=False)

    if request.method == 'POST':
        # Парсим request - приходят данные в JSON формате
        data = JSONParser().parse(request)
        # Десериализация
        product = ProductSerializer(data=data)
        if product.is_valid():
            product.save()
            return JsonResponse(product.data, status=201)
        return JsonResponse(product.errors, status=400)


# Представления на основе функций
@api_view(['GET', 'POST'])
def nutrition_list(request, format=None):  # format - для суффиксов к url адресам
    if request.method == 'GET':
        products = Product.objects.all()
        serailizer = ProductSerializer(products, many=True)
        # Используем класс Response из DRF
        return Response(serailizer.data)

    if request.method == 'POST':
        # Десериализация, здесь доступен новый объект request, имеющий атрибут data
        # парсить request - не нужно
        product = ProductSerializer(data=request.data)
        if product.is_valid():
            product.save()
            # Используем статусы состояний DRF, так рекомендуется
            return Response(product.data, status=status.HTTP_201_CREATED)
        return Response(product.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def nutrition_detail(request, pk, format=None): # format - для суффиксов к url адресам

    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serailizer = ProductSerializer(product)
        return Response(serailizer.data, status=status.HTTP_200_OK)

    if request.method == 'PUT':
        prod = ProductSerializer(product, data=request.data)
        if prod.is_valid():
            prod.save()
            return Response(prod.data, status=status.HTTP_201_CREATED)
        return Response(prod.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == "DELETE":
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Далее переписываем представления на основе классов

class ProductListAPIView(APIView):
    
    # Методы определяются как и в случае api_view
    def get(self, request, form=None):
        products = Product.objects.all()
        serailizer = ProductSerializer(products, many=True)
        return Response(serailizer.data)

    def post(self, request, form=None):
        product = ProductSerializer(data=request.data)
        if product.is_valid():
            product.save()
            # Используем статусы состояний DRF, так рекомендуется
            return Response(product.data, status=status.HTTP_201_CREATED)
        return Response(product.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductDetailAPIView(APIView):

    def get_object(self, pk):
        try:
            object = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            raise Http404
        return object

    def get(self, request, pk, format=None):
        product = self.get_object(pk)
        serializer = ProductSerializer(product)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk, format=None):
        product = self.get_object(pk)
        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        product = self.get_object(pk)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Далее убираем дублирование кода с помощью миксинов
# GenericAPIView - наследуется от APIView, базовый класс, для работы с queryset
# и serializer
# Миксины реализуют обработку get, post и.т.д. запросов
class ProductListAPIView(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    generics.GenericAPIView
):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    # Разрешаем методы отработки запросов
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)  # list - вывод записей

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)  # create - создание записи  


class ProductDetailAPIView(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView
):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    # Разрешаем методы отработки запросов
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)  # retrieve - одна запись

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)  

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)          


# Существуют общие представления включающие вышеприведенный функционал
# Product API

class ProductListAPIView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    # Аутентификация
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,]

    # При создании записи, автор добавляется автоматически
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ProductDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    # разрешили доступ только для аут. по токенам (простые или JWT)
    # те кто зашел по кукам, доступа иметь не будут

    # authentication_classes = [
    #     authentication.TokenAuthentication,
    #     JWTAuthentication,
    # ]

    permission_classes = [
        permissions.IsAuthenticated,
        IsOwnerUserOrReadOnly  # ограничение на действия только владельцем
    ]


class ProdutsListHighlightsAPIView(generics.GenericAPIView):
    queryset = Product.objects.all()
    renderer_classes = [StaticHTMLRenderer]

    def get(self, request, *args, **kwargs):
        product = self.get_object()
        return Response(product)


# Maker API
class MakerListAPIView(generics.ListCreateAPIView):
    queryset = Maker.objects.all()
    serializer_class = MakerSerializer

    permission_classes = [
        permissions.IsAuthenticated,
    ]


class MakerDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Maker.objects.all()
    serializer_class = MakerSerializer

    permission_classes = [
        permissions.IsAuthenticated,
    ]


# Country API
class CountryListAPIView(generics.ListCreateAPIView):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer

    permission_classes = [
        permissions.IsAuthenticated,
    ]


class CountryDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer

    permission_classes = [
        permissions.IsAuthenticated,
    ]  


# Category API
class CategoryListAPIView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    permission_classes = [
        permissions.IsAuthenticated,
    ]


class CategoryDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    permission_classes = [
        permissions.IsAuthenticated,
    ]


# Используем ViewSets, заменяя два класса на каждую сущность, одним

# Product
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    # Аутентификация
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsOwnerUserOrReadOnly,
    ]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    # дополнительный метод, которому будет присвоен маршрут в API (по url будет вызываться)
    @action(methods=['GET'], detail=True,
            url_path='highlight', renderer_classes=[StaticHTMLRenderer], url_name='highlight')
    def get_highlight(self, request, *args, **kwargs):
        product = self.get_object()
        return Response(product)


# Maker
class MakerViewSet(viewsets.ModelViewSet):
    queryset = Maker.objects.all()
    serializer_class = MakerSerializer

    permission_classes = [
        permissions.IsAuthenticated,
    ]


# Country
class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer

    permission_classes = [
        permissions.IsAuthenticated,
    ]


# Category
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    permission_classes = [
        permissions.IsAuthenticated,
    ]
