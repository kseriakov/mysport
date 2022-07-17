from django.db import models
from nutrition.models import Product
from django.contrib.auth import get_user_model


class Image(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    picture = models.ImageField(upload_to='photos/%Y/%m/%d', verbose_name='Фото')
    user = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, verbose_name='Пользователь')
    upload = models.DateTimeField(auto_now_add=True, verbose_name='Добавлено')

    class Meta:
        ordering = ['-upload']
        verbose_name = 'Фото'
        verbose_name_plural = 'Фото'

    def __str__(self):
        return f'Фото: {self.product}'
