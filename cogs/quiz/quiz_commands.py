import discord
from discord import app_commands
from discord.ext import commands
import asyncio
from typing import Optional

from services.quiz_service import QUIZ_DURATION
from data.questions import DIFFICULTY_CONFIG
from .quiz_views import QuizQCMView


class QuizCommands:
    """Commandes slash pour le quiz."""
    
    @app_commands.command(name="quiz", description="Réponds à une question sur la mythologie !")
    @app_commands.describe(
        difficulty="Choisis la difficulté (easy, medium, hard)",
        mode="Choisis le mode de jeu"
    )
    @app_commands.choices(difficulty=[
        app_commands.Choice(name="🟢 Facile", value="easy"),
        app_commands.Choice(name="🟠 Moyen", value="medium"),
        app_commands.Choice(name="🔴 Difficile", value="hard")
    ])
    @app_commands.choices(mode=[
        app_commands.Choice(name="💬 Texte (écrire la réponse)", value="text"),
        app_commands.Choice(name="🔘 QCM (boutons cliquables)", value="qcm")
    ])
    async def quiz(self, interaction: discord.Interaction, difficulty: Optional[str] = None, mode: Optional[str] = "text"):
        """Pose une question de mythologie dans le channel."""
        channel_id = interaction.channel_id
        qcm_mode = mode == "qcm"
        
        # Vérifier s'il y a déjà un quiz en cours dans ce channel
        if self.quiz_service.has_active_quiz(channel_id):
            remaining = self.quiz_service.get_remaining_time(channel_id)
            await interaction.response.send_message(
                f"⚠️ Un quiz est déjà en cours ! Il reste **{remaining}** secondes.",
                ephemeral=True
            )
            return
        
        # Démarrer le quiz
        question_data, diff, end_time = self.quiz_service.start_quiz(channel_id, difficulty, qcm_mode)
        diff_config = self.quiz_service.get_difficulty_config(diff)
        
        embed = discord.Embed(
            title=f"🏛️ Quiz Mythologie {diff_config['emoji']}",
            description=question_data["question"],
            color=diff_config["color"]
        )
        embed.add_field(
            name="Difficulté",
            value=f"{diff_config['emoji']} {diff_config['name']}",
            inline=True
        )
        embed.add_field(
            name="Points",
            value=f"⭐ {self._get_points_for_difficulty(diff)}",
            inline=True
        )
        embed.add_field(
            name="⏱️ Temps",
            value=f"**{QUIZ_DURATION}** secondes",
            inline=True
        )
        
        if qcm_mode:
            embed.add_field(
                name="🔘 Mode QCM",
                value="**Clique sur un bouton pour répondre !**",
                inline=False
            )
            embed.set_footer(text=f"⏰ Le quiz se termine automatiquement dans {QUIZ_DURATION} secondes")
            
            # Créer la vue avec les boutons
            shuffled_choices = self.quiz_service.get_shuffled_choices(channel_id)
            view = QuizQCMView(shuffled_choices, channel_id, self, timeout=QUIZ_DURATION)
            
            await interaction.response.send_message(embed=embed, view=view)
        else:
            embed.add_field(
                name="💬 Mode Texte",
                value="**Écris ta réponse directement dans le chat !**",
                inline=False
            )
            embed.set_footer(text=f"⏰ Le quiz se termine automatiquement dans {QUIZ_DURATION} secondes")
            
            await interaction.response.send_message(embed=embed)
        
        # Annuler l'ancien timer s'il existe
        if channel_id in self.quiz_timers:
            self.quiz_timers[channel_id].cancel()
        
        # Démarrer le timer pour terminer le quiz automatiquement
        self.quiz_timers[channel_id] = asyncio.create_task(
            self.end_quiz_after_timeout(channel_id)
        )
    
    @app_commands.command(name="answer", description="Réponds à la question du quiz (mode texte uniquement)")
    @app_commands.describe(reponse="Ta réponse à la question")
    async def answer(self, interaction: discord.Interaction, reponse: str):
        """Vérifie la réponse de l'utilisateur."""
        channel_id = interaction.channel_id
        user_id = interaction.user.id
        
        # Vérifier s'il y a un quiz en cours
        if not self.quiz_service.has_active_quiz(channel_id):
            await interaction.response.send_message(
                "❌ Il n'y a pas de quiz en cours ou le temps est écoulé ! Utilise `/quiz` pour en lancer un.",
                ephemeral=True
            )
            return
        
        # Vérifier si c'est un quiz QCM
        if self.quiz_service.is_qcm_mode(channel_id):
            await interaction.response.send_message(
                "🔘 Ce quiz est en mode QCM ! Clique sur un bouton pour répondre.",
                ephemeral=True
            )
            return
        
        # Vérifier si l'utilisateur a déjà répondu
        if self.quiz_service.has_user_answered(channel_id, user_id):
            await interaction.response.send_message(
                "⚠️ Tu as déjà répondu à ce quiz ! Attends le prochain.",
                ephemeral=True
            )
            return
        
        # Vérifier la réponse
        is_correct, correct_answer, difficulty, points = self.quiz_service.check_answer(channel_id, reponse)
        diff_config = self.quiz_service.get_difficulty_config(difficulty)
        remaining_time = self.quiz_service.get_remaining_time(channel_id)
        
        # Marquer l'utilisateur comme ayant répondu
        self.quiz_service.mark_user_answered(channel_id, user_id, interaction.user.name, is_correct, points)
        
        # Sauvegarder les stats
        self.stats_service.update_user_stats(
            user_id, 
            interaction.user.name, 
            is_correct, 
            difficulty, 
            points
        )
        
        # Nombre de participants
        answered_count = self.quiz_service.get_answered_count(channel_id)
        
        if is_correct:
            embed = discord.Embed(
                title="✅ Bonne réponse !",
                description=f"Bravo ! Tu as trouvé la bonne réponse !",
                color=discord.Color.green()
            )
            embed.add_field(
                name="Points gagnés",
                value=f"⭐ +{points} points",
                inline=True
            )
        else:
            embed = discord.Embed(
                title="❌ Mauvaise réponse !",
                description=f"Ce n'est pas la bonne réponse... Réessaie au prochain quiz !",
                color=discord.Color.red()
            )
            embed.add_field(
                name="Points gagnés",
                value="⭐ +0 points",
                inline=True
            )
        
        embed.add_field(
            name="Difficulté",
            value=f"{diff_config['emoji']} {diff_config['name']}",
            inline=True
        )
        embed.add_field(
            name="⏱️ Temps restant",
            value=f"**{remaining_time}** secondes",
            inline=True
        )
        embed.set_footer(text=f"👥 {answered_count} personne(s) ont répondu • La réponse sera révélée à la fin !")
        
        # Réponse cachée (ephemeral=True)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="endquiz", description="Termine le quiz en cours et révèle la réponse")
    async def endquiz(self, interaction: discord.Interaction):
        """Termine le quiz et affiche la réponse."""
        channel_id = interaction.channel_id
        
        if not self.quiz_service.get_active_quiz(channel_id):
            await interaction.response.send_message(
                "❌ Il n'y a pas de quiz en cours dans ce channel !",
                ephemeral=True
            )
            return
        
        # Annuler le timer
        if channel_id in self.quiz_timers:
            self.quiz_timers[channel_id].cancel()
            del self.quiz_timers[channel_id]
        
        # Récupérer les infos du quiz avant de le terminer
        quiz_data = self.quiz_service.get_active_quiz(channel_id)
        question_data = quiz_data["question"]
        difficulty = quiz_data["difficulty"]
        correct_answer = question_data["answer"]
        diff_config = self.quiz_service.get_difficulty_config(difficulty)
        results = self.quiz_service.get_quiz_results(channel_id)
        
        # Terminer le quiz
        self.quiz_service.end_quiz(channel_id)
        
        embed = discord.Embed(
            title="🏁 Quiz terminé !",
            description=f"**Question:** {question_data['question']}",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="✅ Bonne réponse",
            value=f"**{correct_answer.capitalize()}**",
            inline=True
        )
        embed.add_field(
            name="Difficulté",
            value=f"{diff_config['emoji']} {diff_config['name']}",
            inline=True
        )
        
        # Résumé des participants
        if results:
            correct_count = sum(1 for r in results if r["is_correct"])
            wrong_count = len(results) - correct_count
            
            embed.add_field(
                name="👥 Participants",
                value=f"{len(results)} personne(s)\n✅ {correct_count} bonne(s) réponse(s)\n❌ {wrong_count} mauvaise(s) réponse(s)",
                inline=False
            )
            
            # Liste des gagnants
            winners = [r for r in results if r["is_correct"]]
            if winners:
                winners_text = "\n".join([f"⭐ {w['username']} (+{w['points']} pts)" for w in winners])
                embed.add_field(
                    name="🏆 Gagnants",
                    value=winners_text,
                    inline=False
                )
        else:
            embed.add_field(
                name="👥 Participants",
                value="Personne n'a répondu !",
                inline=False
            )
        
        embed.set_footer(text="Utilisez /quiz pour lancer un nouveau quiz !")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="quizstatus", description="Affiche le statut du quiz en cours")
    async def quizstatus(self, interaction: discord.Interaction):
        """Affiche le statut du quiz actuel."""
        channel_id = interaction.channel_id
        
        if not self.quiz_service.has_active_quiz(channel_id):
            await interaction.response.send_message(
                "❌ Il n'y a pas de quiz en cours dans ce channel !",
                ephemeral=True
            )
            return
        
        quiz_data = self.quiz_service.get_active_quiz(channel_id)
        question_data = quiz_data["question"]
        difficulty = quiz_data["difficulty"]
        diff_config = self.quiz_service.get_difficulty_config(difficulty)
        answered_count = self.quiz_service.get_answered_count(channel_id)
        remaining_time = self.quiz_service.get_remaining_time(channel_id)
        is_qcm = self.quiz_service.is_qcm_mode(channel_id)
        
        # Vérifier si l'utilisateur a déjà répondu
        has_answered = self.quiz_service.has_user_answered(channel_id, interaction.user.id)
        
        embed = discord.Embed(
            title=f"📊 Quiz en cours {diff_config['emoji']}",
            description=question_data["question"],
            color=diff_config["color"]
        )
        embed.add_field(
            name="Difficulté",
            value=f"{diff_config['emoji']} {diff_config['name']}",
            inline=True
        )
        embed.add_field(
            name="Points",
            value=f"⭐ {self._get_points_for_difficulty(difficulty)}",
            inline=True
        )
        embed.add_field(
            name="⏱️ Temps restant",
            value=f"**{remaining_time}** secondes",
            inline=True
        )
        embed.add_field(
            name="🎮 Mode",
            value="🔘 QCM" if is_qcm else "💬 Texte",
            inline=True
        )
        embed.add_field(
            name="👥 Réponses",
            value=f"{answered_count} participant(s)",
            inline=True
        )
        embed.add_field(
            name="Ton statut",
            value="✅ Tu as déjà répondu" if has_answered else "⏳ Tu n'as pas encore répondu",
            inline=True
        )
        
        if is_qcm:
            embed.set_footer(text="Clique sur un bouton pour répondre • /endquiz pour terminer")
        else:
            embed.set_footer(text="Écris ta réponse dans le chat • /endquiz pour terminer")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)