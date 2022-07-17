from django import template
import calendar

from workout.models import *

register = template.Library()


@register.simple_tag
def generate_day(year, month):
    for day in sum(calendar.monthcalendar(year, month), []):
        yield day


@register.simple_tag
def get_weeks_days():
    days = ('пн', 'вт', 'ср', 'чт', 'пт', 'сб', 'вс',)
    return days


@register.simple_tag
def get_calendar(user):
    qs = get_month_with_workouts(user)
    for year, months in qs.items():
        yield year, months.items()


# Получаем года, месяца и дни, когда были тренировки
def get_month_with_workouts(user):
    qs_workouts = Workout.objects.filter(user=user).order_by('date').values('date', 'pk')
    years_months = {}

    global pk_for_date
    pk_for_date = {}

    for dct in qs_workouts:
        pk = dct['pk']
        year = dct['date'].year
        month = dct['date'].month
        day = dct['date'].day
        years_months[year] = years_months.get(year, {})
        years_months[year][month] = years_months[year].get(month, []) + [day]

        pk_for_date.update({(year, month, day): pk})

    return years_months


# pk - для построения url в календаре на тренировку
@register.simple_tag
def get_workouts_pk(year, month, day):
    return pk_for_date.get((year, month, day))


@register.filter
def name_month(num):
    d = {1: 'Январь', 2: 'Февраль', 3: 'Март', 4: 'Апрель', 5: 'Май', 6: 'Июнь', 7: 'Июль', 8: 'Август',
         9: 'Сентябрь', 10: 'Октябрь', 11: 'Ноябрь', 12: 'Декабрь', }
    if type(num) is int and 1 <= num <= 12:
        return d.get(num)
    else:
        raise ValueError('Неверно указан номер месяца')
    