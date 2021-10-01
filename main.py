from src.app.mentoria import UnidesMentoria
from src.app.equipe import UnidesEquipe
from src.providers.db import DbUnides
from discord.ext import commands
from src.app.bot import Unides
from dotenv import load_dotenv
import discord
import os

load_dotenv()

if __name__ == "__main__":
    
    token = os.getenv('TOKEN')
    server = os.getenv('SERVER')
    intents = discord.Intents.default()
    intents.members = True

    db = DbUnides()

    client = commands.Bot(command_prefix="!", intents=intents)

    client.add_cog(Unides(client, server, db))
    client.add_cog(UnidesMentoria(client, server, db))
    client.add_cog(UnidesEquipe(client, server, db))

    client.run(token)