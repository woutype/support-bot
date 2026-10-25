from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
import asyncpg

from keyboards import (
    get_user_kb,
    get_cancel_kb,
    get_admin_ticket_kb,
    get_all_tickets,
    get_ticket_return,
)
from states import TicketState
from database.db import (
    add_user,
    create_ticket,
    get_user_tickets,
    get_ticket,
)
from config import Config

user_router = Router()


@user_router.message(Command("start"))
async def start(message: Message, pool: asyncpg.Pool):

    await add_user(
        pool=pool,
        tg_id=message.from_user.id,
        username=message.from_user.username,
        full_name=message.from_user.full_name,
    )

    text = (
        f"👋 Hello, <b>{message.from_user.full_name}</b>!\n\n"
        f"<blockquote>Welcome to <b>SupportDesk Help Center</b> 🚀</blockquote>\n\n"
        f"<b>How can we assist you today?</b>\n"
        f"• 🎫 Submit an issue to our support team\n"
        f"• 📋 Track the status of your existing tickets\n\n"
        f"<i>Please choose an option below to begin 👇</i>"
    )

    await message.answer(text, parse_mode="HTML", reply_markup=get_user_kb())


@user_router.message(F.text == "🎫 Create Ticket")
async def start_create_ticket(message: Message, state: FSMContext):

    await state.set_state(TicketState.waiting_for_text)

    text = (
        "📝 <b>Please describe your issue in detail in a single message.</b>\n\n"
        "💡 <i>Tip: Include error codes, account details, or screenshots if applicable.</i>\n\n"
        "Press <b>«❌ Cancel»</b> below at any time to return."
    )

    await message.answer(text, parse_mode="HTML", reply_markup=get_cancel_kb())


@user_router.message(F.text == "❌ Cancel")
async def cancel_ticket(message: Message, state: FSMContext):
    await state.clear()

    text = (
        "🚫 <b>Ticket creation cancelled.</b>\n<i>You have returned to the main menu.</i>"
    )

    await message.answer(text, parse_mode="HTML", reply_markup=get_user_kb())


@user_router.message(TicketState.waiting_for_text)
async def process_ticket_text(message: Message, state: FSMContext, pool: asyncpg.Pool, config: Config):

    if len(message.text) <= 5:
        await message.answer("⚠️ <b>Please describe your issue in more detail</b> (at least 6 characters).", parse_mode="HTML")
        return

    await state.clear()

    ticket_id = await create_ticket(
        pool=pool,
        user_tg_id=message.from_user.id,
        issue_text=message.text
    )

    text = (
        f"✅ <b>Ticket #{ticket_id} successfully created!</b>\n\n"
        f"📄 <b>Your issue:</b>\n<i>«{message.text}»</i>\n\n"
        f"👨‍💻 <i>Our support specialists have been notified and will reply directly in this chat shortly.</i>"
    )

    await message.answer(text, parse_mode="HTML", reply_markup=get_user_kb())

    admin_text = (
        f"🔔 <b>NEW SUPPORT TICKET #{ticket_id}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>From:</b> {message.from_user.full_name} (@{message.from_user.username or 'none'})\n"
        f"🆔 <b>User ID:</b> <code>{message.from_user.id}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📄 <b>Issue Description:</b>\n"
        f"«{message.text}»"
    )

    await message.bot.send_message(
        chat_id=config.tg.admin_id,
        text=admin_text,
        parse_mode="HTML",
        reply_markup=get_admin_ticket_kb(ticket_id),
    )


@user_router.message(F.text == '📋 My Tickets')
async def get_user_tickets_by_id(message: Message, pool: asyncpg.Pool, config: Config):

    tickets_list = await get_user_tickets(user_tg_id=message.from_user.id, pool=pool)

    text = "📋 <b>Your Recent Support Tickets:</b>\n\n<i>Tap any ticket below to view full details and responses:</i>"

    if not tickets_list:
        await message.answer("ℹ️ <b>You don't have any support tickets yet.</b>\n<i>Click «🎫 Create Ticket» to submit one!</i>", parse_mode="HTML")
        return

    await message.answer(
        text=text,
        parse_mode='HTML',
        reply_markup=get_all_tickets(tickets_list)
    )


@user_router.callback_query(F.data == "back_to_list")
async def back_to_tickets_list(callback: CallbackQuery, pool: asyncpg.Pool):

    tickets_list = await get_user_tickets(pool=pool, user_tg_id=callback.from_user.id)

    text = "📋 <b>Your Recent Support Tickets:</b>\n\n<i>Tap any ticket below to view full details and responses:</i>"

    await callback.message.edit_text(
        text=text,
        parse_mode="HTML",
        reply_markup=get_all_tickets(tickets_list),
    )

    await callback.answer()


@user_router.callback_query(F.data.startswith("ticket:"))
async def show_ticket_details(callback: CallbackQuery, pool: asyncpg.Pool):

    ticket_id = int(callback.data.split(":")[1])
    ticket = await get_ticket(pool=pool, ticket_id=ticket_id)

    if not ticket:
        await callback.answer("⚠️ Ticket not found.")
        return

    status_badge = "🟢 ANSWERED" if ticket['status'] == "ANSWERED" else ("🔴 CLOSED" if ticket['status'] == "CLOSED" else "🟡 OPEN")

    text = (
        f"📄 <b>Support Ticket #{ticket['id']}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📌 <b>Status:</b> <code>{status_badge}</code>\n"
        f"❓ <b>Your Inquiry:</b>\n«{ticket['issue_text']}»\n"
    )

    if ticket['admin_reply']:
        text += f"\n━━━━━━━━━━━━━━━━━━━━\n👨‍💻 <b>Support Reply:</b>\n«{ticket['admin_reply']}»"

    await callback.message.edit_text(text=text, parse_mode="HTML", reply_markup=get_ticket_return())
    await callback.answer()