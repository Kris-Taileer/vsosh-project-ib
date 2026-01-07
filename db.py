import sqlite3

class DataBase:
    def __init__(self, db_file):
        self.db_file = db_file

    def connect(self):
        return sqlite3.connect(self.db_file)

def add_user(self, user_id):
    try:
        if self.user_exists(user_id):
            print(f"Пользователь с id {user_id} уже существует.")
            return
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
            print(f"Пользователь с id {user_id} добавлен.")
    except sqlite3.Error as e:
        print(f"Ошибка добавления пользователя: {e}")

    def user_exists(self, user_id):
        try:
            with self.connect() as conn:
                cursor = conn.cursor()
                result =  cursor.execute("SELECT * FROM 'users' WHERE 'user_id' = ?", (user_id,)).fetchall()
                return bool(len(result))
        except sqlite3.Error as e:
            print(f"Ошибка проверки существования пользователя: {e}")

    def set_username(self, user_id, username):
        try:
            with self.connect() as conn:
                cursor = conn.cursor()
                return cursor.execute("UPDATE 'users' SET 'username' = ? WHERE 'user_id' = ?", (username, user_id,))
        except sqlite3.Error as e:
            print(f"Ошибка изменения имени пользователя: {e}")

    def get_signup(self, user_id):
        try:
            with self.connect() as conn:
                cursor = conn.cursor()
                result = cursor.execute("SELECT 'signup' FROM 'users' WHERE 'user_id' = ?", (user_id,)).fetchone()
                return result[0] if result else None
        except sqlite3.Error as e:
            print(f"Ошибка получения статуса регистрации: {e}")

    def set_signup(self, user_id, signup):
        try:
            with self.connect() as conn:
                cursor = conn.cursor()
                return cursor.execute("UPDATE 'users' SET 'signup' = ? WHERE 'user_id' = ?", (signup, user_id,))
        except sqlite3.Error as e:
            print(f"Ошибка изменения статуса регистрации: {e}")

