#!/usr/local/bin/python3
# -*- coding: utf-8 -*-


from setup import PROXY, TOKEN
from telegram import Bot, Update
from telegram.ext import CallbackContext, CommandHandler, Filters, MessageHandler, Updater
import logging
import requests
import json
import csv
import datetime
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.



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


"""Логи ошибок"""
def errors(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            logger = logging.getLogger()
            logger.warning()
            logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
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
def cat_fact(update: Update, context: CallbackContext):
    max = 0
    text = ''
    r = requests.get('https://cat-fact.herokuapp.com/facts')
    answer = json.loads(r.text)
    for i in answer['all']:
        if i['upvotes'] > max:
            max = i['upvotes']
            text = i['text']
    update.message.reply_text(text)

@log_action
def corono_stats(update: Update, context: CallbackContext):
    i = 0;
    text = ''
    now = datetime.datetime.now()
    day = now.day
    if day < 10:
        day = f"0{now.day}"
    month = now.month
    if month < 10:
        month = f"0{now.month}"

    r = requests.get(f'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{month}-{day}-{now.year}.csv')
    if r.status_code == 404:
        day = now.day-1
        if day < 10:
            day = f"0{now.day-1}"

        r = requests.get(f'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{month}-{day}-{now.year}.csv')
    text=f"{month}-{day}-{now.year}\n"
    with open('korona_v.csv', 'w', newline='') as csvfile:
        csvfile.write(r.text)
    with open('korona_v.csv', 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if i > 4:
                break
            if row['Province/State'] != '':
                text += f"Province: {row['Province/State']} -> Confirmed: {row['Confirmed']}\n"
                i += 1
    update.message.reply_text(text)


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
    print(context.error)

@errors
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
    updater.dispatcher.add_handler(CommandHandler('cat_fact', cat_fact))
    updater.dispatcher.add_handler(CommandHandler('corono_stats', corono_stats))

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
