from django.db import models
from django.urls import reverse
from transliterate import translit, slugify


class News(models.Model):
    content = models.TextField(verbose_name='Контент')
    url = models.URLField(verbose_name='URL', unique=True)
    time_add = models.DateTimeField(auto_now_add=True, verbose_name='Время публикации')

    class Meta:
        verbose_name = 'Новости'
        verbose_name_plural = 'Новости'
        ordering = ['-time_add']

    def __str__(self):
        return f'{self.content}'[:30] + '...'
