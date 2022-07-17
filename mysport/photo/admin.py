from django.contrib import admin
from django.utils.safestring import mark_safe
from datetime import datetime

from .models import *


class ImageAdmin(admin.ModelAdmin):
    actions_on_top = True
    list_display = ('__str__', 'get_picture', 'upload', 'user')
    fields = ('product', 'get_picture', 'picture', 'user')
    readonly_fields = ('get_picture', )
    list_filter = ('product__category__name', 'product__maker__name')
    save_on_top = True

    @admin.display(description='Миниатюра')
    def get_picture(self, obj):
        if obj.picture:
            # mark_safe - помечает строку как html код и не экранирует ее
            return mark_safe(f'<img src="{obj.picture.url}" width=40px>')
        else:
            return 'Фото не установлено'


class ImageInline(admin.TabularInline):
    model = Image
    extra = 1
    readonly_fields = ('get_picture', )
    fields = ('get_picture', 'picture', 'user',)

    @admin.display(description='Миниатюра')
    def get_picture(self, obj):
        if obj.picture:
            # mark_safe - помечает строку как html код и не экранирует ее
            return mark_safe(f'<img src="{obj.picture.url}" width=40px>')
        else:
            return 'Фото не установлено'



admin.site.register(Image, ImageAdmin)


