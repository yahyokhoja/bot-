import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN, WEBHOOK_URL, WEBHOOK_PATH, WEBAPP_HOST, WEBAPP_PORT
from handlers import booking, start, faq, menu, broadcast
from aiohttp import web


async def on_startup(dispatcher: Dispatcher):
    # Установка webhook
    await dispatcher.bot.set_webhook(WEBHOOK_URL)


async def on_shutdown(dispatcher: Dispatcher):
    # Снятие webhook при остановке
    await dispatcher.bot.delete_webhook()
    await dispatcher.bot.session.close()


async def handle_webhook(request: web.Request):
    dispatcher = request.app['dispatcher']
    data = await request.json()
    update = types.Update(**data)  # Импорт types из aiogram!
    await dispatcher.process_update(update)
    return web.Response(text='OK')


async def main():
    bot = Bot(token=BOT_TOKEN)
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

    # Добавляем маршрут для webhook
    app.router.add_post(WEBHOOK_PATH, handle_webhook)

    await on_startup(dp)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, WEBAPP_HOST, WEBAPP_PORT)
    await site.start()

    print(f"Webhook bot started at {WEBHOOK_URL}")

    try:
        # Запускаем бесконечный цикл ожидания
        while True:
            await asyncio.sleep(3600)
    finally:
        await on_shutdown(dp)


if __name__ == "__main__":
    asyncio.run(main())
