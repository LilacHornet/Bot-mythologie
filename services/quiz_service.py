import random
import os
import sys
from datetime import datetime, timedelta

# Ajouter le chemin parent pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.questions import mythology_questions, DIFFICULTY_POINTS, DIFFICULTY_CONFIG

# Durée du quiz en secondes
QUIZ_DURATION = 30


class QuizService:
    """Service pour gérer les quiz."""
    
    def __init__(self):
        # Quiz actifs par channel (channel_id -> quiz_data)
        self.active_quizzes: dict = {}
        # Utilisateurs ayant déjà répondu (channel_id -> set of user_ids)
        self.answered_users: dict = {}
        # Résultats des réponses (channel_id -> list of results)
        self.quiz_results: dict = {}
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
    
    def start_quiz(self, channel_id: int, difficulty: str = None, qcm_mode: bool = False) -> tuple[dict, str, datetime]:
        """
        Démarre un quiz dans un channel.
        Retourne (question_data, difficulty, end_time).
        """
        question, diff = self.get_random_question(difficulty)
        start_time = datetime.now()
        end_time = start_time + timedelta(seconds=QUIZ_DURATION)
        
        # Mélanger les choix pour le mode QCM
        shuffled_choices = None
        if qcm_mode and "choices" in question:
            shuffled_choices = question["choices"].copy()
            random.shuffle(shuffled_choices)
        
        self.active_quizzes[channel_id] = {
            "question": question,
            "difficulty": diff,
            "started_at": start_time,
            "ends_at": end_time,
            "qcm_mode": qcm_mode,
            "shuffled_choices": shuffled_choices
        }
        # Réinitialiser les utilisateurs ayant répondu et les résultats
        self.answered_users[channel_id] = set()
        self.quiz_results[channel_id] = []
        
        return question, diff, end_time
    
    def is_qcm_mode(self, channel_id: int) -> bool:
        """Vérifie si le quiz est en mode QCM."""
        if channel_id not in self.active_quizzes:
            return False
        return self.active_quizzes[channel_id].get("qcm_mode", False)
    
    def get_shuffled_choices(self, channel_id: int) -> list | None:
        """Récupère les choix mélangés pour le mode QCM."""
        if channel_id not in self.active_quizzes:
            return None
        return self.active_quizzes[channel_id].get("shuffled_choices")
    
    def has_active_quiz(self, channel_id: int) -> bool:
        """Vérifie si un channel a un quiz en cours."""
        if channel_id not in self.active_quizzes:
            return False
        
        # Vérifier si le quiz n'a pas expiré
        quiz_data = self.active_quizzes[channel_id]
        if datetime.now() > quiz_data["ends_at"]:
            return False
        
        return True
    
    def is_quiz_expired(self, channel_id: int) -> bool:
        """Vérifie si le quiz a expiré."""
        if channel_id not in self.active_quizzes:
            return True
        
        quiz_data = self.active_quizzes[channel_id]
        return datetime.now() > quiz_data["ends_at"]
    
    def get_remaining_time(self, channel_id: int) -> int:
        """Retourne le temps restant en secondes."""
        if channel_id not in self.active_quizzes:
            return 0
        
        quiz_data = self.active_quizzes[channel_id]
        remaining = (quiz_data["ends_at"] - datetime.now()).total_seconds()
        return max(0, int(remaining))
    
    def has_user_answered(self, channel_id: int, user_id: int) -> bool:
        """Vérifie si un utilisateur a déjà répondu au quiz du channel."""
        if channel_id not in self.answered_users:
            return False
        return user_id in self.answered_users[channel_id]
    
    def mark_user_answered(self, channel_id: int, user_id: int, username: str, is_correct: bool, points: int):
        """Marque un utilisateur comme ayant répondu et enregistre son résultat."""
        if channel_id not in self.answered_users:
            self.answered_users[channel_id] = set()
        self.answered_users[channel_id].add(user_id)
        
        if channel_id not in self.quiz_results:
            self.quiz_results[channel_id] = []
        
        self.quiz_results[channel_id].append({
            "user_id": user_id,
            "username": username,
            "is_correct": is_correct,
            "points": points,
            "answered_at": datetime.now()
        })
    
    def get_active_quiz(self, channel_id: int) -> dict | None:
        """Récupère le quiz actif d'un channel."""
        return self.active_quizzes.get(channel_id)
    
    def get_answered_count(self, channel_id: int) -> int:
        """Retourne le nombre d'utilisateurs ayant répondu."""
        if channel_id not in self.answered_users:
            return 0
        return len(self.answered_users[channel_id])
    
    def get_quiz_results(self, channel_id: int) -> list:
        """Retourne les résultats du quiz."""
        return self.quiz_results.get(channel_id, [])
    
    def get_correct_answers_count(self, channel_id: int) -> int:
        """Retourne le nombre de bonnes réponses."""
        results = self.get_quiz_results(channel_id)
        return sum(1 for r in results if r["is_correct"])
    
    def check_answer(self, channel_id: int, answer: str) -> tuple[bool, str, str, int]:
        """
        Vérifie la réponse d'un utilisateur.
        Retourne (is_correct, correct_answer, difficulty, points).
        """
        if channel_id not in self.active_quizzes:
            return False, "", "", 0
        
        quiz_data = self.active_quizzes[channel_id]
        question_data = quiz_data["question"]
        difficulty = quiz_data["difficulty"]
        
        user_answer = answer.lower().strip()
        correct_answer = question_data["answer"]
        alternatives = question_data.get("alternatives", [])
        
        # Pour le mode QCM, vérifier aussi le choix exact
        choices = question_data.get("choices", [])
        correct_choice = choices[0] if choices else correct_answer  # Le premier choix est toujours le bon
        
        all_valid_answers = [correct_answer.lower()] + [alt.lower() for alt in alternatives] + [correct_choice.lower()]
        is_correct = user_answer in all_valid_answers
        
        points = DIFFICULTY_POINTS[difficulty] if is_correct else 0
        
        return is_correct, correct_answer, difficulty, points
    
    def check_qcm_answer(self, channel_id: int, choice_index: int) -> tuple[bool, str, str, int]:
        """
        Vérifie la réponse QCM d'un utilisateur.
        Retourne (is_correct, correct_answer, difficulty, points).
        """
        if channel_id not in self.active_quizzes:
            return False, "", "", 0
        
        quiz_data = self.active_quizzes[channel_id]
        question_data = quiz_data["question"]
        difficulty = quiz_data["difficulty"]
        shuffled_choices = quiz_data.get("shuffled_choices", [])
        
        if not shuffled_choices or choice_index >= len(shuffled_choices):
            return False, "", difficulty, 0
        
        selected_choice = shuffled_choices[choice_index]
        correct_choice = question_data["choices"][0]  # Le premier choix est toujours le bon
        correct_answer = question_data["answer"]
        
        is_correct = selected_choice == correct_choice
        points = DIFFICULTY_POINTS[difficulty] if is_correct else 0
        
        return is_correct, correct_answer, difficulty, points
    
    def end_quiz(self, channel_id: int) -> dict | None:
        """
        Termine le quiz d'un channel.
        Retourne les données du quiz terminé ou None.
        """
        quiz_data = self.active_quizzes.get(channel_id)
        results = self.quiz_results.get(channel_id, [])
        
        if channel_id in self.active_quizzes:
            del self.active_quizzes[channel_id]
        if channel_id in self.answered_users:
            del self.answered_users[channel_id]
        if channel_id in self.quiz_results:
            del self.quiz_results[channel_id]
        
        if quiz_data:
            quiz_data["results"] = results
            return quiz_data
        return None
    
    def get_difficulty_config(self, difficulty: str) -> dict:
        """Retourne la configuration d'une difficulté."""
        return DIFFICULTY_CONFIG.get(difficulty, DIFFICULTY_CONFIG["easy"])
    
    def get_available_difficulties(self) -> list[str]:
        """Retourne la liste des difficultés disponibles."""
        return list(self.questions.keys())