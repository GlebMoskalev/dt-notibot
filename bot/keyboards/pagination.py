from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters.callback_data import CallbackData

class Pagination(CallbackData, prefix="pag"):
    prefix: str
    page: int

def Pagination_keyboard(page: int,
                          total_pages: int,
                          prefix: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    buttons = [
        ("⬅️", Pagination(page=page - 1,
                          prefix=prefix).pack() if page > 1 else "null"),
        (f"{page} / {total_pages}", "null"),
        ("➡️", Pagination(
            page=page + 1,
            prefix=prefix).pack() if page < total_pages else "null"),
    ]

    builder.row(*[
        InlineKeyboardButton(text=text, callback_data=callback_data)
        for text, callback_data in buttons
    ])
    return builder.as_markup()