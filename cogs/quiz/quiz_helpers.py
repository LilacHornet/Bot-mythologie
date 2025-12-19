import discord
import asyncio

from data.questions import DIFFICULTY_POINTS
from services.quiz_service import QUIZ_DURATION


class QuizHelpers:
    """Méthodes utilitaires pour le quiz."""
    
    def _get_points_for_difficulty(self, difficulty: str) -> int:
        """Retourne les points pour une difficulté."""
        return DIFFICULTY_POINTS.get(difficulty, 1)
    
    async def end_quiz_after_timeout(self, channel_id: int):
        """Termine le quiz après le timeout."""
        await asyncio.sleep(QUIZ_DURATION)
        
        if not self.quiz_service.get_active_quiz(channel_id):
            return
        
        embed = self._build_timeout_embed(channel_id)
        self.quiz_service.end_quiz(channel_id)
        
        try:
            channel = self.bot.get_channel(channel_id)
            if channel:
                await channel.send(embed=embed)
        except Exception as e:
            print(f"Erreur lors de l'envoi du résultat: {e}")
    
    def _build_timeout_embed(self, channel_id: int) -> discord.Embed:
        """Construit l'embed de timeout."""
        quiz_data = self.quiz_service.get_active_quiz(channel_id)
        question_data = quiz_data["question"]
        difficulty = quiz_data["difficulty"]
        diff_config = self.quiz_service.get_difficulty_config(difficulty)
        results = self.quiz_service.get_quiz_results(channel_id)
        
        embed = discord.Embed(
            title="⏰ Temps écoulé !",
            description=f"**Question:** {question_data['question']}",
            color=discord.Color.orange()
        )
        embed.add_field(name="✅ Réponse", value=f"**{question_data['answer'].capitalize()}**", inline=True)
        embed.add_field(name="Difficulté", value=f"{diff_config['emoji']} {diff_config['name']}", inline=True)
        
        self._add_timeout_results(embed, results)
        embed.set_footer(text="Utilisez /quiz pour un nouveau quiz !")
        
        return embed
    
    def _add_timeout_results(self, embed: discord.Embed, results: list):
        """Ajoute les résultats à l'embed de timeout."""
        if not results:
            embed.add_field(name="👥 Participants", value="Personne n'a répondu !", inline=False)
            return
        
        correct = sum(1 for r in results if r["is_correct"])
        embed.add_field(
            name="👥 Résultats",
            value=f"{len(results)} participant(s) • ✅ {correct} bonne(s) réponse(s)",
            inline=False
        )
        
        winners = [r for r in results if r["is_correct"]]
        if winners:
            text = "\n".join([f"⭐ {w['username']} (+{w['points']} pts)" for w in winners[:5]])
            embed.add_field(name="🏆 Gagnants", value=text, inline=False)