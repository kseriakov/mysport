import telebot
from telebot import types
from datetime import datetime
import os
import sys
from pathlib import Path
import re
import secrets


__all__ = ['add_new_workout', ]

_new_route = str(Path(__file__).resolve().parent.parent)
# Добавляем в пути для поиска модулей питона текущую директорию
sys.path.append(_new_route)

# Теперь импортируем джанго
import django

# Добавляем в переменные окружения путь с настройками нашего проекта
os.environ['DJANGO_SETTINGS_MODULE'] = 'mysport.settings'

django.setup()

from mysport.settings import env
from workout.models import Workout
from users.models import SecureCode
from django.contrib.auth import get_user_model


TOKEN = env('TOKEN_BOT')
bot = telebot.TeleBot(token=TOKEN)


@bot.message_handler(commands=['start'])
def start_message(msg):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    buttons = ['Добавить упражнение', 'Посмотреть историю', 'Все команды']
    keyboard.add(*buttons)
    bot.send_message(chat_id=msg.chat.id, text='Телеграмм-бот MySport приветствует вас!', reply_markup=keyboard)


@bot.callback_query_handler(lambda x: x.data == 'ID')
def get_id(call: types.CallbackQuery):
    bot.send_message(chat_id=call.message.chat.id, text=f'Ваш ID:')
    bot.send_message(chat_id=call.message.chat.id, text=f'{call.from_user.id}')
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(lambda x: x.data == 'add_telegram')
def get_secure_code(call: types.CallbackQuery):
   secure_code = generate_secure_code(call.from_user.id)
   bot.send_message(chat_id=call.message.chat.id, text=f'Ваш код:')
   bot.send_message(chat_id=call.message.chat.id, text=secure_code)
   bot.send_message(chat_id=call.message.chat.id, text='Введите его в личном кабинете на вкладке - '
                                                       '"Привязать аккаунт Telegram"')
   bot.answer_callback_query(call.id)


@bot.message_handler(commands=['history'])
@bot.callback_query_handler(lambda x: x.data == 'history')
def get_history_year(msg):
    qs_dates = Workout.objects.filter(telegram_id=msg.from_user.id).values('date')

    if not qs_dates:
        if isinstance(msg, types.Message):
            bot.send_message(chat_id=msg.chat.id, text='Тренировки отсутствуют')
        else:
            bot.send_message(chat_id=msg.message.chat.id, text='Тренировки отсутствуют')
            bot.answer_callback_query(msg.id)

    qs_dates = [date.get('date') for date in qs_dates]
    unique_year = set()
    for date in qs_dates:
        unique_year.add(date.year)

    unique_year = sorted(unique_year)
    year_buttons = []
    for year in unique_year:
        button = types.InlineKeyboardButton(text=f'{year}', callback_data=f'get_year_{year}')
        year_buttons.append(button)
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(*year_buttons)

    if isinstance(msg, types.Message) and year_buttons:
        bot.send_message(chat_id=msg.chat.id, text='Выберите год', reply_markup=keyboard)
    elif year_buttons:
        bot.send_message(chat_id=msg.message.chat.id, text='Выберите год', reply_markup=keyboard)
        bot.answer_callback_query(msg.id)


@bot.callback_query_handler(lambda x: "get_year" in x.data)
def get_history_month(call: types.CallbackQuery):
    year = call.data[-4:]
    qs_dates = Workout.objects.filter(date__year=year, telegram_id=call.from_user.id).values('date')
    qs_dates = [date.get('date') for date in qs_dates]
    unique_months = set()
    for date in qs_dates:
        unique_months.add(date.month)
    unique_months = sorted(unique_months)
    month_buttons = []
    for month in unique_months:
        button = types.InlineKeyboardButton(text=f'{month}', callback_data=f'get_month_{year}_{month}')
        month_buttons.append(button)
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(*month_buttons)

    bot.send_message(chat_id=call.message.chat.id, text='Выберите месяц', reply_markup=keyboard)

    # Ответ, чтобы телеграм знал, что ответ получен
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(lambda x: "get_month" in x.data)
def get_history_days(call: types.CallbackQuery):
    year, month = call.data.split('_')[-2:]
    qs_dates = Workout.objects.filter(date__year=year, date__month=month, telegram_id=call.from_user.id).values('date')
    qs_dates = [date.get('date') for date in qs_dates]
    unique_days = set()
    for date in qs_dates:
        unique_days.add(date.day)
    unique_days = sorted(unique_days)
    days_buttons = []
    for day in unique_days:
        button = types.InlineKeyboardButton(text=f'{day}', callback_data=f'get_day_{year}_{month}_{day}')
        days_buttons.append(button)
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(*days_buttons)

    bot.send_message(chat_id=call.message.chat.id, text='Выберите день', reply_markup=keyboard)

    # Ответ, чтобы телеграм знал, что ответ получен
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(lambda x: "get_day" in x.data)
def get_history_workout(call: types.CallbackQuery):
    year, month, day = call.data.split('_')[-3:]
    qs = Workout.objects.filter(date__year=year, date__month=month, date__day=day, telegram_id=call.from_user.id)
    history = ''
    for i in qs:
        history = f'{i.date}\n'
        for k, v in i.content.items():
            history += f'{k}: {v}\n'
    history = history.rstrip()
    bot.send_message(chat_id=call.message.chat.id, text=history)
    bot.answer_callback_query(call.id)


