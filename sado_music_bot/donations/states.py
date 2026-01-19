"""
FSM States for donation flow
"""
from aiogram.fsm.state import State, StatesGroup


class DonationNote(StatesGroup):
    waiting_note = State()

