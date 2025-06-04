import os
import random

from selenium import webdriver
from selenium.webdriver.common.proxy import ProxyType, Proxy
from splinter import Browser
from splinter.exceptions import ElementDoesNotExist
from selenium.webdriver.chrome.options import Options
import time
import re
from .models import Offers
from django.conf import settings
from tqdm import tqdm
import requests


class Parser:
    def __init__(self,url, headless=False):
        self.start_url = url
        self.jobs = []
        self.browser = None
        self.cards_list = []
        self.archive = []

        # self._get_proxy_list()
        # self.proxy = self._get_proxy()

        self.proxy = '23.247.136.254:80'


        # Set up proxy configuration
        proxy = {
            "proxy" : {
                "http": self.proxy,
                "https": self.proxy,
            }
         }
        chrome_options = Options()
        chrome_options.add_argument(f'--proxy-server={proxy}')

        # chrome_options = webdriver.ChromeOptions()
        # chrome_options.add_argument(f'--proxy-server={self.proxy}')
        # browser = webdriver.Chrome(chrome_options=chrome_options)
        #
        # chrome_options = Options()
        # chrome_options.add_argument(f'--proxy-server={self.proxy}')
        # if headless :
        #     chrome_options.add_argument("--headless")  # Включаем безголовый режим


        self.browser = Browser('chrome', options=chrome_options)

        kwork_ids = Offers.objects.values_list('kwork_id', flat=True)
        # Преобразуем QuerySet в список
        self.archive = list(kwork_ids)

    def get_card(self, url):
        self.browser.visit(url)
        cards = self.browser.find_by_css('.want-card')
        for card in cards:
            title = card.find_by_css('h1')
            url = title.find_by_tag('a')
            self.cards_list.append(url['href'])
            time.sleep(0.3)

    def _get_proxy(self):
        return random.choice(self.proxy_list)

    def _get_proxy_list(self):
        file_path = os.path.join(settings.BASE_DIR, 'assets', 'proxy', 'working_proxies.txt')
        print(file_path)
        """Читает прокси из файла."""
        with open(file_path, 'r') as file:
            self.proxy_list = [line.strip() for line in file if line.strip()]



    def _get_card_info(self, card_url):
        ''''
        на вход url карточки из биржи
        :return
        {title, discription, wanted_cost, cost, buyer, projects , deal , last_time, offers}
        '''
        print(card_url, 'url')
        browser = self.browser
        browser.visit(card_url)
        id = card_url.split("/")[-1]
        post = (browser.find_by_css('.want-card'))
        post.text.split('\n')
        texts = post.text.split('\n')
        title = texts[0]
        start_form_index = self._find_index(texts, 'Желаемый бюджет')
        discription = "\n".join(texts[1: start_form_index])
        param = texts[start_form_index:]
        print(card_url, 'url')
        # Инициализация переменных
        wanted_cost = None
        cost = None
        buyer = None
        projects = None
        deal = None
        last_time = None
        offers = None
        # Извлечение данных с обработкой ошибок
        try:
            wanted_cost = self._get_price(param[0])
        except Exception as e:
            print(f"Ошибка при получении желаемой стоимости: {e}")
            wanted_cost = None  # Или пустая строка: wanted_cost = ''
        try:
            cost = self._get_price(param[1])
        except Exception as e:
            print(f"Ошибка при получении стоимости: {e}")
            cost = None  # Или пустая строка: cost = ''
        try:
            buyer = self._get_data(param, 'Покупатель')
        except Exception as e:
            print(f"Ошибка при получении покупателя: {e}")
            buyer = None  # Или пустая строка: buyer = ''
        try:
            projects = self._get_data(param, 'Размещено проектов')
        except Exception as e:
            print(f"Ошибка при получении размещенных проектов: {e}")
            projects = None  # Или пустая строка: projects = ''
        try:
            deal = self._get_data(param, 'Нанято')
        except Exception as e:
            print(f"Ошибка при получении данных о нанятых: {e}")
            deal = None  # Или пустая строка: deal = ''
        try:
            last_time = self._get_data(param, 'Осталось')
        except Exception as e:
            print(f"Ошибка при получении оставшегося времени: {e}")
            last_time = None  # Или пустая строка: last_time = ''
        try:
            offers = self._get_data(param, 'Предложений')
        except Exception as e:
            print(f"Ошибка при получении количества предложений: {e}")
            offers = None  # Или пустая строка: offers = ''
        # wanted_cost = self._get_price(param[0])
        # cost = self._get_price(param[1])
        # buyer = self._get_data(param, 'Покупатель')
        # projects = self._get_data(param, 'Размещено проектов')
        # deal = self._get_data(param, 'Нанято')
        # last_time = self._get_data(param, 'Осталось')
        # offers = self._get_data(param, 'Предложений')
        data = {"id" : id,
                "title" :title,
                "wanted_cost": wanted_cost,
                "cost" : cost,
                "buyer" : buyer,
                "projects" : projects,
                "deal" : deal,
                "last_time":  last_time,
                "offers" : offers,
                "description" :discription,
                "url" : card_url
                }

        self.jobs.append(data)


    def _get_price(self, string):
        test = r'[0-9][\s\S]+?₽'
        price = re.findall(test, string)[0]
        price = price.replace("₽", " ")
        price = price.replace(" ", "")
        return int(price)

    def _get_data(self, text, search_term):

            for i in text:
                try:
                    if search_term in i:
                        return i.split(":")[-1]
                except :
                    return None

    def _find_index(self, data, search_term):
        # search_term = 'Желаемый бюджет'
        index = -1
        for i, item in enumerate(data):
            if search_term in item:
                index = i
                break
        return index
    def test_ip(self):

        # Переход на сайт, который показывает ваш IP-адрес
        self.browser.visit('http://httpbin.org/ip')
        # Даем время на загрузку страницы
        time.sleep(2)
        # Получаем IP-адрес
        ip_address = self.browser.find_by_tag('body').text
        print("Ваш IP-адрес:", ip_address)
        self.browser.quit()

    def start(self):
        # self.test_ip()
        browser = self.browser
        browser.visit(self.start_url)
        page = browser.find_by_css('.pagination__item')[-2].text
        #бход страниц
        list =[self.get_card(self.start_url + f'&page={x}') for x in tqdm(range(1, int(page)+1))]
        # запуск извлечения информации
        filtered_cards = [card for card in self.cards_list if not any(str(id) in card for id in self.archive)]

        # поставить бар отслеживания
        [self._get_card_info(x) for x in tqdm(filtered_cards)]

        self.save_offers()

    def save_offers(self):
        data = self.jobs
        for item in data:
            Offers.objects.create(
                title=item['title'],
                description=item['description'],
                wanted_cost=item['wanted_cost'],
                cost=item['cost'],
                buyer=item['buyer'],
                projects=item['projects'],
                deal=item['deal'],
                last_time=item['last_time'],
                # Обратите внимание, что last_time - строка, вам может понадобиться преобразовать её в DateTime
                offers=int(item['offers']),  # Преобразуем в целое число
                url=item['url'],
                kwork_id=int(item['id'])  # Преобразуем id в целое число
            )
        # self.jobs = []

if __name__ == '__main__':
    base_url = 'https://kwork.ru/projects?fc=41'
    parser = Parser(base_url, True)
    parser.start()
    print( *parser.jobs, sep='\n')