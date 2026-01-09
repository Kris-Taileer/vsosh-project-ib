import time
from datetime import datetime
import subprocess
import socket
import os
import json
from dotenv import load_dotenv
import sqlite3
import sys
sys.path.append('/home/kris/pyTelegramBotAPI/')
import telebot
import json_db
import threading

load_dotenv()
token = os.getenv('TOKEN')
bot = telebot.TeleBot(token)
HOSTS_FILE = 'hosts_data.json'

def init_data_file():
    if not os.path.exists(HOSTS_FILE):
        with open(HOSTS_FILE, 'w', encoding='utf-8') as f:
            json.dump({}, f)

def load_user_hosts(user_id):
    init_data_file()
    try:
        with open(HOSTS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get(str(user_id), [])
    except:
        return []

def save_user_hosts(user_id, hosts):
    init_data_file()
    with open(HOSTS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    data[str(user_id)] = hosts
    with open(HOSTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_all_hosts():
    init_data_file()
    try:
        with open(HOSTS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        all_hosts = []
        for user_id_str, hosts in data.items():
            for host_info in hosts:
                all_hosts.append({'user_id': int(user_id_str), 'host': host_info['host'], 'interval': host_info.get('interval', 60), 'last_check': host_info.get('last_check')})
        return all_hosts
    except:
        return []

def ping_host_simple(host):
    try:
        param = '-n' if subprocess.os.name == 'nt' else '-c'
        command = ['ping', param, '2', host]
        result = subprocess.run(command, capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except:
        return False

def check_host_and_notify(host_info):
    try:
        user_id = host_info['user_id']
        host = host_info['host']
        is_available = ping_host_simple(host)
        status = " :) ДОСТУПЕН" if is_available else " :( НЕДОСТУПЕН"
        message = (
            f" *Автоматическая проверка*\n\n"
            f" Хост: `{host}`\n"
            f" Статус: {status}\n"
            f" Время: {datetime.now().strftime('%H:%M:%S')}"
        )

        bot.send_message(user_id, message, parse_mode='Markdown')
        update_last_check(user_id, host)
        print(f" Проверен {host} для пользователя {user_id}")



    except Exception as e:
        print(f" Ошибка при проверке {host_info.get('host')}: {str(e)}")

def update_last_check(user_id, host):
    hosts = load_user_hosts(user_id)

    for h in hosts:
        if h['host'] == host:
            h['last_check'] = datetime.now().isoformat()
            break

    save_user_hosts(user_id, hosts)

def scheduler_loop():
    print("!!! Планировщик запущен")

    while True:
        try:
            all_hosts = get_all_hosts()
            for host_info in all_hosts:
                user_id = host_info['user_id']
                host = host_info['host']
                interval = host_info['interval']
                last_check = host_info.get('last_check')

                should_check = False

                if last_check:
                    last_time = datetime.fromisoformat(last_check)
                    seconds_passed = (datetime.now() -last_time).total_seconds()
                    if seconds_passed >= interval:
                        should_check = True
                else:
                    should_check = True
                if should_check:  #starting in another thread!!! assíncrona!!!
                    thread = threading.Thread(target=check_host_and_notify, args=(host_info,),daemon=True)
                    thread.start()
            time.sleep(10)

        except Exception as e:
            print(f" Ошибка в планировщике: {str(e)}")
            time.sleep(30)

def start_scheduler():
    thread = threading.Thread(target=scheduler_loop, daemon=True)
    thread.start()
    print(" :D Планировщик запущен")

@bot.message_handler(commands=['start'])
def send_welcome(message):

    welcome_text = (
        "Привет! Я бот для мониторинга хостов.\n\n"
        "Я могу автоматически проверять доступность ваших серверов "
        "и отправлять вам уведомления.\n\n"
        " Используйте /help для списка команд"
    )
    bot.send_message(message.chat.id, welcome_text)

@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = (
        " >>*Основные команды:*\n\n"
        "`/start` - Начать работу с ботом\n"
        "`/help` - Справка по командам\n\n"
        " >>*Управление хостами:*\n"
        "`/pingadd <хост> <интервал>` - Добавить хост в мониторинг\n"
        "`/pingdelete <хост>` - Удалить хост\n"
        "`/pinglist` - Список ваших хостов\n\n"
        " >>*Проверка вручную:*\n"
        "`/pinghost <хост>` - Проверить хост сейчас\n\n"
        " >>*Настройки:*\n"
        "`/pinginterval <хост> <секунды>` - Изменить интервал\n"
        "`/pingstatus` - Статус мониторинга\n\n"
        " *Примеры:*\n"
        "`/pingadd google.com 60` - проверять каждую минуту\n"
        "`/pingdelete myserver.com` - удалить из мониторинга\n"
        "`/pinglist` - показать все хосты"
    )
    bot.send_message(message.chat.id, help_text, parse_mode='Markdown')

@bot.message_handler(commands=['pinghost'])
def ping_host(message):
    command_parts = message.text.split()

    if len(command_parts) < 2:
        bot.send_message(message.chat.id, "Пожалуйста, укажите хост для проверки.\n" "Пример: /pinghost google.com")
        return

    host = command_parts[1]
    try:
        status_msg = bot.send_message(message.chat.id, f"проверяю хост: {host}")
        try:
            param = '-n' if subprocess.os.name == 'nt' else '-c'
            command = ['ping', param, '4', host]

            result = subprocess.run(command, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                response = f" :) Хост {host} доступен!\n\n Результат:\n{result.stdout}"
            else:
                response = f" :( Хост {host} не доступен\n\n Вывод:\n{result.stdout}"

        except subprocess.TimeoutExpired:
            response = f" :\ Таймаут при проверке хоста {host}"
        bot.edit_message_text(response, message.chat.id, status_msg.message_id)

    except Exception as e:
        error_response = f" Произошла ошибка при проверке хоста {host}\nошибка: {str(e)}"
        bot.send_message(message.chat.id, error_response)



@bot.message_handler(commands=['pingadd'])
def add_host_command(message):
    try:
        parts = message.text.split()
        if len(parts) < 3:
            bot.send_message(message.chat.id, "> Используйте: `/pingadd <хост> <интервал>`\n" "Пример: `/pingadd google.com 60`\n\n" "Интервал в секундах (минимум 10)", parse_mode='Markdown')
            return

        host = parts[1]
        try:
            interval = int(parts[2])
            if interval < 10:
                bot.send_message(message.chat.id, ">:( Интервал не может быть меньше 10 секунд")
                return
        except ValueError:
            bot.send_message(message.chat.id, ">:( Интервал должен быть числом")
            return

        user_id = message.from_user.id
        hosts = load_user_hosts(user_id)
        for h in hosts:
            if h['host'] == host:
                bot.send_message(message.chat.id, f" >Хост `{host}` уже есть в вашем списке", parse_mode='Markdown')
                return

        hosts.append({'host': host, 'interval': interval, 'last_check': None})
        save_user_hosts(user_id, hosts)

        response = (
            f" > *Хост добавлен*\n\n"
            f" Хост: `{host}`\n"
            f" Интервал: {interval} секунд\n"
            f" Пользователь: {message.from_user.first_name}\n\n"
            f" Бот будет проверять этот хост каждые {interval} секунд\n"
            f"и отправлять вам уведомления."
        )
        bot.send_message(message.chat.id, response, parse_mode='Markdown')

    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {str(e)}")

@bot.message_handler(commands=['pingdelete'])
def delete_host_command(message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.send_message(message.chat.id, " > Используйте: `/pingdelete <хост>`\n" "Пример: `/pingdelete google.com`", parse_mode='Markdown')
            return

        host = parts[1]
        user_id = message.from_user.id
        hosts = load_user_hosts(user_id)
        new_hosts = [h for h in hosts if h['host'] != host]

        if len(new_hosts) == len(hosts):
            bot.send_message(message.chat.id,
                           f" >Хост `{host}` не найден в вашем списке", parse_mode='Markdown')
            return

        save_user_hosts(user_id, new_hosts)
        bot.send_message(message.chat.id,
                       f" >Хост `{host}` удален из мониторинга", parse_mode='Markdown')

    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {str(e)}")

@bot.message_handler(commands=['pinglist'])
def list_hosts_command(message):
    try:
        user_id = message.from_user.id
        hosts = load_user_hosts(user_id)

        if not hosts:
            bot.send_message(message.chat.id, "📭 *Список пуст*\n\n" "Добавьте хосты командой:\n" "`/pingadd <хост> <интервал>`", parse_mode='Markdown')
            return
        response = f"*Ваши хосты ({len(hosts)}):*\n\n"

        for i, host_info in enumerate(hosts, 1):
            host = host_info['host']
            interval = host_info['interval']
            last_check = host_info.get('last_check')

            if last_check:
                last_time = datetime.fromisoformat(last_check)
                time_ago = int((datetime.now() - last_time).total_seconds())
                last_info = f" {time_ago} сек назад"
            else:
                last_info = " Ещё не проверялся"
            response += f"{i}. `{host}`\n"
            response += f"   Каждые {interval} сек | {last_info}\n\n"
        bot.send_message(message.chat.id, response, parse_mode='Markdown')

    except Exception as e:
        bot.send_message(message.chat.id, f"ошибка: {str(e)}")

@bot.message_handler(func=lambda message: True)
def handle_other_messages(message):
    bot.send_message(message.chat.id,"Я не понимаю эту команду (я немного глупый)\n\n" "Используйте `/help` для списка команд\n\n", parse_mode='Markdown')

if __name__ == '__main__':
    print("=" * 50)
    print("<<< БОТ ДЛЯ МОНИТОРИНГА ХОСТОВ >>>")
    print("=" * 50)

    start_scheduler()

    print("Планировщик запущен")
    print("Бот запущен. Ожидание команд бубубу...")
    print("=" * 50)

    try:
        bot.polling(none_stop=True)
    except KeyboardInterrupt:
        print("\nБот остановлен пользователем")
    except Exception as e:
        print(f"\nОшибка: {str(e)}")
