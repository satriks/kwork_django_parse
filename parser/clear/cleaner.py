from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor, as_completed

import asyncio
import json
import os

import aiohttp
from tqdm import tqdm


async def clear_proxy_s1(input_file):
    """Асинхронная проверка прокси на подключение и получение json"""
    proxies = read_file(input_file)
    tasks = []
    # Создаем прогресс-бар
    with tqdm(total=len(proxies), desc="Проверка прокси") as pbar:
        for proxy in proxies:
            task = asyncio.create_task(check_proxy(f'http://{proxy}'))
            task.add_done_callback(lambda x: pbar.update(1))  # Обновляем прогресс-бар по завершении задачи
            tasks.append(task)
    res = await asyncio.gather(*tasks)
    working_proxies = [cut(url) for url in res if url != False]
    return working_proxies

    #

async def check_proxy(proxy):
    """Проверяет, работает ли прокси."""
    # print(f'Тест прокси {proxy}')
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('http://httpbin.org/ip', proxy=proxy, timeout=5) as response:
                ip = await response.json()
                # print(ip, proxy)
                return proxy
    except Exception:
        return False
def read_file(input_file):
    '''Чтение списка прокси из файла'''
    with open(input_file, 'r', encoding='utf-8') as file:
        if input_file.split('.')[-1] == 'json':
            data = json.load(file)

            try:
                res = [f"{p['ip']}:{p['port']}" for p in data]
            except Exception as e:
                # print(e)
                pass
            try:
                res = [f"{p['host']}:{p['port']}" for p in data]
            except Exception as e:
                # print(e)
                pass
            #
            return res
        if input_file.split('.')[-1] == 'txt':
            return [line.strip() for line in file if line.strip()]
    print('Чтение файла с прокси завершено ')

def cut(string):
    '''Убирает http'''
    return string.replace('http://', '').replace('https://', '')


def clear_proxy_s2(proxies):
    correct_proxies = []

    # Создаем пул потоков с 3 потоками
    with ThreadPoolExecutor(max_workers=3) as executor:
        # Запускаем задачи проверки прокси
        future_to_proxy = {executor.submit(check_proxy_with_selenium, proxy): proxy for proxy in proxies}

        # Обрабатываем результаты по мере завершения
        for future in tqdm(as_completed(future_to_proxy), total=len(proxies), desc='Проверка прокси'):
            proxy = future_to_proxy[future]
            try:
                result = future.result()
                if result:
                    correct_proxies.append(proxy)
                    tqdm.write(f'Прокси работает: {proxy}')
            except Exception as e:
                tqdm.write(f'{proxy} - не работает: {e}')
    write_working_proxies_to_file(correct_proxies)
    print(correct_proxies)
    print('Проверка прокси закончена')

def check_proxy_with_selenium(proxy):
    """Проверяет прокси с использованием Selenium."""
    try:
        driver = get_driver(proxy)
        if check_selenium(driver):
            return True
    except Exception as e:
        print(f'Ошибка при проверке {proxy}: {e}')
    finally:
        driver.quit()  # Закрываем драйвер, если он был открыт
    return False


def get_driver(proxy):
    chrome_options = Options()
    chrome_options.add_argument(f'--proxy-server={proxy}')
    chrome_options.add_argument('--headless')  # Запуск в безголовом режимеА
    # chrome_options.add_argument('--no-sandbox')  # Для некоторых систем, чтобы избежать ошибок
    # chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-extensions")  # Отключение расширений
    chrome_options.add_argument("--disable-gpu")  # Отключение графического процессора (если не нужен)
    chrome_options.add_argument("--log-level=3")  # Отключение логов (только ошибки)

    # print(f"Подготовка драйвера {proxy}")

    # Настройка драйвера
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_page_load_timeout(6)

    return driver

def check_selenium(driver):
    try:
        driver.get('https://kwork.ru/')

        element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.TAG_NAME, 'h1'))
        )
        driver.quit()
        return True
    except Exception as e:
        return False

def write_working_proxies_to_file(proxies):
    """Записывает работающие прокси в файл."""
    output_file = 'assets/proxy.txt'

    with open(output_file, 'a') as file:
        for proxy in proxies:
            file.write(f"{proxy}\n")
    print(f'Записанно в файл {output_file}')

def run(file):
    print('Очистка прокси Шаг 1')
    data = asyncio.run(clear_proxy_s1(file))
    print(f'\n Найдено {len(data)} рабочих прокси')
    print('Очистка прокси Шаг 2')
    clear_proxy_s2(data)

if __name__ == '__main__':
    file = 'proxylist.json'
    run(file)