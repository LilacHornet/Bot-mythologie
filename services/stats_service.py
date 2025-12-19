import json
import os

STATS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "user_stats.json")


class StatsService:
    """Service pour gérer les statistiques des utilisateurs."""
    
    def __init__(self):
        self.stats_file = STATS_FILE
    
    def load_stats(self) -> dict:
        """Charge les statistiques depuis le fichier JSON."""
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    if content.strip():
                        return json.loads(content)
            except (json.JSONDecodeError, IOError):
                pass
        return {}
    
    def save_stats(self, stats: dict):
        """Sauvegarde les statistiques dans le fichier JSON."""
        with open(self.stats_file, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=4, ensure_ascii=False)
    
    def update_user_stats(self, user_id: int, username: str, is_correct: bool):
        """Met à jour les statistiques d'un utilisateur."""
        stats = self.load_stats()
        user_id_str = str(user_id)
        
        if user_id_str not in stats:
            stats[user_id_str] = {
                "username": username,
                "correct": 0,
                "wrong": 0,
                "total": 0
            }
        
        stats[user_id_str]["username"] = username
        stats[user_id_str]["total"] += 1
        
        if is_correct:
            stats[user_id_str]["correct"] += 1
        else:
            stats[user_id_str]["wrong"] += 1
        
        self.save_stats(stats)
    
    def get_user_stats(self, user_id: int) -> dict | None:
        """Récupère les statistiques d'un utilisateur."""
        stats = self.load_stats()
        return stats.get(str(user_id))
    
    def get_leaderboard(self, limit: int = 10) -> list:
        """Récupère le classement des meilleurs joueurs."""
        stats = self.load_stats()
        sorted_users = sorted(
            stats.items(),
            key=lambda x: x[1]["correct"],
            reverse=True
        )[:limit]
        return sorted_users