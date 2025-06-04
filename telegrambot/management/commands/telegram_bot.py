from django.core.management.base import BaseCommand
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from django.conf import settings
from telegram.ext._handlers.callbackqueryhandler import CallbackQueryHandler
from parser.models import Offers
from asgiref.sync import sync_to_async

@sync_to_async
def get_offer(kwork_id):
   return Offers.objects.get(kwork_id=kwork_id)

@sync_to_async
def set_offer_status(kwork_id, status):
   offer = Offers.objects.get(kwork_id=kwork_id)
   offer.status = status
   offer.save()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Привет! Я ваш бот.')
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Получаем ID чата
    chat_id = update.message.chat.id
    # Отправляем ID чата обратно пользователю
    await update.message.reply_text(f'Ваш ID чата: {chat_id}')
    # Вызываем вашу функцию Django (если нужно)
    my_function(chat_id)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # Подтверждение нажатия кнопки
    # print('был запрос')
    # Обработка нажатия кнопки и обновление статуса в модели

    id = query.data.split(":")[-1].strip()
    if 'not_interesting' in query.data:
        await query.edit_message_text(text="Вы выбрали: Не интересно")
        offer = await get_offer(id)
        if offer:
            await set_offer_status(id, 'not_interesting')
        print('Вы выбрали: Не интересно')


    elif 'interesting' in query.data:
        offer = await get_offer(id)

        await query.edit_message_text(text=f"Вы выбрали: Интересно \n{offer} \n{offer.wanted_cost} \n{offer.url}")
        if offer:
            await set_offer_status(id, 'interesting')
        print(f'Вы выбрали: Интересно {offer}')
    # Пример обновления статуса в модели
    # YourModel.objects.create(status=status, timestamp=timezone.now())
    # await query.edit_message_text(text=f"Вы выбрали: {status}")
def my_function(chat_id):
    # Ваша логика здесь
    print(chat_id)
    print("Функция вызвана!")
class Command(BaseCommand):
    help = 'Запуск бота Telegram'
    def handle(self, *args, **kwargs):
        application = ApplicationBuilder().token(settings.TELEGRAM_BOT_TOKEN).build()
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

        application.add_handler(CallbackQueryHandler(button_callback))  # Добавьте этот обработчик
        application.run_polling()