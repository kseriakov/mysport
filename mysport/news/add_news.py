import os
import sys
from pathlib import Path

_new_route = Path.cwd()
# Добавляем в пути для поиска модулей питона текущую директорию
sys.path.append(_new_route)

# Теперь импортируем джанго
import django

# Добавляем в переменные окружения путь с настройками нашего проекта
os.environ['DJANGO_SETTINGS_MODULE'] = 'mysport.settings'

django.setup()

from news.news_class import SportNews
from news.models import News


sn = SportNews(search_url='https://news.sportbox.ru/')
list_news = sn.get_news()
for news in sn.get_news():
    try:
        News.objects.create(**news)
    except:
        pass




