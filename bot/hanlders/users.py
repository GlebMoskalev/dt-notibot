from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery
from bot.messages import error_message
from bot.services.postgresql import DataBase,RoleEnum
from bot.filters import CommandAccessFilter
from bot.messages.admin import users_message, user_names_not_found
from bot.keyboards import Pagination_keyboard, Pagination
from aiogram import F


def register_users_handler(dp: Dispatcher, db: DataBase) -> None:
    handler = UsersHandler(db)
    dp.message.register(
        handler.users_handler,
        CommandAccessFilter(command='users', db=db)
    )

    dp.callback_query.register(
        handler.users_callback,
        Pagination.filter(F.prefix == 'users')
    )

class UsersHandler:
    def __init__(self, db: DataBase):
        self.db = db
        self.__users_in_page = 1

    async def users_handler(self, message: Message) -> None:
        try:
            user_names = await self.db.get_all_names(RoleEnum.User)
            if user_names is None:
                await message.answer(text=user_names_not_found())
                return
            all_pages = len(user_names) // self.__users_in_page + (len(user_names) % self.__users_in_page != 0)
            paginator = Pagination_keyboard(1, all_pages, "users")
            
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
    
    async def users_callback(self, callback: CallbackQuery, callback_data: Pagination) -> None:
        try:
            page = callback_data.page
            user_names = await self.db.get_all_names(RoleEnum.User)
            if user_names is None:
                await callback.message.answer(text=user_names_not_found())
                return
            all_pages = len(user_names) // self.__users_in_page + (len(user_names) % self.__users_in_page != 0)
            paginator = Pagination_keyboard(page, all_pages, "users")

            users = users_message(user_names, self.__users_in_page * (page - 1), self.__users_in_page)
            print(f'Return less or equal {self.__users_in_page} user names on page {page} in chat {callback.message.chat.id}')
            print(users)
            await callback.answer()
            await callback.message.edit_text(
                text=users,
                reply_markup=paginator
            )
        except Exception as e:
            await callback.message.answer(error_message())
            print(e)