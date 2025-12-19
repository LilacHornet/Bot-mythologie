import os
import sys

# Ajouter le chemin parent pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mythology_info import mythology_figures


class LearnService:
    """Service pour les fiches d'apprentissage sur la mythologie."""
    
    def __init__(self):
        self.figures = mythology_figures
    
    def search_figure(self, query: str) -> dict | None:
        """
        Recherche une figure mythologique par son nom.
        Retourne les informations ou None si non trouvée.
        """
        query_lower = query.lower().strip()
        
        # Recherche exacte
        if query_lower in self.figures:
            return self.figures[query_lower]
        
        # Recherche par nom romain
        for key, figure in self.figures.items():
            if figure.get("roman_name", "").lower() == query_lower:
                return figure
        
        # Recherche partielle
        for key, figure in self.figures.items():
            if query_lower in key or query_lower in figure["name"].lower():
                return figure
            if query_lower in figure.get("roman_name", "").lower():
                return figure
        
        return None
    
    def get_all_figures(self) -> list[str]:
        """Retourne la liste de toutes les figures disponibles."""
        return [figure["name"] for figure in self.figures.values()]
    
    def get_figures_by_category(self) -> dict[str, list[str]]:
        """Retourne les figures organisées par catégorie."""
        categories = {
            "Dieux Olympiens": [],
            "Héros": [],
            "Créatures": [],
            "Titans": []
        }
        
        olympians = ["zeus", "poseidon", "hades", "hera", "athena", "apollon", 
                     "artemis", "ares", "aphrodite", "hephaistos", "hermes", "dionysos"]
        heroes = ["heracles", "persee", "thesee", "ulysse", "achille", "jason", "orphee"]
        creatures = ["meduse", "minotaure", "cerbere"]
        titans = ["cronos", "prometheus", "atlas"]
        
        for key, figure in self.figures.items():
            if key in olympians:
                categories["Dieux Olympiens"].append(figure["name"])
            elif key in heroes:
                categories["Héros"].append(figure["name"])
            elif key in creatures:
                categories["Créatures"].append(figure["name"])
            elif key in titans:
                categories["Titans"].append(figure["name"])
        
        return categories
    
    def get_random_figure(self) -> dict:
        """Retourne une figure aléatoire."""
        import random
        key = random.choice(list(self.figures.keys()))
        return self.figures[key]