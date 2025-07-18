def start_new_event_message() -> str:
    return 'Чтобы добавить новое событие, ответьте на следующие вопросы:'

def section_event_message() -> str:
    return 'Выберите тип события из представленных ниже вариантов'

def description_event_message() -> str:
    return 'Отлично!\nТеперь отправьте заголовок события: это должно быть одно сообщение. Используйте одно-два предложения для выражения главной темы события.'

# формат имени зависит от того, какая этика в компании. Я ориентируюсь на Контур
def organizers_event_message() -> str:
    return 'Заголовок загружен.\nВведите спикера события в формате ИФ. Если спикеров несколько, укажите их через запятую'

def start_time_event_message() -> str:
    return 'Теперь введите время и дату начала события в следующем формате:\n```\nДень.Месяц Часы:Минуты```\nПример ввода (событие начинается 6 мая в 10:30):\n```\n6.05 10:30```\nВнимание! День и месяц необходимо ввести в числовом формате'

def end_time_event_message() -> str:
    return 'Введите время и дату окончания события в следующем формате:\n```\nДень.Месяц Часы:Минуты```\nПример ввода (событие кончается 6 мая в 11:15):\n```\n6.05 11:15```\nВнимание! День и месяц необходимо ввести в числовом формате'

def end_new_event_message() -> str:
    return 'Новое событие успешно записано!'