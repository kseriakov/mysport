from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import *


class NewsAdmin(admin.ModelAdmin):
    list_display = ('get_title', 'time_add')
    fields = ('content', 'url', 'time_add')
    readonly_fields = ('time_add', )

    @admin.display(description='Новость')
    def get_title(self, obj):
        title = obj.content[:50] + '...'
        return mark_safe(title)


admin.site.register(News, NewsAdmin)
