import json
import os

from config import STATS_FILE


class StatsService:
    """Service pour gérer les statistiques des utilisateurs."""
    
    def __init__(self):
        self.stats_file = STATS_FILE
        self.stats = self._load_stats()
    
    def _load_stats(self) -> dict:
        """Charge les statistiques depuis le fichier JSON."""
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}
    
    def _save_stats(self):
        """Sauvegarde les statistiques dans le fichier JSON."""
        with open(self.stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, indent=4, ensure_ascii=False)
    
    def get_user_stats(self, user_id: int) -> dict | None:
        """Récupère les statistiques d'un utilisateur."""
        return self.stats.get(str(user_id))
    
    def update_user_stats(self, user_id: int, username: str, is_correct: bool, difficulty: str, points: int):
        """Met à jour les statistiques d'un utilisateur."""
        user_id_str = str(user_id)
        
        if user_id_str not in self.stats:
            self.stats[user_id_str] = {
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
        
        user_stats = self.stats[user_id_str]
        user_stats["username"] = username
        user_stats["total"] += 1
        
        if is_correct:
            user_stats["correct"] += 1
            user_stats["points"] = user_stats.get("points", 0) + points
        else:
            user_stats["wrong"] += 1
        
        # Stats par difficulté
        if "by_difficulty" not in user_stats:
            user_stats["by_difficulty"] = {
                "easy": {"correct": 0, "wrong": 0},
                "medium": {"correct": 0, "wrong": 0},
                "hard": {"correct": 0, "wrong": 0}
            }
        
        if difficulty not in user_stats["by_difficulty"]:
            user_stats["by_difficulty"][difficulty] = {"correct": 0, "wrong": 0}
        
        if is_correct:
            user_stats["by_difficulty"][difficulty]["correct"] += 1
        else:
            user_stats["by_difficulty"][difficulty]["wrong"] += 1
        
        self._save_stats()
    
    def get_leaderboard(self, limit: int = 10, sort_by: str = "points") -> list[tuple[str, dict]]:
        """
        Retourne le classement des utilisateurs.
        sort_by peut être 'points', 'correct', ou 'total'.
        """
        if not self.stats:
            return []
        
        def get_sort_key(item):
            user_id, user_stats = item
            if sort_by == "points":
                return user_stats.get("points", 0)
            elif sort_by == "correct":
                return user_stats.get("correct", 0)
            else:
                return user_stats.get("total", 0)
        
        sorted_users = sorted(self.stats.items(), key=get_sort_key, reverse=True)
        return sorted_users[:limit]
    
    def get_user_rank(self, user_id: int) -> int | None:
        """Retourne le rang d'un utilisateur (basé sur les points)."""
        if not self.stats:
            return None
        
        user_id_str = str(user_id)
        if user_id_str not in self.stats:
            return None
        
        sorted_users = sorted(
            self.stats.items(),
            key=lambda x: x[1].get("points", 0),
            reverse=True
        )
        
        for i, (uid, _) in enumerate(sorted_users):
            if uid == user_id_str:
                return i + 1
        
        return None
    
    def reset_user_stats(self, user_id: int) -> bool:
        """Réinitialise les statistiques d'un utilisateur."""
        user_id_str = str(user_id)
        
        if user_id_str in self.stats:
            del self.stats[user_id_str]
            self._save_stats()
            return True
        
        return False
    
    def get_total_users(self) -> int:
        """Retourne le nombre total d'utilisateurs."""
        return len(self.stats)
    
    def get_global_stats(self) -> dict:
        """Retourne les statistiques globales."""
        total_correct = sum(u.get("correct", 0) for u in self.stats.values())
        total_wrong = sum(u.get("wrong", 0) for u in self.stats.values())
        total_points = sum(u.get("points", 0) for u in self.stats.values())
        total_quizzes = sum(u.get("total", 0) for u in self.stats.values())
        
        return {
            "total_users": len(self.stats),
            "total_quizzes": total_quizzes,
            "total_correct": total_correct,
            "total_wrong": total_wrong,
            "total_points": total_points,
            "average_success_rate": (total_correct / total_quizzes * 100) if total_quizzes > 0 else 0
        }