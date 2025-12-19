import discord
import os
from dotenv import load_dotenv
load_dotenv()



bot = discord.Client(intents=discord.Intents.all())


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.event
async def on_member_join(member):
    channel = bot.get_channel(1450078155304865855)
    await channel.send(f"{member.mention} nous a rejoints.")








bot.run(os.getenv('DISCORD_TOKEN'))