from bot.services import DataBase
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton
from aiogram import Dispatcher
from aiogram.filters import StateFilter, and_f
from bot.filters import CommandAccessFilter, IsEditingEventFilter
from collections import defaultdict
from bot.messages import schedules_message, error_message, favorites_schedules_message, edit_event
from bot.keyboards import Pagination_keyboard, Pagination
from aiogram import F
from bot.states import EventStates
from aiogram.fsm.context import FSMContext
from datetime import datetime
from typing import List
import re

def register_schedule_handlers(dp: Dispatcher, db: DataBase) -> None:
    handler = ScheduleHandler(db)

    dp.message.register(
        handler.start_schedule,
        CommandAccessFilter(command='schedule', db=db)
    )

    dp.callback_query.register(
        handler.schedule_callback,
        Pagination.filter(F.prefix == 'schedule')
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
    
    dp.message.register(
        handler.start_edit_event_command,
        lambda message: message.text.startswith("/edit_event_")
    )
    
    dp.message.register(
        handler.edit_section_command,
        and_f(StateFilter(EventStates.waiting_for_section), IsEditingEventFilter())
    )
    
    dp.message.register(
        handler.edit_organizers_command,
        and_f(StateFilter(EventStates.waiting_for_description), IsEditingEventFilter())
    )
    
    dp.message.register(
        handler.edit_start_time_command,
        and_f(StateFilter(EventStates.waiting_for_organizers), IsEditingEventFilter())
    )
    
    dp.message.register(
        handler.edit_end_time_command,
        and_f(StateFilter(EventStates.waiting_for_start_time), IsEditingEventFilter())
    )
    
    dp.message.register(
        handler.edit_end_edit_event_command,
        and_f(StateFilter(EventStates.waiting_for_end_time), IsEditingEventFilter())
    )

class ScheduleHandler:
    def __init__(self, db: DataBase):
        self.db = db
        self.limit = 5

        self.user_page_events = defaultdict(list)
        self.user_favorite_events = defaultdict(list)
        self.last_favorites_message = defaultdict(list)
        self.event_sections = None
        self.next_command = '➡️Next'
        self.event_sections = self.db.get_event_sections()

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
                sent_message= await message.answer(
                    text=text_favorite,
                    reply_markup=Pagination_keyboard(page, total_pages,
                                                            "favorite_schedules")
                )
                self.last_favorites_message[user_id] = sent_message.message_id
            elif callback is not None:
                await callback.message.edit_text(
                    text=text_favorite,
                    reply_markup=Pagination_keyboard(page, total_pages,
                                                            "favorite_schedules")
                )
                self.last_favorites_message[ user_id] = callback.message.message_id
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
                    reply_markup=Pagination_keyboard(page, total_pages, "schedule")
                )
            elif callback is not None:
                await callback.message.edit_text(
                    text=text_schedules,
                    reply_markup=Pagination_keyboard(page, total_pages, "schedule")
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

    async def start_edit_event_command(self, message: Message, state: FSMContext) -> None:
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
                event = await self.db.get_event(event_id)
                await state.set_data({"is_editing_event": True})
                await state.update_data(event=event)
                edit_message = edit_event.start_edit_event_message() + '\n' + edit_event.section_edit_event_message(event['section'])

                await message.answer(edit_message, reply_markup=self.__create_section_buttons(), parse_mode='Markdown')
                await state.set_state(EventStates.waiting_for_section)
            else:
                await message.answer(
                    "Неверный индекс события. Используйте /schedule для просмотра доступных событий.")
        except ValueError:
            await message.answer(
                "Ошибка в формате команды. Пример: /edit_event_1")
        except Exception as e:
            print(e)
            await message.answer("Произошла ошибка. Попробуйте снова.")
    
    async def edit_section_command(self, message: Message, state: FSMContext) -> None:
        section = message.text
        event = await state.get_value('event')
        if section != self.next_command:
            if section not in self.event_sections:
                await message.answer('Неопознанный тип события. Выберите корректный тип события')
                return
            event['section'] = section
            await state.update_data(event=event)

        description_message = edit_event.description_edit_event_message(event['description'])
        await message.answer(text=description_message, reply_markup=self.__create_next_button_markup(), parse_mode='Markdown')
        await state.set_state(EventStates.waiting_for_description)
        
    async def edit_organizers_command(self, message: Message, state: FSMContext) -> None:
        description = message.text.strip()
        event = await state.get_value('event')
        if description != self.next_command:
            if description == '':
                await message.answer('Введите, пожалуйста, непустое описание события')
                return
            event['description'] = description
            await state.update_data(event=event)
        
        organizers_message = edit_event.organizers_edit_event_message(
            self.__reparse_orgnizers(event['organizers']))
        await message.answer(text=organizers_message, parse_mode='Markdown')
        await state.set_state(EventStates.waiting_for_organizers)
    
    async def edit_start_time_command(self, message: Message, state: FSMContext) -> None:
        organizers = message.text
        event = await state.get_value('event')
        if organizers != self.next_command:
            if not self.__check_orgnizers_format(organizers):
                await message.answer('Используйте формат: Имя Фамилия - для представления спикера. Введите спикеров снова')
                return
            event['organizers'] = self.__parse_orgnizers(organizers)
            await state.update_data(event=event)
            
        start_date_message = edit_event.start_time_edit_event_message(
            self.__parse_time_to_string(event['start_time']))
        await message.answer(text=start_date_message, reply_markup=self.__create_next_button_markup(), parse_mode='Markdown')
        await state.set_state(EventStates.waiting_for_start_time)
    
    async def edit_end_time_command(self, message: Message, state: FSMContext) -> None:
        start_time = message.text
        event = await state.get_value('event')
        if start_time != self.next_command:
            if not self.__check_time_format(start_time):
                await message.answer('Для ввода времени используйте формат:\n```\nДень.Месяц Часы:Минуты```', parse_mode='Markdown')
                return
            event['start_time'] = self.__parse_time_string(start_time)
            await state.update_data(event=event)
            
        end_date_message = edit_event.end_time_edit_event_message(
            self.__parse_time_to_string(event['end_time']))
        await message.answer(text=end_date_message, reply_markup=self.__create_next_button_markup(), parse_mode='Markdown')
        await state.set_state(EventStates.waiting_for_end_time)
    
    async def edit_end_edit_event_command(self, message: Message, state: FSMContext) -> None:
        end_time = message.text
        is_next = end_time == self.next_command
        if not is_next and not self.__check_time_format(end_time):
            await message.answer('Для ввода времени используйте формат:\n```\nДень.Месяц Часы:Минуты```', parse_mode='Markdown')
            return
        
        event = await state.get_value('event')
        try:
            end_datetime = self.__parse_time_string(end_time) if not is_next else event['end_time']
            
            event_data = {
                'event_id': event['id'],
                'section': event['section'],
                'description': event['description'],
                'organizers': event['organizers'],
                'start_time': event['start_time'],
                'end_time': end_datetime
            }
            
            await self.db.update_event(**event_data)
            end_message = edit_event.end_new_edit_event_message()
            await message.answer(text=end_message, parse_mode='Markdown')

        except Exception as e:
            await message.answer("Произошла ошибка при обновлении события. Пожалуйста, попробуйте снова.")
            print(f"Error creating event: {e}")
        finally:
            await state.clear()

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

                favorite_schedules, total = await self.db.get_favorite_events_paginated(
                    user_id, self.limit, 0)
                total_pages = (total + self.limit - 1) // self.limit if total > 0 else 1
                self.user_favorite_events[user_id] = [event["id"] for event in favorite_schedules]

                if user_id in self.last_favorites_message:
                    try:
                        await message.bot.edit_message_text(
                            chat_id=message.chat.id,
                            message_id=self.last_favorites_message[user_id],
                            text=favorites_schedules_message(
                                favorite_schedules),
                            reply_markup=Pagination_keyboard(
                                1, total_pages,
                                "favorite_schedules")
                        )
                    except Exception as e:
                        print(e)

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

    def __check_orgnizers_format(self, orgs: str) -> bool:
        orgs = orgs.strip()
        while '  ' in orgs:
            orgs = orgs.replace('  ', ' ')
        while ', ' in orgs:
            orgs = orgs.replace(', ', ',')
        while ' ,' in orgs:
            orgs = orgs.replace(' ,', ',')
        return all([name != ''
                    for org in orgs.split(',')
                    for name in org.split()])
    
    def __parse_orgnizers(self, orgs: str) -> List[str]:
        orgs = orgs.strip()
        while '  ' in orgs:
            orgs = orgs.replace('  ', ' ')
        while ', ' in orgs:
            orgs = orgs.replace(', ', ',')
        while ' ,' in orgs:
            orgs = orgs.replace(' ,', ',')
        return orgs.split(',')

    def __reparse_orgnizers(self, orgs: List[str]) -> str:
        return ', '.join(orgs)
    
    def __check_time_format(self, time: str) -> bool:
        time = time.strip()
        while '  ' in time:
            time = time.replace('  ', ' ')
    
        pattern = r'^\d{1,2}\.\d{1,2} \d{1,2}:\d{1,2}$'
        if not re.fullmatch(pattern, time):
            return False
        
        try:
            self.__parse_time_string(time)
            return True
        except (ValueError, AttributeError):
            return False
        
    def __create_section_buttons(self) -> ReplyKeyboardMarkup:
        keyboards = []
        for section in self.event_sections:
            keyboards.append([KeyboardButton(text=section)])
        
        keyboards.append([self.__create_next_button()])
        
        return ReplyKeyboardMarkup(
            keyboard=keyboards,
            resize_keyboard=True,
            one_time_keyboard=True
        )
    
    def __create_next_button_markup(self) -> ReplyKeyboardMarkup:
        return ReplyKeyboardMarkup(
            keyboard=[[self.__create_next_button()]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
    
    def __create_next_button(self) -> KeyboardButton:
        return KeyboardButton(text=self.next_command)
    
    def __parse_time_string(self, time_str: str) -> datetime:
        date_part, time_part = time_str.split()
        day, month = map(int, date_part.split('.'))
        hours, minutes = map(int, time_part.split(':'))
        
        current_year = datetime.now().year
        return datetime(
            year=current_year,
            month=month,
            day=day,
            hour=hours,
            minute=minutes
        )
    
    def __parse_time_to_string(self, time: datetime) -> str:
        return f'{time.day}.{time.month} {time.hour}:{time.minute}'