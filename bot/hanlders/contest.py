import re
from datetime import datetime

from aiogram import Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.orm import Session

from bot.messages import error_message
from bot.messages.superadmin import leaderboards_message
from bot.services.migrations.sqlalchemy import get_users_by_friend_count
from bot.services.postgresql import DataBase
from bot.filters import CommandAccessFilter
from bot.states.event_states import ContestCreationStates


def register_contest_handlers(dp: Dispatcher, db: DataBase, session: Session) -> None:
    handler = ContestHandler(db, session)
    # dp.message.register(
    #     handler.start_contest,
    #     CommandAccessFilter(command='start_contest', db=db)
    # )

    dp.message.register(
        handler.get_leaderboard,
        CommandAccessFilter(command='leaderboard', db=db)
    )


class ContestHandler:
    def __init__(self, db: DataBase, session: Session):
        self.db = db
        self.session = session


    async def get_leaderboard(self, message: Message):
        try:
            leaderboards = get_users_by_friend_count(self.session)
            await message.answer(leaderboards_message(leaderboards, 0, len(leaderboards)))
        except Exception as e:
            await message.answer(error_message())
            print(e)

    def __check_time_format(self, time: str) -> bool:
        time = time.strip()
        while '  ' in time:
            time = time.replace('  ', ' ')

        pattern = r'^\d{1,2}\.\d{1,2} \d{1,2}:\d{1,2}$'
        if not re.fullmatch(pattern, time):
            return False

        try:
            self.__parse_time_string(time)
            return True
        except (ValueError, AttributeError):
            return False

    @staticmethod
    def __parse_time_string(time_str: str) -> datetime:
        date_part, time_part = time_str.split()
        day, month = map(int, date_part.split('.'))
        hours, minutes = map(int, time_part.split(':'))

        current_year = datetime.now().year
        return datetime(
            year=current_year,
            month=month,
            day=day,
            hour=hours,
            minute=minutes
        )