import wikipedia


class WikipediaService:
    """Service pour les recherches Wikipedia."""
    
    def __init__(self, lang: str = "fr"):
        self.lang = lang
    
    def get_mythology_link(self, figure_name: str) -> str:
        """
        Récupère le lien Wikipedia pour une figure mythologique.
        Retourne l'URL ou un message d'erreur.
        """
        try:
            wikipedia.set_lang(self.lang)
            search_results = wikipedia.search(figure_name + " mythologie")
            if not search_results:
                search_results = wikipedia.search(figure_name)
            
            if search_results:
                page = wikipedia.page(search_results[0], auto_suggest=False)
                return page.url
            else:
                return f"Aucune page Wikipedia trouvée pour '{figure_name}'."
        except wikipedia.exceptions.PageError:
            return f"Aucune page Wikipedia trouvée pour '{figure_name}'."
        except wikipedia.exceptions.DisambiguationError as e:
            try:
                page = wikipedia.page(e.options[0], auto_suggest=False)
                return page.url
            except Exception:
                return f"Plusieurs résultats trouvés : {', '.join(e.options[:5])}"