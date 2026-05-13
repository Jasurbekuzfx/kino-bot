import sqlite3

class Database:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()
        self.create_table()

    def create_table(self):
        with self.connection:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY
                )
            """)

    def add_user(self, user_id):
        with self.connection:
            self.cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))

    # Bu yerga kinolarni qidirish funksiyalarini qo'shishingiz mumkin
