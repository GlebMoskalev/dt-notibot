from aiogram import Dispatcher
from aiogram.types import Message
from bot.messages import no_invite_links_message, error_message, invite_links_message, secrets_update_message
from bot.services.postgresql import DataBase
import os
from dotenv import load_dotenv
from bot.filters import CommandAccessFilter

load_dotenv()
bot_username = os.getenv('BOT_USERNAME')

def register_invite_handlers(dp: Dispatcher, db: DataBase) -> None:
    handler = InviteHandler(db)
    dp.message.register(
        handler.invite_links_handler,
        CommandAccessFilter(command='invite_links', db=db)
    )

    dp.message.register(
        handler.update_invite_secrets,
        CommandAccessFilter(command='update_invite_secrets', db=db)
    )

class InviteHandler:
    def __init__(self, db: DataBase):
        self.db = db

    async def invite_links_handler(self, message: Message):
        try:
            invite_dict = await self.db.get_invite_dict()
            if not invite_dict:
                await message.answer(no_invite_links_message())
                return

            await message.answer(
                invite_links_message(invite_dict, bot_username))
        except Exception as e:
            await message.answer(error_message())
            print(e)

    async def update_invite_secrets(self, message: Message):
        try:
            await self.db.regenerate_invite_codes()
            await message.answer(secrets_update_message())

        except Exception as e:
            await message.answer(error_message())
            print(e)