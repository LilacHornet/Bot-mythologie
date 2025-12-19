import discord
from discord import app_commands
from discord.ext import commands
import os
import sys

# Ajouter le chemin parent pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.funfacts import get_random_funfact, get_funfact_embed, FUNFACTS


class FunfactCog(commands.Cog):
    """Cog pour les funfacts."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @app_commands.command(name="funfact", description="Affiche un fait amusant sur la mythologie grecque")
    async def funfact(self, interaction: discord.Interaction):
        """Affiche un funfact aléatoire."""
        funfact = get_random_funfact()
        embed = get_funfact_embed(funfact)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="funfactcount", description="Affiche le nombre de funfacts disponibles")
    async def funfact_count(self, interaction: discord.Interaction):
        """Affiche le nombre de funfacts."""
        count = len(FUNFACTS)
        
        # Compter par catégorie
        categories = {}
        for fact in FUNFACTS:
            cat = fact["category"]
            categories[cat] = categories.get(cat, 0) + 1
        
        embed = discord.Embed(
            title="📊 Statistiques Fun Facts",
            description=f"**{count}** fun facts disponibles !",
            color=discord.Color.blue()
        )
        
        # Afficher les catégories
        cat_text = "\n".join([f"• **{cat}**: {num}" for cat, num in sorted(categories.items())])
        embed.add_field(
            name="📂 Par catégorie",
            value=cat_text,
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(FunfactCog(bot))