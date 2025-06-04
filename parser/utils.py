import telegram
from django.conf import settings
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

async def send_telegram_message(message, kwork_id ):
    bot = telegram.Bot(token=settings.TELEGRAM_BOT_TOKEN)
    chat_id = settings.TELEGRAM_CHAT_ID
    keyboard = [
        [
            InlineKeyboardButton("Интересно", callback_data=f'interesting : {kwork_id}'),
            InlineKeyboardButton("Не интересно", callback_data=f'not_interesting : {kwork_id}')
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    # ID чата или пользователя
    await bot.send_message(chat_id=chat_id, text=message, reply_markup=reply_markup)