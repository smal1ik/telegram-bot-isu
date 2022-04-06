import os
import telebot
import logging
import psycopg2
from config import *
from flask import Flask, request

bot = telebot.TeleBot(BOT_TOKEN)
server = Flask(__name__)
logger = telebot.logger
logger.setLevel(logging.DEBUG)

connection = psycopg2.connect(DB_URI, sslmode="require")
cur = connection.cursor()

@bot.message_handler(commands=["start"])
def start(message):
    id = message.from_user.id
    username = message.from_user.first_name
    bot.reply_to(message, f"Hello, {username}")

    cur.execute(f"SELECT telegram_id FROM telegram_user WHERE telegram_id = {id}")
    result = cur.fetchone()

    if not result:
        cur.execute("INSERT INTO telegram_user(telegram_id, username) VALUES (%s, %s)", (id, username))
        connection.commit()
        connection.close()


@server.route(f"/{BOT_TOKEN}", methods=["POST"])
def rederict_message():
    json_string = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200


if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=APP_URL)
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))