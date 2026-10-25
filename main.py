import asyncio
from aiogram import Bot, Dispatcher
from config import load_config


async def main():
    config = load_config()
    bot = Bot(token=config.tg.token)
    dp = Dispatcher()