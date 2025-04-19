import asyncpg
import uuid
import secrets
from enum import Enum
from typing import Optional, Dict, Union, List

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
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO users (chat_id, telegram_name, role)
                VALUES ($1, $2, $3)
                ON CONFLICT (chat_id)
                DO UPDATE SET telegram_name = EXCLUDED.telegram_name, role = EXCLUDED.role
                """,
                chat_id, telegram_name, str(role)
            )

    # вряд ли пользователей будет много,
    # поэтому всех выгружаем без пагинации и дело с концом
    async def get_user_names(self) -> Optional[List[str]]:
        print('Get all user names')
        async with self.pool.acquire() as conn:
            result = await conn.fetch(
                "SELECT telegram_name FROM users WHERE role = $1",
                RoleEnum.User
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