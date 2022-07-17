from statistics import mean
from django import template


register = template.Library()


@register.simple_tag
def get_avg_ratio(obj):
    avg_ratio = 'Нет оценок'
    qs = obj.ratio_set.all()
    if qs:
        avg_ratio = round(mean((item.score for item in qs)), 2)
    return avg_ratio


@register.simple_tag(takes_context=True)
def get_score_user(context):
    res = {}
    products = context['products']
    user = context['user']
    for product in products:
        qs_user_ratio = product.ratio_set.filter(user=user)
        if qs_user_ratio:
            user_ratio = qs_user_ratio.last()
            res.setdefault(product.pk, user_ratio.score)
    print(res)
    return res


@register.filter
def get_dict_object(d, key):
    return d.get(key)


@register.filter
def len_queryset(qs):
    return len(qs)