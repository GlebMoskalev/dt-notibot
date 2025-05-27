from typing import List, Tuple


def admins_message(names: List[str], begin: int, count: int) -> str:
    names_with_numbers = [f'{number + 1}. {name}' for number, name in enumerate(names)
                          if begin <= number and number < begin + count]
    return 'Список администраторов:\n' + '\n'.join(names_with_numbers)

def admin_names_not_found() -> str:
    return 'Не найдено ни одного администратора'

def superadmins_message(names: List[str], begin: int, count: int) -> str:
    names_with_numbers = [f'{number + 1}. {name}' for number, name in enumerate(names)
                          if begin <= number and number < begin + count]
    return 'Список супер-администраторов:\n' + '\n'.join(names_with_numbers)

def friends_message(names: List[str], begin: int, count: int) -> str:
    names_with_numbers = [f'{number + 1}. @{name}' for number, name in enumerate(names)
                          if begin <= number and number < begin + count]
    return 'Список друзей:\n' + '\n'.join(names_with_numbers)

def leaderboards_message(leaders: List[Tuple[str, int]], begin: int, count: int) -> str:
    names_with_numbers = [f'{number + 1}. @{item[0]}: {item[1]} {pluralize_friends(item[1])}' for number, item in enumerate(leaders)
                          if begin <= number and number < begin + count]
    return 'Таблица лидеров:\n' + '\n'.join(names_with_numbers)

def pluralize_friends(n: int) -> str:
    n = abs(n) % 100
    last_digit = n % 10

    if 11 <= n <= 19:
        return "друзей"
    if last_digit == 1:
        return "друг"
    if 2 <= last_digit <= 4:
        return "друга"
    return "друзей"

def superadmin_names_not_found() -> str:
    return 'Не найдено ни одного супер-администратора'