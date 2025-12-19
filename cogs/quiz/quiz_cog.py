import discord
from discord import app_commands
from discord.ext import commands
import os
import sys
import asyncio
from typing import Optional

# Ajouter le chemin parent pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.quiz_service import QuizService, QUIZ_DURATION
from services.stats_service import StatsService
from data.questions import DIFFICULTY_CONFIG

from .quiz_commands import QuizCommands
from .quiz_listeners import QuizListeners
from .quiz_helpers import QuizHelpers
from .stats_commands import StatsCommands


class QuizCog(QuizCommands, StatsCommands, QuizListeners, QuizHelpers, commands.Cog):
    """Cog pour les commandes de quiz."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.quiz_service = QuizService()
        self.stats_service = StatsService()
        # Dictionnaire pour stocker les tâches de fin de quiz
        self.quiz_timers: dict[int, asyncio.Task] = {}
    
    def cog_unload(self):
        """Annule toutes les tâches en cours lors du déchargement du cog."""
        for task in self.quiz_timers.values():
            task.cancel()