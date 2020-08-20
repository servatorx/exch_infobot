
# -*- coding: utf-8 -*-

import telebot
import config
import dbworker
import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
from tabulate import tabulate
from random import randint
from telebot import types
import datetime
import matplotlib.pyplot as plt

bot = telebot.TeleBot(config.token)
months = {'Янв': "01", 'Фев': "02", 'Мар':"03", 'Апр':"04", 'Май':"05", 'Июн':"06", 'Июл':"07", 'Авг':"08", 'Сен':"09", 'Окт':"10",'Ноя':"11",'Дек':"12"}



def stat(url):
    website = requests.get(url).text
    soup = BeautifulSoup(website, 'lxml')
    table = soup.find_all('table')[0]
    rows = table.find_all('tr')
    fields_list = []

    for i in range(4):
        col = []
        col.append(rows[0].find_all('th')[i+1].get_text().strip())
        for row in rows[1:]:
            r = row.find_all('td')
            col.append(r[i+1].get_text().strip())
        fields_list.append(col)
    d = dict()
    for i in range(4):
        d[fields_list[i][0]] = fields_list[i][1:]
    df = pd.DataFrame(d)
    df = df.rename(columns={'Букв. код': 'Код'})
    return df


codes = list(stat('https://cbr.ru/currency_base/daily/')['Код'])



@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "Привет! я инфобот по курсам валют :) \n"
                                      "Узнать курс на сегдня по всем валютам: /all \n"
                                      "Узнать курс по конкретной валюте на дату: /specify \n"
                                      "Используйте /info или чтобы узнать что может сообщить бот.\n"
                                      "Используйте /commands чтобы получить список доступных комманд.\n"
                                      "Введите /reset чтобы сбросить данные и начать заново."
                                      "Введите /history посмотреть курс Доллара США за последние 30 дней.")
    dbworker.set_state(message.chat.id, config.States.S_ENTER_TYPE.value)
# По команде /reset будем сбрасывать состояния, возвращаясь к началу диалога
@bot.message_handler(commands=["reset"])
def cmd_reset(message):

    bot.send_message(message.chat.id, "Начнем заново.\n"
                                      "Курс по каким валютам вам интересен? Все или конкретная валюта: /all or /specify.\n"
                                      "Используйте /info или /commands чтобы узнать что может сообщить бот.")
    dbworker.set_state(message.chat.id, config.States.S_ENTER_TYPE.value)

@bot.message_handler(commands=["info"])
def cmd_info(message):
    bot.send_message(message.chat.id, "Я инфобот, который может сообщиться Вам информацию\n"
                                      "о курсах валют, утсановленных Центральным Банком РФ.\n"
                                      "Вы можете запросить как все установленные курсы валют на сегодня,\n"
                                      "или уточнить курс по конкретный валюте на желаемую дату\n"
                                      "Если вы ввели какие-то данные неверно, вы\n"
                                      "можете вольсользваться командой /reset и начать заново.\n"
                                    "Если вы запросите курс на будущее - то получите ответ с установленным курсмом на сегодняший день.")
    bot.send_message(message.chat.id, "Также я могу прислать вам график курса Доллара США за последние 30 дней.\n"
                                      "Для этого введите комманду /history\n")

@bot.message_handler(commands=["commands"])
def cmd_commands(message):
    bot.send_message(message.chat.id, "/reset - сбросить введенные данные и начать заново.\n"
                                      "/start - нчало диалога с ботом.\n"
                                      "/info - узнать какую информацию может предоставить бот\n"
                                      "/commands - получить список доступных комманд\n"
                                      "/history - посмотреть график курса Доллара США за последние 30 дней.\n"
                                      "/all - посмотреть все установленные курсы валют на сегодня.\n"
                                      "/specify - посмотреть курс по конкретной валюте на дату.")

