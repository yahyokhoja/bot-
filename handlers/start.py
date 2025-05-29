from aiogram import Router, types
from aiogram.types import Message
from aiogram.filters import Command
from keyboards import main_menu
import sqlite3


router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Привет! Выберите действие:", reply_markup=main_menu)


@router.message(Command(commands=["users"]))
async def show_users(message: types.Message):
    conn = sqlite3.connect("db.sqlite3")
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, first_name FROM telegram_users")
    users = cursor.fetchall()
    conn.close()

    if not users:
        await message.answer("Пользователи не найдены.")
        return

    text = "Список пользователей:\n"
    for user_id, username, first_name in users:
        username_text = f"@{username}" if username else "(нет username)"
        text += f"ID: {user_id}, {username_text}, Имя: {first_name}\n"

    await message.answer(text)
