from aiogram import Dispatcher, F
from .invite import register_invite_handlers
from .start import register_start_handlers
from bot.services import DataBase
from aiogram.types import Message
from bot.messages import command_not_found_message, access_denied_message
from bot.commands import admin_commands, super_admin_commands, user_commands

def register_all_handlers(dp: Dispatcher, db: DataBase) -> None:
    register_start_handlers(dp, db)
    register_invite_handlers(dp, db)

    dp.message.register(unknown_command_handler, F.text.startswith('/'))


async def unknown_command_handler(message: Message):
    command = message.text.split()[0][1:]
    all_commands = [cmd.command for cmd in
                    user_commands + admin_commands + super_admin_commands]

    if command in all_commands:
        await message.answer(access_denied_message())
    else:
        await message.answer(command_not_found_message())

