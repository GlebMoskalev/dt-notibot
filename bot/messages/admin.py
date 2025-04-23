from typing import List


def users_message(names: List[str], begin: int, count: int) -> str:
    names_with_numbers = [f'{number + 1}. {name}' for number, name in enumerate(names)
                          if begin <= number and number < begin + count]
    return 'Список пользователей:\n' + '\n'.join(names_with_numbers)

def user_names_not_found() -> str:
    return 'Не найдено ни одного пользователя'