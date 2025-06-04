import os
import psycopg2
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    return psycopg2.connect(DATABASE_URL)

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        telegram_id BIGINT UNIQUE NOT NULL,
        username TEXT NOT NULL,
        registration_date TIMESTAMP NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bot_settings (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL
    );
    """)

    # Вставляем начальную запись, если её нет
    cursor.execute("""
    INSERT INTO bot_settings (name)
    SELECT 'FoodBot'
    WHERE NOT EXISTS (SELECT 1 FROM bot_settings WHERE id = 1);
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id SERIAL PRIMARY KEY,
        user_id BIGINT NOT NULL REFERENCES users(id),
        item_name TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        status TEXT DEFAULT 'new',
        created_at TIMESTAMP NOT NULL
    );
    """)

    conn.commit()
    cursor.close()
    conn.close()

def save_user(user):
    """
    Сохраняет пользователя в базу, если его там нет.
    user - объект с атрибутами id и username
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE telegram_id = %s", (user.id,))
    if cursor.fetchone() is None:
        registration_date = datetime.now()
        cursor.execute(
            "INSERT INTO users (telegram_id, username, registration_date) VALUES (%s, %s, %s)",
            (user.id, user.username or "", registration_date)
        )
        conn.commit()
    cursor.close()
    conn.close()

def save_order(telegram_id, item_name, quantity):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE telegram_id = %s", (telegram_id,))
    user = cursor.fetchone()
    if user is None:
        cursor.close()
        conn.close()
        raise ValueError("Пользователь не найден в базе")

    user_id = user[0]
    created_at = datetime.now()

    cursor.execute("""
        INSERT INTO orders (user_id, item_name, quantity, created_at)
        VALUES (%s, %s, %s, %s)
    """, (user_id, item_name, quantity, created_at))

    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    create_tables()
    print("Таблицы созданы успешно!")
