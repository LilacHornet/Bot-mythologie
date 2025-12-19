import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} est connecté!')
    try:
        synced = await bot.tree.sync()
        print(f"Synchronisé {len(synced)} commande(s)")
    except Exception as e:
        print(f"Erreur de synchronisation: {e}")

async def load_cogs():
    await bot.load_extension("cogs.mythology_cog")
    await bot.load_extension("cogs.quiz")
    await bot.load_extension("cogs.daily_myth_cog")
    await bot.load_extension("cogs.funfact_cog")

@bot.event
async def setup_hook():
    await load_cogs()

bot.run(os.getenv('DISCORD_TOKEN'))