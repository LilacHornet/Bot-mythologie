import os
import sys
import random
import discord

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mythology_info import mythology_figures, get_figure, get_figures_by_category


class LearnService:
    """Service pour les informations sur les figures mythologiques."""
    
    def __init__(self):
        self.figures = mythology_figures
    
    def search_figure(self, name: str) -> dict | None:
        """Recherche une figure mythologique par son nom."""
        return get_figure(name)
    
    def get_random_figure(self) -> dict:
        """Retourne une figure mythologique aléatoire."""
        return random.choice(list(self.figures.values()))
    
    def get_all_figures(self) -> list[str]:
        """Retourne la liste de toutes les figures."""
        return [figure["name"] for figure in self.figures.values()]
    
    def get_figures_by_category(self) -> dict[str, list[str]]:
        """Retourne les figures groupées par catégorie."""
        return get_figures_by_category()
    
    def get_figure_count(self) -> int:
        """Retourne le nombre de figures."""
        return len(self.figures)
    
    def build_figure_embed(self, figure: dict) -> discord.Embed:
        """Construit l'embed pour une figure mythologique."""
        emoji = figure.get("image_emoji", "🏛️")
        color = figure.get("color", 0xFFD700)
        
        embed = discord.Embed(
            title=f"{emoji} {figure['name']}",
            description=figure.get("description", ""),
            color=color
        )
        
        # Champs principaux
        fields = [
            ("🏛️ Nom romain", figure.get("roman_name")),
            ("👑 Titre", figure.get("title")),
            ("⚜️ Domaine", figure.get("domain")),
            ("👨‍👩‍👧 Parents", figure.get("parents")),
            ("👫 Fratrie", figure.get("siblings")),
            ("💑 Époux/Épouse", figure.get("consort")),
            ("👶 Enfants", figure.get("children"))
        ]
        
        for name, value in fields:
            if value:
                embed.add_field(name=name, value=value, inline=True)
        
        # Symboles
        if figure.get("symbols"):
            symbols = ", ".join(figure["symbols"]) if isinstance(figure["symbols"], list) else figure["symbols"]
            embed.add_field(name="🔱 Symboles", value=symbols, inline=True)
        
        # Mythes célèbres
        if figure.get("famous_myths"):
            myths_text = "\n".join([f"• {myth}" for myth in figure["famous_myths"]])
            embed.add_field(name="📜 Mythes célèbres", value=myths_text, inline=False)
        
        return embed