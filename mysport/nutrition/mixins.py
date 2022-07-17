from .models import *


class AddRatio:

    def add_ratio(self, request):
        if pk := request.POST.get('prod_pk'):
            product = Product.objects.get(pk=pk)
            score = request.POST.get('add-score')
            if product and score:
                Ratio.objects.update_or_create(product=product, maker=product.maker, user=request.user,
                                               defaults={'score': score})