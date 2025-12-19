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
        self.active_quizzes: dict = {}
        self.answered_users: dict = {}
        self.quiz_results: dict = {}
        self.questions = mythology_questions
    
    # ==================== QUESTIONS ====================
    
    def get_random_question(self, difficulty: str = None) -> tuple[dict, str]:
        """Retourne une question aléatoire avec sa difficulté."""
        if difficulty is None or difficulty not in self.questions:
            difficulty = random.choice(list(self.questions.keys()))
        
        question = random.choice(self.questions[difficulty])
        return question, difficulty
    
    # ==================== GESTION DU QUIZ ====================
    
    def start_quiz(self, channel_id: int, difficulty: str = None, qcm_mode: bool = False) -> tuple[dict, str, datetime]:
        """Démarre un quiz. Retourne (question_data, difficulty, end_time)."""
        question, diff = self.get_random_question(difficulty)
        end_time = datetime.now() + timedelta(seconds=QUIZ_DURATION)
        
        shuffled_choices = self._prepare_choices(question, qcm_mode)
        
        self.active_quizzes[channel_id] = {
            "question": question,
            "difficulty": diff,
            "started_at": datetime.now(),
            "ends_at": end_time,
            "qcm_mode": qcm_mode,
            "shuffled_choices": shuffled_choices
        }
        self.answered_users[channel_id] = set()
        self.quiz_results[channel_id] = []
        
        return question, diff, end_time
    
    def _prepare_choices(self, question: dict, qcm_mode: bool) -> list | None:
        """Prépare les choix mélangés pour le mode QCM."""
        if not qcm_mode or "choices" not in question:
            return None
        shuffled = question["choices"].copy()
        random.shuffle(shuffled)
        return shuffled
    
    def end_quiz(self, channel_id: int) -> dict | None:
        """Termine le quiz et retourne ses données."""
        quiz_data = self.active_quizzes.get(channel_id)
        results = self.quiz_results.get(channel_id, [])
        
        self._cleanup_quiz(channel_id)
        
        if quiz_data:
            quiz_data["results"] = results
        return quiz_data
    
    def _cleanup_quiz(self, channel_id: int):
        """Nettoie les données d'un quiz."""
        self.active_quizzes.pop(channel_id, None)
        self.answered_users.pop(channel_id, None)
        self.quiz_results.pop(channel_id, None)
    
    # ==================== VÉRIFICATIONS ====================
    
    def has_active_quiz(self, channel_id: int) -> bool:
        """Vérifie si un quiz est actif et non expiré."""
        if channel_id not in self.active_quizzes:
            return False
        return datetime.now() <= self.active_quizzes[channel_id]["ends_at"]
    
    def is_quiz_expired(self, channel_id: int) -> bool:
        """Vérifie si le quiz a expiré."""
        if channel_id not in self.active_quizzes:
            return True
        return datetime.now() > self.active_quizzes[channel_id]["ends_at"]
    
    def is_qcm_mode(self, channel_id: int) -> bool:
        """Vérifie si le quiz est en mode QCM."""
        quiz = self.active_quizzes.get(channel_id)
        return quiz.get("qcm_mode", False) if quiz else False
    
    def get_remaining_time(self, channel_id: int) -> int:
        """Retourne le temps restant en secondes."""
        if channel_id not in self.active_quizzes:
            return 0
        remaining = (self.active_quizzes[channel_id]["ends_at"] - datetime.now()).total_seconds()
        return max(0, int(remaining))
    
    # ==================== UTILISATEURS ====================
    
    def has_user_answered(self, channel_id: int, user_id: int) -> bool:
        """Vérifie si un utilisateur a déjà répondu."""
        return user_id in self.answered_users.get(channel_id, set())
    
    def mark_user_answered(self, channel_id: int, user_id: int, username: str, is_correct: bool, points: int):
        """Marque un utilisateur comme ayant répondu."""
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
    
    # ==================== GETTERS ====================
    
    def get_active_quiz(self, channel_id: int) -> dict | None:
        """Récupère le quiz actif d'un channel."""
        return self.active_quizzes.get(channel_id)
    
    def get_shuffled_choices(self, channel_id: int) -> list | None:
        """Récupère les choix mélangés pour le mode QCM."""
        quiz = self.active_quizzes.get(channel_id)
        return quiz.get("shuffled_choices") if quiz else None
    
    def get_answered_count(self, channel_id: int) -> int:
        """Retourne le nombre d'utilisateurs ayant répondu."""
        return len(self.answered_users.get(channel_id, set()))
    
    def get_quiz_results(self, channel_id: int) -> list:
        """Retourne les résultats du quiz."""
        return self.quiz_results.get(channel_id, [])
    
    def get_correct_answers_count(self, channel_id: int) -> int:
        """Retourne le nombre de bonnes réponses."""
        return sum(1 for r in self.get_quiz_results(channel_id) if r["is_correct"])
    
    def get_difficulty_config(self, difficulty: str) -> dict:
        """Retourne la configuration d'une difficulté."""
        return DIFFICULTY_CONFIG.get(difficulty, DIFFICULTY_CONFIG["easy"])
    
    def get_available_difficulties(self) -> list[str]:
        """Retourne la liste des difficultés disponibles."""
        return list(self.questions.keys())
    
    # ==================== VÉRIFICATION DES RÉPONSES ====================
    
    def check_answer(self, channel_id: int, answer: str) -> tuple[bool, str, str, int]:
        """Vérifie une réponse texte. Retourne (is_correct, correct_answer, difficulty, points)."""
        quiz = self.active_quizzes.get(channel_id)
        if not quiz:
            return False, "", "", 0
        
        question_data = quiz["question"]
        difficulty = quiz["difficulty"]
        
        is_correct = self._is_answer_correct(answer, question_data)
        points = DIFFICULTY_POINTS[difficulty] if is_correct else 0
        
        return is_correct, question_data["answer"], difficulty, points
    
    def check_qcm_answer(self, channel_id: int, choice_index: int) -> tuple[bool, str, str, int]:
        """Vérifie une réponse QCM. Retourne (is_correct, correct_answer, difficulty, points)."""
        quiz = self.active_quizzes.get(channel_id)
        if not quiz:
            return False, "", "", 0
        
        question_data = quiz["question"]
        difficulty = quiz["difficulty"]
        shuffled_choices = quiz.get("shuffled_choices", [])
        
        if not shuffled_choices or choice_index >= len(shuffled_choices):
            return False, "", difficulty, 0
        
        selected = shuffled_choices[choice_index]
        correct = question_data["choices"][0]  # Premier choix = bonne réponse
        is_correct = selected == correct
        points = DIFFICULTY_POINTS[difficulty] if is_correct else 0
        
        return is_correct, question_data["answer"], difficulty, points
    
    def _is_answer_correct(self, answer: str, question_data: dict) -> bool:
        """Vérifie si une réponse est correcte."""
        user_answer = answer.lower().strip()
        correct = question_data["answer"].lower()
        alternatives = [alt.lower() for alt in question_data.get("alternatives", [])]
        
        choices = question_data.get("choices", [])
        correct_choice = choices[0].lower() if choices else ""
        
        valid_answers = [correct] + alternatives + ([correct_choice] if correct_choice else [])
        return user_answer in valid_answers