from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


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


def get_all_tickets(tickets_list: list) -> InlineKeyboardMarkup:

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"⚡ Ticket number: {item['id']}", callback_data=f"ticket:{item['id']}")]
                for item in tickets_list
        ]
    )

    return keyboard


def get_ticket_return() -> InlineKeyboardMarkup:

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Назад", callback_data='back_to_list')]
        ]
    )

    return keyboard