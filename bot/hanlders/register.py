from aiogram import Dispatcher, F
from sqlalchemy.orm import Session

from .contest import register_contest_handlers
from .friends import register_friends_handlers
from .invite import register_invite_handlers
from .start import register_start_handlers
from .schedule import register_schedule_handlers
from .users import register_users_handler
from .admins import register_admins_handler
from .superadmins import register_superadmins_handler
from .new_event import register_new_event_handlers
from bot.services import DataBase
from aiogram.types import Message
from bot.messages import command_not_found_message, access_denied_message
from bot.commands import admin_commands, super_admin_commands, user_commands

async def register_all_handlers(dp: Dispatcher, db: DataBase, session: Session) -> None:
    register_start_handlers(dp, db)
    register_invite_handlers(dp, db)
    await register_schedule_handlers(dp, db)

    register_users_handler(dp, db)
    register_admins_handler(dp, db)
    register_superadmins_handler(dp, db)

    register_friends_handlers(dp, db, session)
    register_contest_handlers(dp, db, session)

    await register_new_event_handlers(dp, db)

    dp.message.register(unknown_command_handler, F.text.startswith('/'))


async def unknown_command_handler(message: Message) -> None:
    command = message.text.split()[0][1:]
    all_commands = [cmd.command for cmd in
                    user_commands + admin_commands + super_admin_commands]

    if command in all_commands:
        await message.answer(access_denied_message())
    else:
        await message.answer(command_not_found_message())

