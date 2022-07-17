from django import template
from ..models import *
import re


register = template.Library()


@register.inclusion_tag('news/news_bar.html')
def get_news_in_bar():
    news_list = News.objects.all()[:5]
    return {'news_list': news_list}


@register.filter
def delete_num(s):
    s = re.sub(r'[1-9]?[0-9]?$', '', s)
    return s