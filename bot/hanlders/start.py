from bot.messages import welcome_message, expired_link_message, error_message
from aiogram import Dispatcher
from aiogram.types import Message, BotCommandScopeChat
from aiogram.filters import CommandStart, CommandObject
from bot.services.postgresql import DataBase
from bot.commands import admin_commands, user_commands, super_admin_commands

def register_start_handlers(dp: Dispatcher, db: DataBase) -> None:
    handler = StartHandler(db)
    dp.message.register(handler.start_handler, CommandStart(deep_link=True))

class StartHandler:
    def __init__(self, db: DataBase):
        self.db = db

    async def start_handler(self, message: Message, command: CommandObject):
        try:
            role = await self.db.check_invite_code(command.args)
            if role is not None:
                await self.db.add_users(message.chat.id, message.from_user.username,
                                   role)

                available_commands = user_commands
                if role == "Admin":
                    available_commands = [cmd for cmd in
                                          user_commands + admin_commands]
                elif role == "SuperAdmin":
                    available_commands = [cmd for cmd in
                                          user_commands + admin_commands + super_admin_commands]

                await message.bot.set_my_commands(available_commands,
                                                  scope=BotCommandScopeChat(
                                                      chat_id=message.chat.id))

                await message.answer(welcome_message())
            else:
                await message.answer(expired_link_message())
        except Exception as e:
            await message.answer(error_message())
            print(e)