import os
import sys

# Ajouter le chemin parent pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.figures import mythology_figures
import random


class LearnService:
    """Service pour les informations sur les figures mythologiques."""
    
    def __init__(self):
        self.figures = mythology_figures
    
    def search_figure(self, name: str) -> dict | None:
        """Recherche une figure mythologique par son nom."""
        name_lower = name.lower().strip()
        
        # Recherche exacte
        for figure in self.figures:
            if self._matches_figure(figure, name_lower):
                return figure
        
        # Recherche partielle
        for figure in self.figures:
            if self._partial_match(figure, name_lower):
                return figure
        
        return None
    
    def _matches_figure(self, figure: dict, name: str) -> bool:
        """Vérifie si le nom correspond exactement à une figure."""
        if figure["name"].lower() == name:
            return True
        if figure.get("roman_name", "").lower() == name:
            return True
        return name in [alias.lower() for alias in figure.get("aliases", [])]
    
    def _partial_match(self, figure: dict, name: str) -> bool:
        """Vérifie si le nom correspond partiellement à une figure."""
        if name in figure["name"].lower():
            return True
        if name in figure.get("roman_name", "").lower():
            return True
        return any(name in alias.lower() for alias in figure.get("aliases", []))
    
    def get_random_figure(self) -> dict:
        """Retourne une figure mythologique aléatoire."""
        return random.choice(self.figures)
    
    def get_all_figures(self) -> list[str]:
        """Retourne la liste de toutes les figures."""
        return [figure["name"] for figure in self.figures]
    
    def get_figures_by_category(self) -> dict[str, list[str]]:
        """Retourne les figures groupées par catégorie."""
        categories = {}
        for figure in self.figures:
            category = figure.get("category", "Autre")
            if category not in categories:
                categories[category] = []
            categories[category].append(figure["name"])
        return categories
    
    def get_figure_count(self) -> int:
        """Retourne le nombre de figures."""
        return len(self.figures)