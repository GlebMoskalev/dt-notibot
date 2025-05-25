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
        lecturer = event.get("organizers", "Неизвестно")
        if hasattr(start_time, "strftime"):
            formatted_time = start_time.strftime("%d.%m.%Y %H:%M")
        else:
            formatted_time = str(start_time)
        message_lines.append(
            f"📌 {description}\n\t🕒 {formatted_time}\n\t👨🏻‍💼 {lecturer}\n\t➕ /add_favorite_{idx}\n\t📝 /edit_event_{idx}\n"
        )

    return "\n".join(message_lines)

def favorites_schedules_message(schedules: List[Dict]) -> str:
    if not schedules:
        return no_schedules_message()

    message_lines = ["📅 Расписние расписание: \n"]
    for idx, event in enumerate(schedules, start=1):
        description = event.get("description", "Без описания")
        start_time = event.get("start_time", "Неизвестно")
        lecturer = event.get("organizers", "Неизвестно")
        if hasattr(start_time, "strftime"):
            formatted_time = start_time.strftime("%d.%m.%Y %H:%M")
        else:
            formatted_time = str(start_time)
        message_lines.append(
            f"📌 {description}\n\t🕒 {formatted_time}\n\t👨🏻‍💼 {lecturer}\n\t➖ /remove_favorite_{idx}\n"
        )

    return "\n".join(message_lines)