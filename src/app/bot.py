from src.helpers.mail import open_mail_file 
from src.providers.db import DbUnides
from src.helpers.user import UserDB
from discord.ext import commands
import discord
import json
import ast


class Unides(commands.Cog):
    def __init__(self, client, server: str, db: DbUnides):
        self.client = client
        self.server = server
        self.db = UserDB(db)
        self.no_roles = ['unidis', '@everyone', '@here']
        self.mails = open_mail_file()


    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.client.user} está pronto para ser usado")
        guild: discord.Guild = discord.utils.get(self.client.guilds, name=self.server)

        for i in guild.members:
            if not self.db.get_user(i.id):
                roles = []

                for j in i.roles:
                    if j.name in self.no_roles:
                        continue

                    roles.append(j.name)

                print('adding user')
                self.db.add_user(i.name, i.id, json.dumps(roles))


    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        user = self.db.get_user(member.id)

        if user and user['email']:
            await member.send(f'Seja bem vindo novamente {member.name}')
            guild: discord.Guild = discord.utils.get(self.client.guilds, name=self.server)

            for i in ast.literal_eval(user['roles']):
                if i in self.no_roles:
                    continue
                
                await member.add_roles(discord.utils.get(guild.roles, name=i))

            return

        elif user and not user['email']:
            await member.send("Precisamos validar seu email para entrar no hackathon da NASA")
            return

        await member.send('Seja bem vindo ao server do Univem para hackathon da NASA')
        await member.send("Primeiramente gostaria de validar sua inscrição, bem simples")
        await member.send("Use o comando !auth <email>, com isso iremos validar e te autorizar para seus canais")
        

    @commands.command(name='auth', help="Faz a autenticação no server como membro", pass_context=True)
    async def auth(self, context: discord.ext.commands.context.Context, email: str = ''):
        guild: discord.Guild = discord.utils.get(self.client.guilds, name=self.server)

        if not guild:
            return

        if not isinstance(context.channel, discord.channel.DMChannel):
            await context.send(f"{context.message.author.name} Vamos fazer isso no privado, para proteger sua privacidade ta bom!")
            return

        if not email:
            await context.send(f"Por favor nos passe seu email")
            return

        guild: discord.Guild = discord.utils.get(self.client.guilds, name=self.server)

        if not guild:
            return

        user: discord.Member = discord.utils.get(guild.members, name=context.message.author.name)

        if not user:
            await context.send(f"Você não foi encontrado no server do Univem")
            return

        if self.db.get_user_by_email(email):
            await context.send(f"Este email já está em uso, contacte o suporte")
            return

        if email in self.mails:
            role: discord.Role = discord.utils.get(guild.roles, name='PARTICIPANTES')

            await user.add_roles(role)
            await context.send(f"Validação feita com sucesso, volte ao server e verá novos canais")
            await context.send(f"Estamos felizes de o ter como participante, esperamos que se divirta e ganhe!!!")

            self.db.change_user(
                user.id, 
                json.dumps(list(set([*['PARTICIPANTES'], *[i.name for i in user.roles]]))), 
                email
            )

        else:
            await context.send(f"Seu email não foi encontrado, entre em contato com o suporte do evento")