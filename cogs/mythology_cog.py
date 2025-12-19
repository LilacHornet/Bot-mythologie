import discord
from discord import app_commands
from discord.ext import commands
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.learn_service import LearnService
from services.wikipedia_service import WikipediaService


class MythologyCog(commands.Cog):
    """Cog pour les commandes d'apprentissage."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.learn_service = LearnService()
        self.wikipedia_service = WikipediaService()
    
    @app_commands.command(name="learn", description="Apprends sur une figure mythologique")
    @app_commands.describe(figure="Le nom de la figure (ex: Zeus, Hercule)")
    async def learn(self, interaction: discord.Interaction, figure: str):
        """Affiche les informations sur une figure mythologique."""
        await interaction.response.defer()
        
        result = self.learn_service.search_figure(figure)
        
        if not result:
            await interaction.followup.send(
                f"❌ Aucune info sur **{figure}**.\n"
                f"💡 Utilisez `/learnfigures` pour voir la liste.\n"
                f"🔍 Ou `/mythology {figure}` pour chercher sur Wikipedia.",
                ephemeral=True
            )
            return
        
        embed = self.learn_service.build_figure_embed(result)
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
        
        category_emojis = {
            "Dieux Olympiens": "⚡",
            "Héros": "🦸",
            "Créatures": "🐉",
            "Titans": "🗿"
        }
        
        for category, figures in categories.items():
            if figures:
                emoji = category_emojis.get(category, "🏛️")
                embed.add_field(
                    name=f"{emoji} {category}",
                    value=", ".join(sorted(figures)),
                    inline=False
                )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="randomfigure", description="Découvre une figure mythologique au hasard")
    async def random_figure(self, interaction: discord.Interaction):
        """Affiche une figure mythologique aléatoire."""
        await interaction.response.defer()
        
        result = self.learn_service.get_random_figure()
        embed = self.learn_service.build_figure_embed(result)
        embed.set_footer(text="🎲 Figure aléatoire • Utilisez /learn pour chercher une figure spécifique")
        
        await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="mythology", description="Recherche un article Wikipedia sur la mythologie")
    @app_commands.describe(recherche="Le sujet à rechercher (ex: Zeus, Guerre de Troie, Olympe)")
    async def mythology(self, interaction: discord.Interaction, recherche: str):
        """Recherche un lien Wikipedia sur la mythologie."""
        await interaction.response.defer()
        
        # Recherche sur Wikipedia
        result = self.wikipedia_service.get_mythology_link(recherche)
        
        # Vérifier que result est bien un dictionnaire
        if not isinstance(result, dict):
            await interaction.followup.send(
                f"❌ Erreur inattendue lors de la recherche.",
                ephemeral=True
            )
            return
        
        # Vérifier si erreur
        if "error" in result:
            await interaction.followup.send(
                f"❌ {result['error']}\n💡 Essayez avec un autre terme.",
                ephemeral=True
            )
            return
        
        # Vérifier que les clés nécessaires existent
        if "title" not in result or "url" not in result:
            await interaction.followup.send(
                f"❌ Impossible de récupérer les informations pour '{recherche}'.",
                ephemeral=True
            )
            return
        
        # Construire l'embed
        embed = discord.Embed(
            title=f"📖 {result['title']}",
            url=result['url'],
            description=result.get('summary', 'Aucun résumé disponible.'),
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="🔗 Lien Wikipedia",
            value=f"[Lire l'article complet]({result['url']})",
            inline=False
        )
        
        embed.set_footer(text="🏛️ Source : Wikipedia • Mythologie Grecque")
        
        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(MythologyCog(bot))