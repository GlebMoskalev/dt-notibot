from aiogram.types import BotCommand

user_commands = [
    # Schedule commands
    BotCommand(command="schedule", description="Полное расписание всего мероприятия"),
    BotCommand(command="schedule_favorites", description="Расписание только с избранными событиями"),

    # Friend Invite Commands
    BotCommand(command="friends", description="Список друзей"),
    BotCommand(command="accept_invite", description="Ввести код приглашения"),
    BotCommand(command="invite_code", description="Получить мой код приглашения"),

    # Contest commands
    BotCommand(command="leaderboard", description="Текущий рейтинг конкурса"),
]