def no_invite_links_message() -> str:
    return "Ссылки на приглашения не найдены"

def invite_links_message(invite_dict: dict, bot_username: str) -> str:
    if not invite_dict:
        return no_invite_links_message()
    links_message = "Ссылки на приглашения:\n"
    for role, code in invite_dict.items():
        links_message += f"{role}: https://t.me/{bot_username}?start={code}\n\n"
    return links_message