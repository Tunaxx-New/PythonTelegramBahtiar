from __future__ import print_function

import os.path
import random
import time
from datetime import date

from queue import Queue
import telegram
from googleapiclient.http import MediaFileUpload
from telegram import Update, ForceReply, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler, Filters, Updater

telegram_bot_token = '6083695592:AAGrWxYDm6MQP6UVWKCCA1SsTkDybSitGi4'
bot = telegram.Bot(token=telegram_bot_token)

print("Hello. Cleint has just started.")

data = {
    'Даниил': [
        'лох',
        'урод',
        'уёбок'
    ],
    'Диас': [
        '💪Красавчик'
    ],
    'Нурхан': [
        '💪Красавчик'
    ],
    'Аяжан': [
        '💪Красавчиха'
    ],
    'Никита': [
        '💪Красавчик'
    ],
}


def generate(update: Update, context) -> None:
    print(1)
    keyboard = [
        [],
    ]
    for user, i in enumerate(data):
        print(i)
        keyboard[0].append(InlineKeyboardButton(i, callback_data=str(i)))

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text("Please choose:", reply_markup=reply_markup)


def button(update: Update, context) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    print(query)
    name = query['data']
    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See ht   tps://core.telegram.org/bots/api#callbackquery
    result = data[name][random.randrange(0, len(data[name]))]
    query.edit_message_text(text=f'{name} {result}')



def main():
    updater = Updater(bot=bot, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("g", generate))
    dispatcher.add_handler(CallbackQueryHandler(button))
    updater.start_polling()


if __name__ == '__main__':
    main()