@bot.message_handler(commands=['history'])
def history(message):
    bot.send_message(message.chat.id, "Минутку... \n")
    dbworker.set_state(message.chat.id, config.States.S_ENTER_HIST.value)
    now = datetime.datetime.now()
    year = now.year
    month = now.month
    day = now.day
    my_list = []
    dates_list = []
    if day < 30:
        print(day - 30)
    for i in range(day, 0, -1):
        d = str(i)
        m = str(month)
        y = str(year)
        if int(i) < 10:
            d = '0' + str(i)
        if month < 10:
            m = '0' + str(month)
        code = "USD" #dbworker.get_property(message.chat.id, "code")
        url = 'https://cbr.ru/currency_base/daily/?UniDbQuery.Posted=True&UniDbQuery.To='
        dates_list.append(d + '.' + m + '.' + y)
    month = month - 1
    for i in range(30, 30 - abs(day - 30), -1):
        d = str(i)
        m = str(month)
        y = str(year)
        if int(i) < 10:
            d = '0' + str(i)
        if month < 10:
            m = '0' + str(month)
        dates_list.append(d + '.' + m + '.' + y)
    #my_list = [69.1219, 69.1219, 70.395, 69.7524, 69.4822, 69.618, 69.5725, 69.5725, 69.5725, 69.4835, 68.8376, 68.8376,
    #              69.466, 69.1284, 69.1284, 69.1284, 69.9513, 70.4413, 70.4413, 70.5198, 70.4999, 70.4999, 70.4999,
    #              71.3409, 72.1719, 71.2379, 70.88, 71.2298, 71.2298, 71.2298]
    #my_list.reverse()
    y = my_list.copy()
    fig = plt.figure()
    ax = fig.add_subplot(111)
    dates_list.reverse()
    x = dates_list
    fig.suptitle('Курс USD за последние 30 дней', fontsize=20)
    plt.xticks(rotation=270)
    ax.plot(x, y)
    # ax.scatter([0, 1, 2, 3, 4], [1, 3, 8, 12, 27])
    #plt.show()
    plt.draw()
    fig.savefig('exch.png', dpi=100)
    img = open('exch.png', 'rb')
    bot.send_photo(message.chat.id, img)
    dbworker.set_state(message.chat.id, config.States.S_START.value)


@bot.message_handler(commands=["all"])
def cmd_listregions(message):
    x = stat('https://cbr.ru/currency_base/daily/')
    curr_dict = {}
    for i in x.iterrows():
        # print()
        curr_dict[i[1][0]] = [i[1][2], i[1][3], i[1][1]]
    msg_list = []
    for i in curr_dict:
        msg_list.append(str(i) + ": " + str(round(float(curr_dict[i][1].replace(",",".")),2)) + " руб. за " + str(curr_dict[i][2]) + " " + str(
            curr_dict[i][0]) + "\n")

    mess_tosend = ""
    for i in msg_list:
        mess_tosend = mess_tosend + i  # + "\n"
    #print(message)
    bot.send_message(message.chat.id, "Курсы валют, установленные ЦБ РФ на сегодня:")
    bot.send_message(message.chat.id, mess_tosend)
    #bot.send_message(message.chat.id, tabulate(x, headers=x.columns, tablefmt="grid"))
    dbworker.del_state(str(message.chat.id) + 'country')

@bot.message_handler(commands=["specify"])
def cmd_specify(message):
    dbworker.set_state(message.chat.id, config.States.S_ENTER_TYPE.value)
    bot.send_message(message.chat.id, "Вам необходимо ввести код валюты, и потом, дату на которую хотите узнать курс.\n"
                                      "Например: USD Для доллара США или EUR для Евро.\n")
    bot.send_message(message.chat.id, "Если вы не знаете коды валют, введите /codes.\n")
    dbworker.set_state(message.chat.id, config.States.S_ENTER_CODE.value)

@bot.message_handler(commands=["codes"])
def cmd_codes(message):
    x = stat('https://cbr.ru/currency_base/daily/')
    #print("Fdsfsd")
    j = ""
    for i in x[['Код', 'Валюта']].iterrows():
        j = j + str(i[1][0]) + "  " + str(i[1][1]) + "\n"
    bot.send_message(message.chat.id, j)


@bot.message_handler(content_types=["text"], func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_ENTER_CODE.value
                     and message.text.strip().lower() not in ('/reset', '/info', '/start', '/commands',
                                                              '/listregions', '/listregions',
                                                              '/listfields'))
def code_day(message):
    if message.text.upper() in codes:
        cur = message.text
        currency = cur.upper()
        print(currency)
        bot.reply_to(message, 'Введите число на которое хотите узнать курс: ')
        dbworker.set_property(message.chat.id, currency, "code")
        dbworker.set_state(message.chat.id, config.States.S_ENTER_DAY.value)
    else:
        bot.send_message(message.chat.id, "Вы ввели неверный код валюты. Попробуйте еще раз.")


@bot.message_handler(content_types=["text"], func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_ENTER_DAY.value
                     and message.text.strip().lower() not in ('/reset', '/info', '/start', '/commands',
                                                              '/listregions', '/listregions',
                                                              '/listfields'))
