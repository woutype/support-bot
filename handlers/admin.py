from aiogram import Router, F
from aiogram.types import CallbackQuery
import asyncpg
from database.db import close_spam_ticket, get_ticket
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from states import AdminState
from database.db import close_spam_ticket, get_ticket, update_ticket

admin_router = Router()


@admin_router.callback_query(F.data.startswith("close:"))
async def close_ticket_callback(callback: CallbackQuery, pool: asyncpg.Pool):

    ticket_id = int(callback.data.split(":")[1])

    ticket = await get_ticket(pool=pool, ticket_id=ticket_id)

    if not ticket:
        await callback.answer("Тикет не найден.")
        return

    await close_spam_ticket(pool=pool, ticket_id=ticket_id)

    await callback.message.edit_text(
        text=f"{callback.message.text}\n\n❌ <b>Обращение закрыто без ответа.</b>",
        parse_mode="HTML"
    )

    await callback.bot.send_message(
        chat_id=ticket['user_tg_id'],
        text=f"ℹ️ Ваше обращение <b>#{ticket_id}</b> было отклонено специалистом поддержки.",
        parse_mode="HTML"
    )

    await callback.answer("Тикет закрыт!")


@admin_router.callback_query(F.data.startswith("reply:"))
async def start_admin_reply(callback: CallbackQuery, state: FSMContext):

    ticket_id = int(callback.data.split(":")[1])

    await state.set_state(AdminState.waiting_for_reply)

    await state.update_data(ticket_id=ticket_id)

    await callback.message.reply(
        f"✍️ Введите ответ на обращение <b>#{ticket_id}</b>:\n"
        f"<i>(Клиент получит ваше сообщение от имени бота).</i>",
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
        await message.answer("Ошибка: обращение не найдено.")
        return

    await update_ticket(
        pool=pool,
        answer=message.text,
        admin_id=message.from_user.id,
        ticket_id=ticket_id,
    )

    client_text = (
        f"📩 <b>Получен ответ службы поддержки по обращению #{ticket_id}:</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"«{message.text}»\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"<i>Если у вас остались вопросы, вы можете создать новое обращение.</i>"
    )

    await message.bot.send_message(
        chat_id=ticket["user_tg_id"],
        text=client_text,
        parse_mode="HTML",
    )

    await message.answer(f"✅ Ответ успешно отправлен автору обращения #{ticket_id}!")

