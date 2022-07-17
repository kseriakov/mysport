import requests
from bs4 import BeautifulSoup as bs
from random_user_agent.user_agent import UserAgent


class SportNews:
    def __init__(self, search_url):
        self.search_url = search_url
        self.news = []

    def _get_headers(self):
        user_agent = UserAgent()
        random_user_agent = user_agent.get_random_user_agent()
        self.headers = {
            'User-Agent': random_user_agent,
        }

    def _get_content(self):
        self._get_headers()
        request = requests.get(self.search_url, headers=self.headers)
        if request.ok and request.status_code == 200 and (content := request.content):
            return content
        else:
            raise ValueError('Передан неверный параметр "search_url"')

    def get_news(self):
        bsoup = bs(self._get_content(), 'html.parser')
        div_top_news = bsoup.find(name='div', class_='col-lg-12')
        div_list_news = div_top_news.find(name='div', class_='col-lg-7').find_all(name='li')
        for div_news in div_list_news:
            div_news_a = div_news.a
            url = self.search_url + div_news_a['href']
            content = div_news_a.get_text()
            self.news.append({'url': url, 'content': content})
        return self.news









