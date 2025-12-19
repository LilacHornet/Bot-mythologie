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
    
    def _get_default_user_stats(self, username: str) -> dict:
        """Retourne les statistiques par défaut pour un nouvel utilisateur."""
        return {
            "username": username,
            "correct": 0,
            "wrong": 0,
            "total": 0,
            "points": 0,
            "by_difficulty": {
                "easy": {"correct": 0, "wrong": 0},
                "medium": {"correct": 0, "wrong": 0},
                "hard": {"correct": 0, "wrong": 0}
            }
        }
    
    def update_user_stats(self, user_id: int, username: str, is_correct: bool, difficulty: str = "easy", points: int = 0):
        """Met à jour les statistiques d'un utilisateur."""
        stats = self.load_stats()
        user_id_str = str(user_id)
        
        if user_id_str not in stats:
            stats[user_id_str] = self._get_default_user_stats(username)
        
        # Migration des anciennes stats si nécessaire
        if "by_difficulty" not in stats[user_id_str]:
            stats[user_id_str]["by_difficulty"] = {
                "easy": {"correct": 0, "wrong": 0},
                "medium": {"correct": 0, "wrong": 0},
                "hard": {"correct": 0, "wrong": 0}
            }
        if "points" not in stats[user_id_str]:
            stats[user_id_str]["points"] = 0
        
        stats[user_id_str]["username"] = username
        stats[user_id_str]["total"] += 1
        
        if is_correct:
            stats[user_id_str]["correct"] += 1
            stats[user_id_str]["points"] += points
            stats[user_id_str]["by_difficulty"][difficulty]["correct"] += 1
        else:
            stats[user_id_str]["wrong"] += 1
            stats[user_id_str]["by_difficulty"][difficulty]["wrong"] += 1
        
        self.save_stats(stats)
    
    def get_user_stats(self, user_id: int) -> dict | None:
        """Récupère les statistiques d'un utilisateur."""
        stats = self.load_stats()
        return stats.get(str(user_id))
    
    def get_leaderboard(self, limit: int = 10, sort_by: str = "points") -> list:
        """Récupère le classement des meilleurs joueurs."""
        stats = self.load_stats()
        
        # Trier par points ou par bonnes réponses
        if sort_by == "points":
            sorted_users = sorted(
                stats.items(),
                key=lambda x: x[1].get("points", 0),
                reverse=True
            )[:limit]
        else:
            sorted_users = sorted(
                stats.items(),
                key=lambda x: x[1]["correct"],
                reverse=True
            )[:limit]
        
        return sorted_users