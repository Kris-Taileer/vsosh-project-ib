import sqlite3

class DataBase:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()

    def add_user(self, user_id):
        with self.connection:
            self.cursor.execute("INSERT INTO 'users' ('user_id') VALUE (?)", (user_id,))

    def user_exists(self, user_id):
        with self.connection:
            result =  self.cursor.execute("SELECT * FROM 'users' WHERE 'user_id' = ?", (user_id,)).fetchall()
            return bool(len(result))

    def set_username(self, user_id, username):
        with self.connection:
            return self.cursor.execute("UPDATE 'users' SET 'username' = ? WHERE 'user_id' = ?", (username, user_id,))

    def get_signup(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT 'signup' FROM 'users' WHERE 'user_id' = ?", (user_id,)).fetchall()
