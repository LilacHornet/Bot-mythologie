import discord
import os
from dotenv import load_dotenv
load_dotenv
bot = discord.Client(intents=discord.Intents.all())

bot.run(os.getenv('DISCORD_TOKEN'))