@bot.message_handler(commands=['commands'])
def get_list_commands(msg):
    button_id = types.InlineKeyboardButton(text=f'Мой ID', callback_data=f'ID')
    button_history = types.InlineKeyboardButton(text=f'История', callback_data=f'history')
    keyboard = types.InlineKeyboardMarkup().add(button_id, button_history, row_width=2)

    if not get_user_model().objects.filter(securecode__telegram_id=msg.from_user.id):
        button_add_telegram = types.InlineKeyboardButton(text=f'Привязать аккаунт', callback_data=f'add_telegram')
        keyboard.add(button_add_telegram)

    bot.send_message(chat_id=msg.chat.id, text='Доступны следующие команды:', reply_markup=keyboard)


@bot.message_handler()
def what_to_do(msg):
    if msg.text == 'Новая тренировка':
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        buttons = ['Добавить упражнение', 'Посмотреть историю', 'Все команды']
        keyboard.add(*buttons)
        bot.send_message(chat_id=msg.chat.id, text='Хорошей тренировки! Теперь вы можете добавлять записи', reply_markup=keyboard)
    elif msg.text == 'Добавить упражнение':
        bot.send_message(chat_id=msg.chat.id, text='Укажите упражнение, количество подходов и повторов')
    elif msg.text == 'Посмотреть историю':
        bot.send_message(chat_id=msg.chat.id, text='/history')
    elif msg.text == 'Все команды':
        bot.send_message(chat_id=msg.chat.id, text='/commands')
    else:
        add_new_workout(msg.text, telegram_id=msg.from_user.id)
        bot.send_message(chat_id=msg.chat.id, text='Упражнение успешно добавлено')


def add_new_workout(content, telegram_id=None, user=None, date=None):
    if not date:
        date = datetime.today()

    qs_u, qs_t, = [], []
    _user_id, _telegram_id = None, None

    # Если сохраняем данные из бота (передали telegram_id), то проверяем, если ли для telegram_id - user на сайте
    if telegram_id:
        if qs := SecureCode.objects.filter(telegram_id=telegram_id).values('user'):
            _user_id = qs.last().get('user')

        qs_t = Workout.objects.filter(date=date, telegram_id=telegram_id)

    # Если сохраняем данные с сайта (передали user), то проверяем, если привязан ли telegram_id к данному user
    if user:
        if qs := SecureCode.objects.filter(user=user).values('telegram_id'):
            _telegram_id = qs.last().get('telegram_id')

        qs_u = Workout.objects.filter(date=date, user=user)

    if qs_u or qs_t:
        workout = (qs_u or qs_t).last()
        last_exercise = list(workout.content.keys())[-1]
        number_last_exercise = int(re.search(r'\d{1,2}$', last_exercise).group(0))
        workout.content.update({f'Упражнение {number_last_exercise + 1}': content})

    else:
        workout = Workout.objects.create()
        workout.content = {'Упражнение 1': content}
        if telegram_id:
            workout.telegram_id = telegram_id
        else:
            workout.user = user

    if _user_id:
        workout.user_id = _user_id
    if _telegram_id:
        workout.telegram_id = _telegram_id

    workout.save()


def generate_secure_code(telegram_id):
    secure_code = secrets.token_hex(16)
    if qs := SecureCode.objects.filter(telegram_id=telegram_id):
        obj = qs.last()
        obj.code = secure_code
        obj.save()
    else:
        SecureCode.objects.create(code=secure_code, telegram_id=telegram_id)

    return secure_code


if __name__ == '__main__':
    bot.infinity_polling(timeout=0)