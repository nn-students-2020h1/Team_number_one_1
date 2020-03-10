#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import logging

from setup import PROXY, TOKEN
from telegram import Bot, Update
from telegram.ext import CallbackContext, CommandHandler, Filters, MessageHandler, Updater
from itertools import islice

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.

import datetime

LOG_ACTIONS = []
LOG_TIME_MY = [0]
count = [-1]

"""['message']['chat']['first_name']"""
def log_action(func):
    def inner(*args, **kwargs):
        update = args[0]

        global txt_name
        txt_name = str(update.message.from_user.id) + '_' + str(update.effective_user.first_name)

        if (LOG_TIME_MY[0] != datetime.datetime.now().time().minute):
            LOG_TIME_MY[0] = datetime.datetime.now().time().minute
            count[0] += 1
            LOG_ACTIONS.append([])
            """print(datetime.datetime.now().time().minute)"""

        

        LOG_ACTIONS[count[0]].append({
            'function': func.__name__,
            'user': update.effective_user.first_name,
            'message': update.message.text,
            'time':str(datetime.datetime.now().time()),
        })
        
        for i in LOG_ACTIONS:
            print(i)

        bot_logs = open("C:\\Users\\Семен\\venv_my\\files\\" + txt_name + '.txt', 'a')
        bot_logs.write(f"{LOG_ACTIONS[count[0]][-1]['message']}" + '\n')
        bot_logs.close()

        func(*args, **kwargs)
    return inner

@log_action
def history(update: Update, context: CallbackContext):
    history_list = []
    bot_logs = "C:\\Users\\Семен\\venv_my\\files\\" + txt_name + '.txt'
    line_counter = len(open(bot_logs).readlines())
    line_counter -= 1
    if line_counter == 0:
        update.message.reply_text('Вы ещё не писали мне сообщения')
        n = 0
    elif line_counter == 1:
        n = 1
        text = 'Ваше последнее сообщение\n'
    elif line_counter < 5:
        n = line_counter
        text = f'Ваши последние {n} сообщения\n'
    else:
        n = 5
        text = f'Ваши последние 5 сообщений\n'
    s=""
    block = 0
    with open(bot_logs, 'r') as input_file:
        for i in input_file:
            block += 1
            if  0<line_counter-block<6:
                s += i

    update.message.reply_text(text + s)



@log_action
def start(update: Update, context: CallbackContext):
    """Send a message when the command /start is issued."""
    update.message.reply_text(f'Привет, {update.effective_user.first_name}!')

@log_action
def chat_help(update: Update, context: CallbackContext):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Введи команду /start для начала. ')

@log_action
def echo(update: Update, context: CallbackContext):
    """Echo the user message."""
    update.message.reply_text(update.message.text)

@log_action
def error(update: Update, context: CallbackContext):
    """Log Errors caused by Updates."""
    logger.warning(f'Update {update} caused error {context.error}')


def main():
    bot = Bot(
        token=TOKEN,
        base_url=PROXY,  # delete it if connection via VPN
    )
    updater = Updater(bot=bot, use_context=True)

    # on different commands - answer in Telegram
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('help', chat_help))
    updater.dispatcher.add_handler(CommandHandler('history', history))

    # on noncommand i.e message - echo the message on Telegram
    updater.dispatcher.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    updater.dispatcher.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    logger.info('Start Bot')
    main()
