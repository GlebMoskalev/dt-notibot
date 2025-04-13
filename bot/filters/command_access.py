from aiogram.filters import BaseFilter
from aiogram.types import Message
from bot.services.postgresql import DataBase
from bot.commands import admin_commands, super_admin_commands, user_commands

class CommandAccessFilter(BaseFilter):
    def __init__(self, command: str, db: DataBase):
        self.command = command
        self.db = db

    async def __call__(self, message: Message) -> bool:
        command = message.text.split()[0][1:]
        if command != self.command:
            return False

        try:
            user_role = await self.db.get_user_role(message.chat.id)
            if user_role is None:
                return False
        except Exception as e:
            print(e)
            return False

        available_commands = []
        if user_role == "User":
            available_commands = [cmd.command for cmd in user_commands]
        elif user_role == "Admin":
            available_commands = [cmd.command for cmd in
                                  user_commands + admin_commands]
        elif user_role == "SuperAdmin":
            available_commands = [cmd.command for cmd in
                                  user_commands + admin_commands + super_admin_commands]

        if command not in available_commands:
            return False

        return True