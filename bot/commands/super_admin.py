from aiogram.types import BotCommand

super_admin_commands = [
    BotCommand(command="admins", description="Получение списка всех админов"),
    BotCommand(command="super_admins", description="Получение списка всех суперадминов"),
    BotCommand(command="update_invite_secrets", description="Обновить секреты для инвайтов сотрудников"),
    BotCommand(command="invite_links", description="Получение списка ссылок на приглашения")
]