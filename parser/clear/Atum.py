import asyncio
import random

import requests

from parser.clear.proxy_check_selenium import clear_proxy_s2, clear_proxy_s2_treading
from parser.clear.proxy_checker import clear_proxy_s1


class Atum:
    def __init__(self, filename):
        self.filename = filename
        self.proxies = self.load_proxies()
        self.error_count = {proxy: 0 for proxy in self.proxies}


    def clear_proxies_step1(self):
        output_file = './working_proxies_30_05.txt'
        asyncio.run(clear_proxy_s1(output_file))
    def clear_proxies_step2(self):
        file = './working_proxies_30_05.txt'
        clear_proxy_s2(file)

    def load_proxies(self):
        """Загружает список прокси из файла."""
        with open(self.filename, 'r') as file:
            proxies = [line.strip() for line in file if line.strip()]
        return proxies


    def save_proxies(self):
        """Сохраняет обновленный список прокси в файл."""
        with open(self.filename, 'w') as file:
            for proxy in self.proxies:
                file.write(f"{proxy}\n")

    def delete(self, proxy):
        print("del", proxy)
        del self.error_count[proxy]
        self.proxies.remove(proxy)
        self.save_proxies()

    def check_errors(self):
        error_proxy = []
        for elem in self.error_count.items():
            (proxy, count)  = elem
            if count > 0:
                error_proxy.append(proxy)
        [self.delete(proxy) for proxy in error_proxy]
    def get_proxy(self):
        try:
            if len(self.proxies) < 1:
                raise Exception("кончились прокси")
            return random.choice(self.proxies)
        except :
            raise Exception("кончились прокси")


    def upate_proxy(self, proxy ):
        print(proxy)
        if proxy in self.proxies:
            self.error_count[proxy] +=1
            self.check_errors()


# Пример использования
if __name__ == "__main__":
    proxy_manager = Atum('../../assets/proxy.txt')
    proxy_manager.check_errors()
