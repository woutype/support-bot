from aiogram.fsm.state import StatesGroup, State


class TicketState(StatesGroup):
    waiting_for_text = State()


class AdminState(StatesGroup):
    waiting_for_reply = State()