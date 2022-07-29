from django.db.models import Q, Count

from workout.models import Workout
from workout_telebot.bot import add_new_workout


class LinkWorkouts:

    def get_workouts_queryset(self):
        self.workouts_queryset = Workout.objects.all()

    # Привязываем пользователя с сайта к записям из бота, которые не имели ссылки на пользователя
    def link_user_to_workouts(self, sec_code_obj):
        user = sec_code_obj.user
        telegram_id = sec_code_obj.telegram_id
        query_t = Q(telegram_id=telegram_id) & Q(user__isnull=True)
        qs_t = self.workouts_queryset.filter(query_t)
        for workout in qs_t:
            workout.user = user
            workout.save()

    # Изменяем телеграм, если раннее был привязан другой аккаунт или записи добавлялись через сайт
    # Т.е. при смене аккаунта телеграм, все записи сохраняются за пользователем с сайта, и в новом боте будут доступны
    def link_telegram_to_workouts(self, sec_code_obj):
        self._user = sec_code_obj.user
        telegram_id = sec_code_obj.telegram_id
        query_u = Q(user=self._user) & ~Q(telegram_id__exact=telegram_id)
        qs_u = self.workouts_queryset.filter(query_u)
        for workout in qs_u:
            workout.telegram_id = telegram_id
            workout.save()

    # Сольем в одну тренировку записи, которые одновременно
    # были добавлены в один день с сайта и в телеграмме
    def merge_double_days(self):
        for_user_qs = Workout.objects.filter(user=self._user)
        double_days = for_user_qs.values('date').annotate(
            pk=Count('pk')).filter(pk__gt=1).values('date')
        for item in double_days:
            date = item['date']
            qs_double_days = for_user_qs.filter(date=date)
            workout_day_one, workout_day_two = qs_double_days
            new_content_for_day_one = workout_day_two.content
            for content in new_content_for_day_one.values():
                # Контент будет добавлен к первой найденной тренировке,
                # это как раз будет - workout_day_one, так как выбирали по порядку
                add_new_workout(content, user=self._user, date=date)

            workout_day_two.delete()

    # В одну функцию
    def link_data_user(self, sec_code_obj):
        self.get_workouts_queryset()
        self.link_user_to_workouts(sec_code_obj)
        self.link_telegram_to_workouts(sec_code_obj)
        self.merge_double_days()





