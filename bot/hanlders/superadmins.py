from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.messages import error_message
from bot.services.postgresql import DataBase, RoleEnum
from bot.filters import CommandAccessFilter
from bot.messages.superadmin import superadmins_message, superadmin_names_not_found
from bot.callbacks.pagination import Pagination


def register_superadmins_handler(dp: Dispatcher, db: DataBase) -> None:
    handler = SuperAdminsHandler(db)
    dp.message.register(
        handler.superadmins_handler,
        CommandAccessFilter(command='super_admins', db=db)
    )

    dp.callback_query.register(
        handler.superadmins_callback,
        Pagination.filter()
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
            paginator = await self.get_paginated_superadmin_names(len(superadmin_names))
            
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
            paginator = await self.get_paginated_superadmin_names(len(superadmin_names), page)

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
            
    async def get_paginated_superadmin_names(self, total_count: int, page: int = 0) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()  
        start_offset = page * self.__superadmins_in_page
        end_offset = start_offset + self.__superadmins_in_page
        print(f'Return superadmins with interval: {start_offset}-{end_offset}')
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