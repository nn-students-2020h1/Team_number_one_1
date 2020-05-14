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
import time
import sqlite3
import re

from itertools import islice
from operator import sub

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.



LOG_ACTIONS = []
LOG_TIME_MY = [0]
count = [-1]

#Подкллючение базы данных

__connection = None
def get_connect():
    global __connection
    if __connection is None:
        __connection = sqlite3.connect('base1.db')
    return __connection

def init_db(force: bool = False):
    conn = get_connect()
    c = conn.cursor()
    if force:
        c.execute('DROP TABLE IF EXISTS corono')
    c.execute("""
        CREATE TABLE IF NOT EXISTS corono (
            active     INTEGER NOT NULL,
            death      INTEGER NOT NULL,
            recovered  INTEGER NOT NULL
        )
    """)

    conn.commit()

def add_message(active: int , death: int, recovered: int):
    conn = get_connect()
    c = conn.cursor()
    print("**")
    c.execute('INSERT INTO corono (active, death, recovered) VALUES (?, ?, ?)', (active, death, recovered))

    conn.commit()

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
    #print(update.message['text'])
    user_message = update.message['text']
    dat = re.findall(r'((?:0[1-9]|[12][0-9]|3[01])\-(?:0[1-9]|1[012])\-(?:202[0-9]|2[1-9][0-9][0-9]))', user_message)
    #print(user_message, dat)
    i = 0;
    text = ''
    now = datetime.datetime.now()
    day = now.day
    if day < 10:
        day = f"0{now.day}"
    month = now.month
    if month < 10:
        month = f"0{now.month}"

    #print(f'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/'f'{month}-{day}-{now.year}.csv')
    if dat:
        r = requests.get(f'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/'f'{dat[0]}.csv')
        text += f"{dat[0]}\n"
        print("++++")
    else:
        r = requests.get(f'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/'f'{month}-{day}-{now.year}.csv')
        text += f'{month}-{day}-{now.year}\n'
        print("*****")


    if r.status_code == 404:
        day = now.day-1
        if day < 10:
            day = f"0{now.day-1}"

        if dat:
            r = requests.get(f'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/'f'{dat[0]}.csv')
        else:
            r = requests.get(f'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/'f'{month}-{day}-{now.year}.csv')

    #print("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/03-26-2020.csv")
    #print(f'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{month}-{day}-{now.year}.csv')
    with open('korona_v.csv', 'w', newline='') as csvfile:
        csvfile.write(r.text)
    with open('korona_v.csv', 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if i > 4:
                break
            if row['Province_State'] != '':
                text += f"Province: {row['Province_State']} -> Confirmed: {row['Confirmed']}\n"
                i += 1
    update.message.reply_text(text)

def request_covid(i=0):
    while True:
        data = (datetime.date.today() - datetime.timedelta(days=i)).strftime("%m-%d-%Y")

        r = requests.get(
            f'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{data}.csv')
        #print(f'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{data}.csv')
        if r.status_code == 200:
            break
        i += 1
    return data, r

def covid_file(data, r, parametr):
    while True:
        try:
            with open(f'corono_stats/{data}.csv', 'r', encoding='utf-8') as file:
                act_cor = CovidAnalitic(csv.DictReader(file))
                curent = act_cor.top_covid(parametr, -1)

                break


        except:
            with open(f'corono_stats/{data}.csv', 'w', encoding='utf-8') as file:
                file.write(r.text)
    return curent


class CovidAnalitic:
    def __init__(self, reader):
        self.reader = reader  # reader = csv.DictReader(file)

    def top_covid(self, parametr='Active', n=5):
        list = []
        for row in self.reader:
            if not row[parametr].isdigit():
                continue
            list.append({'Country': row['Country_Region'], 'Parametr': int(row[parametr])})
        list.sort(key=lambda d: d['Parametr'], reverse=True)
        if n != -1:
            top = list[:n]
        else:
            top = list
        return top


    @staticmethod
    def contrast_day(parametr):
        day, r = request_covid()
        yesterday, ry = request_covid(2)
        curent = covid_file(day, r, parametr)
        print("!!!")
        per = covid_file(yesterday, ry, parametr)
        new = []
        for i in range(len(per)):
            new.append(
                {'Country': per[i]['Country'],
                 'Parametr': curent[i]['Parametr'] - per[i]['Parametr']
                 })

        return new


@log_action
def corona_details(update: Update, context: CallbackContext):
    new_active = CovidAnalitic.contrast_day('Active')
    new_death = CovidAnalitic.contrast_day('Deaths')
    new_recovered = CovidAnalitic.contrast_day('Recovered')


    text = 'Мировая статистика за последние сутки:\n'

    sum = 0
    for i in new_active:
        sum += i['Parametr']
    active_save = sum
    text += 'Новые заражённые: {}\n'.format(sum)
    sum = 0
    for i in new_death:
        sum += i['Parametr']
    death_save = sum
    text += 'Смертей: {}\n'.format(sum)
    sum = 0
    for i in new_recovered:
        sum += i['Parametr']
    recovered_save = sum
    text += 'Выздоровевших: {}\n'.format(sum)
    update.message.reply_text(text)

    init_db()
    print("***")
    print(active_save, death_save, recovered_save)
    add_message(active=active_save, death=death_save, recovered=recovered_save)


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
        base_url=PROXY,
    )
    updater = Updater(bot=bot, use_context=True)

    # on different commands - answer in Telegram
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('help', chat_help))
    updater.dispatcher.add_handler(CommandHandler('history', history))
    updater.dispatcher.add_handler(CommandHandler('cat_fact', cat_fact))
    updater.dispatcher.add_handler(CommandHandler('corono_stats', corono_stats))
    updater.dispatcher.add_handler(CommandHandler('corona_stats_dynamic', corona_details))

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
