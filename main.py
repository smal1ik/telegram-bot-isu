import os
import telebot
import logging
import psycopg2
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
    global pointer_group

    id = message.from_user.id
    username = message.from_user.first_name
    pointer_group.update({id: 0})
    print(pointer_group)
    bot.send_message(message.chat.id, start_message)

    keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
    groups = requestToBD.get_group()
    for number in groups[0:5]:
        keyboard.add(telebot.types.InlineKeyboardButton(text=number[0], callback_data='group'+str(number)))
    keyboard.row(telebot.types.InlineKeyboardButton('👉', callback_data='right'))
    bot.send_message(id, text="Выберите группу:", reply_markup=keyboard)
    # bot.register_next_step_handler_by_chat_id(id, set_number_gruop)

    # cur.execute(f"SELECT telegram_id FROM telegram_user WHERE telegram_id = {id}")
    # result = cur.fetchone()

    # if not result:
    #     cur.execute("INSERT INTO telegram_user(telegram_id, name) VALUES (%s, %s)", (id, username))
    #     connection.commit()


def inline_number_group(user_id, messageid):
    global pointer_group
    pointer = pointer_group[user_id]
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
    groups = requestToBD.get_group()
    print(pointer_group)

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
    print(number_group)
    if requestToBD.insert_user(user_id, number_group):
        bot.send_message(user_id, "Окей, я запомнил, твоя группа " + number_group + ".")
    else:
        bot.send_message(user_id, "Ты уже есть в базе данных, но можешь изменить информацию о себе.")
    # if requestToBD.check_group(number_group):
    #     bot.send_message(message.from_user.id, "Окей, я запомнил, твоя группа " + number_group + ".")
    # else:
    #     bot.send_message(message.from_user.id, "Такой группы не существует. Попробуй снова.")
    #     bot.register_next_step_handler_by_chat_id(message.chat.id, set_number_gruop)


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
