from aiogram.fsm.state import State, StatesGroup


class QAStates(StatesGroup):
    waiting_for_question = State()
