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
    singups VARCHAR DEFAULT setusername
)
''')
conn.commit()

db = DataBase('users.db')


@bot.message_handler(content_types=['text'])
def start(message):
    if (not db.user_exists(message.from_user.id)):
        db.add_user(message.from_user.id)
        bot.send_message(message.from_user.id, "Укажите Юзернейм:")
    else:
        bot.send_message(message.from_user.id, "Вы уже зарегестрированы") #reply markup needed


@bot.message_handler(content_types=['text'])
def bot_message(message):
    if db.get_signup(message.from_user.id) == "setusername":
        if (len(message.text) > 15):
            bot.send_message(message.from_user.id, "Никнейм не должен привышать 15 символов")
        elif '@' in message.text or '/' in message.text:
            bot.send_message(message.from_user.id, "Вы ввели запрещённый символ")
        else:
            db.set_username(message.from_user.id, message.text)
            db.set_signup(message.from_user.id, "done")
            bot.send_message(message.from_user.id, "Регистрация завершена успешно")
    else:
        bot.send_message(message.from_user.id, "Что?")

bot.polling(none_stop=True, interval=0)
