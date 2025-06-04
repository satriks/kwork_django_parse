from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Offers  # Импортируйте вашу модель
from .utils import send_telegram_message  # Импортируйте функцию для отправки сообщений
import asyncio




@receiver(post_save, sender=Offers)
def notify_new_record(sender, instance, created, **kwargs):
    print('Отправленно сообщение в телеграм')
    if created:
        message = f'{instance.title} \n Создана новая запись: {instance.kwork_id} \n \n   {instance.description} \n цена :  {instance.wanted_cost} - {instance.cost} \n посмотреь детально \n {instance.url}'
        asyncio.run(send_telegram_message(message, instance.kwork_id))  # Запускаем асинхронную функцию