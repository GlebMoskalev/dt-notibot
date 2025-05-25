from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import BaseFilter


class IsAddingEventFilter(BaseFilter):
    async def __call__(self, message: Message, state: FSMContext) -> bool:
        data = await state.get_data()
        return data.get("is_adding_event", False)

class IsEditingEventFilter(BaseFilter):
    async def __call__(self, message: Message, state: FSMContext) -> bool:
        data = await state.get_data()
        return data.get("is_editing_event", False)