import discord
from discord import app_commands
import asyncio
from typing import Optional

from services.quiz_service import QUIZ_DURATION
from .quiz_views import QuizQCMView


class QuizCommands:
    """Commandes slash pour le quiz."""
    
    @app_commands.command(name="quiz", description="Réponds à une question sur la mythologie !")
    @app_commands.describe(
        difficulty="Choisis la difficulté",
        mode="Choisis le mode de jeu"
    )
    @app_commands.choices(difficulty=[
        app_commands.Choice(name="🟢 Facile", value="easy"),
        app_commands.Choice(name="🟠 Moyen", value="medium"),
        app_commands.Choice(name="🔴 Difficile", value="hard")
    ])
    @app_commands.choices(mode=[
        app_commands.Choice(name="💬 Texte", value="text"),
        app_commands.Choice(name="🔘 QCM", value="qcm")
    ])
    async def quiz(self, interaction: discord.Interaction, difficulty: Optional[str] = None, mode: Optional[str] = "text"):
        """Lance un quiz."""
        channel_id = interaction.channel_id
        
        if self.quiz_service.has_active_quiz(channel_id):
            remaining = self.quiz_service.get_remaining_time(channel_id)
            await interaction.response.send_message(
                f"⚠️ Un quiz est déjà en cours ! Il reste **{remaining}** secondes.",
                ephemeral=True
            )
            return
        
        qcm_mode = mode == "qcm"
        question_data, diff, end_time = self.quiz_service.start_quiz(channel_id, difficulty, qcm_mode)
        
        embed = self._build_quiz_embed(question_data, diff, qcm_mode)
        
        if qcm_mode:
            view = QuizQCMView(self.quiz_service.get_shuffled_choices(channel_id), channel_id, self, QUIZ_DURATION)
            await interaction.response.send_message(embed=embed, view=view)
        else:
            await interaction.response.send_message(embed=embed)
        
        self._start_quiz_timer(channel_id)
    
    def _build_quiz_embed(self, question_data: dict, difficulty: str, qcm_mode: bool) -> discord.Embed:
        """Construit l'embed du quiz."""
        diff_config = self.quiz_service.get_difficulty_config(difficulty)
        
        embed = discord.Embed(
            title=f"🏛️ Quiz Mythologie {diff_config['emoji']}",
            description=question_data["question"],
            color=diff_config["color"]
        )
        embed.add_field(name="Difficulté", value=f"{diff_config['emoji']} {diff_config['name']}", inline=True)
        embed.add_field(name="Points", value=f"⭐ {self._get_points_for_difficulty(difficulty)}", inline=True)
        embed.add_field(name="⏱️ Temps", value=f"**{QUIZ_DURATION}** secondes", inline=True)
        
        mode_text = "**Clique sur un bouton !**" if qcm_mode else "**Écris ta réponse !**"
        mode_name = "🔘 Mode QCM" if qcm_mode else "💬 Mode Texte"
        embed.add_field(name=mode_name, value=mode_text, inline=False)
        embed.set_footer(text=f"⏰ Le quiz se termine dans {QUIZ_DURATION} secondes")
        
        return embed
    
    def _start_quiz_timer(self, channel_id: int):
        """Démarre le timer de fin de quiz."""
        if channel_id in self.quiz_timers:
            self.quiz_timers[channel_id].cancel()
        self.quiz_timers[channel_id] = asyncio.create_task(self.end_quiz_after_timeout(channel_id))
    
    @app_commands.command(name="answer", description="Réponds à la question du quiz")
    @app_commands.describe(reponse="Ta réponse à la question")
    async def answer(self, interaction: discord.Interaction, reponse: str):
        """Vérifie la réponse de l'utilisateur."""
        channel_id = interaction.channel_id
        user_id = interaction.user.id
        
        error = self._validate_answer_request(channel_id, user_id)
        if error:
            await interaction.response.send_message(error, ephemeral=True)
            return
        
        is_correct, _, difficulty, points = self.quiz_service.check_answer(channel_id, reponse)
        self._record_answer(channel_id, user_id, interaction.user.name, is_correct, difficulty, points)
        
        embed = self._build_answer_embed(is_correct, difficulty, points, channel_id)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    def _validate_answer_request(self, channel_id: int, user_id: int) -> str | None:
        """Valide une demande de réponse. Retourne le message d'erreur ou None."""
        if not self.quiz_service.has_active_quiz(channel_id):
            return "❌ Pas de quiz en cours ! Utilise `/quiz` pour en lancer un."
        if self.quiz_service.is_qcm_mode(channel_id):
            return "🔘 Ce quiz est en mode QCM ! Clique sur un bouton."
        if self.quiz_service.has_user_answered(channel_id, user_id):
            return "⚠️ Tu as déjà répondu ! Attends le prochain quiz."
        return None
    
    def _record_answer(self, channel_id: int, user_id: int, username: str, is_correct: bool, difficulty: str, points: int):
        """Enregistre une réponse."""
        self.quiz_service.mark_user_answered(channel_id, user_id, username, is_correct, points)
        self.stats_service.update_user_stats(user_id, username, is_correct, difficulty, points)
    
    def _build_answer_embed(self, is_correct: bool, difficulty: str, points: int, channel_id: int) -> discord.Embed:
        """Construit l'embed de réponse."""
        diff_config = self.quiz_service.get_difficulty_config(difficulty)
        remaining = self.quiz_service.get_remaining_time(channel_id)
        answered = self.quiz_service.get_answered_count(channel_id)
        
        if is_correct:
            embed = discord.Embed(title="✅ Bonne réponse !", color=discord.Color.green())
            embed.add_field(name="Points gagnés", value=f"⭐ +{points}", inline=True)
        else:
            embed = discord.Embed(title="❌ Mauvaise réponse !", color=discord.Color.red())
            embed.add_field(name="Points gagnés", value="⭐ +0", inline=True)
        
        embed.add_field(name="Difficulté", value=f"{diff_config['emoji']} {diff_config['name']}", inline=True)
        embed.add_field(name="⏱️ Temps restant", value=f"**{remaining}** sec", inline=True)
        embed.set_footer(text=f"👥 {answered} personne(s) ont répondu")
        
        return embed
    
    @app_commands.command(name="endquiz", description="Termine le quiz en cours")
    async def endquiz(self, interaction: discord.Interaction):
        """Termine le quiz et affiche la réponse."""
        channel_id = interaction.channel_id
        
        if not self.quiz_service.get_active_quiz(channel_id):
            await interaction.response.send_message("❌ Pas de quiz en cours !", ephemeral=True)
            return
        
        self._cancel_timer(channel_id)
        embed = self._build_end_quiz_embed(channel_id)
        self.quiz_service.end_quiz(channel_id)
        
        await interaction.response.send_message(embed=embed)
    
    def _cancel_timer(self, channel_id: int):
        """Annule le timer d'un quiz."""
        if channel_id in self.quiz_timers:
            self.quiz_timers[channel_id].cancel()
            del self.quiz_timers[channel_id]
    
    def _build_end_quiz_embed(self, channel_id: int) -> discord.Embed:
        """Construit l'embed de fin de quiz."""
        quiz_data = self.quiz_service.get_active_quiz(channel_id)
        question_data = quiz_data["question"]
        difficulty = quiz_data["difficulty"]
        diff_config = self.quiz_service.get_difficulty_config(difficulty)
        results = self.quiz_service.get_quiz_results(channel_id)
        
        embed = discord.Embed(
            title="🏁 Quiz terminé !",
            description=f"**Question:** {question_data['question']}",
            color=discord.Color.blue()
        )
        embed.add_field(name="✅ Bonne réponse", value=f"**{question_data['answer'].capitalize()}**", inline=True)
        embed.add_field(name="Difficulté", value=f"{diff_config['emoji']} {diff_config['name']}", inline=True)
        
        self._add_results_to_embed(embed, results)
        embed.set_footer(text="Utilisez /quiz pour un nouveau quiz !")
        
        return embed
    
    def _add_results_to_embed(self, embed: discord.Embed, results: list):
        """Ajoute les résultats à l'embed."""
        if not results:
            embed.add_field(name="👥 Participants", value="Personne n'a répondu !", inline=False)
            return
        
        correct_count = sum(1 for r in results if r["is_correct"])
        wrong_count = len(results) - correct_count
        
        embed.add_field(
            name="👥 Participants",
            value=f"{len(results)} personne(s)\n✅ {correct_count} bonne(s)\n❌ {wrong_count} mauvaise(s)",
            inline=False
        )
        
        winners = [r for r in results if r["is_correct"]]
        if winners:
            winners_text = "\n".join([f"⭐ {w['username']} (+{w['points']} pts)" for w in winners])
            embed.add_field(name="🏆 Gagnants", value=winners_text, inline=False)
    
    @app_commands.command(name="quizstatus", description="Affiche le statut du quiz")
    async def quizstatus(self, interaction: discord.Interaction):
        """Affiche le statut du quiz actuel."""
        channel_id = interaction.channel_id
        
        if not self.quiz_service.has_active_quiz(channel_id):
            await interaction.response.send_message("❌ Pas de quiz en cours !", ephemeral=True)
            return
        
        embed = self._build_status_embed(channel_id, interaction.user.id)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    def _build_status_embed(self, channel_id: int, user_id: int) -> discord.Embed:
        """Construit l'embed de statut."""
        quiz = self.quiz_service.get_active_quiz(channel_id)
        diff_config = self.quiz_service.get_difficulty_config(quiz["difficulty"])
        
        embed = discord.Embed(
            title=f"📊 Quiz en cours {diff_config['emoji']}",
            description=quiz["question"]["question"],
            color=diff_config["color"]
        )
        embed.add_field(name="Difficulté", value=f"{diff_config['emoji']} {diff_config['name']}", inline=True)
        embed.add_field(name="⏱️ Temps restant", value=f"**{self.quiz_service.get_remaining_time(channel_id)}** sec", inline=True)
        embed.add_field(name="🎮 Mode", value="🔘 QCM" if quiz.get("qcm_mode") else "💬 Texte", inline=True)
        embed.add_field(name="👥 Réponses", value=f"{self.quiz_service.get_answered_count(channel_id)}", inline=True)
        
        has_answered = self.quiz_service.has_user_answered(channel_id, user_id)
        embed.add_field(name="Ton statut", value="✅ Répondu" if has_answered else "⏳ En attente", inline=True)
        
        return embed