from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse, reverse_lazy


class Workout(models.Model):
    date = models.DateField(auto_now_add=True, verbose_name='Дата тренировки')
    content = models.JSONField(verbose_name='Содержание тренировки', blank=True, null=True)
    telegram_id = models.BigIntegerField(blank=True, null=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, blank=True, null=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f'{self.date}'

    def get_absolute_url(self):
        return reverse('history_workout_detail', kwargs={
            'year': self.date.year,
            'month': self.date.month,
            'day': self.date.day,
            'pk': self.pk
        })

