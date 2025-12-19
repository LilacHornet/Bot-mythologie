import discord
from discord import app_commands
from discord.ext import commands
import os
import sys

# Ajouter le chemin parent pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.wikipedia_service import WikipediaService


class MythologyCog(commands.Cog):
    """Cog pour les commandes liées à la mythologie."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.wikipedia_service = WikipediaService()
    
    @app_commands.command(name="mythology", description="Get Wikipedia link for a mythological figure")
    async def mythology(self, interaction: discord.Interaction, figure: str):
        """Commande pour obtenir le lien Wikipedia d'une figure mythologique."""
        link = self.wikipedia_service.get_mythology_link(figure)
        await interaction.response.send_message(f"**{figure}**: {link}")


async def setup(bot: commands.Bot):
    await bot.add_cog(MythologyCog(bot))