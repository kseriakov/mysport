from django.contrib.auth import get_user_model
from django.db import models


class SecureCode(models.Model):
    code = models.CharField(max_length=100, unique=True, db_index=True)
    telegram_id = models.BigIntegerField(db_index=True, unique=True)
    user = models.OneToOneField(get_user_model(), on_delete=models.PROTECT, null=True, blank=True)
    time_create = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-time_create']

    def __str__(self):
        return f'{self.user}' if self.user else f'Telegram_id: {self.telegram_id}'