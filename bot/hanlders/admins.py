from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.messages import error_message
from bot.services.postgresql import DataBase, RoleEnum
from bot.filters import CommandAccessFilter
from bot.messages.superadmin import admins_message, admin_names_not_found
from bot.callbacks.pagination import Pagination


def register_admins_handler(dp: Dispatcher, db: DataBase) -> None:
    handler = AdminsHandler(db)
    dp.message.register(
        handler.admins_handler,
        CommandAccessFilter(command='admins', db=db)
    )

    dp.callback_query.register(
        handler.admins_callback,
        Pagination.filter()
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
            paginator = await self.get_paginated_admin_names(len(admin_names))
            
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
            paginator = await self.get_paginated_admin_names(len(admin_names), page)

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
            
    async def get_paginated_admin_names(self, total_count: int, page: int = 0) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()  
        start_offset = page * self.__admins_in_page
        end_offset = start_offset + self.__admins_in_page
        print(f'Return admins with interval: {start_offset}-{end_offset}')
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