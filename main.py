import os

from dotenv import load_dotenv
from db import DataBase
import sqlite3
import sys
sys.path.append('/home/kris/pyTelegramBotAPI/')
import telebot

load_dotenv()
token = os.getenv('TOKEN')
bot = telebot.TeleBot(token=token)
conn = sqlite3.connect('users.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    singup VARCHAR DEFAULT 'setusername'
)
''')
conn.commit()

db = DataBase('users.db')


@bot.message_handler(content_types=['text'])
def handle_message(message):
    user_id = message.from_user.id

    if not db.user_exists(user_id):
        db.add_user(user_id)
        bot.send_message(user_id, "Укажите Юзернейм:")
    elif db.get_signup(user_id) == "setusername":
        if len(message.text) > 15:
            bot.send_message(user_id, "Никнейм не должен превышать 15 символов")
        elif '@' in message.text or '/' in message.text:
            bot.send_message(user_id, "Вы ввели запрещённый символ")
        else:
            db.set_username(user_id, message.text)
            db.set_signup(user_id, "done")
            bot.send_message(user_id, "Регистрация завершена успешно")
    else:
        bot.send_message(user_id, "Вы уже зарегистрированы.")

bot.polling(none_stop=True, interval=0)
