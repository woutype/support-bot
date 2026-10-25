import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import load_config

from handlers import routers


async def main():
    config = load_config()
    bot = Bot(token=config.tg.token)
    dp = Dispatcher()

    for router in routers:
        dp.include_router(router)

    logging.basicConfig(
        level=logging.INFO,
    )

    logging.info("🚀 Бот успешно запущен!")

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())