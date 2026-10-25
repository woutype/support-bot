from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message


user_router = Router()


@user_router.message(Command("start"))
async def start(message: Message):

    text = (
        f"👋 Здравствуйте, <b>{message.from_user.full_name}</b>!\n\n"
        f"Добро пожаловать в службу технической поддержки.\n"
        f"Здесь вы можете задать вопрос специалистам или сообщить о проблеме."
    )

    await message.answer(text, parse_mode="HTML")