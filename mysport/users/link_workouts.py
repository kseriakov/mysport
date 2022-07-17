from django.db.models import Q
import asyncio
from asgiref.sync import sync_to_async

from workout.models import Workout


# Привязываем пользователя с сайта к записям из бота, которые не имели ссылки на пользователя
def link_user_to_workouts(sec_code_obj):
    user = sec_code_obj.user
    telegram_id = sec_code_obj.telegram_id
    query_t = Q(telegram_id=telegram_id) & Q(user__isnull=True)
    qs_t = Workout.objects.filter(query_t)
    for workout in qs_t:
        workout.user = user
        workout.save()


# Изменяем телеграм, если раннее был привязан другой аккаунт или записи добавлялись через сайт
# Т.е. при смене аккаунта телеграм, все записи сохраняются за пользователем с сайта, и в новом боте будут доступны
def link_telegram_to_workouts(sec_code_obj):
    user = sec_code_obj.user
    telegram_id = sec_code_obj.telegram_id
    query_u = Q(user=user) & ~Q(telegram_id__exact=telegram_id)
    qs_u = Workout.objects.filter(query_u)
    for workout in qs_u:
        workout.telegram_id = telegram_id
        workout.save()


# В одну функцию
def link_data_user(sec_code_obj):
    link_user_to_workouts(sec_code_obj)
    link_telegram_to_workouts(sec_code_obj)





