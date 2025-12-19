import discord
from discord import app_commands
from discord.ext import commands
import os
import sys

# Ajouter le chemin parent pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.quiz_service import QuizService
from services.stats_service import StatsService


class QuizCog(commands.Cog):
    """Cog pour les commandes de quiz."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.quiz_service = QuizService()
        self.stats_service = StatsService()
    
    @app_commands.command(name="quiz", description="Réponds à une question sur la mythologie !")
    async def quiz(self, interaction: discord.Interaction):
        """Pose une question de mythologie à l'utilisateur."""
        question_data = self.quiz_service.start_quiz(interaction.user.id)
        
        embed = discord.Embed(
            title="🏛️ Quiz Mythologie",
            description=question_data["question"],
            color=discord.Color.gold()
        )
        embed.set_footer(text="Utilisez /answer pour répondre !")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="answer", description="Réponds à la question du quiz")
    async def answer(self, interaction: discord.Interaction, reponse: str):
        """Vérifie la réponse de l'utilisateur."""
        user_id = interaction.user.id
        
        if not self.quiz_service.has_active_quiz(user_id):
            await interaction.response.send_message(
                "❌ Tu n'as pas de quiz en cours ! Utilise `/quiz` pour commencer.",
                ephemeral=True
            )
            return
        
        is_correct, correct_answer = self.quiz_service.check_answer(user_id, reponse)
        
        # Sauvegarder les stats
        self.stats_service.update_user_stats(user_id, interaction.user.name, is_correct)
        
        # Terminer le quiz
        self.quiz_service.end_quiz(user_id)
        
        if is_correct:
            embed = discord.Embed(
                title="✅ Bonne réponse !",
                description=f"Bravo ! La réponse était bien **{correct_answer.capitalize()}** !",
                color=discord.Color.green()
            )
        else:
            embed = discord.Embed(
                title="❌ Mauvaise réponse !",
                description=f"La bonne réponse était **{correct_answer.capitalize()}**.",
                color=discord.Color.red()
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
        percentage = (correct / total * 100) if total > 0 else 0
        
        embed = discord.Embed(
            title=f"📊 Statistiques de {interaction.user.name}",
            color=discord.Color.blue()
        )
        embed.add_field(name="✅ Bonnes réponses", value=str(correct), inline=True)
        embed.add_field(name="❌ Mauvaises réponses", value=str(wrong), inline=True)
        embed.add_field(name="📝 Total", value=str(total), inline=True)
        embed.add_field(name="📈 Taux de réussite", value=f"{percentage:.1f}%", inline=False)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="leaderboard", description="Affiche le classement des meilleurs joueurs")
    async def leaderboard(self, interaction: discord.Interaction):
        """Affiche le classement des joueurs."""
        sorted_users = self.stats_service.get_leaderboard(10)
        
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
            percentage = (user_stats["correct"] / user_stats["total"] * 100) if user_stats["total"] > 0 else 0
            description += f"{medal} {user_stats['username']} - {user_stats['correct']} ✅ ({percentage:.1f}%)\n"
        
        embed.description = description
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(QuizCog(bot))