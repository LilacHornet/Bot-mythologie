import json
import os
import sys

# Ajouter le chemin parent pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import STATS_FILE


class StatsService:
    """Service pour gérer les statistiques des utilisateurs."""
    
    def __init__(self):
        self.stats_file = STATS_FILE
        self.stats = self._load_stats()
    
    # ==================== FICHIER ====================
    
    def _load_stats(self) -> dict:
        """Charge les statistiques depuis le fichier JSON."""
        if not os.path.exists(self.stats_file):
            return {}
        try:
            with open(self.stats_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    
    def _save_stats(self):
        """Sauvegarde les statistiques dans le fichier JSON."""
        with open(self.stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, indent=4, ensure_ascii=False)
    
    # ==================== UTILISATEUR ====================
    
    def get_user_stats(self, user_id: int) -> dict | None:
        """Récupère les statistiques d'un utilisateur."""
        return self.stats.get(str(user_id))
    
    def update_user_stats(self, user_id: int, username: str, is_correct: bool, difficulty: str, points: int):
        """Met à jour les statistiques d'un utilisateur."""
        user_id_str = str(user_id)
        
        if user_id_str not in self.stats:
            self.stats[user_id_str] = self._create_default_stats(username)
        
        self._update_stats_values(user_id_str, username, is_correct, difficulty, points)
        self._save_stats()
    
    def _create_default_stats(self, username: str) -> dict:
        """Crée des statistiques par défaut pour un nouvel utilisateur."""
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
    
    def _update_stats_values(self, user_id_str: str, username: str, is_correct: bool, difficulty: str, points: int):
        """Met à jour les valeurs des statistiques."""
        stats = self.stats[user_id_str]
        stats["username"] = username
        stats["total"] += 1
        
        if is_correct:
            stats["correct"] += 1
            stats["points"] = stats.get("points", 0) + points
        else:
            stats["wrong"] += 1
        
        self._update_difficulty_stats(stats, difficulty, is_correct)
    
    def _update_difficulty_stats(self, stats: dict, difficulty: str, is_correct: bool):
        """Met à jour les statistiques par difficulté."""
        if "by_difficulty" not in stats:
            stats["by_difficulty"] = {}
        
        if difficulty not in stats["by_difficulty"]:
            stats["by_difficulty"][difficulty] = {"correct": 0, "wrong": 0}
        
        key = "correct" if is_correct else "wrong"
        stats["by_difficulty"][difficulty][key] += 1
    
    def reset_user_stats(self, user_id: int) -> bool:
        """Réinitialise les statistiques d'un utilisateur."""
        user_id_str = str(user_id)
        if user_id_str in self.stats:
            del self.stats[user_id_str]
            self._save_stats()
            return True
        return False
    
    # ==================== CLASSEMENT ====================
    
    def get_leaderboard(self, limit: int = 10, sort_by: str = "points") -> list[tuple[str, dict]]:
        """Retourne le classement des utilisateurs."""
        if not self.stats:
            return []
        
        sorted_users = sorted(
            self.stats.items(),
            key=lambda x: x[1].get(sort_by, 0),
            reverse=True
        )
        return sorted_users[:limit]
    
    def get_user_rank(self, user_id: int) -> int | None:
        """Retourne le rang d'un utilisateur (basé sur les points)."""
        user_id_str = str(user_id)
        if not self.stats or user_id_str not in self.stats:
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
    
    # ==================== STATISTIQUES GLOBALES ====================
    
    def get_total_users(self) -> int:
        """Retourne le nombre total d'utilisateurs."""
        return len(self.stats)
    
    def get_global_stats(self) -> dict:
        """Retourne les statistiques globales."""
        total_correct = sum(u.get("correct", 0) for u in self.stats.values())
        total_wrong = sum(u.get("wrong", 0) for u in self.stats.values())
        total_quizzes = sum(u.get("total", 0) for u in self.stats.values())
        
        return {
            "total_users": len(self.stats),
            "total_quizzes": total_quizzes,
            "total_correct": total_correct,
            "total_wrong": total_wrong,
            "total_points": sum(u.get("points", 0) for u in self.stats.values()),
            "average_success_rate": (total_correct / total_quizzes * 100) if total_quizzes > 0 else 0
        }