import enum

from sqlalchemy import create_engine, Column, UUID, BigInteger, String, Enum, TIMESTAMP, JSON, ForeignKey, Integer
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


class User(Base):
    __tablename__ = 'users'

    chat_id = Column(BigInteger, primary_key=True)
    role = Column(Enum(RoleEnum), nullable=False)
    telegram_name = Column(String(32), nullable=False)

    friends_as_first = relationship("Friend",
                                    foreign_keys="Friend.first_chat_id",
                                    back_populates="first_user")
    friends_as_second = relationship("Friend",
                                     foreign_keys="Friend.second_chat_id",
                                     back_populates="second_user")
    sent_friendship_invites = relationship("FriendshipInvite",
                                           foreign_keys="FriendshipInvite.sender_id",
                                           back_populates="sender")
    received_friendship_invites = relationship("FriendshipInvite",
                                               foreign_keys="FriendshipInvite.receiver_id",
                                               back_populates="receiver")
    favorite_events = relationship("FavouriteEvent", back_populates="user")


class Friend(Base):
    __tablename__ = 'friends'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_chat_id = Column(BigInteger, ForeignKey('users.chat_id'),
                           nullable=False)
    second_chat_id = Column(BigInteger, ForeignKey('users.chat_id'),
                            nullable=False)

    first_user = relationship("User", foreign_keys=[first_chat_id],
                              back_populates="friends_as_first")
    second_user = relationship("User", foreign_keys=[second_chat_id],
                               back_populates="friends_as_second")


class Invite(Base):
    __tablename__ = 'invites'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    secret_code = Column(String(20), nullable=False)
    role = Column(Enum(RoleEnum), nullable=False)


class FriendshipInvite(Base):
    __tablename__ = 'friendship_invites'

    id = Column(Integer, primary_key=True, autoincrement=True)
    sender_id = Column(BigInteger, ForeignKey('users.chat_id'), nullable=False)
    receiver_id = Column(BigInteger, ForeignKey('users.chat_id'), nullable=False)
    invite_status = Column(Enum(InviteStatusEnum), nullable=False,
                           default=InviteStatusEnum.Pending)

    sender = relationship("User", foreign_keys=[sender_id],
                          back_populates="sent_friendship_invites")
    receiver = relationship("User", foreign_keys=[receiver_id],
                            back_populates="received_friendship_invites")


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