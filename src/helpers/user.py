from src.providers.db import DbUnides
from typing import Union


class UserDB:
    def __init__(self, db: DbUnides):
        self.db = db

    
    def commit(self):
        self.db.commit()


    def add_user(self, name: str, discord_id: str, roles: str):
        cursor = self.db.open_cursor()
        cursor.execute(
            f"""
                INSERT INTO users (name, discord_id, roles) VALUES (?, ?, ?)
            """,
            [name, discord_id, roles]
        )

        self.commit()
        cursor.close()


    def get_user(self, discord_id: str) -> Union[dict, None]:
        cursor = self.db.open_cursor()
        cursor.execute(
            f"""
                SELECT * FROM users WHERE discord_id = ? LIMIT 1
            """,
            [discord_id]
        )

        user = cursor.fetchone()
        cursor.close()

        return user


    def get_user_by_email(self, email: str) -> Union[dict, None]:
        cursor = self.db.open_cursor()
        cursor.execute(
            f"""
                SELECT * FROM users WHERE email = ? LIMIT 1
            """,
            [email]
        )

        user = cursor.fetchone()
        cursor.close()

        return user


    def get_all_user(self) -> list:
        cursor = self.db.open_cursor()
        cursor.execute(
            f"""
                SELECT * FROM users
            """,
        )

        user = cursor.fetchall()
        cursor.close()

        return user or []


    def change_user(self, discord_id: str, roles: str, email: str):
        cursor = self.db.open_cursor()
        cursor.execute(
            f"""
                UPDATE users SET roles = ?, email = ? WHERE discord_id = ?
            """,
            [roles, email, discord_id]
        )

        self.commit()
        cursor.close()