from aiogram.fsm.state import StatesGroup, State

class ContactState(StatesGroup):
    waiting_message = State()
