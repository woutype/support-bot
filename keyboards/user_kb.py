from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


def get_user_kb() -> ReplyKeyboardMarkup:

     keyboard = ReplyKeyboardMarkup(
         keyboard=[
             [KeyboardButton(text="🎫 Create Ticket")],
             [KeyboardButton(text="📋 My Tickets")],
         ],
         resize_keyboard=True
     )

     return keyboard


def get_cancel_kb() -> ReplyKeyboardMarkup:

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="❌ Cancel")],
        ],
        resize_keyboard=True
    )

    return keyboard


def get_all_tickets(tickets_list: list) -> InlineKeyboardMarkup:

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"🎫 Ticket #{item['id']} [{item['status']}]", callback_data=f"ticket:{item['id']}")]
                for item in tickets_list
        ]
    )

    return keyboard


def get_ticket_return() -> InlineKeyboardMarkup:

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Back to List", callback_data='back_to_list')]
        ]
    )

    return keyboard