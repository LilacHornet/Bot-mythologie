import discord
from discord import app_commands
from discord.ext import commands
import os
import sys
from typing import Optional

# Ajouter le chemin parent pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.wikipedia_service import WikipediaService
from services.learn_service import LearnService


class MythologyCog(commands.Cog):
    """Cog pour les commandes liées à la mythologie."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.wikipedia_service = WikipediaService()
        self.learn_service = LearnService()
    
    @app_commands.command(name="mythology", description="Get Wikipedia link for a mythological figure")
    @app_commands.describe(figure="Nom de la figure mythologique")
    async def mythology(self, interaction: discord.Interaction, figure: str):
        """Commande pour obtenir le lien Wikipedia d'une figure mythologique."""
        await interaction.response.defer()
        link = self.wikipedia_service.get_mythology_link(figure)
        await interaction.followup.send(f"**{figure}**: {link}")
    
    @app_commands.command(name="learn", description="Apprends tout sur une figure mythologique")
    @app_commands.describe(figure="Nom du dieu, héros ou créature (ex: Zeus, Hercule, Méduse)")
    async def learn(self, interaction: discord.Interaction, figure: str):
        """Affiche une fiche détaillée sur une figure mythologique."""
        await interaction.response.defer()
        
        figure_data = self.learn_service.search_figure(figure)
        
        if not figure_data:
            # Suggérer des figures disponibles
            available = self.learn_service.get_figures_by_category()
            suggestions = []
            for category, names in available.items():
                suggestions.extend(names[:3])
            
            embed = discord.Embed(
                title="❌ Figure non trouvée",
                description=f"Je n'ai pas trouvé d'informations sur **{figure}**.",
                color=discord.Color.red()
            )
            embed.add_field(
                name="💡 Suggestions",
                value=", ".join(suggestions[:10]),
                inline=False
            )
            embed.set_footer(text="Utilisez /figures pour voir toutes les figures disponibles")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        # Créer l'embed principal
        embed = discord.Embed(
            title=f"{figure_data['image_emoji']} {figure_data['name']}",
            description=figure_data["description"],
            color=figure_data["color"]
        )
        
        # Informations générales
        embed.add_field(
            name="🏛️ Titre",
            value=figure_data["title"],
            inline=False
        )
        
        if figure_data.get("roman_name"):
            embed.add_field(
                name="🇮🇹 Nom romain",
                value=figure_data["roman_name"],
                inline=True
            )
        
        embed.add_field(
            name="⚡ Domaine",
            value=figure_data["domain"],
            inline=True
        )
        
        # Symboles
        if figure_data.get("symbols"):
            embed.add_field(
                name="🔮 Symboles",
                value=", ".join(figure_data["symbols"]),
                inline=False
            )
        
        # Famille
        embed.add_field(
            name="👨‍👩‍👧 Parents",
            value=figure_data["parents"],
            inline=True
        )
        
        if figure_data.get("consort"):
            embed.add_field(
                name="💕 Époux/Épouse",
                value=figure_data["consort"],
                inline=True
            )
        
        if figure_data.get("children") and figure_data["children"] != "Aucun":
            embed.add_field(
                name="👶 Enfants",
                value=figure_data["children"],
                inline=True
            )
        
        # Mythes célèbres
        if figure_data.get("famous_myths"):
            embed.add_field(
                name="📜 Mythes célèbres",
                value="• " + "\n• ".join(figure_data["famous_myths"]),
                inline=False
            )
        
        embed.set_footer(text="Utilisez /mythology pour le lien Wikipedia complet")
        
        await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="figures", description="Liste toutes les figures mythologiques disponibles")
    async def figures(self, interaction: discord.Interaction):
        """Affiche la liste de toutes les figures disponibles par catégorie."""
        await interaction.response.defer()
        
        categories = self.learn_service.get_figures_by_category()
        
        embed = discord.Embed(
            title="📚 Figures Mythologiques Disponibles",
            description="Utilisez `/learn <nom>` pour en apprendre plus sur une figure.",
            color=discord.Color.gold()
        )
        
        category_emojis = {
            "Dieux Olympiens": "⚡",
            "Héros": "🦸",
            "Créatures": "🐉",
            "Titans": "🏔️"
        }
        
        for category, figures in categories.items():
            if figures:
                emoji = category_emojis.get(category, "📖")
                embed.add_field(
                    name=f"{emoji} {category}",
                    value=", ".join(figures),
                    inline=False
                )
        
        embed.set_footer(text=f"Total: {sum(len(f) for f in categories.values())} figures")
        
        await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="random_figure", description="Découvre une figure mythologique au hasard")
    async def random_figure(self, interaction: discord.Interaction):
        """Affiche une figure mythologique aléatoire."""
        await interaction.response.defer()
        
        figure_data = self.learn_service.get_random_figure()
        
        embed = discord.Embed(
            title=f"🎲 {figure_data['image_emoji']} {figure_data['name']}",
            description=figure_data["description"],
            color=figure_data["color"]
        )
        
        embed.add_field(
            name="🏛️ Titre",
            value=figure_data["title"],
            inline=False
        )
        
        if figure_data.get("roman_name"):
            embed.add_field(
                name="🇮🇹 Nom romain",
                value=figure_data["roman_name"],
                inline=True
            )
        
        embed.add_field(
            name="⚡ Domaine",
            value=figure_data["domain"],
            inline=True
        )
        
        if figure_data.get("symbols"):
            embed.add_field(
                name="🔮 Symboles",
                value=", ".join(figure_data["symbols"]),
                inline=False
            )
        
        embed.set_footer(text="Utilisez /learn pour plus de détails • /random_figure pour une autre")
        
        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(MythologyCog(bot))