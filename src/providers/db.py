from typing import Union
import sqlite3
import os

class DbUnides:
    def __init__(self):
        exists = False

        if os.path.exists('./database.sqlite3'):
            exists = True

        self.db = sqlite3.connect('./database.sqlite3')
        self.db.row_factory = self.dict_cursor

        if not exists:
            self.__create_tables()


    def dict_cursor(self, cursor: sqlite3.Cursor, row) -> dict:
        d = {}

        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]

        return d
            

    def open_cursor(self) -> sqlite3.Cursor:
        return self.db.cursor()


    def __create_tables(self):
        print('CREATING TABLES')
        cursor = self.open_cursor()
        cursor.execute(
            """
                CREATE TABLE users (
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    email TEXT,
                    discord_id TEXT,
                    roles TEXT
                )
            """
        )

        self.commit()
        cursor.close()


    def commit(self):
        self.db.commit()
        

    def add_user(self, name: str, discord_id: str, roles: str):
        cursor = self.open_cursor()
        cursor.execute(
            f"""
                INSERT INTO users (name, discord_id, roles) VALUES (?, ?, ?)
            """,
            [name, discord_id, roles]
        )

        self.commit()
        cursor.close()


    def get_user(self, discord_id: str) -> Union[dict, None]:
        cursor = self.open_cursor()
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
        cursor = self.open_cursor()
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
        cursor = self.open_cursor()
        cursor.execute(
            f"""
                SELECT * FROM users
            """,
        )

        user = cursor.fetchall()
        cursor.close()

        return user or []


    def change_user(self, discord_id: str, roles: str, email: str):
        cursor = self.open_cursor()
        cursor.execute(
            f"""
                UPDATE users SET roles = ?, email = ? WHERE discord_id = ?
            """,
            [roles, email, discord_id]
        )

        self.commit()
        cursor.close()