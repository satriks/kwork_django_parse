import os

import requests
import asyncio
import aiohttp
import json

from django.conf import settings


async def check_proxy(proxy):
    """Проверяет, работает ли прокси."""
    print(f'Тест прокси {proxy}')
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('http://httpbin.org/ip', proxy=proxy, timeout=5) as response:
                ip = await response.json()
                # print(ip, proxy)
                return proxy
    except Exception:
        return False

def read_proxies_from_file(file_path):
    """Читает прокси из файла."""
    with open(file_path, 'r') as file:
        return [line.strip() for line in file if line.strip()]
def write_working_proxies_to_file(proxies, output_file):
    """Записывает работающие прокси в файл."""
    with open(output_file, 'w') as file:
        for proxy in proxies:
            file.write(f"{proxy}\n")

def get_proxy_jason():
    file_path = os.path.join(settings.BASE_DIR, 'parser','clear', 'proxylist2.json')
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        res = [f"{p['ip']}:{p['port']}" for p in data]
        print('Чтение файла с прокси завершено ')
        #
        return res

async def clear_proxy_s1(output_file):

    proxies = get_proxy_jason()
    tasks = [asyncio.create_task(check_proxy(f'http://{proxy}')) for proxy in proxies]
    res = await asyncio.gather(*tasks)

    working_proxies = [cut(url) for url in res if url != False]
    write_working_proxies_to_file(working_proxies, output_file)
    print(f"Работающие прокси записаны в файл: {output_file}")

def cut(string):
    'http://4cFfE9:SHK5Lx@168.81.64.138:8000'
    return string.replace('http://', '').replace('https://', '')

if __name__ == "__main__":
    # input_file = 'proxy.txt'  # Укажите путь к вашему файлу с прокси
    output_file = './working_proxies_28_05.txt'
    asyncio.run(clear_proxy_s1(output_file))# Укажите путь к выходному файлу

    # proxies = get_proxy_jason()
    # write_working_proxies_to_file(proxies, output_file)
