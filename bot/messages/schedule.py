from typing import List, Dict

def no_schedules_message() -> str:
    return "Список расписания пуст."

def schedules_message(schedules: List[Dict]) -> str:
    if not schedules:
        return no_schedules_message()

    message_lines = ["📅 Расписние расписание: \n"]
    for idx, event in enumerate(schedules, start=1):
        description = event.get("description", "Без описания")
        start_time = event.get("start_time", "Неизвестно")
        message_lines.append(
            f"🕒 {start_time}\n   📌 {description}\n  ➕ /add_favorite_{idx}\n"
        )

    return "\n".join(message_lines)

def favorites_schedules_message(schedules: List[Dict]) -> str:
    if not schedules:
        return no_schedules_message()

    message_lines = ["📅 Расписние расписание: \n"]
    for idx, event in enumerate(schedules, start=1):
        description = event.get("description", "Без описания")
        start_time = event.get("start_time", "Неизвестно")
        message_lines.append(
            f"🕒 {start_time}\n   📌 {description}\n  ➕ /remove_favorite_{idx}\n"
        )

    return "\n".join(message_lines)