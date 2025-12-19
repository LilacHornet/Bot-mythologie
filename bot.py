import discord
from discord.ext import commands
from config import DISCORD_TOKEN, WELCOME_CHANNEL_ID


class MythologyBot(commands.Bot):
    """Bot principal de mythologie."""
    
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents)
    
    async def setup_hook(self):
        """Charge les cogs au démarrage."""
        await self.load_extension("cogs.mythology_cog")
        await self.load_extension("cogs.quiz_cog")
        await self.tree.sync()
    
    async def on_ready(self):
        print(f'We have logged in as {self.user}')
    
    async def on_member_join(self, member: discord.Member):
        channel = self.get_channel(WELCOME_CHANNEL_ID)
        if channel:
            await channel.send(f"{member.mention} nous a rejoints.")


def main():
    bot = MythologyBot()
    bot.run(DISCORD_TOKEN)


if __name__ == "__main__":
    main()