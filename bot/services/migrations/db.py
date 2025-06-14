import datetime
import enum

from sqlalchemy import create_engine, Column, UUID, BigInteger, String, Enum, TIMESTAMP, JSON, ForeignKey, Integer, \
    DateTime, Boolean, UniqueConstraint, func, union_all, select
from sqlalchemy.orm import declarative_base, relationship
from dotenv import load_dotenv
import os
import uuid



load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL не указан в .env файле")

engine = create_engine(DATABASE_URL)
Base = declarative_base()


class RoleEnum(enum.Enum):
    User = "User"
    Admin = "Admin"
    SuperAdmin = "SuperAdmin"


class SectionEnum(enum.Enum):
    Lecture = "Lecture"
    Break = "Break"


class InviteStatusEnum(enum.Enum):
    Pending = "Pending"
    Approved = "Approved"
    Rejected = "Rejected"

class Friend(Base):
    __tablename__ = 'friends'

    user_id = Column(BigInteger, ForeignKey('users.chat_id'),
                     primary_key=True,
                     nullable=False)
    friend_id = Column(BigInteger, ForeignKey('users.chat_id'),
                       primary_key = True,
                       nullable=False)



class User(Base):
    __tablename__ = 'users'

    chat_id = Column(BigInteger, primary_key=True)
    role = Column(Enum(RoleEnum), nullable=False)
    telegram_name = Column(String(32), nullable=False)
    unique_code = Column(String(32), nullable=False)
    favorite_events = relationship("FavouriteEvent", back_populates="user")

    friends = relationship(
        'User',
        secondary='friends',
        primaryjoin=chat_id == Friend.user_id,
        secondaryjoin=chat_id == Friend.friend_id,
        # back_populates="users"
    )

class Invite(Base):
    __tablename__ = 'invites'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    secret_code = Column(String(20), nullable=False)
    role = Column(Enum(RoleEnum), nullable=False)

class Event(Base):
    __tablename__ = 'events'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    start_time = Column(TIMESTAMP, nullable=False)
    end_time = Column(TIMESTAMP, nullable=False)
    section = Column(Enum(SectionEnum), nullable=False)
    description = Column(String(255), nullable=True)
    organizers = Column(JSON, nullable=True)

    favourite_events = relationship("FavouriteEvent", back_populates="event")


class FavouriteEvent(Base):
    __tablename__ = 'favourite_events'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.chat_id'), nullable=False)
    event_id = Column(UUID(as_uuid=True), 
                     ForeignKey('events.id', ondelete='CASCADE'),
                     nullable=False)

    user = relationship("User", back_populates="favorite_events")
    event = relationship("Event", back_populates="favourite_events")


class NotificatedEvents(Base):
    __tablename__ = 'notificated_events'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(UUID(as_uuid=True), nullable=False)