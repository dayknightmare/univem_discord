from src.helpers.mentores import open_mentores_file, find_mentor_by_id, AgendamentoDB
from src.providers.db import DbUnides
from src.helpers.mail import Mail
from discord.ext import commands
from threading import Thread
import discord


class UnidesMentoria(commands.Cog):
    def __init__(self, client, server: str, db: DbUnides):
        self.client = client
        self.server = server
        self.mentores = open_mentores_file()
        self.db = AgendamentoDB(db)
        self.mail = Mail()

    
    @commands.command(name='mentoria', help="Traz todos os mentores e seus possivéis horários")
    async def mentoria(self, context: discord.ext.commands.context.Context):
        await context.send("Mentores disponíveis:")

        for i in self.mentores:
            horario = self.db.get_next_time_agendamento(i)

            embedVar = discord.Embed(title=f"{i['name']} | #{i['id']}", description=f"{i['hora']} até {i['hora_fim']}\n", color=0x00ff00)
            embedVar.add_field(name="Skills", value=i['desc'], inline=False)

            if horario == -1 or horario == None:
                embedVar.add_field(name="Próximo horário", value='Indisponível', inline=False)

            else:
                embedVar.add_field(name="Próximo horário", value=f"{horario[1]} até {horario[2]}", inline=False)

            await context.send(embed=embedVar)

        await context.send("Para agendar digite !agendar #<número_do_mentor>")       
        await context.send("exemplo:\n!agendar #1")       
        

    @commands.command(name='agendar', help="Realiza o agendamento com um mentor para isso passe o #id para que possamos marcar", pass_context=True)
    async def agendar(self, context: discord.ext.commands.context.Context, id: str = ""):
        if id == "" or not id.startswith("#"):
            await context.send("ID inválido, exemplo de um ID válido: #1")
            return

        id = id.replace("#", '')

        if not id.isnumeric():
            await context.send("ID inválido, exemplo de um ID válido: #1")
            return

        mentor = find_mentor_by_id(self.mentores, int(id))

        if not mentor:
            await context.send("Mentor não encontrado")
            return

        ag = self.db.get_next_time_agendamento(mentor)

        if not ag:
            await context.send("Não aceitamos agendamentos após as 23 horas, tente amanhã por favor")
            return

        if ag == -1:
            await context.send(f"Neste horário o mentor não faz mentorias, apenas entre {mentor['hora']} e {mentor['hora_fim']}")
            return

        self.db.agendar(ag[3], ag[1], ag[2], mentor, str(context.message.author.id))
        Thread(target=self.mail.send_mail, args=[
            mentor['email'], 
            f"""
            {context.message.author.name} e sua equipe pediu uma mentoria as {ag[1]} no hackthon da NASA, quando chegar a hora converse com {context.message.author.name} numa sala do Discord (#mentor-0{mentor['id']}).

            Qualquer dúvida contacte o @suporte para mais informações
            """, 
            f"Agendamento de mentoria as {ag[1]}"
        ]).start()

        await context.send(f"Ficou marcado seu agendamento com o mentor **{mentor['name']}** para o dia {ag[0]} as **{ag[1]} até {ag[2]}**")


    @commands.command(name='agendamentos', help="Lista todos os agendamentos marcados por você")
    async def agendamentos(self, context: discord.ext.commands.context.Context):
        ags = self.db.agendamentos(str(context.message.author.id))

        if len(ags) == 0:
            await context.send("Você ainda não realizou nenhum agendamento")
            return

        for i in ags:
            mentor = find_mentor_by_id(self.mentores, int(i['mentor']))
            embedVar = discord.Embed(title=f"Agendamento | #{i['id']}", description=f"{i['data_hora_inicio']} até {i['data_hora_fim']}\n", color=0x0000ff)
            embedVar.add_field(name="Mentor", value=mentor['name'], inline=False)
            embedVar.add_field(name="Sala", value=f"#mentor-0{mentor['id']}", inline=False)
            await context.send(embed=embedVar)


    @commands.command(name='cancelar', help="Cancela uma mentoria marcada por você, para isso passe o #id da mentoria")
    async def cancelar(self, context: discord.ext.commands.context.Context, id: str):
        if id == "" or not id.startswith("#"):
            await context.send("ID inválido, exemplo de um ID válido: #1")
            return

        id = id.replace("#", '')

        if not id.isnumeric():
            await context.send("ID inválido, exemplo de um ID válido: #1")
            return
        
        ags = self.db.agendamentos(str(context.message.author.id))

        mentoria = None

        for i in ags:
            if int(i['id']) == int(id):
                mentor = find_mentor_by_id(self.mentores, int(i['mentor']))

                Thread(target=self.mail.send_mail, args=[
                    mentor['email'], 
                    f"""
                    {context.message.author.name} cancelou a mentoria que seria realizado as {i['data_hora_inicio']} no canal #mentor-0{mentor['id']}

                    Qualquer dúvida contacte o @suporte para mais informações
                    """, 
                    f"Cancelamento da mentoria das {i['data_hora_inicio']}"
                ]).start()
                self.db.cancelar(int(id))

                await context.send("Agendamento cancelado com sucesso")
                return

        await context.send("Mentoria não encontrada")
        return