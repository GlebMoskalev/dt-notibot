from aiogram.filters.callback_data import CallbackData
    

class Pagination(CallbackData, prefix="page"):
    page: int