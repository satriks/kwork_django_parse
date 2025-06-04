import os
import queue
import concurrent.futures
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from django.conf import settings


from parser.clear.Atum import Atum
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from .models import Offers

import random
import json
import time

class Kworker:
    def __init__(self, url):
        file_path = os.path.join(settings.BASE_DIR, 'parser', 'assets', 'proxy.txt')
        self.proxy_manager = Atum(file_path)
        self.url = url
        self.cards_url = []
        self.link_dict = {}
        self.count = 1
        self.checking_proxy = ''
        self.controller = {}

    def proxy_control(self, proxy):
        self.checking_proxy = proxy
        if proxy not in self.controller:
            self.controller[proxy] = 0
    def get_driver(self):
        proxy = self.proxy_manager.get_proxy()
        self.proxy_control(proxy)
        chrome_options = Options()
        chrome_options.add_argument(f'--proxy-server={proxy}')
        chrome_options.add_argument('--headless')  # Запуск в безголовом режиме
        chrome_options.add_argument('--no-sandbox')  # Для некоторых систем, чтобы избежать ошибок
        chrome_options.add_argument('--disable-dev-shm-usage')
        print("-" * 30)
        print(f"Запуск подключения {proxy}")
        # Настройка драйвера
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        # driver.set_page_load_timeout(20)

        return driver

    def main_pars(self):
        url = self.url
        print("-" * 30)
        print(f'Начат парсинг главной страницы : {url}')

        cards_url = []
        pagination = 0

        browser = self.get_driver()


        def cards_info():
            cards = browser.find_elements(By.CLASS_NAME, 'want-card')
            # uels = [x.get_attribute('href') for x in cards]
            links = [x.find_element(By.TAG_NAME, 'a') for x in cards]
            urls = [x.get_attribute('href') for x in links]
            [cards_url.append(url) for url in urls]
            print(f'Выполнен парсинг страницы {self.count}')
            self.count +=1


        url = url
        try:
            browser.get(url)
            time.sleep(5)
            cards_info()
            try:
                next_page_btn = browser.find_element(By.CLASS_NAME, 'pagination__arrow--next')
            except:
                next_page_btn = None

            while next_page_btn:
                next_page_btn.click()
                time.sleep(random.randint(1, 3))
                cards_info()
                try:
                    next_page_btn = browser.find_element(By.CLASS_NAME, 'pagination__arrow--next')
                except:
                    next_page_btn = None

        except Exception as e:

            raise e

        finally:
            self.cards_url = cards_url


    def run(self):
        check = 1
        while check:
            try:
                self.main_pars()
                check = 0
            except Exception as e:
                self.controller[self.checking_proxy] += 1
                self.count = 0
                print('Ошибка в парсинге главной страницы. Перезапуск')
                print(e)
        self.count = 1
        print('Запуск парсинга карточек ')
        self.create_link_dict()
        self.parsing_cards()

        if any(self.controller.values()) :
            print('*' * 22)
            print("Ошибки в прокси:")
            [print(item) for item in self.controller.items() if item[-1] > 0]
        return self.controller

    def save_card(self, card):
        try:
            # print(card['url'], "попытка записи")
            Offers.objects.create(**card)
            print('Успешно записано', card['url'])
        except Exception as e:
            print('Ошибка при записи')
            # print(e)



    def process_task(self, task):
        # Симуляция выполнения задачи с возможностью возникновения ошибки
        if random.choice([True, False]):  # Случайно выберем, произойдет ли ошибка
            raise ValueError(f"Ошибка при обработке задачи: {task}")
        print(f"Задача {task} успешно выполнена.")

    def parsing_cards(self):
        cards = []
        all_offers = Offers.objects.all()
        kwork_ids = [offer.kwork_id for offer in all_offers]
        task_queue = queue.Queue()
        test_dict = self.link_dict
        ready = {key: value for key, value in test_dict.items() if int(key) in kwork_ids}
        print(len(ready), "Карточки уже есть и были убраны ")
        filtered_dict = {key: value for key, value in test_dict.items() if int(key) not in kwork_ids}

        for i in filtered_dict.values():
            task_queue.put(i)

        def process_task(task):
            print(f'Начал парсинг карточки {task}')
            try:
                card = self.card_parse(task)
                self.save_card(card)
                return card
            except Exception as e:
                print(f"Ошибка при обработке задачи {task}: {e}")
                return None  # Возвращаем None в случае ошибки

        # Используем ThreadPoolExecutor для выполнения задач в 6 потоках
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
            futures = []
            while not task_queue.empty():
                task = task_queue.get()
                futures.append(executor.submit(process_task, task))
                task_queue.task_done()  # Указываем, что задача обработана
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result is not None:
                    cards.append(result)
                else:
                    # Если задача не была успешно обработана, можно добавить её обратно в очередь
                    task_queue.put(task)
        print("Все задачи обработаны.")
        return cards    # def parsing_cards(self):
    #
    #     cards = []
    #     all_offers = Offers.objects.all()
    #     kwork_ids = [offer.kwork_id for offer in all_offers]
    #
    #     task_queue = queue.Queue()
    #
    #
    #     test_dict = self.link_dict
    #
    #     ready = {key: value for key, value in test_dict.items() if int(key) in kwork_ids}
    #     print(len(ready), "Карточки уже есть и были убраны ")
    #     filtered_dict = {key: value for key, value in test_dict.items() if int(key) not in kwork_ids}
    #     # print(filtered_dict," фильтрованый дик")
    #     for i in filtered_dict.values():
    #         task_queue.put(i)
    #     # Обрабатываем задачи из очереди
    #     while not task_queue.empty():
    #         print(f'Еще в обработаке : {task_queue.qsize()}')
    #         task = task_queue.get()
    #         print(f'Начал парсинг карточки {task}')
    #
    #         try:
    #             card = self.card_parse(task)
    #             cards.append(card)
    #             self.save_card(card)
    #         except Exception as e:
    #             # print(e)
    #             print(f"Возвращаем задачу {task} обратно в очередь.")
    #             task_queue.put(task)
    #             self.controller[self.checking_proxy] += 1# Возвращаем задачу обратно в очередь
    #         finally:
    #             task_queue.task_done()  # Указываем, что задача обработана (даже если произошла ошибка)
    #
    #     print("Все задачи обработаны.")
    #     return cards



    def create_link_dict(self):
        link_dict = {}
        for url in self.cards_url:
            # Извлекаем идентификатор проекта из URL
            project_id = url.split('/')[-1]
            # Добавляем в словарь
            link_dict[project_id] = url
        self.link_dict = link_dict

    def dict_write(self):
        with open('links.json', 'w', encoding='utf-8') as json_file:
            json.dump(self.link_dict, json_file, ensure_ascii=False, indent=4)
        print("Словарь записан в файл links.json")

    def card_parse(self, url):
        browser = self.get_driver()
        card = {}
        card['url'] = url
        card['kwork_id'] = url.split('/')[-1]
        try:
            browser.get(url)
            time.sleep(random.randint(1, 3))
            title = browser.find_element(By.TAG_NAME, 'h1')
            card['title'] = title.text

            description = browser.find_element(By.CLASS_NAME, 'wants-card__description-text')
            card['description'] = description.text


            try :
                price = browser.find_element(By.CLASS_NAME, 'wants-card__price').find_element(By.TAG_NAME, 'div')
                price = self.clear_price(price.text)
            except Exception as e :
                price = None
            card['wanted_cost'] = price


            try :
                hight_price = browser.find_element(By.CLASS_NAME, 'wants-card__description-higher-price').find_element(By.TAG_NAME, 'div')
                hight_price = self.clear_price(hight_price.text)
                # print(self.clear_price(hight_price.text))
            except:
                hight_price = None

            card['cost'] = hight_price


            try :
                files_list = browser.find_element(By.CLASS_NAME, 'files-list')
                files = files_list.find_elements(By.TAG_NAME, 'a')
                liks = []
                for file in files:
                    liks.append(file.get_attribute('href'))
                files = ('\n').join(liks)

            except Exception as e:
                files = None

            card['files'] = files

            user = None
            projects = None
            hired = None

            try:
                info = browser.find_element(By.CLASS_NAME, 'dib')
                # print(info.text)
                dib = info.text.split('\n')
                dib = list(map(lambda x : x.split(':')[-1], dib))
                try:
                    user = dib[0]
                except:
                    user = None
                try:
                    projects = dib[1]
                except:
                    projects = None
                try:
                    hired =  dib[2].strip().replace('%', "")
                except:
                    hired = None

                # print(f'Пользователь {user}', projects, hired , sep='\n')
            except Exception as e:
                info = None
                print(e)
            card['buyer'] = user
            card['projects'] = projects
            card['deal'] = hired

            timer = None
            offers = None

            try:
                informer = browser.find_element(By.CLASS_NAME, 'want-card__informers-row')
                informer = informer.text.split('\n')
                [timer, offers] = list(map(lambda x : x.split(":")[-1], informer))
                # print(f"остаось времени { timer }", f"Предложений { offers}")
            except:
                info = None

            card['last_time'] = timer
            card['offers'] = offers
            time.sleep(1)
            return card


        except Exception as e:
            raise e

    def clear_price(self, price):
        # price = price.split(':')[-1]
        price = price.strip().replace('до', '').replace('₽', '')
        price = price.replace('Цена' , '').replace(" ", '')
        price = int(price)
        return price


if __name__ == '__main__':
    # test_url = "https://kwork.ru/projects/2845972"
    url = 'https://kwork.ru/projects?fc=41'
    # url = test_url
    kwork = Kworker(url)
    # kwork.card_parse(url)
    # kwork.parsing_cards()

    kwork.run()
    # kwork.create_link_dict()
    # kwork.dict_write()

# from parser.Kworker import Kworker
# url = 'https://kwork.ru/projects?fc=41'
# kwork = Kworker(url)
