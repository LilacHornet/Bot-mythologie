import warnings
import os
import sys

# Supprimer les avertissements de BeautifulSoup
warnings.filterwarnings("ignore", category=UserWarning)

import wikipedia

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class WikipediaService:
    """Service pour les recherches Wikipedia."""
    
    def __init__(self, lang: str = "fr"):
        self.lang = lang
        wikipedia.set_lang(lang)
    
    def get_mythology_link(self, search_term: str) -> dict:
        """
        Recherche un article Wikipedia sur la mythologie.
        Retourne un dictionnaire avec url, title, summary ou error.
        """
        try:
            # Essayer d'abord avec "mythologie grecque"
            search_query = f"{search_term} mythologie grecque"
            results = wikipedia.search(search_query, results=5)
            
            if not results:
                # Essayer sans précision
                results = wikipedia.search(search_term, results=5)
            
            if not results:
                return {"error": f"Aucun résultat trouvé pour '{search_term}'."}
            
            # Essayer chaque résultat jusqu'à en trouver un valide
            for result in results:
                try:
                    page = wikipedia.page(result, auto_suggest=False)
                    summary = wikipedia.summary(result, sentences=3, auto_suggest=False)
                    
                    return {
                        "title": page.title,
                        "url": page.url,
                        "summary": summary
                    }
                except wikipedia.exceptions.DisambiguationError as e:
                    # Prendre la première option de désambiguïsation
                    if e.options:
                        try:
                            first_option = e.options[0]
                            page = wikipedia.page(first_option, auto_suggest=False)
                            summary = wikipedia.summary(first_option, sentences=3, auto_suggest=False)
                            return {
                                "title": page.title,
                                "url": page.url,
                                "summary": summary
                            }
                        except Exception:
                            continue
                except wikipedia.exceptions.PageError:
                    continue
                except Exception:
                    continue
            
            return {"error": f"Impossible de charger les informations pour '{search_term}'."}
            
        except Exception as e:
            return {"error": f"Erreur lors de la recherche : {str(e)}"}
    
    def search_figure(self, figure_name: str) -> dict:
        """Recherche spécifique pour une figure mythologique."""
        return self.get_mythology_link(figure_name)