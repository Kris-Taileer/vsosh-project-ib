import os
from dotenv import load_dotenv
import pyTelegramBotAPI/telebot
import sqlite3


load_dotenv()

conn = sqlite3.connect('users.db', check_same_thread=False)
cursor = conn.cursor()


cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash BLOB
    singup VARCHAR
)
''')
conn.commit()



application.run_polling()