from datetime import datetime
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DATABASE_URL")

def save_order(telegram_id, item_name, quantity):
    try:
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()

        # Найти пользователя
        cursor.execute("SELECT id FROM users WHERE telegram_id = %s", (telegram_id,))
        user = cursor.fetchone()
        if user is None:
            print(f"Пользователь с telegram_id={telegram_id} не найден")
            conn.close()
            return False

        user_id = user[0]
        created_at = datetime.now()

        # Сохранить заказ
        cursor.execute("""
            INSERT INTO orders (user_id, item_name, quantity, created_at)
            VALUES (%s, %s, %s, %s)
        """, (user_id, item_name, quantity, created_at))

        conn.commit()
        conn.close()
        print(f"✅ Заказ сохранён: user_id={user_id}, item={item_name}, quantity={quantity}")
        return True

    except Exception as e:
        print(f"❌ Ошибка при сохранении заказа: {e}")
        return False
