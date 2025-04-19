from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.messages import error_message
from bot.services.postgresql import DataBase
from bot.filters import CommandAccessFilter
from bot.messages.admin import users_message
from bot.callbacks.pagination import Pagination


def register_users_handler(dp: Dispatcher, db: DataBase) -> None:
    handler = UsersHandler(db)
    dp.message.register(
        handler.users_handler,
        CommandAccessFilter(command='users', db=db)
    )

    dp.callback_query.register(
        handler.users_callback,
        Pagination.filter()
    )

class UsersHandler:
    def __init__(self, db: DataBase):
        self.db = db
        self.__users_in_page = 10

    async def users_handler(self, message: Message):
        try:
            user_names = await self.db.get_user_names()
            paginator = await self.get_paginated_user_names(len(user_names))
            
            users = users_message(user_names, 0, self.__users_in_page)
            print(f'Return less or equal {self.__users_in_page} user names on page 0 in chat {message.chat.id}')
            print(users)
            await message.answer(
                text=users,
                reply_markup=paginator
            )
        except Exception as e:
            await message.answer(error_message())
            print(e)
    
    async def users_callback(self, callback: CallbackQuery, callback_data: Pagination):
        try:
            page = callback_data.page
            user_names = await self.db.get_user_names()
            paginator = await self.get_paginated_user_names(len(user_names), page)

            print(f'Return less or equal {self.__users_in_page} user names on page {page} in chat {callback.message.chat.id}')
            print(users)
            await callback.answer()
            await callback.message.edit_text(
                text=users_message(user_names, self.__users_in_page * page, self.__users_in_page),
                reply_markup=paginator
            )
        except Exception as e:
            await callback.message.answer(error_message())
            print(e)
            
    async def get_paginated_user_names(self, total_count: int, page: int = 0) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()  
        start_offset = page * self.__users_in_page
        end_offset = start_offset + self.__users_in_page
        print(f'Return users with interval: {start_offset}-{end_offset}')
        buttons_row = []
    
        if page > 0:
            print('Add left button for user names')
            buttons_row.append(  
                InlineKeyboardButton(  
                    text="⬅️",  
                    callback_data=Pagination(page=page - 1).pack(),  
                )  
            )  
        if end_offset < total_count:
            print('Add right button for user names')
            buttons_row.append(  
                InlineKeyboardButton(  
                    text="➡️",  
                    callback_data=Pagination(page=page + 1).pack(),  
                )  
            )
        builder.row(*buttons_row)

        return builder.as_markup()