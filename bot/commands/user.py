from aiogram.types import BotCommand

user_commands = [
    BotCommand(command="schedule", description="Полное расписание всего мероприятия"),
    BotCommand(command="schedule_favorites", description="Расписание только с избранными событиями"),
    BotCommand(command="friends", description="Список друзей"),
    BotCommand(command="friendship_invites_sent", description="Список отправленных приглашений на дружбу"),
    BotCommand(command="friendship_send", description="Отправить приглашение на дружбу"),
    BotCommand(command="friendship_invites_received", description="Cписок полученных приглашений на дружбу")
]