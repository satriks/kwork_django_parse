from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Run my function'
    def handle(self, *args, **kwargs):
        from parser.Kworker import Kworker
        urls= ['https://kwork.ru/projects?c=41&attr=211','https://kwork.ru/projects?c=41&attr=7352', 'https://kwork.ru/projects?keyword=react&c=all', 'https://kwork.ru/projects?keyword=django&c=all', 'https://kwork.ru/projects?keyword=python&c=all']
        # urls = ['https://kwork.ru/projects?keyword=django&c=all']
        # url = 'https://kwork.ru/projects?fc=41'
        # url= 'https://kwork.ru/projects?keyword=react&c=all'
        not_working_proxy = {}
        kwork = None
        for url in urls:
            kwork = Kworker(url)
            errors_proxy: dict = kwork.run()
            for k, v in  errors_proxy.items():
                if v > 0 :
                    if k in not_working_proxy:
                        not_working_proxy[k] += v
                    else :
                        not_working_proxy[k] = v
        if not_working_proxy :
            print('*' * 22)
            print("Ошибки в прокси:")
            [print(item) for item in not_working_proxy.items() if item[-1] > 0]
            for error_proxy in not_working_proxy.items():
                if error_proxy[-1] > 10:
                    if kwork:
                        kwork.proxy_manager.delete(error_proxy[0])



        self.stdout.write(self.style.SUCCESS('-' * 40))
        self.stdout.write(self.style.SUCCESS('Команда выполнена успешно!'))
