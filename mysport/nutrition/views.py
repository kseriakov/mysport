from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView

from .mixins import AddRatio
from .models import *
from .forms import *
from photo.views import ImageCreateView


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
        self.object_list = self.get_queryset()
        self.add_ratio(request)
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

    # def add_ratio(self, request):
    #     pk = request.POST.get('prod_pk')
    #     product = Product.objects.get(pk=pk)
    #     score = request.POST.get('add-score')
    #     if product and score:
    #         Ratio.objects.update_or_create(product=product, maker=product.maker, user=request.user,
    #                                        defaults={'score': score})


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










