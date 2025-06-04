import os
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

# === Основные параметры бота ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN не задан! Убедитесь, что переменная окружения BOT_TOKEN установлена.")

# === Webhook-параметры ===
USE_WEBHOOK = os.getenv("USE_WEBHOOK", "false").lower() == "true"

WEBHOOK_HOST = os.getenv("WEBHOOK_HOST", "") if USE_WEBHOOK else ""
if USE_WEBHOOK and not WEBHOOK_HOST:
    raise ValueError("❌ WEBHOOK_HOST не задан при включённом USE_WEBHOOK!")

WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}" if USE_WEBHOOK else None

# === Локальный или серверный хост ===
WEBAPP_HOST = os.getenv("WEBAPP_HOST", "0.0.0.0")  # для запуска локально или на сервере
WEBAPP_PORT = int(os.getenv("PORT", 3000))         # для Heroku: PORT, локально: 3000

# === Параметры базы данных ===
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 5432))

# === Telegram ID админа (для уведомлений) ===
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))  # можно задать ID админа в .env
