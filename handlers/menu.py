from aiogram import Router, F
from aiogram.types import Message

router = Router()

services_text = (
    "📋 Наши услуги:\n"
    "1. Веб-разработка\n"
    "2. Создание телеграм-ботов\n"
    "3. IT-консультации\n"
    "4. Техническая поддержка\n"
    "📝 Чтобы оставить заявку, нажмите кнопку '📝 Оставить заявку'"
)

@router.message(F.text == "📋 Меню услуг")
async def send_services(message: Message):
    await message.answer(services_text)
