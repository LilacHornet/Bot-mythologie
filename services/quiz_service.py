import random
import os
import sys

# Ajouter le chemin parent pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.questions import mythology_questions


class QuizService:
    """Service pour gérer les quiz."""
    
    def __init__(self):
        self.active_quizzes: dict = {}
        self.questions = mythology_questions
    
    def get_random_question(self) -> dict:
        """Retourne une question aléatoire."""
        return random.choice(self.questions)
    
    def start_quiz(self, user_id: int) -> dict:
        """Démarre un quiz pour un utilisateur."""
        question = self.get_random_question()
        self.active_quizzes[user_id] = question
        return question
    
    def has_active_quiz(self, user_id: int) -> bool:
        """Vérifie si un utilisateur a un quiz en cours."""
        return user_id in self.active_quizzes
    
    def get_active_quiz(self, user_id: int) -> dict | None:
        """Récupère le quiz actif d'un utilisateur."""
        return self.active_quizzes.get(user_id)
    
    def check_answer(self, user_id: int, answer: str) -> tuple[bool, str]:
        """
        Vérifie la réponse d'un utilisateur.
        Retourne (is_correct, correct_answer).
        """
        if user_id not in self.active_quizzes:
            return False, ""
        
        question_data = self.active_quizzes[user_id]
        user_answer = answer.lower().strip()
        correct_answer = question_data["answer"]
        alternatives = question_data.get("alternatives", [])
        
        all_valid_answers = [correct_answer] + alternatives
        is_correct = user_answer in all_valid_answers
        
        return is_correct, correct_answer
    
    def end_quiz(self, user_id: int):
        """Termine le quiz d'un utilisateur."""
        if user_id in self.active_quizzes:
            del self.active_quizzes[user_id]