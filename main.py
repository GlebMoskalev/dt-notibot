import asyncio
from bot.hanlders import register_all_handlers
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
import os
from bot.services import DataBase, NotificationDaemon


async def main():
    load_dotenv()
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise ValueError("BOT_TOKEN not found in environment variables")

    bot = Bot(token=token)
    dp = Dispatcher()

    db = DataBase(os.getenv("DATABASE_URL"))
    notificated_daemon = NotificationDaemon(bot, db)

    try:
        await db.connect()
        # await db.regenerate_invite_codes()
    
        asyncio.create_task(notificated_daemon.run())

        register_all_handlers(dp, db)
        await dp.start_polling(bot)
    except Exception as e:
        print(f"Startup error: {e}")
    finally:
        await db.close()


if __name__ == "__main__":
    asyncio.run(main())