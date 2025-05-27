from bot.services import DataBase
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram import Dispatcher
from aiogram.filters import StateFilter, and_f
from bot.filters import CommandAccessFilter, IsAddingEventFilter
from bot.messages import new_event
from bot.states import EventStates
from aiogram.fsm.context import FSMContext
import re
from datetime import datetime
from typing import List


def register_new_event_handlers(dp: Dispatcher, db: DataBase) -> None:
    handler = NewEventHandler(db)
    
    dp.message.register(
        handler.add_event_command,
        CommandAccessFilter(command='add_event', db=db)
    )
    
    dp.message.register(
        handler.section_command,
        and_f(StateFilter(EventStates.waiting_for_section), IsAddingEventFilter())
    )
    
    dp.message.register(
        handler.organizers_command,
        and_f(StateFilter(EventStates.waiting_for_description), IsAddingEventFilter())
    )
    
    dp.message.register(
        handler.start_time_command,
        and_f(StateFilter(EventStates.waiting_for_organizers), IsAddingEventFilter())
    )
    
    dp.message.register(
        handler.end_time_command,
        and_f(StateFilter(EventStates.waiting_for_start_time), IsAddingEventFilter())
    )
    
    dp.message.register(
        handler.end_add_event_command,
        and_f(StateFilter(EventStates.waiting_for_end_time), IsAddingEventFilter())
    )

class NewEventHandler:
    def __init__(self, db: DataBase):
        self.db = db
        self.limit = 5
        self.event_sections = None
        self.event_sections = self.db.get_event_sections()

    async def add_event_command(self, message: Message, state: FSMContext) -> None:
        await state.set_data({"is_adding_event": True})
        section_buttons = self.__create_section_buttons()
        start_message = new_event.start_new_event_message() + '\n' + new_event.section_event_message()
        await message.answer(text=start_message, reply_markup=section_buttons)
        await state.set_state(EventStates.waiting_for_section)
    
    async def section_command(self, message: Message, state: FSMContext) -> None:
        section = message.text
        if section not in self.event_sections:
            await message.answer('Неопознанный тип события. Выберите корректный тип события')
            return
        await state.update_data(section=section)

        description_message = new_event.description_event_message()
        await message.answer(text=description_message)
        await state.set_state(EventStates.waiting_for_description)
    
    async def organizers_command(self, message: Message, state: FSMContext) -> None:
        description = message.text.strip()
        if description == '':
            await message.answer('Введите, пожалуйста, непустое описание события')
            return
        await state.update_data(description=description)
        
        organizers_message = new_event.organizers_event_message()
        await message.answer(text=organizers_message)
        await state.set_state(EventStates.waiting_for_organizers)
    
    async def start_time_command(self, message: Message, state: FSMContext) -> None:
        organizers = message.text
        if not self.__check_orgnizers_format(organizers):
            await message.answer('Используйте формат: Имя Фамилия - для представления спикера. Введите спикеров снова')
            return
        await state.update_data(organizers=self.__parse_orgnizers(organizers))
        
        start_date_message = new_event.start_time_event_message()
        await message.answer(text=start_date_message, parse_mode='Markdown')
        await state.set_state(EventStates.waiting_for_start_time)
    
    async def end_time_command(self, message: Message, state: FSMContext) -> None:
        start_time = message.text
        if not self.__check_time_format(start_time):
            await message.answer('Для ввода времени используйте формат:\n```\nДень.Месяц Часы:Минуты```', parse_mode='Markdown')
            return
        await state.update_data(start_time=start_time)
        
        end_date_message = new_event.end_time_event_message()
        await message.answer(text=end_date_message, parse_mode='Markdown')
        await state.set_state(EventStates.waiting_for_end_time)
    
    async def end_add_event_command(self, message: Message, state: FSMContext) -> None:
        end_time = message.text
        if not self.__check_time_format(end_time):
            await message.answer('Для ввода времени используйте формат:\n```\nДень.Месяц Часы:Минуты```', parse_mode='Markdown')
            return
        
        data = await state.get_data()
        try:
            start_datetime = self.__parse_time_string(data['start_time'])
            end_datetime = self.__parse_time_string(end_time)
            
            event_data = {
                'section': data['section'],
                'description': data['description'],
                'organizers': data['organizers'],
                'start_time': start_datetime,
                'end_time': end_datetime
            }
            
            event_id = await self.db.add_event(**event_data)
            end_message = new_event.end_new_event_message()
            await message.answer(text=end_message)

        except Exception as e:
            await message.answer("Произошла ошибка при создании события. Пожалуйста, попробуйте снова.")
            print(f"Error creating event: {e}")
        finally:
            await state.clear()
        

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
        
        return ReplyKeyboardMarkup(
            keyboard=keyboards,
            resize_keyboard=True,
            one_time_keyboard=True
        )
    
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