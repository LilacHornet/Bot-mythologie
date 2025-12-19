import random
import os
import sys

# Ajouter le chemin parent pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.questions import mythology_questions, DIFFICULTY_POINTS, DIFFICULTY_CONFIG


class QuizService:
    """Service pour gérer les quiz."""
    
    def __init__(self):
        self.active_quizzes: dict = {}
        self.questions = mythology_questions
    
    def get_random_question(self, difficulty: str = None) -> tuple[dict, str]:
        """
        Retourne une question aléatoire.
        Si difficulty est None, choisit une difficulté aléatoire.
        Retourne (question, difficulty).
        """
        if difficulty is None:
            difficulty = random.choice(["easy", "medium", "hard"])
        
        if difficulty not in self.questions:
            difficulty = "easy"
        
        question = random.choice(self.questions[difficulty])
        return question, difficulty
    
    def start_quiz(self, user_id: int, difficulty: str = None) -> tuple[dict, str]:
        """
        Démarre un quiz pour un utilisateur.
        Retourne (question_data, difficulty).
        """
        question, diff = self.get_random_question(difficulty)
        self.active_quizzes[user_id] = {
            "question": question,
            "difficulty": diff
        }
        return question, diff
    
    def has_active_quiz(self, user_id: int) -> bool:
        """Vérifie si un utilisateur a un quiz en cours."""
        return user_id in self.active_quizzes
    
    def get_active_quiz(self, user_id: int) -> dict | None:
        """Récupère le quiz actif d'un utilisateur."""
        return self.active_quizzes.get(user_id)
    
    def check_answer(self, user_id: int, answer: str) -> tuple[bool, str, str, int]:
        """
        Vérifie la réponse d'un utilisateur.
        Retourne (is_correct, correct_answer, difficulty, points).
        """
        if user_id not in self.active_quizzes:
            return False, "", "", 0
        
        quiz_data = self.active_quizzes[user_id]
        question_data = quiz_data["question"]
        difficulty = quiz_data["difficulty"]
        
        user_answer = answer.lower().strip()
        correct_answer = question_data["answer"]
        alternatives = question_data.get("alternatives", [])
        
        all_valid_answers = [correct_answer] + alternatives
        is_correct = user_answer in all_valid_answers
        
        points = DIFFICULTY_POINTS[difficulty] if is_correct else 0
        
        return is_correct, correct_answer, difficulty, points
    
    def end_quiz(self, user_id: int):
        """Termine le quiz d'un utilisateur."""
        if user_id in self.active_quizzes:
            del self.active_quizzes[user_id]
    
    def get_difficulty_config(self, difficulty: str) -> dict:
        """Retourne la configuration d'une difficulté."""
        return DIFFICULTY_CONFIG.get(difficulty, DIFFICULTY_CONFIG["easy"])
    
    def get_available_difficulties(self) -> list[str]:
        """Retourne la liste des difficultés disponibles."""
        return list(self.questions.keys())