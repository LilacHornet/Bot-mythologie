import wikipedia


class WikipediaService:
    """Service pour les recherches Wikipedia."""
    
    def __init__(self, lang: str = "fr"):
        self.lang = lang
    
    def get_mythology_link(self, figure_name: str) -> str:
        """Récupère le lien Wikipedia pour une figure mythologique."""
        try:
            wikipedia.set_lang(self.lang)
            return self._search_and_get_url(figure_name)
        except wikipedia.exceptions.PageError:
            return f"Aucune page Wikipedia trouvée pour '{figure_name}'."
        except wikipedia.exceptions.DisambiguationError as e:
            return self._handle_disambiguation(e)
        except Exception as e:
            return f"Erreur lors de la recherche: {str(e)}"
    
    def _search_and_get_url(self, figure_name: str) -> str:
        """Recherche et retourne l'URL Wikipedia."""
        search_results = wikipedia.search(figure_name + " mythologie")
        
        if not search_results:
            return f"Aucun résultat trouvé pour '{figure_name}'."
        
        page = wikipedia.page(search_results[0])
        return page.url
    
    def _handle_disambiguation(self, error: wikipedia.exceptions.DisambiguationError) -> str:
        """Gère les erreurs de désambiguïsation."""
        try:
            if error.options:
                page = wikipedia.page(error.options[0])
                return page.url
        except Exception:
            pass
        return "Plusieurs résultats trouvés. Soyez plus précis dans votre recherche."
    
    def get_summary(self, figure_name: str, sentences: int = 3) -> str:
        """Récupère un résumé Wikipedia."""
        try:
            wikipedia.set_lang(self.lang)
            search_results = wikipedia.search(figure_name + " mythologie")
            
            if not search_results:
                return f"Aucun résultat trouvé pour '{figure_name}'."
            
            return wikipedia.summary(search_results[0], sentences=sentences)
        except wikipedia.exceptions.DisambiguationError as e:
            if e.options:
                return wikipedia.summary(e.options[0], sentences=sentences)
            return "Résultat ambigu."
        except Exception as e:
            return f"Erreur: {str(e)}"