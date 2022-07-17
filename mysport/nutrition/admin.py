from django.contrib import admin
from django.utils.safestring import mark_safe
from datetime import datetime

from .models import *
from photo.admin import ImageInline


class RatioInline(admin.TabularInline):
    model = Ratio
    extra = 1
    exclude = ('maker', )

    def get_queryset(self, request):
        qs = super(RatioInline, self).get_queryset(request)
        res = qs.filter(create_at__gt=datetime.now())
        return res


class ProductAdmin(admin.ModelAdmin):
    list_display = ('category', 'maker', 'price', 'published', 'create_at')
    # exclude = ('user', )  # скрыть author поле, чтобы оно не отображалось в форме изменений
    fields = ('category', 'maker', 'price', 'get_photo', 'content', 'slug', 'published', 'user', 'create_at')
    readonly_fields = ('get_photo', 'create_at')
    save_on_top = True

    inlines = [RatioInline, ImageInline]

    @admin.display(description='Фото')
    def get_photo(self, obj):
        if obj.image_set.all():
            # mark_safe - помечает строку как html код и не экранирует ее
            return mark_safe(f'<img src="{obj.image_set.last().picture.url}" width=100px>')
        else:
            return 'Фото не установлено'

    # def save_model(self, request, obj, form, change):
    #     if not obj.pk:
    #         obj.user = request.user
    #     super().save_model(request, obj, form, change)


class RatioAdmin(admin.ModelAdmin):
    list_display = ('product', 'maker', 'score', 'user', 'create_at')
    fields = ('product', 'score', 'user', 'create_at')
    readonly_fields = ('create_at', )


admin.site.register(Product, ProductAdmin)
admin.site.register(Maker)
admin.site.register(Comment)
admin.site.register(Country)
admin.site.register(Category)
admin.site.register(Ratio, RatioAdmin)
