from aiogram.fsm.state import StatesGroup, State


class TicketState(StatesGroup):
    waiting_for_text = State()