from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_admin_ticket_kb(ticket_id: int) -> InlineKeyboardMarkup:

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✍️ Reply", callback_data=f"reply:{ticket_id}"),
                InlineKeyboardButton(text="❌ Close Ticket", callback_data=f"close:{ticket_id}")
            ],
        ]
    )

    return keyboard