import psycopg2
import uuid
import secrets
from enum import Enum
from typing import Optional, Dict, Union, Tuple, List

class RoleEnum(str, Enum):
    User = "User"
    Admin = "Admin"
    SuperAdmin = "SuperAdmin"

class DataBase:
    def __init__(self, dsn):
        self.connect = psycopg2.connect(dsn)
        self.cursor = self.connect.cursor()

    def add_users(self, chat_id: int, telegram_name: str, role: Union[str, RoleEnum]) -> None:
        with self.connect:
            self.cursor.execute(
                """
                INSERT INTO users (chat_id, telegram_name, role)
                VALUES (%s, %s, %s)
                ON CONFLICT (chat_id)
                DO UPDATE SET telegram_name = EXCLUDED.telegram_name, role = EXCLUDED.role
                """
                ,
                (chat_id, telegram_name, role)
            )

    def get_user_role(self, chat_id: int) -> Optional[str]:
        with self.connect:
            self.cursor.execute(
                "SELECT role FROM users WHERE chat_id = %s", (chat_id,)
            )
            result = self.cursor.fetchone()
            return result[0] if result else None

    def regenerate_invite_codes(self) -> None:
        with self.connect:
            for role in RoleEnum:
                new_code = secrets.token_urlsafe(12)[:20]
                self.cursor.execute(
                    "SELECT id FROM invites WHERE role = %s", (role.value,)
                )
                existing = self.cursor.fetchone()

                if existing:
                    self.cursor.execute(
                        "UPDATE invites SET secret_code = %s WHERE role = %s",
                        (new_code, role.value)
                    )
                else:
                    self.cursor.execute(
                        "INSERT INTO invites (id, secret_code, role) VALUES (%s, %s, %s)",
                        (str(uuid.uuid4()), new_code, role.value)
                    )

    def check_invite_code(self, code: str) -> Optional[str]:
        with self.connect:
            self.cursor.execute(
                "SELECT role FROM invites WHERE secret_code = %s", (code,)
            )
            result = self.cursor.fetchone()
            return result[0] if result else None

    def get_invite_dict(self) -> Dict[str, str]:
        with self.connect:
            self.cursor.execute("SELECT role, secret_code FROM invites")
            result = self.cursor.fetchall()
            return {row[0]: row[1] for row in result}

    def close(self) -> None:
        if self.cursor:
            self.cursor.close()
        if self.connect:
            self.connect.close()