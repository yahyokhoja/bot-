import sqlite3
from datetime import datetime

def create_tables():
    # Подключаемся к базе данных (если файла нет, он будет создан)
    conn = sqlite3.connect("db.sqlite3")
    cursor = conn.cursor()

    # Создаем таблицу для пользователей
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER UNIQUE NOT NULL,
        username TEXT NOT NULL,
        registration_date TEXT NOT NULL
    );
    """)

    # Создаем таблицу для настроек бота
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bot_settings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    );
    """)

    # Добавляем начальную запись в таблицу настроек (имя бота)
    cursor.execute("""
    INSERT OR IGNORE INTO bot_settings (name) VALUES ('FoodBot');
    """)

    conn.commit()
    conn.close()

def save_user(user):
    """
    Сохраняет пользователя в базу, если его там ещё нет.
    user - объект from_user из aiogram.
    """
    conn = sqlite3.connect("db.sqlite3")
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE telegram_id = ?", (user.id,))
    if cursor.fetchone() is None:
        registration_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO users (telegram_id, username, registration_date) VALUES (?, ?, ?)",
            (user.id, user.username or "", registration_date)
        )
        conn.commit()
    conn.close()

if __name__ == "__main__":
    create_tables()
    print("Таблицы созданы успешно!")
