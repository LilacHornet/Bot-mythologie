import discord
from discord import app_commands
from discord.ext import commands
import os
import sys
from typing import Optional

# Ajouter le chemin parent pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.quiz_service import QuizService
from services.stats_service import StatsService
from data.questions import DIFFICULTY_CONFIG


class QuizCog(commands.Cog):
    """Cog pour les commandes de quiz."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.quiz_service = QuizService()
        self.stats_service = StatsService()
    
    @app_commands.command(name="quiz", description="Réponds à une question sur la mythologie !")
    @app_commands.describe(difficulty="Choisis la difficulté (easy, medium, hard)")
    @app_commands.choices(difficulty=[
        app_commands.Choice(name="🟢 Facile", value="easy"),
        app_commands.Choice(name="🟠 Moyen", value="medium"),
        app_commands.Choice(name="🔴 Difficile", value="hard")
    ])
    async def quiz(self, interaction: discord.Interaction, difficulty: Optional[str] = None):
        """Pose une question de mythologie à l'utilisateur."""
        question_data, diff = self.quiz_service.start_quiz(interaction.user.id, difficulty)
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
        embed.set_footer(text="Utilisez /answer pour répondre !")
        
        await interaction.response.send_message(embed=embed)
    
    def _get_points_for_difficulty(self, difficulty: str) -> int:
        """Retourne le nombre de points pour une difficulté."""
        from data.questions import DIFFICULTY_POINTS
        return DIFFICULTY_POINTS.get(difficulty, 1)
    
    @app_commands.command(name="answer", description="Réponds à la question du quiz")
    @app_commands.describe(reponse="Ta réponse à la question")
    async def answer(self, interaction: discord.Interaction, reponse: str):
        """Vérifie la réponse de l'utilisateur."""
        user_id = interaction.user.id
        
        if not self.quiz_service.has_active_quiz(user_id):
            await interaction.response.send_message(
                "❌ Tu n'as pas de quiz en cours ! Utilise `/quiz` pour commencer.",
                ephemeral=True
            )
            return
        
        is_correct, correct_answer, difficulty, points = self.quiz_service.check_answer(user_id, reponse)
        diff_config = self.quiz_service.get_difficulty_config(difficulty)
        
        # Sauvegarder les stats
        self.stats_service.update_user_stats(
            user_id, 
            interaction.user.name, 
            is_correct, 
            difficulty, 
            points
        )
        
        # Terminer le quiz
        self.quiz_service.end_quiz(user_id)
        
        if is_correct:
            embed = discord.Embed(
                title="✅ Bonne réponse !",
                description=f"Bravo ! La réponse était bien **{correct_answer.capitalize()}** !",
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
                description=f"La bonne réponse était **{correct_answer.capitalize()}**.",
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
        embed.set_footer(text="Utilise /quiz pour une nouvelle question !")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="stats", description="Affiche tes statistiques de quiz")
    async def stats(self, interaction: discord.Interaction):
        """Affiche les statistiques de l'utilisateur."""
        user_stats = self.stats_service.get_user_stats(interaction.user.id)
        
        if not user_stats:
            await interaction.response.send_message(
                "📊 Tu n'as pas encore répondu à un quiz ! Utilise `/quiz` pour commencer.",
                ephemeral=True
            )
            return
        
        correct = user_stats["correct"]
        wrong = user_stats["wrong"]
        total = user_stats["total"]
        points = user_stats.get("points", 0)
        percentage = (correct / total * 100) if total > 0 else 0
        
        embed = discord.Embed(
            title=f"📊 Statistiques de {interaction.user.name}",
            color=discord.Color.blue()
        )
        embed.add_field(name="⭐ Points", value=str(points), inline=True)
        embed.add_field(name="✅ Bonnes réponses", value=str(correct), inline=True)
        embed.add_field(name="❌ Mauvaises réponses", value=str(wrong), inline=True)
        embed.add_field(name="📝 Total", value=str(total), inline=True)
        embed.add_field(name="📈 Taux de réussite", value=f"{percentage:.1f}%", inline=True)
        
        # Stats par difficulté
        by_diff = user_stats.get("by_difficulty", {})
        diff_stats = ""
        for diff, config in DIFFICULTY_CONFIG.items():
            diff_data = by_diff.get(diff, {"correct": 0, "wrong": 0})
            diff_total = diff_data["correct"] + diff_data["wrong"]
            if diff_total > 0:
                diff_pct = (diff_data["correct"] / diff_total * 100)
                diff_stats += f"{config['emoji']} {config['name']}: {diff_data['correct']}/{diff_total} ({diff_pct:.0f}%)\n"
        
        if diff_stats:
            embed.add_field(name="📋 Par difficulté", value=diff_stats, inline=False)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="leaderboard", description="Affiche le classement des meilleurs joueurs")
    async def leaderboard(self, interaction: discord.Interaction):
        """Affiche le classement des joueurs."""
        sorted_users = self.stats_service.get_leaderboard(10, sort_by="points")
        
        if not sorted_users:
            await interaction.response.send_message(
                "📊 Aucune statistique disponible pour le moment.",
                ephemeral=True
            )
            return
        
        embed = discord.Embed(
            title="🏆 Classement Mythologie",
            color=discord.Color.gold()
        )
        
        medals = ["🥇", "🥈", "🥉"]
        description = ""
        
        for i, (user_id, user_stats) in enumerate(sorted_users):
            medal = medals[i] if i < 3 else f"**{i+1}.**"
            points = user_stats.get("points", 0)
            correct = user_stats["correct"]
            description += f"{medal} {user_stats['username']} - ⭐ {points} pts ({correct} ✅)\n"
        
        embed.description = description
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(QuizCog(bot))