def day(message):
    if message.text in ('1', '2', '3', '4', '5', '6','7', '8', '9','10','11','12','13','14','15','16','17','18',
                         '19', '20', '21', '22', '23', '24', '25', '26', '27', '28',
                         '29', '30', '31'):
        #currency = messages.text
        dbworker.set_property(message.chat.id, message.text, "day")

        bot.reply_to(message, 'Введите месяц')
        #dbworker.set_property(messages.chat.id, currency, "code")
        markup = types.ReplyKeyboardMarkup()
        itembtn1 = types.KeyboardButton('Янв')
        itembtn2 = types.KeyboardButton('Фев')
        itembtn3 = types.KeyboardButton('Мар')
        itembtn4 = types.KeyboardButton('Апр')
        itembtn5 = types.KeyboardButton('Май')
        itembtn6 = types.KeyboardButton('Июн')
        itembtn7 = types.KeyboardButton('Июл')
        itembtn8 = types.KeyboardButton('Авг')
        itembtn9 = types.KeyboardButton('Сен')
        itembtn10 = types.KeyboardButton('Окт')
        itembtn11 = types.KeyboardButton('Ноя')
        itembtn12 = types.KeyboardButton('Дек')


        markup.add(itembtn1, itembtn2, itembtn3, itembtn4, itembtn5, itembtn6, itembtn7, itembtn8, itembtn9,
                   itembtn10, itembtn11, itembtn12)
        bot.send_message(message.chat.id, "Выберите месяц:", reply_markup=markup)
        dbworker.set_state(message.chat.id, config.States.S_ENTER_MONTH.value)
    else:
        bot.send_message(message.chat.id, "Вы ввели неверную дату. Попробуйте еще раз.")
        dbworker.set_state(message.chat.id, config.States.S_ENTER_DAY.value)




@bot.message_handler(content_types=["text"], func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_ENTER_MONTH.value
                     and message.text.strip().lower() not in ('/reset', '/info', '/start', '/commands',
                                                              '/listregions', '/listregions',
                                                              '/listfields'))
def ent_month(message):
    if message.text in ('Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн', 'Июл', 'Авг', 'Сен', 'Окт','Ноя','Дек'):
        dbworker.set_property(message.chat.id, message.text, "month")
        markup = types.ReplyKeyboardMarkup()
        itembtn1 = types.KeyboardButton('2010')
        itembtn2 = types.KeyboardButton('2011')
        itembtn3 = types.KeyboardButton('2012')
        itembtn4 = types.KeyboardButton('2013')
        itembtn5 = types.KeyboardButton('2014')
        itembtn6 = types.KeyboardButton('2015')
        itembtn7 = types.KeyboardButton('2016')
        itembtn8 = types.KeyboardButton('2017')
        itembtn9 = types.KeyboardButton('2018')
        itembtn10 = types.KeyboardButton('2019')
        itembtn11 = types.KeyboardButton('2020')



        markup.add(itembtn1, itembtn2, itembtn3, itembtn4, itembtn5, itembtn6, itembtn7, itembtn8, itembtn9,
                   itembtn10, itembtn11)
        bot.send_message(message.chat.id, "Выберите год:", reply_markup=markup)
        dbworker.set_state(message.chat.id, config.States.S_ENTER_YEAR.value)
    else:
        bot.send_message(message.chat.id, "Вы ввели неверный месяц. Попробуйте еще раз.")
        dbworker.set_state(message.chat.id, config.States.S_ENTER_MONTH.value)


@bot.message_handler(content_types=["text"], func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_ENTER_YEAR.value
                     and message.text.strip().lower() not in ('/reset', '/info', '/start', '/commands',
                                                              '/listregions', '/listregions',
                                                              '/listfields'))
def result_ret(message):
    if message.text in ('2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019', '2020'):
        year = message.text
        day = dbworker.get_property(message.chat.id, "day")
        if int(day) < 10:
            day = '0' + day
        month = dbworker.get_property(message.chat.id, "month")
        code = dbworker.get_property(message.chat.id, "code")
        print(code, day, year, month)
        print(day+ '.' + months[month] + '.' + year)
        markup = types.ReplyKeyboardRemove(selective=False)
        bot.send_message(message.chat.id, "Минутку...", reply_markup=markup)
        url = 'https://cbr.ru/currency_base/daily/?UniDbQuery.Posted=True&UniDbQuery.To='
        x = stat(url + day + '.' + months[month] + '.' + year)
        x.set_index('Код', inplace=True)

        result_ex = x.loc[code]
        bot.send_message(message.chat.id, f"Курс {code} на {day + '.' + months[month] + '.' + year}")
        bot.send_message(message.chat.id, f"{result_ex[2]} руб. за {result_ex[0]} {result_ex[1]}")

        dbworker.set_state(message.chat.id, config.States.S_START.value)
    else:
        #bot.send_message(message.chat.id, "История ежедневного курса валют у Банка России .")
        bot.send_message(message.chat.id, "Вы ввели неверный год. Попробуйте еще раз.")
        dbworker.set_state(message.chat.id, config.States.S_ENTER_YEAR.value)
    bot.send_message(message.chat.id, "Используйте /info или /commands чтобы узнать что может сообщить бот.")



if __name__ == "__main__":
    bot.infinity_polling()
