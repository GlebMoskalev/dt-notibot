from aiogram import Dispatcher
from .invite import register_invite_handlers
from .start import register_start_handlers

def register_all_handlers(dp: Dispatcher):
    register_start_handlers(dp)
    register_invite_handlers(dp)
