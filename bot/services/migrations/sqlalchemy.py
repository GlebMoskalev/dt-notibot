import random
from typing import Type

from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from bot.services.migrations.db import Friend, User, Contest


# TODO: Create a repository

def get_active_contest(session: Session):
    return session.query(Contest).first()

def get_users_by_friend_count(session, limit=10):
    return (
        session.query(
            User.telegram_name,
            func.count(Friend.friend_id).label('friend_count')
        )
        .join(Friend, User.chat_id == Friend.user_id)
        .group_by(User.chat_id)
        .order_by(desc('friend_count'))
        .limit(limit)
        .all()
    )

def recreate_invite_code(session: Session, chat_id: int):
    new_code = random.randint(100_000, 1_000_000)
    session.query(User).filter(User.chat_id == chat_id).update(
        {User.unique_code: new_code},
        synchronize_session='fetch'
    )
    session.commit()
    return new_code

def get_user_by_chat_id(session: Session, chat_id:int):
    return session.query(User).filter_by(chat_id=chat_id).first()

def get_user_by_invite_code(session: Session, invite_code: int):
    return session.query(User).filter_by(unique_code=str(invite_code)).first()

def try_add_friend(session: Session, user1: User, user2: User):
    user2_not_friend = user2 not in user1.friends
    user_1_not_friend = user1 not in user2.friends

    if not user2_not_friend and not user_1_not_friend:
        return False

    if user2_not_friend:
        user1.friends.append(user2)
    if user_1_not_friend:
        user2.friends.append(user1)

    session.commit()

    return True