import concurrent.futures
from selenium.webdriver.common.by import By

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from tqdm import tqdm
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def proxy_reader(file_path):
    """Читает прокси из файла."""
    with open(file_path, 'r') as file:
        return [line.strip() for line in file if line.strip()]

def write_working_proxies_to_file(proxies):
    """Записывает работающие прокси в файл."""
    output_file = 'working_proxies_step2_txt'

    with open(output_file, 'w') as file:
        for proxy in proxies:
            file.write(f"{proxy}\n")
    print(f'Записанно в файл {output_file}')

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
    # driver.set_page_load_timeout(20)

    return (driver, proxy)

def check_selenium(driver):
    try:
        # driver.set_page_load_timeout(8)
        driver.get('https://kwork.ru/')

        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'h1'))
        )
        # if 'Покупайте фриланс-услуги' in element.text.strip():
            # print(f'OK')
        driver.quit()
        return True
    except Exception as e:
        return False


def clear_proxy_s2(file_path):
    correct_proxies = []
    proxies = proxy_reader(file_path)
    for proxy in tqdm(proxies, desc='Проверка прокси'):
        # print(f'Проверка прокси {proxy}')
        try :
            tqdm.write(f'Проверка {proxy}')
            driver, proxy = get_driver(proxy)
            if check_selenium(driver):
                correct_proxies.append(proxy)
                # print(f'Прокси работает : {proxy}')
        except Exception as e:
            # print(f'{proxy} - не работает')
            print(e)

    write_working_proxies_to_file(correct_proxies)
    print(correct_proxies)
    print('Проверка прокси закончена')
# def run(file_path):
#     correct_proxies = []
#     proxies = proxy_reader(file_path)
#     drivers = []
#     # for proxy in proxies:
#     #     try:
#     #         driver = get_driver(proxy)
#     #         drivers.append(driver)
#     #     except:
#     #         print(f'{proxy} не работате ')
#     with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
#         futures = {executor.submit(get_driver, proxy): proxy for proxy in proxies}
#         try :
#             for future in concurrent.futures.as_completed(futures):
#
#                 result = future.result()
#                 print(result, "Тут пишется результат футуры")
#                 if  result:
#
#                     driver, proxy = result
#                     print(f'Старт теста {proxy}')
#                     future = executor.submit(check_selenium, driver)
#                     future.running()
#         except:
#             print(42)
  # ------------------------------------------
def clear_proxy_s2_treading(file_path):
    correct_proxies = []
    proxies = proxy_reader(file_path)

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(get_driver, proxy): proxy for proxy in proxies}

        for future in concurrent.futures.as_completed(futures):
            proxy = futures[future]
            try:
                driver = future.result()  # Получаем драйвер
                print(f'Старт теста {proxy}')
                # Проверяем прокси
                check_future = executor.submit(check_selenium, driver)
                if check_future.result():  # Если прокси работает
                    correct_proxies.append(proxy)
                    print(f'Прокси работает : {proxy}')
            except Exception as e:
                print(f'Ошибка с прокси {proxy}: {e}')

    write_working_proxies_to_file(correct_proxies)
    print(correct_proxies)
    print('Проверка прокси завершена ')


    # ------------------------------------------
    # Используем ThreadPoolExecutor для многопоточности
    # with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
    #     futures = {executor.submit(check_selenium, get_driver(driver)): driver for driver in drivers}
    #
    #     for future in concurrent.futures.as_completed(futures):
    #         result = future.result()
    #         if result:
    #             correct_proxies.append(result)
    #             print(f'Прокси работает : {result}')

    # write_working_proxies_to_file(correct_proxies)
    # print(correct_proxies)


if __name__ == "__main__":
    file = 'working_proxies_28_05.txt'
    clear_proxy_s2(file)