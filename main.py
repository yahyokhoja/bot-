import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.bot import DefaultBotProperties
from aiohttp import web

from config import (
    BOT_TOKEN,
    USE_WEBHOOK,
    WEBHOOK_URL,
    WEBHOOK_PATH,
    WEBAPP_HOST,
    WEBAPP_PORT
)

from handlers import booking, start, faq, menu, broadcast

import logging

# Логирование
logging.basicConfig(
    level=logging.INFO,
    filename='log.txt',
    filemode='a',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)



async def on_startup(bot: Bot):
    if USE_WEBHOOK:
        await bot.set_webhook(WEBHOOK_URL)
        print(f"✅ Webhook установлен: {WEBHOOK_URL}")


async def on_shutdown(bot: Bot):
    if USE_WEBHOOK:
        await bot.delete_webhook()
        print("🔻 Webhook удалён")
    await bot.session.close()
    print("🔻 Сессия закрыта")


async def handle_webhook(request: web.Request):
    app = request.app
    dispatcher = app['dispatcher']
    data = await request.json()
    update = types.Update(**data)
    await dispatcher.feed_update(bot=app['bot'], update=update)
    return web.Response(text='OK')


async def main():
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode="HTML")
    )
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Подключаем роутеры
    dp.include_router(start.router)
    dp.include_router(booking.router)
    dp.include_router(menu.router)
    dp.include_router(faq.router)
    dp.include_router(broadcast.router)

    if USE_WEBHOOK:
        # Webhook-режим (используется на деплое)
        app = web.Application()
        app['bot'] = bot
        app['dispatcher'] = dp

        # Регистрируем webhook путь
        app.router.add_post(WEBHOOK_PATH, handle_webhook)

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, WEBAPP_HOST, WEBAPP_PORT)
        await site.start()

        await on_startup(bot)
        print(f"🚀 Webhook bot запущен на {WEBHOOK_URL}")

        try:
            while True:
                await asyncio.sleep(3600)
        finally:
            await on_shutdown(bot)

    else:
        # Polling-режим (локальная разработка)
        print("🚀 Бот запущен в режиме polling (локальная разработка)")
        await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
