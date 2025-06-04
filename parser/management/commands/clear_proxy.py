import os
from django.conf import settings
from django.core.management.base import BaseCommand
from parser.clear import cleaner

class Command(BaseCommand):
    help = 'Run my function'
    def handle(self, *args, **kwargs):


        file_path = os.path.join(settings.BASE_DIR, 'assets', 'proxylist.json')
        cleaner.run(file_path)


        self.stdout.write(self.style.SUCCESS('-' * 40))
        self.stdout.write(self.style.SUCCESS('Команда выполнена успешно!'))
