from django.contrib.auth import get_user_model
from django.db import models


class UserMessage(models.Model):
    content = models.CharField(max_length=250, verbose_name='Содержание')
    create_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата')
    user_sender = models.ForeignKey(get_user_model(), on_delete=models.PROTECT,
                                    verbose_name='Отправитель', related_name='sender', db_index=True)
    user_recipient = models.ForeignKey(get_user_model(), on_delete=models.PROTECT,
                                       verbose_name='Получатель', related_name='recipient', db_index=True)

    read = models.BooleanField(auto_created=True, default=False, verbose_name='Прочитано')

    class Meta:
        verbose_name = 'Сообщения'
        verbose_name_plural = 'Сообщения'
        ordering = ['-create_at']

    def __str__(self):
        minute = self.create_at.minute
        hour = self.create_at.hour
        day = self.create_at.day
        month = self.create_at.month
        year = self.create_at.year

        return f'{hour}:{minute} ... {day}.{month}.{year} : from {self.user_sender} to {self.user_recipient}'
