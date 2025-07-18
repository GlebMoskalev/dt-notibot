import random

import asyncpg
import uuid
import json
import secrets
from enum import Enum
from typing import Optional, Dict, Union, List
from datetime import datetime
from bot.services.migrations.db import SectionEnum

from bot.services.migrations.db import User

from bot.services.migrations.db import User

class RoleEnum(str, Enum):
    User = "User"
    Admin = "Admin"
    SuperAdmin = "SuperAdmin"

class DataBase:
    def __init__(self, dsn: str) -> None:
        self.dsn: str = dsn
        self.pool: Optional[asyncpg.Pool] = None

    async def connect(self) -> None:
        self.pool = await asyncpg.create_pool(self.dsn)

    async def add_users(self, chat_id: int, telegram_name: Optional[str], role: Union[str, RoleEnum]) -> None:
        new_code = random.randint(100_000, 1_000_000)
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO users (chat_id, telegram_name, role, unique_code)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (chat_id)
                DO UPDATE SET telegram_name = EXCLUDED.telegram_name, role = EXCLUDED.role
                """,
                chat_id, telegram_name, str(role), str(new_code)
            )


    async def get_invite_code(self, chat_id: int):
        async with self.pool.acquire() as conn:
            result = await conn.fetchrow(
                "SELECT unique_code FROM users WHERE chat_id = $1",
                chat_id
            )
            return result["unique_code"]

    async def get_user_by_code(self, code: int) -> Optional[User]:
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(
                "SELECT * FROM users WHERE unique_code = $1",
                str(code)
            )

    async def get_user_by_id(self, code: int) -> Optional[User]:
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(
                "SELECT * FROM users WHERE unique_code = $1",
                str(code)
            )

    async def regenerate_invite_code(self, chat_id: int) -> int:
        new_code = random.randint(100_000, 1_000_000)
        async with self.pool.acquire() as conn:
                await conn.execute(
                    "UPDATE users SET unique_code = $1 WHERE chat_id = $2",
                    str(new_code), chat_id
                )
        return new_code

    async def add_friend(self, sender_id: int, receiver_id: int):
        async with self.pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO friends (sender_chat_id, receiver_chat_id) VALUES ($1, $2)",
                sender_id, receiver_id
            )

    # вряд ли сущностей будет много,
    # поэтому всех выгружаем без пагинации и дело с концом
    async def get_all_names(self, role: RoleEnum) -> Optional[List[str]]:
        print(f'Get all {role} names')
        async with self.pool.acquire() as conn:
            result = await conn.fetch(
                "SELECT telegram_name FROM users WHERE role = $1",
                role
            )
            return [item['telegram_name'] for item in result] if result else None

    async def get_user_role(self, chat_id: int) -> Optional[str]:
        async with self.pool.acquire() as conn:
            result = await conn.fetchrow(
                "SELECT role FROM users WHERE chat_id = $1", chat_id
            )
            return result["role"] if result else None

    async def regenerate_invite_codes(self) -> None:
        async with self.pool.acquire() as conn:
            for role in RoleEnum:
                new_code: str = secrets.token_urlsafe(12)[:20]
                existing = await conn.fetchrow(
                    "SELECT id FROM invites WHERE role = $1", role.value
                )

                if existing:
                    await conn.execute(
                        "UPDATE invites SET secret_code = $1 WHERE role = $2",
                        new_code, role.value
                    )
                else:
                    await conn.execute(
                        "INSERT INTO invites (id, secret_code, role) VALUES ($1, $2, $3)",
                        str(uuid.uuid4()), new_code, role.value
                    )

    async def check_invite_code(self, code: str) -> Optional[str]:
        async with self.pool.acquire() as conn:
            result = await conn.fetchrow(
                "SELECT role FROM invites WHERE secret_code = $1", code
            )
            return result["role"] if result else None

    async def get_invite_dict(self) -> Dict[str, str]:
        async with self.pool.acquire() as conn:
            result = await conn.fetch("SELECT role, secret_code FROM invites")
            return {row["role"]: row["secret_code"] for row in result}

    async def close(self) -> None:
        if self.pool:
            await self.pool.close()
            self.pool = None


    async def get_event(self, event_id: str) -> Dict:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT id, start_time, end_time, section, description, organizers
                FROM events
                WHERE id=$1
                """,
                event_id
            )

            event = \
                {
                    "id": str(row["id"]),
                    "start_time": row["start_time"],
                    "end_time": row["end_time"],
                    "section": row["section"],
                    "description": row["description"],
                    "organizers": row["organizers"]
                }
                
            while not isinstance(event['organizers'], list):
                event['organizers'] = json.loads(event['organizers'])

            return event

    async def get_events_paginated(self, limit: int = 5, offset: int = 0) -> tuple[List[Dict], int]:
        async with self.pool.acquire() as conn:
            events = await conn.fetch(
                """
                SELECT id, start_time, end_time, section, description, organizers
                FROM events
                ORDER BY start_time
                LIMIT $1 OFFSET $2
                """,
                limit, offset
            )

            total_count = await conn.fetchval(
                "SELECT COUNT(*) FROM events"
            )

            formatted_events = [
                {
                    "id": str(row["id"]),
                    "start_time": row["start_time"],
                    "end_time": row["end_time"],
                    "section": row["section"],
                    "description": row["description"],
                    "organizers": row["organizers"]
                }
                for row in events
            ]

            return formatted_events, total_count

    async def add_favorite(self, user_id: int, event_id: str) -> None:
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO favourite_events (user_id, event_id)
                VALUES ($1, $2)
                ON CONFLICT DO NOTHING
                """,
                user_id, event_id
            )

    async def is_event_favorite(self, user_id: int, event_id: str) -> bool:
        async with self.pool.acquire() as conn:
            result = await conn.fetchval(
                """
                SELECT 1 FROM favourite_events
                WHERE user_id = $1 AND event_id = $2
                """,
                user_id, event_id
            )
            return result is not None

    async def remove_favorite(self, user_id: int, event_id: str) -> None:
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                DELETE FROM favourite_events
                WHERE user_id = $1 AND event_id = $2
                """,
                user_id, event_id
            )

    async def remove_event(self, event_id: str) -> None:
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                DELETE FROM events
                WHERE id = $1
                """,
                event_id
            )

    async def get_favorite_events_paginated(self, user_id: int, limit: int = 5,
                                            offset: int = 0) -> tuple[List[Dict], int]:
        async with self.pool.acquire() as conn:
            events = await conn.fetch(
                """
                SELECT e.id, e.start_time, e.end_time, e.section, e.description, e.organizers
                FROM events e
                JOIN favourite_events f ON e.id = f.event_id
                WHERE f.user_id = $1
                ORDER BY e.start_time
                LIMIT $2 OFFSET $3
                """,
                user_id, limit, offset
            )

            total_count = await conn.fetchval(
                """
                SELECT COUNT(*)
                FROM favourite_events
                WHERE user_id = $1
                """,
                user_id
            )

            formatted_events = [
                {
                    "id": str(row["id"]),
                    "start_time": row["start_time"],
                    "end_time": row["end_time"],
                    "section": row["section"],
                    "description": row["description"],
                    "organizers": row["organizers"]
                }
                for row in events
            ]

            return formatted_events, total_count
    
    async def get_users_by_favorite_events(self, event_ids: List) -> List[str]:
        async with self.pool.acquire() as conn:
            users = await conn.fetch(
                    """
                    SELECT DISTINCT(user_id)
                    FROM favourite_events
                    WHERE event_id = ANY($1)
                    """,
                    event_ids
                )
            return [user['user_id'] for user in users]

    def get_event_sections(self) -> List[str]:
        all_sections = list(SectionEnum)
        return [section.value for section in all_sections]
    
    async def add_event(
        self,
        section: str,
        description: str,
        organizers: List[str],
        start_time: datetime,
        end_time: datetime
    ) -> None:
        if not all([section, description, organizers]):
            raise ValueError("Missing required fields")

        if end_time <= start_time:
            raise ValueError("End time must be after start time")
        
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO events (
                    id,
                    section,
                    description,
                    organizers,
                    start_time,
                    end_time
                ) VALUES ($1, $2, $3, $4, $5, $6)
                """,
                str(uuid.uuid4()),
                section,
                description,
                json.dumps(organizers, ensure_ascii=False),
                start_time,
                end_time
            )

    async def update_event(
            self,
            event_id: str,
            section: str,
            description: str,
            organizers: List[str],
            start_time: datetime,
            end_time: datetime
        ) -> None:
            if end_time <= start_time:
                raise ValueError("End time must be after start time")
            
            async with self.pool.acquire() as conn:
                await conn.execute(
                    """
                    UPDATE events
                    SET section=$2,
                        description=$3,
                        organizers=$4,
                        start_time=$5,
                        end_time=$6
                    WHERE id=$1
                    """,
                    event_id,
                    section,
                    description,
                    json.dumps(organizers, ensure_ascii=False),
                    start_time,
                    end_time
                )
    
    async def add_notificated_event(self, event_id: str) -> None:
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO notificated_events (
                    event_id
                ) VALUES ($1)
                """,
                event_id
            )
    
    async def get_notificated_events(self) -> List:
        async with self.pool.acquire() as conn:
            events = await conn.fetch(
                """
                SELECT DISTINCT(event_id)
                FROM notificated_events
                """
            )

            return list([str(row['event_id']) for row in events])