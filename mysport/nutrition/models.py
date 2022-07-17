from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse

from transliterate import translit, slugify


def get_translit(word):
    trnslt = translit(word, language_code='ru', reversed=True)
    return trnslt


class Product(models.Model):
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, verbose_name='Продукт')
    maker = models.ForeignKey('Maker', on_delete=models.PROTECT, verbose_name='Производитель')
    content = models.TextField(verbose_name='Описание', db_index=True)
    price = models.FloatField(verbose_name='Цена')
    create_at = models.DateTimeField(auto_now_add=True, verbose_name='Запись создана')
    published = models.BooleanField(default=True, verbose_name='Опубликовано')
    user = models.ForeignKey(get_user_model(),  on_delete=models.SET_NULL, null=True, verbose_name='Пользователь')
    slug = models.SlugField(max_length=150, blank=True, null=True)

    class Meta:
        ordering = ['-create_at']
        verbose_name = 'Спортпит'
        verbose_name_plural = 'Спортпит'

        constraints = [
            models.CheckConstraint(check=models.Q(price__gte=0), name='product_price_gte_0'),
        ]

        indexes = [
            models.Index(fields=['price']),
        ]

    def save(self, *args, **kwargs):
        super(Product, self).save(*args, **kwargs)
        if not self.slug:
            self.slug = slugify(f'{self.category.slug}-{self.maker.slug}-{self.pk}', 'el')
            self.save()

    def __str__(self):
        return f'{self.category} | {self.maker}'

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'slug': self.slug})


class Category(models.Model):
    name = models.CharField(max_length=150, verbose_name='Название')
    slug = models.SlugField(max_length=150, blank=True, null=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Категория спортпита'
        verbose_name_plural = 'Категории спортпита'

    def save(self, *args, **kwargs):
        super(Category, self).save(*args, **kwargs)
        if not self.slug:
            self.slug = slugify(f'{get_translit(self.name)}', 'el')
            self.save()

    def __str__(self):
        return f'{self.name}'


class Maker(models.Model):
    name = models.CharField(max_length=150, verbose_name='Марка')
    country = models.ForeignKey('Country', on_delete=models.PROTECT, verbose_name='Страна производства')
    slug = models.SlugField(max_length=150, blank=True, null=False)

    class Meta:
        ordering = ['name']
        verbose_name = 'Производитель'
        verbose_name_plural = 'Производители'

        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['country']),
        ]

    def save(self, *args, **kwargs):
        super(Maker, self).save(*args, **kwargs)
        if not self.slug:
            self.slug = slugify(f'{get_translit(self.name)}', 'el')
            self.save()

    def __str__(self):
        return f'{self.name}'


class Comment(models.Model):
    product = models.ForeignKey('Product', on_delete=models.PROTECT, verbose_name='Спортпит')
    maker = models.ForeignKey('Maker', on_delete=models.PROTECT, verbose_name='Производитель')
    content = models.TextField(verbose_name='Комментарий')
    user = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, blank=True, verbose_name='Пользователь')
    create_at = models.DateTimeField(auto_now_add=True, verbose_name='Запись создана')

    class Meta:
        ordering = ['-create_at']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return f'{self.user} - {self.create_at.day}.{self.create_at.month}.{self.create_at.year}'


class Country(models.Model):
    name = models.CharField(max_length=150, verbose_name='Страна производства')

    class Meta:
        ordering = ['name']
        verbose_name = 'Страна производства'
        verbose_name_plural = 'Страны производства'

        indexes = [
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return f'{self.name}'


class Ratio(models.Model):
    ratio_level = [
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5),
        (None, 'Ваша оценка')
    ]

    product = models.ForeignKey('Product', on_delete=models.SET_NULL, null=True, verbose_name='Спортпит')
    maker = models.ForeignKey('Maker', on_delete=models.SET_NULL, null=True, verbose_name='Производитель спортпита')
    score = models.IntegerField(choices=ratio_level, verbose_name='Оценка пользователя')
    user = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, verbose_name='Пользователь')
    create_at = models.DateField(auto_now_add=True, verbose_name='Дата оценки')

    class Meta:
        ordering = ['-create_at']
        verbose_name = 'Рейтинг'
        verbose_name_plural = 'Рейтинги'

    def save(self, *args, **kwargs):
        if not self.maker:
            self.maker = self.product.maker
        super(Ratio, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.create_at}-{self.pk}'


