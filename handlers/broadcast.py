from aiogram import Router, F
from aiogram.types import Message

router = Router()

# Для примера - хранить подписчиков в памяти (для боевого бота лучше использовать БД)
subscribers = set()

@router.message(F.text == "📢 Подписаться на рассылку")
async def subscribe(message: Message):
    user_id = message.from_user.id
    if user_id in subscribers:
        await message.answer("Вы уже подписаны на рассылку!")
    else:
        subscribers.add(user_id)
        await message.answer("Вы успешно подписались на рассылку! 🎉")

# Команда для отправки рассылки (например, админ может отправить это вручную)
# В реальном проекте нужно защитить этот метод, чтобы рассылку мог делать только админ
async def broadcast_message(bot, text: str):
    for user_id in subscribers:
        try:
            await bot.send_message(user_id, text)
        except Exception as e:
            print(f"Ошибка при отправке пользователю {user_id}: {e}")
