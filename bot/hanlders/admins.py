from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery
from bot.messages import error_message
from bot.services.postgresql import DataBase, RoleEnum
from bot.filters import CommandAccessFilter
from bot.messages.superadmin import admins_message, admin_names_not_found
from bot.keyboards import Pagination_keyboard, Pagination
from aiogram import F


def register_admins_handler(dp: Dispatcher, db: DataBase) -> None:
    handler = AdminsHandler(db)
    dp.message.register(
        handler.admins_handler,
        CommandAccessFilter(command='admins', db=db)
    )

    dp.callback_query.register(
        handler.admins_callback,
        Pagination.filter(F.prefix == 'admins')
    )

class AdminsHandler:
    def __init__(self, db: DataBase):
        self.db = db
        self.__admins_in_page = 10

    async def admins_handler(self, message: Message) -> None:
        try:
            admin_names = await self.db.get_all_names(RoleEnum.Admin)
            if admin_names is None:
                await message.answer(text=admin_names_not_found())
                return
            all_pages = len(admin_names) // self.__admins_in_page + (len(admin_names) % self.__admins_in_page != 0)
            paginator = await Pagination_keyboard(1, all_pages, "admins")
            
            admins = admins_message(admin_names, 0, self.__admins_in_page)
            print(f'Return less or equal {self.__admins_in_page} admin names on page 0 in chat {message.chat.id}')
            print(admins)
            await message.answer(
                text=admins,
                reply_markup=paginator
            )
        except Exception as e:
            await message.answer(error_message())
            print(e)
    
    async def admins_callback(self, callback: CallbackQuery, callback_data: Pagination) -> None:
        try:
            page = callback_data.page
            admin_names = await self.db.get_all_names(RoleEnum.Admin)
            if admin_names is None:
                await callback.message.answer(text=admin_names_not_found())
                return
            all_pages = len(admin_names) // self.__admins_in_page + (len(admin_names) % self.__admins_in_page != 0)
            paginator = await Pagination_keyboard(page, all_pages, "admins")

            admins = admins_message(admin_names, self.__admins_in_page * page, self.__admins_in_page)
            print(f'Return less or equal {self.__admins_in_page} admin names on page {page} in chat {callback.message.chat.id}')
            print(admins)
            await callback.answer()
            await callback.message.edit_text(
                text=admins,
                reply_markup=paginator
            )
        except Exception as e:
            await callback.message.answer(error_message())
            print(e)