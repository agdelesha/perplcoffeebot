import sqlite3
from datetime import datetime, timedelta
import os
from bot.config.config import DATABASE_FILE, BOT_DIR

USERS_FILE = os.path.join(BOT_DIR, 'resources', 'users.txt')

def init_db():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        bonuses INTEGER DEFAULT 0
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS admins (
        user_id INTEGER PRIMARY KEY,
        added_by INTEGER,
        added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS pending_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        request_type TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    conn.commit()
    conn.close()

def load_users():
    try:
        with open(USERS_FILE, 'r') as file:
            return set(file.read().splitlines())
    except FileNotFoundError:
        return set()

def save_user(user_id):
    with open(USERS_FILE, 'a') as file:
        file.write(f"{user_id}\n")

def get_user_bonuses(user_id):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT bonuses FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0

def update_user_bonuses(user_id, bonuses):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO users (user_id, bonuses) VALUES (?, ?)', (user_id, bonuses))
    conn.commit()
    conn.close()

def add_pending_request(user_id, request_type):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO pending_requests (user_id, request_type) VALUES (?, ?)', (user_id, request_type))
    conn.commit()
    conn.close()

def remove_pending_request(request_id):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM pending_requests WHERE id = ?', (request_id,))
    conn.commit()
    conn.close()

def clear_old_requests():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM pending_requests WHERE timestamp < ?', (datetime.now() - timedelta(days=1),))
    conn.commit()
    conn.close()

def is_admin(user_id: int) -> bool:
    """Проверяет, является ли пользователь админом"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM admins WHERE user_id = ?', (user_id,))
    result = cursor.fetchone() is not None
    conn.close()
    return result

def add_admin(user_id: int, added_by: int) -> bool:
    """Добавляет нового админа"""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO admins (user_id, added_by) VALUES (?, ?)', (user_id, added_by))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def remove_admin(user_id: int) -> bool:
    """Удаляет админа"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM admins WHERE user_id = ?', (user_id,))
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return success

def get_all_admins():
    """Возвращает список всех администраторов с их ID и именами пользователей"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT user_id FROM admins')
    admins = [{'id': row[0], 'username': get_username(row[0])} for row in cursor.fetchall()]
    conn.close()
    return admins

# Функция-заглушка для получения username по user_id
# В реальной реализации необходимо извлечь username из базы данных или API
# Здесь просто возвращаем строку для демонстрации

def get_username(user_id):
    return f'user_{user_id}'
