from aiogram import Dispatcher
from aiogram.types import Message
from bot.messages import no_invite_links_message, error_message, invite_links_message
from bot.services.postgresql import DataBase
import os
from dotenv import load_dotenv
from bot.filters import CommandAccessFilter


load_dotenv()
dsn = os.getenv('DATABASE_URL')
bot_username = os.getenv('BOT_USERNAME')
db = DataBase(dsn)

def register_invite_handlers(dp: Dispatcher):
    dp.message.register(invite_links_handler, CommandAccessFilter(commands=['invite_links'], db=db))


async def invite_links_handler(message: Message):
    try:
        invite_dict = db.get_invite_dict()
        if not invite_dict:
            await message.answer(no_invite_links_message())
            return


        await message.answer(invite_links_message(invite_dict, bot_username))
    except Exception as e:
        await message.answer(error_message())
        print(e)