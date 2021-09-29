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

        cursor.execute(
            """
                CREATE TABLE agendamento (
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    requisitante TEXT,
                    mentor TEXT,
                    mentor_email TEXT,
                    data_dia DATE,
                    data_hora_inicio DATETIME,
                    data_hora_fim DATETIME
                )
            """
        )

        self.commit()
        cursor.close()


    def commit(self):
        self.db.commit()
        