import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import load_config

from database.db import create_pool, init_db
from handlers import routers
from aiogram.types import BotCommand


async def main():

    config = load_config()
    bot = Bot(token=config.tg.token)
    dp = Dispatcher()

    pool = await create_pool(config.sql)
    await init_db(pool)

    for router in routers:
        dp.include_router(router)

    logging.basicConfig(
        level=logging.INFO,
    )

    logging.info("🚀 Bot started successfully!")

    commands = [
        BotCommand(command='start', description="Restart bot / Main menu")
    ]
    await bot.set_my_commands(commands)

    await dp.start_polling(bot, pool=pool, config=config)


if __name__ == '__main__':
    asyncio.run(main())