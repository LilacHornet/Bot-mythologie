import discord
from discord import app_commands
from discord.ext import commands
import os
import sys

# Ajouter le chemin parent pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.learn_service import LearnService
from services.wikipedia_service import WikipediaService


class MythologyCog(commands.Cog):
    """Cog pour les commandes d'apprentissage sur la mythologie."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.learn_service = LearnService()
        self.wikipedia_service = WikipediaService()
    
    @app_commands.command(name="learn", description="Apprends sur une figure mythologique")
    @app_commands.describe(figure="Le nom de la figure mythologique (ex: Zeus, Hercule, Méduse)")
    async def learn(self, interaction: discord.Interaction, figure: str):
        """Affiche les informations sur une figure mythologique."""
        await interaction.response.defer()
        
        result = self.learn_service.search_figure(figure)
        
        if not result:
            await interaction.followup.send(
                f"❌ Je n'ai pas trouvé d'informations sur **{figure}**.\n"
                f"Utilisez `/learnfigures` pour voir la liste des figures disponibles.",
                ephemeral=True
            )
            return
        
        embed = discord.Embed(
            title=f"🏛️ {result['name']}",
            description=result["description"],
            color=result.get("color", discord.Color.gold())
        )
        
        if result.get("roman_name"):
            embed.add_field(
                name="🏛️ Nom romain",
                value=result["roman_name"],
                inline=True
            )
        
        if result.get("symbol"):
            embed.add_field(
                name="⚜️ Symboles",
                value=result["symbol"],
                inline=True
            )
        
        if result.get("domain"):
            embed.add_field(
                name="👑 Domaine",
                value=result["domain"],
                inline=True
            )
        
        if result.get("parents"):
            embed.add_field(
                name="👨‍👩‍👧 Parents",
                value=result["parents"],
                inline=True
            )
        
        if result.get("famous_myths"):
            embed.add_field(
                name="📜 Mythes célèbres",
                value="\n".join([f"• {myth}" for myth in result["famous_myths"]]),
                inline=False
            )
        
        await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="learnfigures", description="Liste toutes les figures mythologiques disponibles")
    async def learnfigures(self, interaction: discord.Interaction):
        """Affiche la liste des figures mythologiques disponibles."""
        categories = self.learn_service.get_figures_by_category()
        
        embed = discord.Embed(
            title="📚 Figures Mythologiques Disponibles",
            description="Utilisez `/learn [nom]` pour en savoir plus sur une figure.",
            color=discord.Color.blue()
        )
        
        for category, figures in categories.items():
            if figures:
                embed.add_field(
                    name=f"🏛️ {category}",
                    value=", ".join(figures),
                    inline=False
                )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="randomfigure", description="Découvre une figure mythologique au hasard")
    async def random_figure(self, interaction: discord.Interaction):
        """Affiche une figure mythologique aléatoire."""
        await interaction.response.defer()
        
        result = self.learn_service.get_random_figure()
        
        embed = discord.Embed(
            title=f"🎲 {result['name']}",
            description=result["description"],
            color=result.get("color", discord.Color.gold())
        )
        
        if result.get("roman_name"):
            embed.add_field(
                name="🏛️ Nom romain",
                value=result["roman_name"],
                inline=True
            )
        
        if result.get("symbol"):
            embed.add_field(
                name="⚜️ Symboles",
                value=result["symbol"],
                inline=True
            )
        
        if result.get("domain"):
            embed.add_field(
                name="👑 Domaine",
                value=result["domain"],
                inline=True
            )
        
        embed.set_footer(text="Utilisez /learn pour chercher une figure spécifique")
        
        await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="mythology", description="Recherche un article Wikipedia sur la mythologie")
    @app_commands.describe(recherche="Le sujet à rechercher (ex: Zeus, Guerre de Troie, Olympe)")
    async def mythology(self, interaction: discord.Interaction, recherche: str):
        """Recherche un lien Wikipedia sur la mythologie."""
        await interaction.response.defer()
        
        result = self.wikipedia_service.get_mythology_link(recherche)
        
        if result.startswith("http"):
            embed = discord.Embed(
                title=f"📖 Wikipedia : {recherche}",
                description=f"Voici le lien Wikipedia pour en savoir plus :",
                color=discord.Color.blue()
            )
            embed.add_field(
                name="🔗 Lien",
                value=result,
                inline=False
            )
            embed.set_footer(text="🏛️ Source : Wikipedia")
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send(
                f"❌ {result}",
                ephemeral=True
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(MythologyCog(bot))