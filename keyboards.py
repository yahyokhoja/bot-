from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📋 Меню услуг")],
        [KeyboardButton(text="📝 Заказивайте")],
        [KeyboardButton(text="📢 Подписаться на рассылку")],
        [KeyboardButton(text="❓ Частые вопросы")]
    ],
    resize_keyboard=True
)
