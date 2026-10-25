from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
import asyncpg

from database.db import close_spam_ticket, get_ticket, update_ticket
from states import AdminState

admin_router = Router()


@admin_router.callback_query(F.data.startswith("close:"))
async def close_ticket_callback(callback: CallbackQuery, pool: asyncpg.Pool):

    ticket_id = int(callback.data.split(":")[1])

    ticket = await get_ticket(pool=pool, ticket_id=ticket_id)

    if not ticket:
        await callback.answer("⚠️ Ticket not found.")
        return

    await close_spam_ticket(pool=pool, ticket_id=ticket_id)

    await callback.message.edit_text(
        text=f"{callback.message.text}\n\n❌ <b>Ticket #{ticket_id} closed without reply.</b>",
        parse_mode="HTML"
    )

    await callback.bot.send_message(
        chat_id=ticket['user_tg_id'],
        text=f"ℹ️ Your support ticket <b>#{ticket_id}</b> has been closed by support.",
        parse_mode="HTML"
    )

    await callback.answer("Ticket closed!")


@admin_router.callback_query(F.data.startswith("reply:"))
async def start_admin_reply(callback: CallbackQuery, state: FSMContext):

    ticket_id = int(callback.data.split(":")[1])

    await state.set_state(AdminState.waiting_for_reply)

    await state.update_data(ticket_id=ticket_id)

    await callback.message.reply(
        f"✍️ <b>Enter your reply for ticket #{ticket_id}:</b>\n\n"
        f"<i>(The client will receive this message directly from the bot).</i>",
        parse_mode="HTML"
    )

    await callback.answer()


@admin_router.message(AdminState.waiting_for_reply)
async def process_admin_reply(message: Message, state: FSMContext, pool: asyncpg.Pool):

    data = await state.get_data()
    ticket_id = data["ticket_id"]
    await state.clear()

    ticket = await get_ticket(pool=pool, ticket_id=ticket_id)

    if not ticket:
        await message.answer("⚠️ Error: Ticket not found.")
        return

    await update_ticket(
        pool=pool,
        answer=message.text,
        admin_id=message.from_user.id,
        ticket_id=ticket_id,
    )

    client_text = (
        f"📩 <b>Support Response for Ticket #{ticket_id}:</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"«{message.text}»\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"<i>If you have any further questions, feel free to submit a new ticket!</i>"
    )

    await message.bot.send_message(
        chat_id=ticket["user_tg_id"],
        text=client_text,
        parse_mode="HTML",
    )

    await message.answer(f"✅ <b>Reply successfully sent to client for ticket #{ticket_id}!</b>", parse_mode="HTML")

