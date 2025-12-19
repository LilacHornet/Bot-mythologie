import discord
import asyncio

from data.questions import DIFFICULTY_POINTS
from services.quiz_service import QUIZ_DURATION


class QuizHelpers:
    """Méthodes utilitaires pour le quiz."""
    
    def _get_points_for_difficulty(self, difficulty: str) -> int:
        """Retourne le nombre de points pour une difficulté."""
        return DIFFICULTY_POINTS.get(difficulty, 1)
    
    async def end_quiz_after_timeout(self, channel_id: int):
        """Termine automatiquement le quiz après le délai."""
        try:
            await asyncio.sleep(QUIZ_DURATION)
            
            # Vérifier si le quiz existe toujours
            if not self.quiz_service.get_active_quiz(channel_id):
                return
            
            # Récupérer les infos avant de terminer
            quiz_data = self.quiz_service.get_active_quiz(channel_id)
            if not quiz_data:
                return
            
            question_data = quiz_data["question"]
            difficulty = quiz_data["difficulty"]
            correct_answer = question_data["answer"]
            diff_config = self.quiz_service.get_difficulty_config(difficulty)
            results = self.quiz_service.get_quiz_results(channel_id)
            
            # Terminer le quiz
            self.quiz_service.end_quiz(channel_id)
            
            # Créer l'embed de fin
            embed = discord.Embed(
                title="⏰ Temps écoulé !",
                description=f"**Question:** {question_data['question']}",
                color=discord.Color.orange()
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
                    value="Personne n'a répondu ! 😢",
                    inline=False
                )
            
            embed.set_footer(text="Utilisez /quiz pour lancer un nouveau quiz !")
            
            # Envoyer le message de fin
            channel = self.bot.get_channel(channel_id)
            if channel:
                await channel.send(embed=embed)
            
            # Nettoyer le timer
            if channel_id in self.quiz_timers:
                del self.quiz_timers[channel_id]
                
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"Erreur lors de la fin du quiz: {e}")