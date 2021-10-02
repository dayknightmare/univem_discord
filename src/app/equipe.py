from src.helpers.equipe import EquipeDB
from src.providers.db import DbUnides
from discord.ext import commands
from dotenv import load_dotenv
import datetime
import discord
import os

load_dotenv()


class UnidesEquipe(commands.Cog):
    def __init__(self, client, server: str, db: DbUnides):
        self.client = client
        self.server = server
        self.db = EquipeDB(db)

        for i in self.client.guilds:
            print(i) 

    
    @commands.command(name='perfil', help="Atribui um perfil ao participante.", pass_context=True)
    async def perfil(self, context: discord.ext.commands.context.Context, perfil: str = ""):
        guild: discord.Guild = discord.utils.get(self.client.guilds, name=self.server)

        if not guild:
            return

        pers = ['dev', 'mkt', 'neg', 'dsg']
        cargos = ["Desenvolvedor de sistemas", "Marketing", "Negócios", "Designer"]

        if perfil.lower() not in pers:
            await context.send("Perfil não encontrado, estes são os perfis que temos:")

            for index, i in enumerate(pers):
                await context.send(f"{i} - {cargos[index]}")

            await context.send("Digite !perfil <sigla_perfil>")

            return

        guild: discord.Guild = discord.utils.get(self.client.guilds, name=self.server)

        if not guild:
            return

        user: discord.Member = discord.utils.get(guild.members, id=context.message.author.id)

        if not user:
            await context.send(f"Você não foi encontrado no server do Univem")
            return
            
        role: discord.Role = discord.utils.get(guild.roles, name=cargos[pers.index(perfil)])

        await user.add_roles(role)
        await context.send(f"Você recebeu o cargo de {cargos[pers.index(perfil)]}")


    @commands.command(name='criaequipe', help="Cria uma equipe.")
    async def criaequipe(self, context: discord.ext.commands.context.Context):
        guild: discord.Guild = discord.utils.get(self.client.guilds, name=self.server)

        if not guild:
            return

        date = datetime.datetime(2021, 10, 2, 10, 0, 0, 0)
        now = datetime.datetime.now() + datetime.timedelta(hours=int(os.getenv("HORA_GTM")))

        if now < date:
            return 

        role_par: discord.Role = discord.utils.get(guild.roles, name='PARTICIPANTES')
        role_fac: discord.Role = discord.utils.get(guild.roles, name='FACILITADORES')
        role_men: discord.Role = discord.utils.get(guild.roles, name='MENTORES')
        user: discord.Member = discord.utils.get(guild.members, id=context.message.author.id)

        if role_par not in user.roles:
            return

        id = self.db.create_equipe(str(context.author.id))
        
        await guild.create_role(name=f"equipe-0{id}")
        role: discord.Role = discord.utils.get(guild.roles, name=f"equipe-0{id}")

        user: discord.Member = discord.utils.get(guild.members, id=context.message.author.id)
        await user.add_roles(role)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True),
            role: discord.PermissionOverwrite(read_messages=True),
            role_men: discord.PermissionOverwrite(read_messages=True),
            role_par: discord.PermissionOverwrite(read_messages=True, send_messages=False),
            role_fac: discord.PermissionOverwrite(read_messages=True),
        }

        cat = await guild.create_category(f"EQUIPE-0{id}")

        channel = await guild.create_text_channel(f"equipe-0{id}", overwrites=overwrites, category=cat)
        channel_voice = await guild.create_voice_channel(f"voz-equipe-0{id}", overwrites=overwrites, category=cat)

        link = await channel.create_invite(max_uses=1, unique=True)

        await user.send(f"Link de acesso para #equipe-0{id}")
        await user.send(link)

    
    @commands.command(name='add', help="Adiciona membro ao canal de equipe", pass_context=True)
    async def add_member(self, context: discord.ext.commands.context.Context, member: discord.Member):
        guild: discord.Guild = discord.utils.get(self.client.guilds, name=self.server)

        if not guild:
            return

        role: discord.Role = discord.utils.get(guild.roles, name='PARTICIPANTES')
        user: discord.Member = discord.utils.get(guild.members, id=context.message.author.id)

        if role not in user.roles:
            return

        if not isinstance(context.channel, discord.channel.TextChannel):
            await context.send("Comando válido apenas em canais")
            return

        if not context.channel.name.startswith("equipe-0"):
            await context.send("Comando válido apenas em canal de equipe")
            return
            
        if not isinstance(member, discord.Member):
            await context.send("Membro não encontrado")
            return

        role: discord.Role = discord.utils.get(guild.roles, name=context.channel.name)
        link = await context.channel.create_invite(max_uses=1, unique=True, )

        await member.send(f"Link de acesso para #{context.channel.name}")
        await member.send(link)
        await context.send("Convite enviado")
        await member.add_roles(role)
