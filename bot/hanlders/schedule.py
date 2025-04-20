from sys import prefix

from aiogram.filters.callback_data import CallbackData
from bot.services import DataBase
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram import Dispatcher
from bot.filters import CommandAccessFilter
from aiogram.utils.keyboard import InlineKeyboardBuilder
from collections import defaultdict
from bot.messages import schedules_message, error_message, favorites_schedules_message

class Pagination(CallbackData, prefix="pag"):
    prefix: str
    page: int

def register_schedule_handlers(dp: Dispatcher, db: DataBase) -> None:
    handler = ScheduleHandler(db)
    dp.message.register(
        handler.start_schedule,
        CommandAccessFilter(command='schedule', db=db)
    )

    dp.callback_query.register(
        handler.schedule_callback,
        Pagination.filter()
    )

    dp.callback_query.register(
        handler.ignore_callback,
        lambda c: c.data == "null"
    )

    dp.message.register(
        handler.favorite_schedule,
        CommandAccessFilter(command='schedule_favorites', db=db)
    )

    dp.message.register(
        handler.remove_favorite_by_command,
        lambda message: message.text.startswith("/remove_favorite_")
    )

    dp.message.register(
        handler.add_favorite_by_command,
        lambda message: message.text.startswith("/add_favorite_")
    )

class ScheduleHandler:
    def __init__(self, db: DataBase):
        self.db = db
        self.limit = 5

        self.user_page_events = defaultdict(list)
        self.user_favorite_events = defaultdict(list)
        self.last_favorites_message = defaultdict(list)

    async def start_schedule(self, message: Message):
        return await self.__handle_schedule_page(message=message, page=1)

    async def favorite_schedule(self, message: Message):
        return await self.__favorite_schedule_page(message=message, page=1)

    async def __favorite_schedule_page(self, page: int, message: Message = None, callback: CallbackQuery = None):
        try:
            offset = (page - 1) * self.limit
            user_id = message.from_user.id if message is not None else callback.from_user.id

            favorite_schedules, total = await self.db.get_favorite_events_paginated(user_id, self.limit, offset)
            total_pages = (total + self.limit - 1) // self.limit if total > 0 else 1

            self.user_favorite_events[user_id] = [event["id"] for event in favorite_schedules]

            text_favorite = favorites_schedules_message(favorite_schedules)
            if message is not None:
                await message.answer(
                    text=text_favorite,
                    reply_markup=self.__pagination_keyboard(page, total_pages,
                                                            "favorite_schedules")
                )
            elif callback is not None:
                await callback.message.edit_text(
                    text=text_favorite,
                    reply_markup=self.__pagination_keyboard(page, total_pages,
                                                            "favorite_schedules")
                )
        except Exception as e:
            print(e)
            if message is not None:
                await message.answer(
                    text=error_message()
                )
            elif callback is not None:
                await callback.message.edit_text(
                    text=error_message()
                )

    async def schedule_callback(self, callback: CallbackQuery, callback_data: Pagination):
        if callback_data.prefix == "schedule":
            return await self.__handle_schedule_page(callback=callback,
                                                     page=callback_data.page)
        elif callback_data.prefix == "favorite_schedules":
            return await self.__favorite_schedule_page(callback=callback,
                                                       page=callback_data.page)

    async def __handle_schedule_page(self, page: int, message: Message = None, callback: CallbackQuery = None):
        try:

            offset = (page - 1) * self.limit
            schedules, total = await self.db.get_events_paginated(self.limit, offset)
            total_pages = (total + self.limit - 1) // self.limit if total > 0 else 1

            user_id = message.from_user.id if message else callback.from_user.id
            self.user_page_events[user_id] = [event["id"] for event in
                                              schedules]

            text_schedules = schedules_message(schedules)
            if message is not None:
                await message.answer(
                    text=text_schedules,
                    reply_markup=self.__pagination_keyboard(page, total_pages, "schedule")
                )
            elif callback is not None:
                await callback.message.edit_text(
                    text=text_schedules,
                    reply_markup=self.__pagination_keyboard(page, total_pages, "schedule")
                )

        except Exception as e:
            print(e)
            if message is not None:
                await message.answer(
                    text=error_message()
                )
            elif callback is not None:
                await callback.message.edit_text(
                    text=error_message()
                )

    async def ignore_callback(self, callback: CallbackQuery):
        await callback.answer()

    async def add_favorite_by_command(self, message: Message):
        try:
            command = message.text
            index = int(command.split("_")[-1])
            user_id = message.from_user.id

            event_ids = self.user_page_events.get(user_id, [])


            if not event_ids:
                await message.answer(
                    "Сначала откройте расписание с помощью /schedule."
                )
                return

            if 1 <= index <= len(event_ids):
                event_id = event_ids[index - 1]

                is_favorite = await self.db.is_event_favorite(user_id,
                                                              event_id)
                if is_favorite:
                    await message.answer("Это событие уже в избранном ⭐")
                    return

                await self.db.add_favorite(user_id, event_id)
                await message.answer("Событие добавлено в избранное! ⭐")
            else:
                await message.answer(
                    "Неверный индекс события. Используйте /schedule для просмотра доступных событий.")
        except ValueError:
            await message.answer(
                "Ошибка в формате команды. Пример: /add_favorite_1")
        except Exception as e:
            print(e)
            await message.answer("Произошла ошибка. Попробуйте снова.")

    async def remove_favorite_by_command(self, message: Message):
        try:
            command = message.text
            index = int(command.split("_")[-1])
            user_id = message.from_user.id

            event_ids = self.user_favorite_events.get(user_id, [])

            if not event_ids:
                await message.answer(
                    "Сначала откройте избранное с помощью /schedule_favorites.")
                return

            if 1 <= index <= len(event_ids):
                event_id = event_ids[index - 1]

                is_favorite = await self.db.is_event_favorite(user_id,
                                                              event_id)
                if not is_favorite:
                    await message.answer("Это событие уже не в избранном.")
                    return

                await self.db.remove_favorite(user_id, event_id)
                await message.answer("Событие удалено из избранного. ❌")
            else:
                await message.answer(
                    "Неверный индекс события. Используйте /schedule_favorites для просмотра.")
        except ValueError:
            await message.answer(
                "Ошибка в формате команды. Пример: /remove_favorite_1")
        except Exception as e:
            print(e)
            await message.answer("Произошла ошибка. Попробуйте снова.")

    def __pagination_keyboard(self, page: int,
                              total_pages: int, prefix: str) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        buttons = [
            ("⬅️", Pagination(page=page - 1, prefix=prefix).pack() if page > 1 else "null"),
            (f"{page} / {total_pages}", "null"),
            ("➡️", Pagination(
                page=page + 1, prefix=prefix).pack() if page < total_pages else "null"),
        ]

        builder.row(*[
            InlineKeyboardButton(text=text, callback_data=callback_data)
            for text, callback_data in buttons
        ])
        return builder.as_markup()
