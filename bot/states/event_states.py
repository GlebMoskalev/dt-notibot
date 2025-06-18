from aiogram.fsm.state import State, StatesGroup


class EventStates(StatesGroup):
    waiting_for_section = State()
    waiting_for_description = State()
    waiting_for_organizers = State()
    waiting_for_start_time = State()
    waiting_for_end_time = State()

class SendFriendInviteState(StatesGroup):
    waiting_for_telegram_code = State()
