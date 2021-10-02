from datetime import datetime, timedelta, time
from src.providers.db import DbUnides
from dotenv import load_dotenv
from typing import Union
import time
import csv
import ast
import os

load_dotenv()


def round_hour(time: datetime) -> datetime:
    hora = (time.replace(second=0, microsecond=0, minute=0, hour=time.hour) + timedelta(hours=time.minute // 30))

    if hora < time:
        hora += timedelta(minutes=30)

    return hora


class AgendamentoDB:
    def __init__(self, db: DbUnides):
        self.db = db

    
    def get_next_time_agendamento(self, mentor: dict) -> Union[list, None, int]:
        cursor = self.db.open_cursor()
        now = round_hour(datetime.now() + timedelta(hours=int(os.getenv("HORA_GTM"))))
        hora_str = now.strftime("%H:%M")
        hora = time.strptime(hora_str, "%H:%M")
        data_str = now.strftime("%Y-%m-%d")
        
        key = "hora_domingo"

        if data_str == "2021-10-02":
            key = "hora_sabado"

        if len(mentor[key]) == 0:
            return -1 
        
        hora_min = time.strptime(mentor[key][0], "%H:%M")

        if hora_min > hora:
            cursor.close()
            return -1

        cursor.execute(
            """
            SELECT * FROM agendamento WHERE data_dia = ? AND mentor = ? AND data_hora_inicio >= ?
            """, 
            [now.strftime("%Y-%m-%d"), mentor['id'], hora_str]
        )

        aulas = cursor.fetchall()

        print(hora_str)

        for i in aulas:
            ts = time.strptime(i['data_hora_fim'], "%H:%M")

            if i['data_hora_inicio'] == hora_str or ts > hora or time.strftime("%H:%M", ts) not in mentor[key]:
                hora_str = time.strftime("%H:%M", ts)
                hora = time.strptime(hora_str, "%H:%M")

                print(hora_str)

            else:
                break

        if hora > time.strptime("23:00", "%H:%M"):
            cursor.close()
            return None

        final_time = datetime.strptime(f"{data_str} {hora_str}", "%Y-%m-%d %H:%M")
        final_time += timedelta(minutes=30)

        cursor.close()

        return [now.strftime("%d"), hora_str, final_time.strftime("%H:%M"), now.strftime("%Y-%m-%d")]


    def agendar(self, dia: str, hora: str, hora_fim: str, mentor: int, req: str):
        cursor = self.db.open_cursor()
        cursor.execute(
            """
                INSERT INTO agendamento (
                    requisitante, 
                    mentor, 
                    mentor_email, 
                    data_dia, 
                    data_hora_inicio, 
                    data_hora_fim
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, 
            [
                req,
                mentor['id'],
                mentor['email'],
                dia,
                hora,
                hora_fim
            ]
        )

        self.db.commit()
        cursor.close()


    def agendamentos(self, user: str) -> list:
        cursor = self.db.open_cursor()

        now = round_hour(datetime.now() + timedelta(hours=int(os.getenv("HORA_GTM"))))
        data_str = now.strftime("%Y-%m-%d")
        hora_str = now.strftime("%H:%M")

        cursor.execute(
            """
                SELECT * FROM agendamento WHERE data_dia = ? AND data_hora_inicio >= ? AND requisitante = ?
            """, 
            [
                data_str,
                hora_str,
                user,
            ]
        )

        ags = cursor.fetchall()
        cursor.close()

        return ags


    def cancelar(self, id: str):
        cursor = self.db.open_cursor()

        cursor.execute(
            """
                DELETE FROM agendamento WHERE id = ?
            """, 
            [
                id,
            ]
        )

        cursor.close()


def open_mentores_file() -> list:
    mentores = []

    c = 1
    with open('./mentores.csv') as f:
        data = csv.reader(f, delimiter=';', quotechar='"')

        for i in data:
            mentores.append({
                'name': i[0],
                'email': i[1],
                'hora_sabado': ast.literal_eval(i[2]),
                'hora_domingo': ast.literal_eval(i[3]),
                'desc': i[4],
                'id': c
            })

            c += 1

    return mentores


def find_mentor_by_id(mentores: list, id: int) -> Union[dict, None]:
    for i in mentores:
        if i['id'] == id:
            return i

    return None