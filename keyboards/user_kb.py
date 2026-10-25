from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_user_kb() -> ReplyKeyboardMarkup:

     keyboard = ReplyKeyboardMarkup(
         keyboard=[
             [KeyboardButton(text="🎫 Создать обращение")],
             [KeyboardButton(text="📋 Мои обращения")],
         ],
         resize_keyboard=True
     )

     return keyboard


def get_cancel_kb() -> ReplyKeyboardMarkup:

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="❌ Отмена")],
        ],
        resize_keyboard=True
    )

    return keyboard