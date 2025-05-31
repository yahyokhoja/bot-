import os
from dotenv import load_dotenv  # <== ЭТО НУЖНО!

load_dotenv()


BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN не задан! Убедитесь, что переменная окружения BOT_TOKEN установлена.")

WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")
if not WEBHOOK_HOST:
    raise ValueError("❌ WEBHOOK_HOST не задан! Установите переменную окружения с адресом вашего сервера, например https://yourdomain.com")

WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

WEBAPP_HOST = "0.0.0.0"  # слушать на всех интерфейсах
WEBAPP_PORT = int(os.getenv("PORT", 3000))  # порт для сервера, Render задаёт через PORT
