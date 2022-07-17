from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import *


class ImageCreateView(CreateView):
    form_class = ImageCreateForm
    template_name = 'nutrition/product_create.html'
    context_object_name = 'form_img'

    def form_valid(self, form):
        print(form.cleaned_data)
        print(self.get_form_kwargs())
        self.object = form.save(commit=False)
        self.object.user = get_user_model().objects.get(pk=self.user_id)
        self.object.product = Product.objects.get(pk=self.product_id)
        self.object = form.save()



