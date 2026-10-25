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
        f"👋 Здравствуйте, <b>{message.from_user.full_name}</b>!\n\n"
        f"<blockquote>Добро пожаловать в службу поддержки <b>SupportDesk</b>.</blockquote>\n\n"
        f"<b>Чем я могу помочь?</b>\n"
        f"• Создать обращение к специалисту\n"
        f"• Посмотреть статус текущих заявок\n\n"
        f"<i>Нажмите кнопку ниже, чтобы начать диалог 👇</i>"
    )

    await message.answer(text, parse_mode="HTML", reply_markup=get_user_kb())


@user_router.message(F.text == "🎫 Создать обращение")
async def start_create_ticket(message: Message, state: FSMContext):

    await state.set_state(TicketState.waiting_for_text)

    text = (
        "📝 <b>Опишите вашу проблему подробно в одном сообщении.</b>\n\n"
        "Если нужно, укажите детали ситуации или код ошибки.\n"
        "Для отмены нажмите кнопку «❌ Отмена» ниже."
    )

    await message.answer(text, parse_mode="HTML", reply_markup=get_cancel_kb())


@user_router.message(F.text == "❌ Отмена")
async def cancel_ticket(message: Message, state: FSMContext):
    await state.clear()

    text = (
        "🚫 Создание обращения отменено. Вы вернулись в главное меню."
    )

    await message.answer(text, reply_markup=get_user_kb())


@user_router.message(TicketState.waiting_for_text)
async def process_ticket_text(message: Message, state: FSMContext, pool: asyncpg.Pool, config: Config):

    if len(message.text) <= 5:
        await message.answer("⚠️ Опишите проблему подробнее (хотя бы от 5 символов).")
        return

    await state.clear()

    ticket_id = await create_ticket(
        pool=pool,
        user_tg_id=message.from_user.id,
        issue_text=message.text
    )

    text = (
        f"✅ <b>Ваше обращение #{ticket_id} принято в обработку!</b>\n\n"
        f"<i>Текст:</i> {message.text}\n\n"
        f"Специалист поддержки скоро ответит вам прямо в этот чат."
    )

    await message.answer(text, parse_mode="HTML", reply_markup=get_user_kb())

    admin_text = (
        f"🔔 <b>Новое обращение #{ticket_id}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>От:</b> {message.from_user.full_name} (@{message.from_user.username or 'нет'})\n"
        f"🆔 <b>ID:</b> <code>{message.from_user.id}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📄 <b>Вопрос:</b>\n"
        f"«{message.text}»"
    )

    await message.bot.send_message(
        chat_id=config.tg.admin_id,
        text=admin_text,
        parse_mode="HTML",
        reply_markup=get_admin_ticket_kb(ticket_id),
    )


@user_router.message(F.text == '📋 Мои обращения')
async def get_user_tickets_by_id(message: Message, pool: asyncpg.Pool, config: Config):

    tickets_list = await get_user_tickets(user_tg_id=message.from_user.id, pool=pool)

    text = "📋 <b>Ваши последние обращения:</b>\n\n<i>Выберите тикет из списка ниже:</i>"

    if not tickets_list:
        await message.answer("ℹ️ У вас пока нет созданных обращений.")
        return

    await message.answer(
        text=text,
        parse_mode='HTML',
        reply_markup=get_all_tickets(tickets_list)
    )


@user_router.callback_query(F.data == "back_to_list")
async def back_to_tickets_list(callback: CallbackQuery, pool: asyncpg.Pool):

    tickets_list = await get_user_tickets(pool=pool, user_tg_id=callback.from_user.id)

    text = "📋 <b>Ваши последние обращения:</b>\n\n<i>Выберите тикет из списка ниже:</i>"

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
        await callback.answer("Тикет не найден.")
        return

    text = (
        f"📄 <b>Обращение #{ticket['id']}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📌 <b>Статус:</b> {ticket['status']}\n"
        f"❓ <b>Ваш вопрос:</b>\n«{ticket['issue_text']}»\n"
    )

    if ticket['admin_reply']:
        text += f"\n━━━━━━━━━━━━━━━━━━━━\n👨‍💻 <b>Ответ поддержки:</b>\n«{ticket['admin_reply']}»"

    await callback.message.edit_text(text=text, parse_mode="HTML", reply_markup=get_ticket_return())
    await callback.answer()