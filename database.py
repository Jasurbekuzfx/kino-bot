import sqlite3

def create_db():
    conn = sqlite3.connect('kino_bot.db')
    cursor = conn.cursor()
    # Kinolar jadvali
    cursor.execute('''CREATE TABLE IF NOT EXISTS movies 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, code TEXT UNIQUE, title TEXT, file_id TEXT)''')
    # Foydalanuvchilar jadvali (Statistika uchun)
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)''')
    conn.commit()
    conn.close()

def add_user(user_id):
    conn = sqlite3.connect('kino_bot.db')
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()

def add_movie(code, title, file_id):
    conn = sqlite3.connect('kino_bot.db')
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO movies (code, title, file_id) VALUES (?, ?, ?)", (code, title, file_id))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def get_movie(code):
    conn = sqlite3.connect('kino_bot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT title, file_id FROM movies WHERE code=?", (code,))
    res = cursor.fetchone()
    conn.close()
    return res

def count_users():
    conn = sqlite3.connect('kino_bot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    res = cursor.fetchone()[0]
    conn.close()
    return res
