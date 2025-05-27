from aiogram import Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy.orm import Session

from bot.keyboards import Pagination_keyboard, Pagination
from bot.messages import error_message
from bot.messages.superadmin import friends_message
from bot.services.migrations.sqlalchemy import get_user_by_chat_id, get_user_by_invite_code, try_add_friend, \
    recreate_invite_code
from bot.services.postgresql import DataBase
from bot.filters import CommandAccessFilter
from bot.states import SendFriendInviteState


def register_friends_handlers(dp: Dispatcher, db: DataBase, session: Session) -> None:
    handler = FriendInviteHandler(session)
    dp.message.register(
        handler.friends_handler,
        CommandAccessFilter(command='friends', db=db)
    )

    dp.message.register(
        handler.post_invite_code_entered_handler,
        StateFilter(SendFriendInviteState.waiting_for_telegram_code)
    )

    dp.message.register(
        handler.get_invite_code,
        CommandAccessFilter(command='invite_code', db=db)
    )

    dp.message.register(
        handler.accept_invite,
        CommandAccessFilter(command='accept_invite', db=db)
    )

    dp.callback_query.register(
        handler.friends_callback,
        Pagination.filter(F.prefix == 'friends')
    )


class FriendInviteHandler:
    def __init__(self, session: Session):
        self.session = session
        self.__friends_in_page = 10

    async def friends_handler(self, message: Message):
        try:
            user = get_user_by_chat_id(self.session, chat_id=message.chat.id)
            friends = user.friends
            if not friends:
                return await message.answer('У вас пока нет друзей')

            friend_names = list(map(lambda u: u.telegram_name, friends))

            page_count = len(friend_names) // self.__friends_in_page + (len(friend_names) % self.__friends_in_page != 0)
            paginator = Pagination_keyboard(1, page_count, "friends")

            return await message.answer(
                text=friends_message(friend_names, 0, self.__friends_in_page),
                reply_markup=paginator,
            )
        except Exception as e:
            await message.answer(error_message())
            print(e)
            return None

    async def friends_callback(self, callback: CallbackQuery, callback_data: Pagination):
        try:
            page = callback_data.page
            print(page)
            user = get_user_by_chat_id(self.session, chat_id=callback.message.chat.id)
            friends = user.friends

            if friends is None:
                return await callback.message.answer('У вас пока нет друзей')

            friend_names = list(map(lambda u: u.telegram_name, friends))
            page_count = len(friend_names) // self.__friends_in_page + (len(friend_names) % self.__friends_in_page != 0)
            paginator = Pagination_keyboard(page, page_count, "friends")

            admins = friends_message(friend_names, self.__friends_in_page * (page - 1), self.__friends_in_page)

            await callback.answer()
            return callback.message.edit_text(
                text=admins,
                reply_markup=paginator
            )
        except Exception as e:
            await callback.message.answer(error_message())
            return print(e)

    async def get_invite_code(self, message: Message):
        try:
            user = get_user_by_chat_id(self.session, message.chat.id)
            await message.answer(f"Ваш код приглашения: `{user.unique_code}`", parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            await message.answer(error_message())
            print(e)

    @staticmethod
    async def accept_invite(message: Message, state: FSMContext):
        try:
            await message.answer(
                "Введите ссылку приглашения пользователя, которого хотите добавить в друзья",
            )
            await state.set_state(SendFriendInviteState.waiting_for_telegram_code.state)
        except Exception as e:
            await message.answer(error_message())
            print(e)

    async def post_invite_code_entered_handler(self, message: Message, state: FSMContext):
        try:
            text = message.text
            invite_code = int(text) if text.isdecimal() else None

            if invite_code is None:
                return await message.answer("Некорректный код приглашения")

            sender = get_user_by_invite_code(self.session, invite_code)
            receiver = get_user_by_chat_id(self.session, message.chat.id)

            if sender.chat_id == message.chat.id:
                return await message.answer("Нельзя отправить приглашение самому себе")

            is_already_friend = not try_add_friend(self.session, sender, receiver)

            if is_already_friend:
                return await message.answer("Этот пользователь уже у Вас в друзьях")

            new_code = recreate_invite_code(self.session, sender.chat_id)
            await message.answer(f"Пользователь @{sender.telegram_name} успешно добавлен в друзья!")

            await message.bot.send_message(sender.chat_id,
                                           f"Пользователь @{sender.telegram_name} успешно добавлен в друзья!")
            await message.bot.send_message(sender.chat_id, f"Ваш новый код: `{new_code}`",
                                           parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            await message.answer(error_message())
            print(e)
        finally:
            await state.clear()
