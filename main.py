import asyncio
from bot.hanlders import register_all_handlers
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
import os


async def main():
    load_dotenv()
    token = os.getenv("TOKEN_API")
    bot = Bot(token=token)
    dp = Dispatcher()

    register_all_handlers(dp)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())