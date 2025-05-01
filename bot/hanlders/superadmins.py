from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery
from bot.messages import error_message
from bot.services.postgresql import DataBase, RoleEnum
from bot.filters import CommandAccessFilter
from bot.messages.superadmin import superadmins_message, superadmin_names_not_found
from bot.keyboards import Pagination_keyboard, Pagination
from aiogram import F


def register_superadmins_handler(dp: Dispatcher, db: DataBase) -> None:
    handler = SuperAdminsHandler(db)
    dp.message.register(
        handler.superadmins_handler,
        CommandAccessFilter(command='super_admins', db=db)
    )

    dp.callback_query.register(
        handler.superadmins_callback,
        Pagination.filter(F.prefix == 'super_admins')
    )

class SuperAdminsHandler:
    def __init__(self, db: DataBase):
        self.db = db
        self.__superadmins_in_page = 10

    async def superadmins_handler(self, message: Message) -> None:
        try:
            superadmin_names = await self.db.get_all_names(RoleEnum.SuperAdmin)
            if superadmin_names is None:
                await message.answer(text=superadmin_names_not_found())
                return
            all_pages = len(superadmin_names) // self.__superadmins_in_page + (len(superadmin_names) % self.__superadmins_in_page != 0)
            paginator = Pagination_keyboard(1, all_pages, "super_admins")
            
            superadmins = superadmins_message(superadmin_names, 0, self.__superadmins_in_page)
            print(f'Return less or equal {self.__superadmins_in_page} superadmin names on page 0 in chat {message.chat.id}')
            print(superadmins)
            await message.answer(
                text=superadmins,
                reply_markup=paginator
            )
        except Exception as e:
            await message.answer(error_message())
            print(e)
    
    async def superadmins_callback(self, callback: CallbackQuery, callback_data: Pagination) -> None:
        try:
            page = callback_data.page
            superadmin_names = await self.db.get_all_names(RoleEnum.SuperAdmin)
            if superadmin_names is None:
                await callback.message.answer(text=superadmin_names_not_found())
                return
            all_pages = len(superadmin_names) // self.__superadmins_in_page + (len(superadmin_names) % self.__superadmins_in_page != 0)
            paginator = Pagination_keyboard(page, all_pages, "super_admins")

            superadmins = superadmins_message(superadmin_names, self.__superadmins_in_page * page, self.__superadmins_in_page)
            print(f'Return less or equal {self.__superadmins_in_page} superadmin names on page {page} in chat {callback.message.chat.id}')
            print(superadmins)
            await callback.answer()
            await callback.message.edit_text(
                text=superadmins,
                reply_markup=paginator
            )
        except Exception as e:
            await callback.message.answer(error_message())
            print(e)