from datetime import datetime
import os
from time import sleep

import telebot
import logging
import psycopg2

import ImageSchedule
from config import *
import requestToBD
import re
from flask import Flask, request

bot = telebot.TeleBot(BOT_TOKEN)
# server = Flask(__name__)
# logger = telebot.logger
# logger.setLevel(logging.DEBUG)

connection = psycopg2.connect(DB_URI, sslmode="require")
cur = connection.cursor()

username = ""
start_message = "Привет, я телеграм бот с расписанием ИГУ.\n" \
                "Для начала введи номер своей группы в формате 02321-ДБ.\n" \
                "Я могу выдавать расписание на учебный цикл, неделю или день.\n"


pointer_group = {}
inline_id = {}

@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, start_message)
    set_group(message)

def set_group(message):
    global pointer_group
    id = message.from_user.id
    pointer_group.update({id: 0})
    id = message.from_user.id
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
    groups = requestToBD.get_group()
    for number in groups[0:5]:
        keyboard.add(telebot.types.InlineKeyboardButton(text=number[0], callback_data='group'+str(number)))
    keyboard.row(telebot.types.InlineKeyboardButton('👉', callback_data='right'))
    bot.send_message(id, text="Выберите группу:", reply_markup=keyboard)

def inline_number_group(user_id, messageid):
    global pointer_group
    pointer = pointer_group[user_id]
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
    groups = requestToBD.get_group()

    if pointer <= 0:
        pointer_group.update({user_id: 0})
        for number in groups[pointer:pointer + 5]:
            keyboard.add(telebot.types.InlineKeyboardButton(text=number[0], callback_data='group'+str(number)))
        keyboard.row(telebot.types.InlineKeyboardButton('👉', callback_data='right'))
    elif pointer // 5 >= len(groups) // 5:
        pointer_group.update({user_id: ((len(groups) // 5) * 5)})
        for number in groups[pointer:pointer + 5]:
            keyboard.add(telebot.types.InlineKeyboardButton(text=number[0], callback_data='group'+str(number)))
        keyboard.row(telebot.types.InlineKeyboardButton('👈', callback_data='left'))
    else:
        for number in groups[pointer:pointer + 5]:
            button = telebot.types.InlineKeyboardButton(text=number[0], callback_data='group-'+str(number))
            keyboard.add(button)
        buttonNext = telebot.types.InlineKeyboardButton('👉', callback_data='right')
        buttonBack = telebot.types.InlineKeyboardButton('👈', callback_data='left')
        keyboard.row(buttonBack, buttonNext)

    bot.edit_message_reply_markup(chat_id=user_id, message_id=messageid, reply_markup=keyboard)

#Выбор группы
@bot.callback_query_handler(func=lambda button: 'group' in button.data)
def process_callback_button1(callback_query):
    global pointer_group
    bot.answer_callback_query(callback_query_id=callback_query.id)
    bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.id)
    pointer_group.pop(callback_query.from_user.id)
    set_number_gruop(callback_query.data[callback_query.data.find('\'')+1:callback_query.data.rfind('\'')], callback_query.from_user.id)




@bot.callback_query_handler(func=lambda button: button.data == 'right')
def process_callback_button1(callback_query):
    global pointer_group
    pointer_group[callback_query.from_user.id] += 5
    inline_number_group(callback_query.from_user.id, callback_query.message.id)
    bot.answer_callback_query(callback_query_id=callback_query.id)


@bot.callback_query_handler(func=lambda button: button.data == 'left')
def process_callback_button1(callback_query):
    global pointer_group
    pointer_group[callback_query.from_user.id] -= 5
    inline_number_group(callback_query.from_user.id, callback_query.message.id)
    bot.answer_callback_query(callback_query_id=callback_query.id)


def set_number_gruop(number_group, user_id):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton("Расписание на сегодня")
    btn2 = telebot.types.KeyboardButton("Расписание на неделю")
    btn3 = telebot.types.KeyboardButton("Изменить группу")
    markup.add(btn1, btn2, btn3)
    if requestToBD.insert_user(user_id, number_group):
        bot.send_message(user_id, "Окей, я запомнил, твоя группа " + number_group + ".", reply_markup=markup)
    else:
        requestToBD.update_user(user_id, number_group)
        bot.send_message(user_id, "Окей, я изменил твою группу на " + number_group + ".", reply_markup=markup)


@bot.message_handler(content_types=['text'])
def func(message):
    if message.text == "Расписание на сегодня":
        date = datetime.strptime("2022-05-24", "%Y-%m-%d")
        ImageSchedule.scheduleImageday(requestToBD.get_schedule_one_day(message.chat.id, date), datetime.weekday(date))
        bot.send_photo(message.chat.id, open(r'red_page.png', 'rb'))
    if message.text == "Расписание на неделю":
        date = datetime.strptime("2022-05-24", "%Y-%m-%d")
        ImageSchedule.scheduleImageWeek(requestToBD.get_schedule_week(message.chat.id, date))
        bot.send_photo(message.chat.id, open(r'red_page.png', 'rb'))
    if message.text == "Изменить группу":
        set_group(message)

bot.infinity_polling()



# @server.route(f"/{BOT_TOKEN}", methods=["POST"])
# def rederict_message():
#     json_string = request.get_data().decode("utf-8")
#     update = telebot.types.Update.de_json(json_string)
#     bot.process_new_updates([update])
#     return "!", 200
#
#
#
# if __name__ == "__main__":
#     bot.remove_webhook()
#     bot.set_webhook(url=APP_URL)
#     server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
