from aiogram.types import BotCommand

admin_commands = [
    BotCommand(command="users", description="Получение списка всех участников"),

    BotCommand(command="add_event", description="Добавление нового события"),

    BotCommand(command="start_contest", description="Запланировать конкурс"),
]