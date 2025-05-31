import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.bot import DefaultBotProperties
from config import BOT_TOKEN, WEBHOOK_URL, WEBHOOK_PATH, WEBAPP_HOST, WEBAPP_PORT
from handlers import booking, start, faq, menu, broadcast
from aiohttp import web


async def on_startup(bot: Bot):
    await bot.set_webhook(WEBHOOK_URL)
    print(f"✅ Webhook установлен: {WEBHOOK_URL}")


async def on_shutdown(bot: Bot):
    await bot.delete_webhook()
    await bot.session.close()
    print("🔻 Webhook удалён и сессия закрыта")


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

    app = web.Application()
    app['bot'] = bot
    app['dispatcher'] = dp

    # Регистрируем webhook путь
    app.router.add_post(WEBHOOK_PATH, handle_webhook)

    # Запускаем веб-сервер aiohttp
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, WEBAPP_HOST, WEBAPP_PORT)
    await site.start()

    # Устанавливаем webhook после запуска сервера (только после того, как публичный адрес доступен)
    await on_startup(bot)

    print(f"🚀 Webhook bot запущен на {WEBHOOK_URL}")

    try:
        while True:
            await asyncio.sleep(3600)
    finally:
        await on_shutdown(bot)


if __name__ == "__main__":
    asyncio.run(main())
