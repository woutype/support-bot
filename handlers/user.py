from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import Message

from keyboards import get_user_kb, get_cancel_kb
from states import TicketState

user_router = Router()


@user_router.message(Command("start"))
async def start(message: Message):

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
async def process_ticket_text(message: Message, state: FSMContext):

    if len(message.text) <= 5:
        await message.answer("⚠️ Опишите проблему подробнее (хотя бы от 5 символов).")
        return

    await state.clear()

    text = (
        f"✅ <b>Ваше обращение принято в обработку!</b>\n\n"
        f"<i>Текст:</i> {message.text}\n\n"
        f"Специалист поддержки скоро ответит вам прямо в этот чат."
    )

    await message.answer(text, parse_mode="HTML", reply_markup=get_user_kb())