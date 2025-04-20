from typing import List


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

def superadmin_names_not_found() -> str:
    return 'Не найдено ни одного супер-администратора'