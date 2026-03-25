import asyncio
import logging

from aiogram import Bot, Dispatcher

from config import API_TOKEN
from handlers import schedule, moderation, auth, admin
from middlewares.subscription import SubscriptionCheckMiddleware
from db import init_db  # <-- добавили

logging.basicConfig(level=logging.INFO)


async def main():
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher()

    # инициализация базы (создаст таблицу users, если её ещё нет)
    await init_db()

    # подключаем роутеры
    dp.include_router(auth.router)
    dp.include_router(schedule.router)
    dp.include_router(moderation.router)
    dp.include_router(admin.router)

    # мидлварь проверки подписки каждые 3 сообщения
    dp.message.middleware(SubscriptionCheckMiddleware())

    logging.info("Старт polling")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
