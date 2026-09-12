from aiogram.fsm.state import State, StatesGroup


class TopupStates(StatesGroup):
    waiting_amount = State()
    waiting_receipt = State()
    waiting_stars_amount = State()


class GiftStates(StatesGroup):
    waiting_username = State()


class NakrutkaStates(StatesGroup):
    waiting_link = State()
    waiting_quantity = State()


class SupportStates(StatesGroup):
    waiting_message = State()
