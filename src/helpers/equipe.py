from src.providers.db import DbUnides


class EquipeDB:
    def __init__(self, db: DbUnides):
        self.db = db

    
    def create_equipe(self, dono: str) -> int:
        cursor = self.db.open_cursor()

        cursor.execute("INSERT INTO equipe (criador) VALUES (?)", [dono])
        self.db.commit()

        return cursor.lastrowid