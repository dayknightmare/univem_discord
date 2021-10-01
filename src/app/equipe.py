from src.providers.db import DbUnides
from discord.ext import commands
import discord


class UnidesEquipe(commands.Cog):
    def __init__(self, client, server: str, db: DbUnides):
        self.client = client
        self.server = server
        self.db = db

    
    @commands.command(name='perfil', help="Atribui um perfil ao participante.", pass_context=True)
    async def perfil(self, context: discord.ext.commands.context.Context, perfil: str = ""):
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

        user: discord.Member = discord.utils.get(guild.members, name=context.message.author.name)

        if not user:
            await context.send(f"Você não foi encontrado no server do Univem")
            return
            
        role: discord.Role = discord.utils.get(guild.roles, name=cargos[pers.index(perfil)])

        await user.add_roles(role)
        await context.send(f"Você recebeu o cargo de {cargos[pers.index(perfil)]}")